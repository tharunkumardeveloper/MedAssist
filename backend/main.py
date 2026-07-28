import json
import logging
from collections import Counter
from datetime import datetime, timedelta
from typing import List, Literal, Optional

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth import create_access_token, get_current_user, hash_password, require_role
from config import settings
from database import Assessment, User, get_db, init_db
from predict import CONDITION_LABELS, SYMPTOM_VOCABULARY, run_assessment
from routers.admin_routes import router as admin_router
from routers.auth_routes import router as auth_router
from routers.patient_routes import router as patient_router
from routers.report_routes import router as report_router
from roles import CLINICAL_STAFF_ROLES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("medassist.main")

app = FastAPI(title="MedAssist AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS allowed origins: %s", settings.cors_origin_list)
logger.info("Database: %s", settings.database_url)


@app.exception_handler(Exception)
async def log_unhandled_exceptions(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


init_db()


def bootstrap_admin():
    if not (settings.bootstrap_admin_email and settings.bootstrap_admin_password):
        return
    from database import SessionLocal

    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.role == "admin").first()
        if existing_admin:
            return
        existing_email = db.query(User).filter(User.email == settings.bootstrap_admin_email).first()
        if existing_email:
            logger.info("Bootstrap admin email already registered with a non-admin role; skipping.")
            return
        admin = User(
            email=settings.bootstrap_admin_email,
            password_hash=hash_password(settings.bootstrap_admin_password),
            role="admin",
        )
        db.add(admin)
        db.commit()
        logger.info("Bootstrap admin account created: %s", settings.bootstrap_admin_email)
    finally:
        db.close()


bootstrap_admin()

app.include_router(auth_router, tags=["auth"])
app.include_router(report_router, tags=["reports"])
app.include_router(patient_router, tags=["patient"])
app.include_router(admin_router, tags=["admin"])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/reference-data")
def reference_data():
    """Static vocab the frontend needs to build the interactive symptom
    picker and lifestyle risk-screening form without hardcoding it."""
    return {
        "symptoms": SYMPTOM_VOCABULARY,
        "risk_conditions": [{"key": k, "label": v} for k, v in CONDITION_LABELS.items()],
        "smoker_status_options": [
            {"value": 4, "label": "Never smoked"},
            {"value": 3, "label": "Former smoker"},
            {"value": 2, "label": "Current smoker (some days)"},
            {"value": 1, "label": "Current smoker (every day)"},
        ],
    }


class LifestyleProfile(BaseModel):
    age: int = Field(..., ge=0, le=120)
    sex: Literal["male", "female"]
    bmi: float = Field(..., ge=10, le=80)
    smoker_status: int = Field(..., ge=1, le=4)
    exercise: bool
    high_cholesterol: bool
    high_blood_pressure: bool
    alcohol_days_per_month: int = Field(0, ge=0, le=30)


class PatientInput(BaseModel):
    symptoms: List[str] = Field(..., min_length=1)
    age: int = Field(..., ge=0, le=120)
    gender: Literal["male", "female"]
    blood_pressure: Literal["normal", "low", "high"] = "normal"
    cholesterol_level: Literal["normal", "high"] = "normal"
    lifestyle: Optional[LifestyleProfile] = None
    risk_conditions: Optional[List[str]] = None


