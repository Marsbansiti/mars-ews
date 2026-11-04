from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash, require_admin
from app.models.users import User, Role
from app.models.audit import AuditLog

router = APIRouter(prefix="/admin/users", tags=["Admin User Management"])

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role_name: str = "Editor"

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role_name: Optional[str] = None
    is_active: Optional[bool] = None

@router.get("")
def list_users(db: Session = Depends(get_db), current_user = Depends(require_admin)):
    users = db.query(User).all()
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role.name if u.role else "Editor",
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat()
        }
        for u in users
    ]

@router.post("")
def create_user(payload: UserCreate, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    role = db.query(Role).filter(Role.name == payload.role_name).first()
    if not role:
        role = db.query(Role).filter(Role.name == "Editor").first()

    new_user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        role_id=role.id if role else None,
        is_active=True,
        is_verified=True
    )
    db.add(new_user)

    audit = AuditLog(
        user_id=current_user.id,
        action_type="USER_CREATED",
        target_type="User",
        target_id=str(new_user.id),
        summary=f"Created newsroom account for {new_user.email} [{payload.role_name}]",
        performed_by=current_user.email
    )
    db.add(audit)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "id": str(new_user.id)}
