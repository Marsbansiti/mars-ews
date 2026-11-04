from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.articles import Article, ArticleSource, ArticleClaim, ArticleRevision, Correction
from app.models.taxonomy import Category
from app.models.sources import NewsSource
from app.models.audit import AnalyticsEvent
from app.schemas.article import ArticleListResponse, ArticleDetailResponse
from app.services.search import search_articles
from app.services.rss import generate_public_rss_feed
from app.services.sitemap import generate_xml_sitemap, generate_google_news_sitemap

router = APIRouter(tags=["Public News"])

def format_article_list_item(a: Article) -> ArticleListResponse:
    cat_name = a.category_rel.name if a.category_rel else "India"
    cat_slug = a.category_rel.slug if a.category_rel else "india"
    return ArticleListResponse(
        id=str(a.id),
        slug=a.slug,
        headline=a.headline,
        summary=a.summary,
        category=cat_name,
        category_slug=cat_slug,
        language=a.language,
        status=a.status,
        risk_level=a.risk_level,
        published_at=a.published_at,
        is_breaking=a.is_breaking,
        is_featured=a.is_featured,
        is_regional=a.is_regional,
        regional_state=a.regional_state,
        hero_image_url=a.hero_image_url,
        hero_image_alt=a.hero_image_alt,
        hero_image_caption=a.hero_image_caption,
        hero_image_license=a.hero_image_license,
        readability_score=a.readability_score,
        reading_time_minutes=a.reading_time_minutes,
        version=a.version,
        sources_count=len(a.sources),
        claims_count=len(a.claims)
    )

@router.get("/news", response_model=List[ArticleListResponse])
def get_published_news(
    category: Optional[str] = Query(None, description="Category slug"),
    regional: Optional[bool] = Query(None, description="Filter regional stories"),
    state: Optional[str] = Query(None, description="Filter state e.g. Odisha"),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Article).filter(Article.status == "PUBLISHED")

    if category:
        cat_obj = db.query(Category).filter(Category.slug == category.lower()).first()
        if cat_obj:
            query = query.filter(Article.category_id == cat_obj.id)

    if regional is not None:
        query = query.filter(Article.is_regional == regional)

    if state:
        query = query.filter(Article.regional_state.ilike(state))

    articles = query.order_by(Article.published_at.desc()).offset(offset).limit(limit).all()
    return [format_article_list_item(a) for a in articles]

@router.get("/news/{slug}", response_model=ArticleDetailResponse)
def get_article_by_slug(slug: str, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.slug == slug, Article.status == "PUBLISHED").first()
    if not article:
        # Check if held or draft (only return if exists with 404 or held message)
        raise HTTPException(status_code=404, detail="Article not found or not currently published")

    # Record view event
    event = AnalyticsEvent(
        event_type="ARTICLE_VIEW",
        article_id=article.id,
        category_slug=article.category_rel.slug if article.category_rel else None,
        metadata_json={"slug": slug}
    )
    db.add(event)
    db.commit()

    base_data = format_article_list_item(article).model_dump()
    return ArticleDetailResponse(
        **base_data,
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

@router.get("/breaking", response_model=List[ArticleListResponse])
def get_breaking_news(limit: int = 10, db: Session = Depends(get_db)):
    articles = db.query(Article).filter(
        Article.status == "PUBLISHED",
        Article.is_breaking == True
    ).order_by(Article.published_at.desc()).limit(limit).all()
    if not articles:
        # fallback to latest 5
        articles = db.query(Article).filter(Article.status == "PUBLISHED").order_by(Article.published_at.desc()).limit(5).all()
    return [format_article_list_item(a) for a in articles]

@router.get("/trending", response_model=List[ArticleListResponse])
def get_trending_news(limit: int = 10, db: Session = Depends(get_db)):
    articles = db.query(Article).filter(
        Article.status == "PUBLISHED"
    ).order_by(Article.is_featured.desc(), Article.published_at.desc()).limit(limit).all()
    return [format_article_list_item(a) for a in articles]

@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    cats = db.query(Category).filter(Category.is_active == True).order_by(Category.display_order.asc()).all()
    return [{"id": str(c.id), "name": c.name, "slug": c.slug, "description": c.description} for c in cats]

@router.get("/sources")
def get_public_sources(db: Session = Depends(get_db)):
    sources = db.query(NewsSource).order_by(NewsSource.credibility_score.desc()).all()
    return [{
        "publisher_name": s.publisher_name,
        "official_website_url": s.official_website_url,
        "language": s.language,
        "country": s.country,
        "source_type": s.source_type,
        "permission_status": s.permission_status,
        "content_usage_policy": s.content_usage_policy,
        "credibility_score": s.credibility_score
    } for s in sources]

@router.get("/search")
def search_public_news(
    q: str = Query(..., min_length=2, description="Search term"),
    category: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    results = search_articles(q, db, category=category, limit=limit)
    return {"query": q, "count": len(results), "articles": results}

@router.get("/rss.xml", response_class=Response)
@router.get("/rss", response_class=Response)
def get_rss(db: Session = Depends(get_db)):
    xml_content = generate_public_rss_feed(db)
    return Response(content=xml_content, media_type="application/rss+xml")

@router.get("/sitemap.xml", response_class=Response)
def get_sitemap(db: Session = Depends(get_db)):
    xml_content = generate_xml_sitemap(db)
    return Response(content=xml_content, media_type="application/xml")

@router.get("/news-sitemap.xml", response_class=Response)
def get_news_sitemap(db: Session = Depends(get_db)):
    xml_content = generate_google_news_sitemap(db)
    return Response(content=xml_content, media_type="application/xml")
