from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.articles import Article
from app.models.sources import NewsSource
from app.models.taxonomy import Category
from app.models.audit import AnalyticsEvent

router = APIRouter(prefix="/admin/analytics", tags=["Admin Analytics"])

@router.get("")
def get_analytics(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # 1. Category Distribution
    cat_counts = (
        db.query(Category.name, func.count(Article.id))
        .join(Article, Article.category_id == Category.id, isouter=True)
        .group_by(Category.name)
        .all()
    )
    category_data = [{"category": name, "count": count or 0} for name, count in cat_counts]

    # 2. Risk Level Breakdown
    risk_counts = (
        db.query(Article.risk_level, func.count(Article.id))
        .group_by(Article.risk_level)
        .all()
    )
    risk_data = [{"risk_level": risk or "LOW", "count": count} for risk, count in risk_counts]

    # 3. Source Status Breakdown
    source_stats = (
        db.query(NewsSource.permission_status, func.count(NewsSource.id))
        .group_by(NewsSource.permission_status)
        .all()
    )
    source_data = [{"status": status, "count": count} for status, count in source_stats]

    # 4. Total Views Recorded
    total_views = db.query(func.count(AnalyticsEvent.id)).scalar() or 0

    return {
        "total_article_views": total_views,
        "category_distribution": category_data,
        "risk_breakdown": risk_data,
        "sources_breakdown": source_data
    }