@app.post("/assess")
def assess(
    patient: PatientInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    input_dict = patient.model_dump()
    result = run_assessment(
        symptoms=patient.symptoms,
        age=patient.age,
        gender=patient.gender,
        blood_pressure=patient.blood_pressure,
        cholesterol_level=patient.cholesterol_level,
        lifestyle=input_dict.get("lifestyle"),
        risk_conditions=patient.risk_conditions,
    )

    record = Assessment(
        user_id=current_user.id,
        input_json=json.dumps(input_dict),
        result_json=json.dumps(result),
        risk_flag=result["risk_assessment"]["flag"],
    )
    db.add(record)
    db.commit()

    logger.info(
        "Assessment recorded: user_id=%s risk_flag=%s",
        current_user.id, result["risk_assessment"]["flag"],
    )
    return result


@app.get("/history")
def history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(Assessment).filter(Assessment.user_id == current_user.id).all()
    return [
        {
            "id": r.id,
            "input": json.loads(r.input_json),
            "result": json.loads(r.result_json),
            "risk_flag": r.risk_flag,
            "created_at": r.created_at.isoformat(),
        }
        for r in records
    ]


AGE_BUCKETS = [(0, 18), (19, 35), (36, 50), (51, 65), (66, 200)]
AGE_BUCKET_LABELS = ["0-18", "19-35", "36-50", "51-65", "66+"]


def age_bucket_label(age: int) -> str:
    for (low, high), label in zip(AGE_BUCKETS, AGE_BUCKET_LABELS):
        if low <= age <= high:
            return label
    return "Unknown"


@app.get("/analytics")
def analytics(
    current_user: User = Depends(require_role(*CLINICAL_STAFF_ROLES)),
    db: Session = Depends(get_db),
):
    all_records = db.query(Assessment).order_by(Assessment.created_at.asc()).all()

    empty_days = []
    today = datetime.utcnow().date()
    for i in range(13, -1, -1):
        empty_days.append((today - timedelta(days=i)).isoformat())

    if not all_records:
        return {
            "total_assessments": 0,
            "total_patients": 0,
            "risk_flag_distribution": {},
            "top_predicted_diseases": [],
            "assessments_per_day": [{"date": d, "count": 0} for d in empty_days],
            "gender_distribution": {},
            "age_distribution": {label: 0 for label in AGE_BUCKET_LABELS},
        }

    risk_counts = Counter()
    disease_counts = Counter()
    gender_counts = Counter()
    age_counts = Counter()
    per_day_counts = Counter()
    user_ids = set()

    for r in all_records:
        risk_counts[r.risk_flag] += 1
        user_ids.add(r.user_id)
        per_day_counts[r.created_at.date().isoformat()] += 1

        input_data = json.loads(r.input_json)
        gender_counts[input_data.get("gender", "unknown")] += 1
        age = input_data.get("age")
        if isinstance(age, int):
            age_counts[age_bucket_label(age)] += 1

        result = json.loads(r.result_json)
        for d in result["disease_prediction"]["top_possible_diseases"]:
            disease_counts[d["disease_canonical"]] += 1

    top_diseases = disease_counts.most_common(10)

    return {
        "total_assessments": len(all_records),
        "total_patients": len(user_ids),
        "risk_flag_distribution": dict(risk_counts),
        "top_predicted_diseases": [{"disease": d, "count": c} for d, c in top_diseases],
        "assessments_per_day": [{"date": d, "count": per_day_counts.get(d, 0)} for d in empty_days],
        "gender_distribution": dict(gender_counts),
        "age_distribution": {label: age_counts.get(label, 0) for label in AGE_BUCKET_LABELS},
    }


TRIAGE_FLAGS = ("HIGH PRIORITY", "REVIEW")


@app.get("/triage")
def triage_queue(
    current_user: User = Depends(require_role(*CLINICAL_STAFF_ROLES)),
    db: Session = Depends(get_db),
    limit: int = 100,
):
    """Cross-patient list of flagged assessments needing clinical follow-up
    (the spec's "Emergency case identification" requirement)."""
    records = (
        db.query(Assessment, User)
        .join(User, Assessment.user_id == User.id)
        .filter(Assessment.risk_flag.in_(TRIAGE_FLAGS))
        .order_by(Assessment.created_at.desc())
        .limit(limit)
        .all()
    )

    items = []
    for r, patient in records:
        result = json.loads(r.result_json)
        top_disease = result["disease_prediction"]["top_possible_diseases"]
        items.append({
            "id": r.id,
            "patient_email": patient.email,
            "risk_flag": r.risk_flag,
            "priority_score": round(min(result["risk_assessment"]["priority_score"] / 3, 1.0), 3),
            "top_disease": top_disease[0]["disease_canonical"] if top_disease else None,
            "reported_symptoms": result["symptom_analysis"]["reported_symptoms"],
            "created_at": r.created_at.isoformat(),
        })

    return {
        "count": len(items),
        "items": items,
    }


@app.get("/me/summary")
def my_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Personal health summary powering the patient dashboard."""
    records = (
        db.query(Assessment)
        .filter(Assessment.user_id == current_user.id)
        .order_by(Assessment.created_at.asc())
        .all()
    )

    if not records:
        return {
            "total_assessments": 0,
            "latest_health_score": None,
            "latest_risk_flag": None,
            "latest_created_at": None,
            "health_score_trend": [],
            "recent_assessments": [],
        }

    trend = []
    for r in records:
        result = json.loads(r.result_json)
        health_score = result.get("health_score")
        if health_score is None:
            health_score = round((1 - result["risk_assessment"]["priority_score"]) * 100)
        trend.append({"date": r.created_at.date().isoformat(), "health_score": health_score})

    latest = records[-1]
    latest_result = json.loads(latest.result_json)

    recent = []
    for r in reversed(records[-5:]):
        result = json.loads(r.result_json)
        top_disease = result["disease_prediction"]["top_possible_diseases"]
        recent.append({
            "id": r.id,
            "risk_flag": r.risk_flag,
            "top_disease": top_disease[0]["disease_canonical"] if top_disease else None,
            "created_at": r.created_at.isoformat(),
        })

    return {
        "total_assessments": len(records),
        "latest_health_score": trend[-1]["health_score"],
        "latest_risk_flag": latest.risk_flag,
        "latest_created_at": latest.created_at.isoformat(),
        "health_score_trend": trend[-14:],
        "recent_assessments": recent,
    }
