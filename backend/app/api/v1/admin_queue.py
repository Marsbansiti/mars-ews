from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.queue import PublishingQueueItem
from app.models.articles import Article
from app.services.publishing import auto_publish_ready_clusters

router = APIRouter(prefix="/admin/queue", tags=["Admin Publishing Queue"])

@router.get("")
def list_publishing_queue(status: Optional[str] = None, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    q = db.query(PublishingQueueItem)
    if status:
        q = q.filter(PublishingQueueItem.status == status)

    queue_items = q.order_by(PublishingQueueItem.scheduled_for.desc()).limit(100).all()
    return [
        {
            "id": str(qi.id),
            "article_id": str(qi.article_id),
            "headline": qi.article.headline if qi.article else "Unknown",
            "status": qi.status,
            "scheduled_for": qi.scheduled_for.isoformat(),
            "retry_count": qi.retry_count,
            "error_log": qi.error_log
        }
        for qi in queue_items
    ]

@router.post("/process-batch")
def process_batch(max_articles: int = 5, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    res = auto_publish_ready_clusters(db, max_articles=max_articles)
    return res
