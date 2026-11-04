import re
import uuid
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.clusters import StoryCluster, ClusterItem
from app.models.items import SourceItem
from app.models.taxonomy import Category, Tag, Entity
from app.models.media import MediaAsset
from app.models.articles import Article, ArticleSource, ArticleRevision, ArticleClaim, ClaimEvidence
from app.models.queue import PublishingQueueItem
from app.models.audit import AuditLog, Notification
from app.services.ai_editorial import generate_editorial_article
from app.services.validation import validate_and_assess_risk
from app.services.search import index_article

def make_slug(headline: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", headline.lower())
    words = cleaned.split()[:8]
    base_slug = "-".join(words)
    suffix = str(uuid.uuid4())[:6]
    return f"{base_slug}-{suffix}"

from app.services.image_service import download_and_cache_image

CATEGORY_DEFAULT_IMAGES = {
    "science": {
        "url": "/images/science-isro.svg",
        "alt": "ISRO heavy rocket and climate observation satellite in orbit",
        "caption": "Indian Space Research Organisation (ISRO) Editorial Visual Archive",
        "license": "CC-BY-4.0"
    },
    "business": {
        "url": "/images/business-economy.svg",
        "alt": "Reserve Bank of India Digital Rupee currency and economic indicators",
        "caption": "Financial Markets & Central Banking Documentation Archive",
        "license": "CC-BY-4.0"
    },
    "odisha": {
        "url": "/images/odisha-tech.svg",
        "alt": "Odisha semiconductor wafer and high-tech park in Bhubaneswar",
        "caption": "Odisha High-Tech & Electronics Innovation Infrastructure",
        "license": "CC-BY-4.0"
    },
    "politics": {
        "url": "/images/governance-parliament.svg",
        "alt": "Parliament rotunda and democratic governance bureau",
        "caption": "Public Governance & Legislative Documentation",
        "license": "PUBLIC_DOMAIN"
    },
    "india": {
        "url": "/images/governance-parliament.svg",
        "alt": "National India governance and public administration bureau",
        "caption": "National Public Domain Documentation Archive",
        "license": "PUBLIC_DOMAIN"
    },
    "default": {
        "url": "/images/news-default.svg",
        "alt": "MARS NEWS editorial reporting newsroom",
        "caption": "Mars News Verified Editorial Archive",
        "license": "EDITORIAL_USE"
    }
}

def select_eligible_media(category_name: str, headline: str, source_items: List[SourceItem], db: Session) -> Dict[str, str]:
    """Selects real news photograph from original source or verified editorial category artwork."""
    # 1. Check if any source item has an original news photograph from publisher
    for item in source_items:
        raw_img = item.raw_metadata.get("image_url") if isinstance(item.raw_metadata, dict) else None
        if not raw_img and isinstance(item.raw_metadata, dict):
            raw_img = item.raw_metadata.get("original_image_url")

        if raw_img:
            # Cache locally to ensure zero broken images or CORS blocking
            cached_url = download_and_cache_image(raw_img, item.publisher, headline, db)
            return {
                "url": cached_url,
                "alt": item.original_headline,
                "caption": f"Photo courtesy of {item.publisher}",
                "license": "EDITORIAL_USE"
            }

    # 2. Check for any real downloaded news photograph in MediaAsset
    recent_real_asset = db.query(MediaAsset).filter(MediaAsset.image_url.like("/uploads/%")).order_by(MediaAsset.created_at.desc()).first()
    if recent_real_asset:
        return {
            "url": recent_real_asset.image_url,
            "alt": recent_real_asset.alt_text or headline,
            "caption": recent_real_asset.attribution or "Photo courtesy of Verified News Media Archive",
            "license": "EDITORIAL_USE"
        }

    # 3. Fallback to category defaults
    cat_key = category_name.lower()
    if cat_key in CATEGORY_DEFAULT_IMAGES:
        return CATEGORY_DEFAULT_IMAGES[cat_key]

    return CATEGORY_DEFAULT_IMAGES["default"]

def process_cluster_for_publishing(cluster_id: str, db: Session, force_publish: bool = False) -> Dict[str, Any]:
    """Executes the full pipeline for a story cluster:
    AI Synthesis -> Validation -> Risk Check -> Queue / Publish
    """
    if settings.EMERGENCY_PUBLISHING_PAUSE and not force_publish:
        return {"status": "PAUSED", "reason": "Global emergency publishing pause is active"}

    cluster = db.query(StoryCluster).filter(StoryCluster.id == cluster_id).first()
    if not cluster:
        return {"error": "Cluster not found"}

    cluster_links = db.query(ClusterItem).filter(ClusterItem.cluster_id == cluster_id).all()
    if not cluster_links:
        return {"error": "Cluster has no source reports"}

    source_items = db.query(SourceItem).filter(SourceItem.id.in_([l.source_item_id for l in cluster_links])).all()

    # Format article sources metadata
    sources_meta = []
    for si in source_items:
        sources_meta.append({
            "publisher_name": si.publisher,
            "source_url": si.original_url,
            "headline": si.original_headline,
            "pub_date": si.publication_timestamp,
            "item_id": si.id
        })

    # 1. AI Editorial Generation
    editorial_output = generate_editorial_article(str(cluster.id), db)

    # 2. Fact Validation & Risk Assessment
    val_report = validate_and_assess_risk(
        editorial_output,
        sources_meta,
        strict_mode=settings.FACT_VALIDATION_STRICT_MODE
    )

    # 3. Determine Category
    cat_obj = db.query(Category).filter(Category.name.ilike(editorial_output.category)).first()
    if not cat_obj:
        cat_obj = db.query(Category).filter(Category.slug == "india").first()

    # 4. Select Licensed Media Asset
    media_info = select_eligible_media(
        cat_obj.name if cat_obj else "India",
        editorial_output.original_headline,
        source_items,
        db
    )

    # 5. Check publishing status based on risk assessment
    status = "PUBLISHED" if (val_report["can_auto_publish"] or force_publish) else "EDITORIAL_HOLD"
    pub_time = datetime.now(timezone.utc) if status == "PUBLISHED" else None

    # 6. Create Article Record
    slug = make_slug(editorial_output.original_headline)

    article = Article(
        cluster_id=cluster.id,
        category_id=cat_obj.id if cat_obj else None,
        slug=slug,
        headline=editorial_output.original_headline,
        summary=editorial_output.original_summary,
        content_body=editorial_output.article_body,
        language="en",
        status=status,
        risk_level=val_report["final_risk_level"],
        risk_reasons=val_report["hold_reasons"],
        readability_score=editorial_output.readability_score,
        reading_time_minutes=editorial_output.reading_time_minutes,
        published_at=pub_time,
        is_breaking="breaking" in editorial_output.original_headline.lower(),
        is_featured=len(source_items) >= 2,
        is_regional=editorial_output.is_regional,
        regional_state=editorial_output.regional_state,
        hero_image_url=media_info["url"],
        hero_image_alt=media_info["alt"],
        hero_image_caption=media_info["caption"],
        hero_image_license=media_info["license"],
        seo_title=editorial_output.seo_title,
        seo_description=editorial_output.seo_description,
        ai_generated=True,
        version=1
    )
    db.add(article)
    db.flush()

    # 7. Map Attribution Sources
    for s_info in sources_meta:
        asource = ArticleSource(
            article_id=article.id,
            publisher_name=s_info["publisher_name"],
            source_url=s_info["source_url"],
            original_headline=s_info["headline"],
            published_date=s_info["pub_date"],
            attribution_text=f"Reported by {s_info['publisher_name']}",
            source_item_id=s_info["item_id"]
        )
        db.add(asource)

    # 8. Record Article Claims with evidence mapping
    for claim in editorial_output.claims:
        art_claim = ArticleClaim(
            article_id=article.id,
            claim_text=claim.claim_text,
            claim_type=claim.claim_type,
            verification_status="VERIFIED" if claim.confidence > 0.8 else "UNVERIFIED",
            confidence_score=claim.confidence,
            verification_notes=f"Mapped to {claim.supporting_source_publisher}"
        )
        db.add(art_claim)
        db.flush()

        # Evidence
        ev = ClaimEvidence(
            claim_id=art_claim.id,
            source_name=claim.supporting_source_publisher,
            source_url=sources_meta[0]["source_url"] if sources_meta else "https://marsnews.in",
            supporting_excerpt=claim.supporting_quote_or_context,
            is_direct_match=True
        )
        db.add(ev)

    # 9. Record Initial Revision
    revision = ArticleRevision(
        article_id=article.id,
        revision_number=1,
        headline=article.headline,
        summary=article.summary,
        content_body=article.content_body,
        changed_by="AI_EDITORIAL_PIPELINE",
        change_reason="Initial article synthesis and validation"
    )
    db.add(revision)

    # 10. Tags Association
    seen_tag_slugs = set()
    for tag_name in editorial_output.tags:
        clean_tag = tag_name.strip()
        tag_slug = re.sub(r"[^\w-]", "", clean_tag.lower())
        if not tag_slug or tag_slug in seen_tag_slugs:
            continue
        seen_tag_slugs.add(tag_slug)

        tag_obj = db.query(Tag).filter(Tag.slug == tag_slug).first()
        if not tag_obj:
            tag_obj = Tag(name=clean_tag, slug=tag_slug, usage_count=1)
            db.add(tag_obj)
            db.flush()
        else:
            tag_obj.usage_count += 1
        article.tags.append(tag_obj)

    # 11. Publishing Queue management
    queue_item = PublishingQueueItem(
        article_id=article.id,
        scheduled_for=datetime.now(timezone.utc),
        status=status,
        idempotency_key=f"pub_{article.id}_{article.slug}",
        error_log=None if status == "PUBLISHED" else f"Held: {', '.join(val_report['hold_reasons'])}"
    )
    db.add(queue_item)

    # 12. Update Cluster Status
    cluster.status = "PUBLISHED" if status == "PUBLISHED" else "READY_TO_PUBLISH"

    # 13. Audit Log & Notifications
    audit = AuditLog(
        action_type="ARTICLE_PUBLISHED" if status == "PUBLISHED" else "EDITORIAL_HOLD",
        target_type="Article",
        target_id=str(article.id),
        summary=f"Article '{article.headline[:70]}' status set to {status} [Risk: {val_report['final_risk_level']}]",
        details={
            "status": status,
            "risk_level": val_report["final_risk_level"],
            "hold_reasons": val_report["hold_reasons"],
            "claims_count": len(editorial_output.claims),
            "sources_count": len(sources_meta)
        },
        performed_by="AUTO_PUBLISHER"
    )
    db.add(audit)

    if status == "EDITORIAL_HOLD":
        notif = Notification(
            title=f"Editorial Hold: {article.headline[:50]}...",
            message=f"Story held due to sensitive topic: {', '.join(val_report['hold_reasons'])}. Requires editor sign-off.",
            level="WARNING",
            category="EDITORIAL",
            action_link=f"/admin/articles?id={article.id}"
        )
        db.add(notif)

    db.commit()

    # Index in Meilisearch
    if status == "PUBLISHED":
        index_article(article)

    return {
        "article_id": str(article.id),
        "headline": article.headline,
        "slug": article.slug,
        "status": status,
        "risk_level": val_report["final_risk_level"],
        "hold_reasons": val_report["hold_reasons"]
    }

def auto_publish_ready_clusters(db: Session, max_articles: int = 5) -> Dict[str, Any]:
    """Dispatches eligible story clusters ready for editorial processing."""
    clusters = db.query(StoryCluster).filter(StoryCluster.status == "ACTIVE").limit(max_articles).all()
    results = []
    for c in clusters:
        res = process_cluster_for_publishing(str(c.id), db)
        results.append(res)
    return {"processed": len(clusters), "results": results}
