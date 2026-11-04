from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.ai import AIJob

router = APIRouter(prefix="/admin/jobs", tags=["Admin AI Jobs"])

@router.get("")
def list_ai_jobs(limit: int = 50, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    jobs = db.query(AIJob).order_by(AIJob.created_at.desc()).limit(limit).all()
    return [
        {
            "id": str(j.id),
            "job_type": j.job_type,
            "model_name": j.model_name,
            "target_id": j.target_id,
            "status": j.status,
            "prompt_tokens": j.prompt_tokens,
            "completion_tokens": j.completion_tokens,
            "total_tokens": j.total_tokens,
            "estimated_cost_usd": j.estimated_cost_usd,
            "execution_time_ms": j.execution_time_ms,
            "error_message": j.error_message,
            "created_at": j.created_at.isoformat()
        }
        for j in jobs
    ]
