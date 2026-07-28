import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import User, get_db
from auth import hash_password, verify_password, create_access_token, validate_password_strength
from rate_limit import enforce_rate_limit
from roles import SELF_SIGNUP_ROLES

router = APIRouter()
logger = logging.getLogger("medassist.auth")

class SignupInput(BaseModel):
    email: EmailStr
    password: str
    role: str = "patient"  # patient / nurse / provider — admin & clinic_admin are provisioned by an existing admin

@router.post("/signup")
def signup(data: SignupInput, request: Request, db: Session = Depends(get_db)):
    enforce_rate_limit(request, "signup")
    if data.role not in SELF_SIGNUP_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")
    validate_password_strength(data.password)
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=data.email, password_hash=hash_password(data.password), role=data.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("New signup: user_id=%s role=%s", user.id, user.role)
    return {"message": "Signup successful", "user_id": user.id, "role": user.role}

@router.post("/login")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    enforce_rate_limit(request, "login")
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        logger.warning("Failed login attempt for email=%s", form_data.username)
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = create_access_token({"sub": user.email})
    logger.info("Login: user_id=%s", user.id)
    return {"access_token": token, "token_type": "bearer", "role": user.role}