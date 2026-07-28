from pathlib import Path
import os

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Boolean, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

from config import settings

DATABASE_URL = settings.database_url

# For Vercel serverless, use /tmp directory for SQLite
if DATABASE_URL.startswith("sqlite:///"):
    if os.environ.get('VERCEL'):
        # On Vercel, use /tmp directory which is writable
        DATABASE_URL = "sqlite:////tmp/medassist.db"
    else:
        # Local development
        db_path = Path(DATABASE_URL.removeprefix("sqlite:///"))
        db_path.parent.mkdir(parents=True, exist_ok=True)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="patient")  # patient / provider / admin
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    assessments = relationship("Assessment", back_populates="user")
    profile = relationship("PatientProfile", back_populates="user", uselist=False)

class PatientProfile(Base):
    __tablename__ = "patient_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)  # ISO date string (YYYY-MM-DD)
    gender = Column(String, nullable=True)
    allergies = Column(Text, nullable=True)
    medical_history = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    input_json = Column(Text)
    result_json = Column(Text)
    risk_flag = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="assessments")

def _run_sqlite_migrations():
    """Add columns introduced after the initial schema to pre-existing SQLite databases.

    create_all() only creates missing tables, not missing columns on existing ones,
    so a dev DB created before `is_active` was added needs this to keep working.
    """
    if not DATABASE_URL.startswith("sqlite"):
        return
    with engine.connect() as conn:
        existing_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(users)"))}
        if "is_active" not in existing_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1"))
            conn.commit()

def init_db():
    Base.metadata.create_all(bind=engine)
    _run_sqlite_migrations()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()