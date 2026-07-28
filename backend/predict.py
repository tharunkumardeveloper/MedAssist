"""MedAssist prediction pipeline — three independent models behind one call:

  Model 1 — symptom-similarity matcher over 155 diseases (183-term symptom
            vocabulary) + a regularized outcome classifier, plus rule-based
            emergency-symptom detection.
  Model 2 — 10 independent BRFSS-trained risk screeners (diabetes, heart
            attack, coronary HD, stroke, asthma, skin cancer, other cancer,
            arthritis, depression, kidney disease).
  Model 3 — TF-IDF retrieval over real MIMIC-IV discharge notes, surfacing
            real prescribed medications for a free-text diagnosis query.

Each model reasons over structurally different data, so results are kept
separate (not merged into one blended score) and presented side by side.
"""

import ast
import os
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Support both local and Vercel deployment
MODEL_DIR = Path(os.environ.get('MODEL_PATH', Path(__file__).parent.parent / "model"))

# ---------------------------------------------------------------------------
# Load all three models' artifacts once at import time
# ---------------------------------------------------------------------------
mlb = joblib.load(MODEL_DIR / "model1_symptom_binarizer.pkl")
outcome_clf = joblib.load(MODEL_DIR / "model1_outcome_classifier.pkl")
outcome_features = joblib.load(MODEL_DIR / "model1_outcome_features.pkl")

risk_models = joblib.load(MODEL_DIR / "model2_brfss_risk_models.pkl")
diabetes_threshold = joblib.load(MODEL_DIR / "model2_diabetes_threshold.pkl")

tfidf = joblib.load(MODEL_DIR / "model3_tfidf_vectorizer.pkl")
treatment_reference = pd.read_csv(MODEL_DIR / "model3_diagnosis_medication_reference.csv").dropna(
    subset=["diagnosis_clean", "medications_clean"]
).reset_index(drop=True)
treatment_matrix = tfidf.transform(treatment_reference["diagnosis_clean"])


def _to_list(x):
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        try:
            v = ast.literal_eval(x)
            return v if isinstance(v, list) else []
        except (ValueError, SyntaxError):
            return [s.strip() for s in x.split(",")] if x else []
    return []


disease_table = pd.read_csv(MODEL_DIR / "model1_disease_symptom_table.csv")
disease_table["symptom_set"] = disease_table["symptom_set"].apply(_to_list)
symptom_matrix = mlb.transform(disease_table["symptom_set"])

SYMPTOM_VOCABULARY = sorted(mlb.classes_.tolist())

# ---------------------------------------------------------------------------
# Model 1a — symptom-similarity matcher
# ---------------------------------------------------------------------------
SYMPTOM_SYNONYMS = {
    "shortness of breath": "difficulty breathing", "sob": "difficulty breathing",
    "breathlessness": "difficulty breathing", "tiredness": "fatigue", "exhaustion": "fatigue",
}

EMERGENCY_SYMPTOM_FLAGS = {
    "chest pain", "difficulty breathing", "shortness of breath",
    "sudden weakness", "slurred speech", "loss of consciousness",
    "severe bleeding", "confusion",
}


def normalize_input_symptoms(symptom_list):
    return [SYMPTOM_SYNONYMS.get(s.lower().strip(), s.lower().strip()) for s in symptom_list]


def predict_disease_from_symptoms(input_symptoms, top_n=5):
    normalized = normalize_input_symptoms(input_symptoms)
    input_vec = mlb.transform([normalized])
    sims = cosine_similarity(input_vec, symptom_matrix)[0]
    ranked_idx = sims.argsort()[::-1][:top_n]
    results = disease_table.iloc[ranked_idx][
        ["disease_canonical", "risk_category", "risk_pct", "cures", "doctor"]
    ].copy()
    results["similarity_score"] = sims[ranked_idx]
    score_sum = results["similarity_score"].sum()
    results["confidence_pct"] = (
        (results["similarity_score"] / score_sum * 100).round(1) if score_sum > 0 else 0.0
    )
    return results.reset_index(drop=True)


