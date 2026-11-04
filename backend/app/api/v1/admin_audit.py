from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.audit import AuditLog

router = APIRouter(prefix="/admin/audit", tags=["Admin Audit Logs"])

@router.get("")
def list_audit_logs(
    action_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    q = db.query(AuditLog)
    if action_type:
        q = q.filter(AuditLog.action_type == action_type)

    logs = q.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
    return [
        {
            "id": str(l.id),
            "action_type": l.action_type,
            "target_type": l.target_type,
            "target_id": l.target_id,
            "summary": l.summary,
            "details": l.details,
            "performed_by": l.performed_by,
            "created_at": l.created_at.isoformat()
        }
        for l in logs
    ]
