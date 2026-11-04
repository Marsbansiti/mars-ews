from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.audit import AuditLog
from app.schemas.dashboard import SystemSettingsSchema

router = APIRouter(prefix="/admin/settings", tags=["Admin System Settings"])

@router.get("", response_model=SystemSettingsSchema)
def get_settings(current_user = Depends(get_current_user)):
    return SystemSettingsSchema(
        emergency_publishing_pause=settings.EMERGENCY_PUBLISHING_PAUSE,
        auto_collect_interval_minutes=settings.AUTO_COLLECT_INTERVAL_MINUTES,
        auto_publish_delay_minutes=settings.AUTO_PUBLISH_DELAY_MINUTES,
        fact_validation_strict_mode=settings.FACT_VALIDATION_STRICT_MODE,
        openai_model=settings.OPENAI_MODEL,
        embedding_model=settings.OPENAI_EMBEDDING_MODEL
    )

@router.patch("", response_model=SystemSettingsSchema)
def update_settings(payload: SystemSettingsSchema, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    old_pause = settings.EMERGENCY_PUBLISHING_PAUSE
    settings.EMERGENCY_PUBLISHING_PAUSE = payload.emergency_publishing_pause
    settings.AUTO_COLLECT_INTERVAL_MINUTES = payload.auto_collect_interval_minutes
    settings.AUTO_PUBLISH_DELAY_MINUTES = payload.auto_publish_delay_minutes
    settings.FACT_VALIDATION_STRICT_MODE = payload.fact_validation_strict_mode
    settings.OPENAI_MODEL = payload.openai_model
    settings.OPENAI_EMBEDDING_MODEL = payload.embedding_model

    summary = "Updated newsroom automation settings"
    if old_pause != settings.EMERGENCY_PUBLISHING_PAUSE:
        status_txt = "ACTIVATED" if settings.EMERGENCY_PUBLISHING_PAUSE else "DEACTIVATED"
        summary = f"GLOBAL EMERGENCY PUBLISHING PAUSE {status_txt} by {current_user.email}"

    audit = AuditLog(
        user_id=current_user.id,
        action_type="SETTINGS_UPDATED",
        target_type="System",
        summary=summary,
        details=payload.model_dump(),
        performed_by=current_user.email
    )
    db.add(audit)
    db.commit()

    return payload
