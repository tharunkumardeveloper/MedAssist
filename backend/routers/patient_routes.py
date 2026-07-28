from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import get_current_user
from database import PatientProfile, User, get_db

router = APIRouter()


class ProfileInput(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None  # YYYY-MM-DD
    gender: Optional[str] = None
    allergies: Optional[str] = None
    medical_history: Optional[str] = None


class ProfileOutput(ProfileInput):
    updated_at: Optional[str] = None


@router.get("/profile", response_model=ProfileOutput)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
    if not profile:
        return ProfileOutput()
    return ProfileOutput(
        full_name=profile.full_name,
        date_of_birth=profile.date_of_birth,
        gender=profile.gender,
        allergies=profile.allergies,
        medical_history=profile.medical_history,
        updated_at=profile.updated_at.isoformat() if profile.updated_at else None,
    )


@router.put("/profile", response_model=ProfileOutput)
def upsert_profile(
    data: ProfileInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
    if not profile:
        profile = PatientProfile(user_id=current_user.id)
        db.add(profile)

    for field, value in data.model_dump().items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return ProfileOutput(
        full_name=profile.full_name,
        date_of_birth=profile.date_of_birth,
        gender=profile.gender,
        allergies=profile.allergies,
        medical_history=profile.medical_history,
        updated_at=profile.updated_at.isoformat() if profile.updated_at else None,
    )
