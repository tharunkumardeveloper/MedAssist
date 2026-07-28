import json
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from auth import get_current_user
from database import Assessment, PatientProfile, get_db
from report_builder import build_pdf

router = APIRouter()

REPORTS_DIR = "generated_reports"
os.makedirs(REPORTS_DIR, exist_ok=True)


@router.get("/report/{assessment_id}")
def generate_report(assessment_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Assessment not found")

    input_data = json.loads(record.input_json)
    result = json.loads(record.result_json)

    profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
    profile_dict = None
    if profile:
        profile_dict = {
            "full_name": profile.full_name,
            "date_of_birth": profile.date_of_birth,
            "gender": profile.gender,
            "allergies": profile.allergies,
            "medical_history": profile.medical_history,
        }

    filepath = os.path.join(REPORTS_DIR, f"report_{assessment_id}_{current_user.id}.pdf")

    build_pdf(
        filepath,
        patient_email=current_user.email,
        profile=profile_dict,
        input_data=input_data,
        result=result,
        assessment_created_at=record.created_at,
        assessment_id=assessment_id,
    )

    return FileResponse(filepath, media_type='application/pdf', filename=f"MedAssist_Report_{assessment_id}.pdf")
