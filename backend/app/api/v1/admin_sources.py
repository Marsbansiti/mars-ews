import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.sources import NewsSource, SourcePermission, SourceHealthLog
from app.models.audit import AuditLog
from app.schemas.source import NewsSourceCreate, NewsSourceUpdate, NewsSourceResponse, SourcePermissionSchema
from app.services.collector import discover_feed_url, test_source_connection

router = APIRouter(prefix="/admin/sources", tags=["Admin Source Manager"])

def format_source_response(src: NewsSource) -> NewsSourceResponse:
    perm_schema = None
    if src.permissions:
        perm_schema = SourcePermissionSchema(
            can_collect_headlines=src.permissions.can_collect_headlines,
            can_collect_descriptions=src.permissions.can_collect_descriptions,
            can_create_original_summaries=src.permissions.can_create_original_summaries,
            can_access_full_text=src.permissions.can_access_full_text,
            can_reuse_images=src.permissions.can_reuse_images,
            can_commercially_redistribute=src.permissions.can_commercially_redistribute,
            can_display_attribution=src.permissions.can_display_attribution,
            notes=src.permissions.notes
        )
    return NewsSourceResponse(
        id=str(src.id),
        publisher_name=src.publisher_name,
        slug=src.slug,
        official_website_url=src.official_website_url,
        language=src.language,
        country=src.country,
        coverage_categories=src.coverage_categories or [],
        source_type=src.source_type,
        rss_feed_url=src.rss_feed_url,
        permission_status=src.permission_status,
        collection_frequency=src.collection_frequency,
        enabled=src.enabled,
        credibility_score=src.credibility_score,
        content_usage_policy=src.content_usage_policy,
        last_successful_collection=src.last_successful_collection,
        last_collection_error=src.last_collection_error,
        consecutive_failures=src.consecutive_failures,
        permissions=perm_schema,
        items_count=len(src.items)
    )

@router.get("", response_model=List[NewsSourceResponse])
def list_sources(
    status: Optional[str] = None,
    enabled: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(NewsSource)
    if status:
        query = query.filter(NewsSource.permission_status == status)
    if enabled is not None:
        query = query.filter(NewsSource.enabled == enabled)
    sources = query.order_by(NewsSource.publisher_name.asc()).all()
    return [format_source_response(s) for s in sources]

@router.post("", response_model=NewsSourceResponse)
def create_source(payload: NewsSourceCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    existing = db.query(NewsSource).filter(NewsSource.publisher_name == payload.publisher_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="A source with this publisher name already exists")

    slug = re.sub(r"[^\w-]", "", payload.publisher_name.lower().replace(" ", "-"))
    src = NewsSource(
        publisher_name=payload.publisher_name,
        slug=slug,
        official_website_url=str(payload.official_website_url),
        language=payload.language,
        country=payload.country,
        coverage_categories=payload.coverage_categories,
        source_type=payload.source_type,
        rss_feed_url=str(payload.rss_feed_url) if payload.rss_feed_url else None,
        permission_status="DISCOVERY_PENDING" if not payload.rss_feed_url else "VERIFIED",
        collection_frequency=payload.collection_frequency,
        enabled=payload.enabled,
        credibility_score=payload.credibility_score,
        content_usage_policy=payload.content_usage_policy
    )
    db.add(src)
    db.flush()

    perms_data = payload.permissions or SourcePermissionSchema()
    perm = SourcePermission(
        source_id=src.id,
        can_collect_headlines=perms_data.can_collect_headlines,
        can_collect_descriptions=perms_data.can_collect_descriptions,
        can_create_original_summaries=perms_data.can_create_original_summaries,
        can_access_full_text=perms_data.can_access_full_text,
        can_reuse_images=perms_data.can_reuse_images,
        can_commercially_redistribute=perms_data.can_commercially_redistribute,
        can_display_attribution=perms_data.can_display_attribution,
        notes=perms_data.notes
    )
    db.add(perm)

    audit = AuditLog(
        user_id=current_user.id,
        action_type="SOURCE_CREATED",
        target_type="Source",
        target_id=str(src.id),
        summary=f"Added new source: {src.publisher_name}",
        performed_by=current_user.email
    )
    db.add(audit)
    db.commit()
    db.refresh(src)
    return format_source_response(src)

@router.patch("/{id}", response_model=NewsSourceResponse)
def update_source(id: str, payload: NewsSourceUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    src = db.query(NewsSource).filter(NewsSource.id == id).first()
    if not src:
        raise HTTPException(status_code=404, detail="Source not found")

    data = payload.model_dump(exclude_unset=True)
    perms_data = data.pop("permissions", None)

    for field, val in data.items():
        setattr(src, field, val)

    if perms_data and src.permissions:
        for p_field, p_val in perms_data.items():
            setattr(src.permissions, p_field, p_val)

    audit = AuditLog(
        user_id=current_user.id,
        action_type="SOURCE_UPDATED",
        target_type="Source",
        target_id=str(src.id),
        summary=f"Updated configuration for: {src.publisher_name}",
        performed_by=current_user.email
    )
    db.add(audit)
    db.commit()
    db.refresh(src)
    return format_source_response(src)

@router.delete("/{id}")
def delete_source(id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    src = db.query(NewsSource).filter(NewsSource.id == id).first()
    if not src:
        raise HTTPException(status_code=404, detail="Source not found")

    publisher_name = src.publisher_name
    db.delete(src)

    audit = AuditLog(
        user_id=current_user.id,
        action_type="SOURCE_DELETED",
        target_type="Source",
        target_id=id,
        summary=f"Deleted source: {publisher_name}",
        performed_by=current_user.email
    )
    db.add(audit)
    db.commit()
    return {"message": f"Source {publisher_name} deleted successfully"}

@router.post("/{id}/test")
def test_connection(id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    src = db.query(NewsSource).filter(NewsSource.id == id).first()
    if not src:
        raise HTTPException(status_code=404, detail="Source not found")
    result = test_source_connection(src)
    return result

@router.post("/{id}/discover")
def run_discovery(id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    src = db.query(NewsSource).filter(NewsSource.id == id).first()
    if not src:
        raise HTTPException(status_code=404, detail="Source not found")

    disc_result = discover_feed_url(src.official_website_url)
    if disc_result.get("recommended_feed"):
        src.rss_feed_url = disc_result["recommended_feed"]
        src.permission_status = "VERIFIED"
        db.commit()
    return disc_result