def detect_emergency(input_symptoms, candidates=None):
    normalized = set(normalize_input_symptoms(input_symptoms))
    flagged = {normalize_input_symptoms([f])[0] for f in EMERGENCY_SYMPTOM_FLAGS}
    matched_flags = normalized & flagged

    high_risk_candidate = False
    if candidates is not None and len(candidates):
        top = candidates.iloc[0]
        high_risk_candidate = (top.get("risk_category") == "high") or (
            pd.notna(top.get("risk_pct")) and top["risk_pct"] >= 20
        )

    is_emergency = len(matched_flags) >= 2 or (len(matched_flags) >= 1 and high_risk_candidate)

    return {
        "emergency_flag": is_emergency,
        "matched_red_flag_symptoms": sorted(matched_flags),
        "reason": (
            "Multiple emergency-pattern symptoms reported" if len(matched_flags) >= 2
            else "Emergency-pattern symptom combined with a high-risk candidate condition" if is_emergency
            else "No emergency pattern detected"
        ),
    }


def assess_risk_from_symptoms(input_symptoms, top_n=3):
    matches = predict_disease_from_symptoms(input_symptoms, top_n=top_n)
    risk_weights = {"low": 1, "moderate": 2, "high": 3, "varies": 2, "unknown": 1}
    matches = matches.copy()
    matches["risk_score"] = matches["risk_category"].map(risk_weights).fillna(1)
    weighted_risk = (
        (matches["risk_score"] * matches["similarity_score"]).sum() / matches["similarity_score"].sum()
        if matches["similarity_score"].sum() > 0 else 1.0
    )
    emergency = detect_emergency(input_symptoms, matches)
    label = "high" if weighted_risk >= 2.5 else "moderate" if weighted_risk >= 1.5 else "low"
    return {
        "matches": matches,
        "overall_risk_score": round(float(weighted_risk), 2),
        "overall_risk_label": label,
        "emergency_flag": emergency["emergency_flag"],
        "emergency_reason": emergency["reason"],
        "matched_red_flag_symptoms": emergency["matched_red_flag_symptoms"],
    }


def outcome_probability(input_symptoms, age, gender, blood_pressure, cholesterol_level):
    """Model 1b — the regularized patient-outcome classifier (fever/cough/
    fatigue/difficulty-breathing flags + demographics), kept as a secondary,
    coarser signal alongside the primary symptom-similarity matcher."""
    normalized = set(normalize_input_symptoms(input_symptoms))
    encoded = {
        "fever": int("fever" in normalized),
        "cough": int("cough" in normalized),
        "fatigue": int("fatigue" in normalized),
        "difficulty_breathing": int("difficulty breathing" in normalized),
    }
    row = pd.DataFrame([encoded])
    for col in outcome_features:
        if col.startswith("gender_"):
            row[col] = int(col == f"gender_{gender.lower()}")
        elif col.startswith("blood_pressure_"):
            row[col] = int(col == f"blood_pressure_{blood_pressure.lower()}")
        elif col.startswith("cholesterol_level_"):
            row[col] = int(col == f"cholesterol_level_{cholesterol_level.lower()}")
    row = row.reindex(columns=outcome_features, fill_value=0)
    return float(outcome_clf.predict_proba(row)[:, 1][0])


# ---------------------------------------------------------------------------
# Model 2 — BRFSS chronic-condition risk screening
# ---------------------------------------------------------------------------
CONDITION_LABELS = {
    "diabetes": "Diabetes", "heart_attack": "Heart Attack", "coronary_hd": "Coronary Heart Disease",
    "stroke": "Stroke", "asthma": "Asthma", "skin_cancer": "Skin Cancer",
    "other_cancer": "Other Cancer", "arthritis": "Arthritis", "depression": "Depression",
    "kidney_disease": "Kidney Disease",
}
CONDITION_KEYS = list(CONDITION_LABELS.keys())
RISK_CAT_COLS = ["_AGEG5YR", "SEX", "_SMOKER3", "BPHIGH4"]


