from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.articles import Article, ArticleRevision, Correction
from app.models.audit import AuditLog
from app.schemas.article import ArticleUpdate, CorrectionCreate, ArticleDetailResponse
from app.api.v1.public import format_article_list_item
from app.services.search import index_article

router = APIRouter(prefix="/admin/articles", tags=["Admin Article Manager"])

@router.get("")
def list_admin_articles(
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    q = db.query(Article)
    if status:
        q = q.filter(Article.status == status)
    if risk_level:
        q = q.filter(Article.risk_level == risk_level)
    if category:
        q = q.filter(Article.category_id == category)

    articles = q.order_by(Article.created_at.desc()).offset(offset).limit(limit).all()
    return [format_article_list_item(a) for a in articles]

@router.get("/{id}")
def get_article_admin_detail(id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    article = db.query(Article).filter(Article.id == id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    base = format_article_list_item(article).model_dump()
    return ArticleDetailResponse(
        **base,
        content_body=article.content_body,
        seo_title=article.seo_title,
        seo_description=article.seo_description,
        ai_generated=article.ai_generated,
        risk_reasons=article.risk_reasons or [],
        sources=[s for s in article.sources],
        claims=[c for c in article.claims],
        revisions=[r for r in article.revisions],
        corrections=[c for c in article.corrections],
        tags=[t.name for t in article.tags]
    )

@router.patch("/{id}")
def update_article(
    id: str,
    payload: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    article = db.query(Article).filter(Article.id == id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    data = payload.model_dump(exclude_unset=True)
    reason = data.pop("change_reason", "Editor modification")

    for k, v in data.items():
        setattr(article, k, v)

    article.version += 1

    # Record revision
    rev = ArticleRevision(
        article_id=article.id,
        revision_number=article.version,
        headline=article.headline,
        summary=article.summary,
        content_body=article.content_body,
        changed_by=current_user.email,
        change_reason=reason
    )
    db.add(rev)

    audit = AuditLog(
        user_id=current_user.id,
        action_type="ARTICLE_EDITED",
        target_type="Article",
        target_id=str(article.id),
        summary=f"Article updated by {current_user.email}: {article.headline[:60]}",
        performed_by=current_user.email
    )
    db.add(audit)
    db.commit()
    db.refresh(article)

    if article.status == "PUBLISHED":
        index_article(article)

    return {"message": "Article updated successfully", "version": article.version}

@router.post("/{id}/publish")
def publish_article(id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    article = db.query(Article).filter(Article.id == id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.status = "PUBLISHED"
    article.published_at = datetime.now(timezone.utc)

    audit = AuditLog(
        user_id=current_user.id,
        action_type="ARTICLE_PUBLISHED",
        target_type="Article",
        target_id=str(article.id),
        summary=f"Published/Released hold by {current_user.email}: {article.headline[:60]}",
        performed_by=current_user.email
    )
    db.add(audit)
    db.commit()

    index_article(article)

    return {"message": "Article published successfully", "status": article.status, "published_at": article.published_at.isoformat()}

@router.post("/{id}/hold")
def hold_article(id: str, reason: str = "Editorial Hold by Newsroom Desk", db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    article = db.query(Article).filter(Article.id == id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.status = "EDITORIAL_HOLD"
    reasons = article.risk_reasons or []
    if reason not in reasons:
        reasons.append(reason)
    article.risk_reasons = reasons

    audit = AuditLog(
        user_id=current_user.id,
        action_type="EDITORIAL_HOLD",
        target_type="Article",
        target_id=str(article.id),
        summary=f"Placed on hold by {current_user.email}: {reason}",
        performed_by=current_user.email
    )
    db.add(audit)
    db.commit()
    return {"message": "Article placed on editorial hold", "status": article.status}

@router.post("/{id}/correct")
def add_correction(id: str, payload: CorrectionCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    article = db.query(Article).filter(Article.id == id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    corr = Correction(
        article_id=article.id,
        correction_notice=payload.correction_notice,
        editor_name=payload.editor_name or current_user.full_name,
        affected_fields=payload.affected_fields
    )
    db.add(corr)

    audit = AuditLog(
        user_id=current_user.id,
        action_type="CORRECTION_ISSUED",
        target_type="Article",
        target_id=str(article.id),
        summary=f"Official correction added to {article.headline[:50]}: {payload.correction_notice[:70]}",
        performed_by=current_user.email
    )
    db.add(audit)
    db.commit()
    return {"message": "Correction recorded successfully", "id": str(corr.id)}
