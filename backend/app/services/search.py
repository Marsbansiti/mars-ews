from typing import List, Dict, Any, Optional
import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.articles import Article

INDEX_NAME = "mars_news_articles"
_MEILISEARCH_CHECKED = False
_MEILISEARCH_AVAILABLE = False

def get_meilisearch_client():
    global _MEILISEARCH_CHECKED, _MEILISEARCH_AVAILABLE
    if _MEILISEARCH_CHECKED:
        if not _MEILISEARCH_AVAILABLE:
            return None
    
    if not settings.MEILISEARCH_URL:
        _MEILISEARCH_CHECKED = True
        _MEILISEARCH_AVAILABLE = False
        return None

    try:
        with httpx.Client(timeout=0.2) as check_client:
            r = check_client.get(f"{settings.MEILISEARCH_URL}/health")
            if r.status_code == 200:
                _MEILISEARCH_CHECKED = True
                _MEILISEARCH_AVAILABLE = True
                from meilisearch_python_sdk import Client
                return Client(url=settings.MEILISEARCH_URL, api_key=settings.MEILISEARCH_MASTER_KEY)
    except Exception:
        pass

    _MEILISEARCH_CHECKED = True
    _MEILISEARCH_AVAILABLE = False
    return None

def index_article(article: Article):
    """Indexes or updates an article in Meilisearch if available; fails silently without blocking."""
    client = get_meilisearch_client()
    if not client:
        return
    try:
        index = client.index(INDEX_NAME)
        doc = {
            "id": str(article.id),
            "slug": article.slug,
            "headline": article.headline,
            "summary": article.summary,
            "content_body": article.content_body,
            "category": article.category_rel.name if article.category_rel else "India",
            "published_at": int(article.published_at.timestamp()) if article.published_at else None,
            "is_breaking": article.is_breaking,
            "is_regional": article.is_regional,
            "regional_state": article.regional_state,
            "hero_image_url": article.hero_image_url
        }
        index.add_documents([doc])
    except Exception:
        pass

def search_articles(query: str, db: Session, category: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """Hybrid search: attempts Meilisearch first, falling back to SQL LIKE queries."""
    client = get_meilisearch_client()
    if client:
        try:
            index = client.index(INDEX_NAME)
            filter_expr = f"category = '{category}'" if category else None
            res = index.search(query, filter=filter_expr, limit=limit)
            return res.hits
        except Exception:
            pass

    # SQL fallback
    q = db.query(Article).filter(Article.status == "PUBLISHED")
    words = query.strip().split()
    for w in words:
        q = q.filter(Article.headline.ilike(f"%{w}%") | Article.summary.ilike(f"%{w}%"))
    if category:
        q = q.filter(Article.category_rel.has(slug=category.lower()))

    results = q.order_by(Article.published_at.desc()).limit(limit).all()
    return [
        {
            "id": str(a.id),
            "slug": a.slug,
            "headline": a.headline,
            "summary": a.summary,
            "category": a.category_rel.name if a.category_rel else "India",
            "hero_image_url": a.hero_image_url,
            "published_at": a.published_at.isoformat() if a.published_at else None
        }
        for a in results
    ]
