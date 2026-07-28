"""PDF generation for MedAssist health assessment reports.

Kept separate from the route handler so the visual/layout logic (gauges,
charts, letterhead, footer) can be read and modified independently of the
request-handling and auth code in routers/report_routes.py.
"""

from datetime import datetime

from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics.shapes import Drawing, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

BRAND_COLOR = colors.HexColor("#1d70f0")
DARK_COLOR = colors.HexColor("#152a56")
GREEN = colors.HexColor("#059669")
AMBER = colors.HexColor("#d97706")
RED = colors.HexColor("#e11d48")

FLAG_COLORS = {"HIGH PRIORITY": RED, "REVIEW": AMBER, "LOW": GREEN}

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="SectionHeading", parent=styles["Heading2"],
                           textColor=DARK_COLOR, spaceBefore=14, spaceAfter=6))
styles.add(ParagraphStyle(name="Small", parent=styles["Normal"], fontSize=9, textColor=colors.grey))
styles.add(ParagraphStyle(name="BigNumber", parent=styles["Normal"], fontSize=28, leading=32,
                           alignment=1, textColor=colors.white))
styles.add(ParagraphStyle(name="BigNumberLabel", parent=styles["Normal"], fontSize=10, leading=12,
                           alignment=1, textColor=colors.white))


def score_color(score: int):
    if score >= 70:
        return GREEN
    if score >= 40:
        return AMBER
    return RED


def health_score_badge(score: int) -> Table:
    color = score_color(score)
    cell = Table(
        [[Paragraph(str(score), styles["BigNumber"])],
         [Paragraph("Health Score / 100", styles["BigNumberLabel"])]],
        colWidths=[1.8 * inch],
    )
    cell.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("TOPPADDING", (0, 0), (-1, 0), 14),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 12),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
    ]))
    return cell


def risk_gauge(priority_score: float) -> Drawing:
    width, height = 320, 34
    d = Drawing(width, height)
    zones = [(0.0, 0.3, GREEN), (0.3, 0.6, AMBER), (0.6, 1.0, RED)]
    for start, end, color in zones:
        d.add(Rect(width * start, 8, width * (end - start), 14, fillColor=color, strokeColor=None))

    marker_x = max(4, min(width - 4, width * priority_score))
    d.add(Polygon(points=[marker_x - 6, 26, marker_x + 6, 26, marker_x, 32], fillColor=DARK_COLOR, strokeColor=None))
    d.add(String(marker_x, 2, f"{priority_score:.0%}", fontSize=8, fillColor=DARK_COLOR, textAnchor="middle"))
    d.add(String(0, 26, "LOW", fontSize=7, fillColor=colors.grey))
    d.add(String(width / 2 - 10, 26, "REVIEW", fontSize=7, fillColor=colors.grey))
    d.add(String(width - 22, 26, "HIGH", fontSize=7, fillColor=colors.grey))
    return d


def disease_match_chart(top_diseases: list) -> Drawing:
    if not top_diseases:
        return Drawing(1, 1)
    names = [d["disease_canonical"] for d in top_diseases]
    ratios = [round(d.get("confidence_pct", 0)) for d in top_diseases]

    chart_height = max(60, 36 * len(names))
    d = Drawing(400, chart_height)
    bc = HorizontalBarChart()
    bc.x = 90
    bc.y = 10
    bc.height = chart_height - 20
    bc.width = 260
    bc.data = [ratios]
    bc.categoryAxis.categoryNames = names
    bc.categoryAxis.labels.fontSize = 8
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 100
    bc.valueAxis.labels.fontSize = 7
    bc.bars[0].fillColor = BRAND_COLOR
    bc.barLabelFormat = "%s%%"
    bc.barLabels.fontSize = 8
    bc.barLabels.dy = 0
    d.add(bc)
    return d


