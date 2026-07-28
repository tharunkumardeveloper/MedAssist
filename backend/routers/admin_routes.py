from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import require_role
from database import Assessment, User, get_db
from roles import ALL_ROLES, USER_MANAGER_ROLES, can_manage_target

router = APIRouter(prefix="/admin")


@router.get("/users")
def list_users(
    current_user: User = Depends(require_role(*USER_MANAGER_ROLES)),
    db: Session = Depends(get_db),
):
    users = db.query(User).order_by(User.created_at.asc()).all()
    assessment_counts = {}
    for (user_id,) in db.query(Assessment.user_id).all():
        assessment_counts[user_id] = assessment_counts.get(user_id, 0) + 1

    return [
        {
            "id": u.id,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat(),
            "assessment_count": assessment_counts.get(u.id, 0),
        }
        for u in users
    ]


class UserUpdateInput(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None


@router.patch("/users/{user_id}")
def update_user(
    user_id: int,
    data: UserUpdateInput,
    current_user: User = Depends(require_role(*USER_MANAGER_ROLES)),
    db: Session = Depends(get_db),
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    if target.id == current_user.id and (
        (data.role is not None and data.role != current_user.role)
        or (data.is_active is False)
    ):
        raise HTTPException(status_code=400, detail="You cannot change your own role or deactivate yourself")

    if data.role is not None and data.role not in ALL_ROLES:
        raise HTTPException(status_code=400, detail=f"Role must be one of {ALL_ROLES}")

    if not can_manage_target(current_user.role, target.role, data.role):
        raise HTTPException(
            status_code=403,
            detail="Clinic admins can only manage patient/nurse/provider accounts and cannot grant admin-level roles",
        )

    if data.role is not None:
        target.role = data.role

    if data.is_active is not None:
        target.is_active = data.is_active

    db.commit()
    db.refresh(target)
    return {
        "id": target.id,
        "email": target.email,
        "role": target.role,
        "is_active": target.is_active,
        "created_at": target.created_at.isoformat(),
    }
