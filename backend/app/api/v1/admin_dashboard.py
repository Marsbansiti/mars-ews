from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.sources import NewsSource
from app.models.items import SourceItem
from app.models.articles import Article
from app.models.clusters import StoryCluster
from app.models.ai import AIJob
from app.models.audit import AuditLog
from app.schemas.dashboard import DashboardOverviewStats

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

@router.get("/dashboard", response_model=DashboardOverviewStats)
def get_dashboard_metrics(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

    total_sources = db.query(func.count(NewsSource.id)).scalar() or 0
    active_sources = db.query(func.count(NewsSource.id)).filter(NewsSource.enabled == True).scalar() or 0

    stories_collected_today = db.query(func.count(SourceItem.id)).filter(SourceItem.created_at >= today_start).scalar() or 0
    total_items = db.query(func.count(SourceItem.id)).scalar() or 0
    articles_processed = db.query(func.count(Article.id)).scalar() or 0
    articles_published = db.query(func.count(Article.id)).filter(Article.status == "PUBLISHED").scalar() or 0
    editorial_holds = db.query(func.count(Article.id)).filter(Article.status == "EDITORIAL_HOLD").scalar() or 0

    duplicate_items = db.query(func.count(SourceItem.id)).filter(SourceItem.processing_status == "DUPLICATE").scalar() or 0

    failed_ai_jobs = db.query(func.count(AIJob.id)).filter(AIJob.status == "FAILED").scalar() or 0
    ai_jobs_count = db.query(func.count(AIJob.id)).scalar() or 0
    total_tokens = db.query(func.sum(AIJob.total_tokens)).scalar() or 0
    estimated_cost = db.query(func.sum(AIJob.estimated_cost_usd)).scalar() or 0.0
    avg_latency = db.query(func.avg(AIJob.execution_time_ms)).scalar() or 0.0

    # Recent activity from audit logs
    recent_logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(8).all()
    activity = [
        {
            "id": str(log.id),
            "action": log.action_type,
            "summary": log.summary,
            "created_at": log.created_at.isoformat(),
            "performed_by": log.performed_by
        }
        for log in recent_logs
    ]

    return DashboardOverviewStats(
        total_sources=total_sources,
        active_sources=active_sources,
        stories_collected_today=stories_collected_today if stories_collected_today > 0 else total_items,
        articles_processed=articles_processed,
        articles_published=articles_published,
        duplicate_stories=duplicate_items,
        editorial_holds=editorial_holds,
        failed_tasks=failed_ai_jobs,
        ai_jobs_count=ai_jobs_count,
        total_tokens_used=int(total_tokens),
        estimated_api_cost_usd=round(float(estimated_cost), 4),
        average_processing_time_ms=round(float(avg_latency), 1),
        system_health="ONLINE" if not settings.EMERGENCY_PUBLISHING_PAUSE else "EMERGENCY_PAUSED",
        emergency_pause=settings.EMERGENCY_PUBLISHING_PAUSE,
        recent_activity=activity
    )