def build_pdf(filepath: str, *, patient_email: str, profile: dict | None,
              input_data: dict, result: dict, assessment_created_at: datetime,
              assessment_id: int):
    doc = SimpleDocTemplate(
        filepath, pagesize=letter,
        topMargin=0.65 * inch, bottomMargin=0.75 * inch,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
    )
    story = []

    # ---- Letterhead ----
    header_table = Table([[
        Paragraph("<b>MedAssist AI</b><br/><font size=9 color='grey'>AI-Powered Health Assessment Report</font>",
                  styles["Normal"]),
        Paragraph(
            f"Report #{assessment_id}<br/>"
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}<br/>"
            f"Assessed: {assessment_created_at.strftime('%Y-%m-%d %H:%M UTC')}",
            styles["Small"],
        ),
    ]], colWidths=[3.8 * inch, 2.5 * inch])
    header_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(header_table)
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", color=BRAND_COLOR, thickness=2))
    story.append(Spacer(1, 14))

    # ---- Patient info + health score side by side ----
    full_name = (profile or {}).get("full_name") or patient_email
    dob = (profile or {}).get("date_of_birth") or "-"
    allergies = (profile or {}).get("allergies") or "None recorded"
    medical_history = (profile or {}).get("medical_history") or "None recorded"

    info_rows = [
        ["Name", full_name],
        ["Email", patient_email],
        ["Date of Birth", dob],
        ["Age", str(input_data.get("age", "-"))],
        ["Gender", str(input_data.get("gender", "-")).title()],
        ["Blood Pressure", str(input_data.get("blood_pressure", "-")).title()],
        ["Cholesterol Level", str(input_data.get("cholesterol_level", "-")).title()],
        ["Known Allergies", allergies],
    ]
    info_table = Table(info_rows, colWidths=[1.5 * inch, 2.7 * inch])
    info_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8fafc")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    health_score = result.get("health_score", round((1 - result["risk_assessment"]["priority_score"]) * 100))
    top_row = Table([[info_table, health_score_badge(health_score)]], colWidths=[4.4 * inch, 2 * inch])
    top_row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (1, 0), (1, 0), "CENTER")]))
    story.append(Paragraph("Patient Information", styles["SectionHeading"]))
    story.append(top_row)

    if medical_history and medical_history != "None recorded":
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"<b>Relevant medical history considered:</b> {medical_history}", styles["Small"]))

    # ---- Symptom analysis ----
    story.append(Paragraph("Symptom Analysis", styles["SectionHeading"]))
    symptoms = result["symptom_analysis"]["reported_symptoms"]
    story.append(Paragraph(
        f"Reported symptoms ({result['symptom_analysis']['symptom_count']}): "
        f"{', '.join(symptoms) if symptoms else 'None reported'}", styles["Normal"]
    ))

    # ---- Disease prediction ----
    story.append(Paragraph("Disease Prediction", styles["SectionHeading"]))
    proba = result["disease_prediction"]["outcome_probability_positive"]
    confidence = result["disease_prediction"].get("prediction_confidence", "N/A")
    story.append(Paragraph(
        f"Model-estimated probability of a positive condition: <b>{proba:.1%}</b> "
        f"&nbsp;&middot;&nbsp; Prediction confidence: <b>{confidence}</b>", styles["Normal"]
    ))
    story.append(Spacer(1, 8))

    top_diseases = result["disease_prediction"]["top_possible_diseases"]
    disease_rows = [["Possible Condition", "Reference Risk Level", "Confidence"]]
    for d in top_diseases:
        disease_rows.append([
            d["disease_canonical"].title(),
            str(d.get("risk_category", "unknown")).title(),
            f"{d.get('confidence_pct', 0):.1f}%",
        ])
    disease_table = Table(disease_rows, colWidths=[2.4 * inch, 1.5 * inch, 1.3 * inch])
    disease_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BACKGROUND", (0, 0), (-1, 0), DARK_COLOR),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(KeepTogether([disease_table, Spacer(1, 10), disease_match_chart(top_diseases)]))

    # ---- Risk assessment ----
    story.append(Paragraph("Risk Assessment", styles["SectionHeading"]))
    risk = result["risk_assessment"]
    flag = risk["flag"]
    flag_color = FLAG_COLORS.get(flag, colors.black)
    normalized_priority = min(risk["priority_score"] / 3, 1.0)
    story.append(Paragraph(
        f"<font color='{flag_color}'><b>{flag}</b></font> &nbsp;&middot;&nbsp; "
        f"Severity: <b>{risk.get('severity_level', 'N/A')}</b> &nbsp;&middot;&nbsp; "
        f"Priority score: <b>{normalized_priority:.0%}</b>", styles["Normal"]
    ))
    story.append(Spacer(1, 6))
    story.append(risk_gauge(normalized_priority))

    if risk.get("emergency_case"):
        story.append(Spacer(1, 8))
        reason = risk.get("emergency_reason", "High-risk symptom pattern detected.")
        alert = Table([[Paragraph(
            f"&#9888; This assessment was flagged as a potential <b>emergency case</b>: {reason}. "
            "Seek immediate medical attention.",
            ParagraphStyle(name="Alert", parent=styles["Normal"], textColor=colors.white)
        )]], colWidths=[6.3 * inch])
        alert.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), RED),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(alert)

    # ---- Lifestyle risk screening (Model 2 — BRFSS) ----
    lifestyle_risk = result.get("lifestyle_risk_screening")
    if lifestyle_risk:
        story.append(Paragraph("Chronic Condition Risk Screening", styles["SectionHeading"]))
        risk_rows = [["Condition", "Risk Probability", "Flagged"]]
        for c in lifestyle_risk:
            risk_rows.append([
                c["label"], f"{c['risk_probability']:.0%}", "Yes" if c["flagged_at_risk"] else "No",
            ])
        risk_table = Table(risk_rows, colWidths=[2.4 * inch, 1.8 * inch, 1.2 * inch])
        risk_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("BACKGROUND", (0, 0), (-1, 0), DARK_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(risk_table)
        story.append(Paragraph(
            "Based on a population-scale CDC BRFSS survey model, independent of the symptom-based prediction above.",
            styles["Small"],
        ))

    # ---- Care plan ----
    story.append(Paragraph("Treatment & Care Plan", styles["SectionHeading"]))
    care_plan = result.get("care_plan", {})
    recs = result["recommendations"]
    care_rows = [
        ["Suggested care", recs.get("suggested_cures") or "-"],
        ["Recommended specialist", recs.get("suggested_doctor") or "-"],
        ["Preventive care", care_plan.get("preventive_care", "-")],
        ["Lifestyle advice", care_plan.get("lifestyle_advice", "-")],
        ["Follow-up guidance", care_plan.get("follow_up_guidance", "-")],
    ]
    care_table = Table(care_rows, colWidths=[1.6 * inch, 4.7 * inch])
    care_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8fafc")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(care_table)

    notes_examples = recs.get("real_world_treatment_examples") or []
    if notes_examples:
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            "<b>Reference: similar real-world hospital discharge cases</b> "
            "(from de-identified MIMIC-IV notes; illustrative only, not a prescription):",
            styles["Small"],
        ))
        for ex in notes_examples:
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"<b>{ex['diagnosis_clean']}</b>", styles["Small"]))
            story.append(Paragraph(ex["medications_clean"][:600], styles["Small"]))

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#e2e8f0"), thickness=1))
    story.append(Spacer(1, 6))
    story.append(Paragraph(result["disclaimer"], styles["Small"]))
    story.append(Paragraph(
        "This report is confidential and intended solely for the named patient and their care team.",
        styles["Small"],
    ))

    def footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(0.7 * inch, 0.5 * inch, "Generated by MedAssist AI")
        canvas.drawRightString(letter[0] - 0.7 * inch, 0.5 * inch, f"Page {doc_.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