def age_to_ageg5yr(age: int) -> int:
    if age < 18:
        return 1
    if age >= 80:
        return 13
    return min(13, 1 + (age - 18) // 5)


def build_lifestyle_row(lifestyle: dict) -> dict:
    """lifestyle: {age, sex ('male'/'female'), bmi, smoker_status (1-4),
    exercise (bool), high_cholesterol (bool), high_blood_pressure (bool),
    alcohol_days_per_month (0-30)}"""
    return {
        "_BMI5": float(lifestyle["bmi"]),
        "EXERANY2": int(bool(lifestyle["exercise"])),
        "TOLDHI2": int(bool(lifestyle["high_cholesterol"])),
        "ALCDAY5": float(lifestyle.get("alcohol_days_per_month", 0)),
        "_AGEG5YR": age_to_ageg5yr(int(lifestyle["age"])),
        "SEX": 1 if lifestyle["sex"].lower().startswith("m") else 2,
        "_SMOKER3": int(lifestyle["smoker_status"]),
        "BPHIGH4": int(bool(lifestyle["high_blood_pressure"])),
    }


def assess_condition_risk(condition: str, lifestyle: dict) -> dict:
    info = risk_models[condition]
    raw = build_lifestyle_row(lifestyle)
    row = {k: v for k, v in raw.items() if k not in RISK_CAT_COLS}
    for col in RISK_CAT_COLS:
        row[f"{col}_{float(raw[col])}"] = 1
    X = pd.DataFrame([row]).reindex(columns=info["features"], fill_value=0)
    proba = float(info["model"].predict_proba(X)[0, 1])
    threshold = diabetes_threshold if condition == "diabetes" else 0.5
    return {
        "condition": condition,
        "label": CONDITION_LABELS[condition],
        "risk_probability": round(proba, 3),
        "flagged_at_risk": bool(proba >= threshold),
        "model_auc": round(float(info["auc"]), 3),
    }


def assess_lifestyle_risks(lifestyle: dict, conditions=None) -> list:
    conditions = conditions or CONDITION_KEYS
    return [assess_condition_risk(c, lifestyle) for c in conditions if c in risk_models]


# ---------------------------------------------------------------------------
# Model 3 — TF-IDF treatment retrieval from real discharge notes
# ---------------------------------------------------------------------------
def recommend_treatment_from_diagnosis(query_text: str, top_n=3):
    query_vec = tfidf.transform([query_text])
    sims = cosine_similarity(query_vec, treatment_matrix)[0]
    ranked_idx = sims.argsort()[::-1][:top_n]
    results = treatment_reference.iloc[ranked_idx][["diagnosis_clean", "medications_clean"]].copy()
    results["similarity_score"] = sims[ranked_idx]
    return results.reset_index(drop=True)


def recommend_treatment_from_table(disease_name: str):
    row = disease_table[disease_table["disease_canonical"] == disease_name]
    if row.empty:
        return None
    row = row.iloc[0]
    return {
        "disease": disease_name,
        "cures": row["cures"],
        "recommended_doctor": row["doctor"],
        "risk_level": row["risk_category"],
        "risk_percentage": row["risk_pct"] if pd.notna(row["risk_pct"]) else None,
    }


# ---------------------------------------------------------------------------
# Care-plan text + severity helpers (presentation layer, model-agnostic)
# ---------------------------------------------------------------------------
def severity_level(risk_score: float) -> str:
    if risk_score >= 2.5:
        return "Severe"
    if risk_score >= 1.5:
        return "Moderate"
    return "Mild"


def build_care_plan(flag: str, emergency: bool) -> dict:
    if flag == "HIGH PRIORITY" or emergency:
        preventive = "Monitor symptoms closely and avoid strenuous activity until evaluated by a clinician."
        follow_up = "Seek in-person medical evaluation within 24 hours."
    elif flag == "REVIEW":
        preventive = "Rest, stay hydrated, and monitor for any worsening of symptoms."
        follow_up = "Schedule a follow-up appointment within 3-5 days if symptoms persist or worsen."
    else:
        preventive = "Maintain a balanced diet, regular exercise, and adequate sleep to support recovery."
        follow_up = "No urgent follow-up required. Book a routine check-up if symptoms persist beyond a week."

    return {
        "preventive_care": preventive,
        "lifestyle_advice": "Maintain good hygiene, balanced nutrition, adequate hydration, and sufficient rest.",
        "follow_up_guidance": follow_up,
        "urgent_care_recommended": flag == "HIGH PRIORITY" or emergency,
    }


# ---------------------------------------------------------------------------
# Unified pipeline — orchestrates all three models behind one call
# ---------------------------------------------------------------------------
def run_assessment(
    symptoms: list,
    age: int,
    gender: str,
    blood_pressure: str = "normal",
    cholesterol_level: str = "normal",
    lifestyle: dict = None,
    risk_conditions: list = None,
) -> dict:
    candidates_df = predict_disease_from_symptoms(symptoms, top_n=5)
    risk = assess_risk_from_symptoms(symptoms, top_n=5)
    proba = outcome_probability(symptoms, age, gender, blood_pressure, cholesterol_level)

    label_to_flag = {"high": "HIGH PRIORITY", "moderate": "REVIEW", "low": "LOW"}
    flag = label_to_flag[risk["overall_risk_label"]]
    if risk["emergency_flag"]:
        flag = "HIGH PRIORITY"

    top_diseases = candidates_df[
        ["disease_canonical", "similarity_score", "confidence_pct", "risk_category", "risk_pct"]
    ].copy()
    top_diseases["similarity_score"] = top_diseases["similarity_score"].round(3)
    top_diseases_records = top_diseases.to_dict("records")
    for d in top_diseases_records:
        if pd.isna(d.get("risk_pct")):
            d["risk_pct"] = None

    top_disease_name = top_diseases_records[0]["disease_canonical"] if top_diseases_records else None
    treatment_from_table = recommend_treatment_from_table(top_disease_name) if top_disease_name else None
    treatment_from_notes = (
        recommend_treatment_from_diagnosis(top_disease_name, top_n=2).to_dict("records")
        if top_disease_name else []
    )

    lifestyle_risk = None
    if lifestyle:
        lifestyle_risk = assess_lifestyle_risks(lifestyle, risk_conditions)

    result = {
        "symptom_analysis": {
            "reported_symptoms": normalize_input_symptoms(symptoms),
            "symptom_count": len(symptoms),
        },
        "disease_prediction": {
            "outcome_probability_positive": round(proba, 3),
            "prediction_confidence": (
                "High" if proba > 0.8 or proba < 0.2 else "Moderate" if proba > 0.65 or proba < 0.35 else "Low"
            ),
            "top_possible_diseases": top_diseases_records,
        },
        "risk_assessment": {
            "priority_score": risk["overall_risk_score"],
            "flag": flag,
            "severity_level": severity_level(risk["overall_risk_score"]),
            "emergency_case": risk["emergency_flag"],
            "emergency_reason": risk["emergency_reason"],
            "matched_red_flag_symptoms": risk["matched_red_flag_symptoms"],
        },
        "recommendations": {
            "suggested_cures": treatment_from_table["cures"] if treatment_from_table else None,
            "suggested_doctor": treatment_from_table["recommended_doctor"] if treatment_from_table else None,
            "real_world_treatment_examples": treatment_from_notes,
        },
        "lifestyle_risk_screening": lifestyle_risk,
        "care_plan": build_care_plan(flag, risk["emergency_flag"]),
        "health_score": round((1 - min(risk["overall_risk_score"] / 3, 1)) * 100),
        "disclaimer": "This is a preliminary AI-generated assessment, not a medical diagnosis. Consult a healthcare professional.",
    }
    return result
