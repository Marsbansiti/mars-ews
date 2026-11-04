import hashlib
import time
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse, urljoin
import httpx
import feedparser
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.models.sources import NewsSource, SourcePermission, SourceHealthLog
from app.models.items import SourceItem
from app.models.audit import AuditLog
from app.services.image_service import extract_image_from_article_url, download_and_cache_image
from app.services.classifier import classify_news

HEADERS = {
    "User-Agent": "MarsNewsEditorialBot/1.0 (+https://marsnews.in/editorial-guidelines; news-intelligence)",
    "Accept": "text/html,application/xhtml+xml,application/xml,application/rss+xml,application/atom+xml;q=0.9,*/*;q=0.8",
}

def normalize_url(url: str) -> str:
    """Strip tracking params and anchors to obtain a clean canonical URL."""
    try:
        parsed = urlparse(url)
        # Drop utm_*, fbclid, etc.
        query_parts = []
        if parsed.query:
            for param in parsed.query.split("&"):
                if not any(param.lower().startswith(p) for p in ["utm_", "fbclid", "gclid", "ref="]):
                    query_parts.append(param)
        clean_query = "&".join(query_parts)
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if clean_query:
            clean_url = f"{clean_url}?{clean_query}"
        return clean_url
    except Exception:
        return url

def compute_content_hash(source_id: str, canonical_url: str, headline: str) -> str:
    normalized_headline = " ".join(headline.lower().split())
    raw = f"{source_id}:{canonical_url}:{normalized_headline}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def discover_feed_url(website_url: str, timeout: float = 10.0) -> Dict[str, Any]:
    """Inspects a publisher website to discover official RSS/Atom links in <head> tags or standard endpoints."""
    discovered = []
    response_time_ms = 0
    http_status = None
    start_time = time.time()

    try:
        with httpx.Client(timeout=timeout, follow_redirects=True, headers=HEADERS) as client:
            resp = client.get(website_url)
            response_time_ms = int((time.time() - start_time) * 1000)
            http_status = resp.status_code

            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                # Look for link[rel=alternate] tags
                for link in soup.find_all("link", rel=lambda r: r and "alternate" in r.lower()):
                    link_type = link.get("type", "").lower()
                    if "rss" in link_type or "atom" in link_type or "xml" in link_type:
                        href = link.get("href")
                        if href:
                            full_url = urljoin(website_url, href)
                            title = link.get("title", "Discovered Feed")
                            discovered.append({"title": title, "url": full_url, "type": link_type})

        # If no link tag found, check standard fallback paths
        if not discovered and http_status == 200:
            candidates = ["/feed", "/rss.xml", "/feed/", "/rss", "/feeds/news.xml"]
            for cand in candidates:
                cand_url = urljoin(website_url, cand)
                try:
                    with httpx.Client(timeout=5.0, follow_redirects=True, headers=HEADERS) as client:
                        r = client.head(cand_url)
                        if r.status_code == 200 and ("xml" in r.headers.get("content-type", "") or "rss" in r.headers.get("content-type", "")):
                            discovered.append({"title": f"Auto-detected {cand}", "url": cand_url, "type": "application/rss+xml"})
                            break
                except Exception:
                    continue

        return {
            "success": True,
            "http_status": http_status,
            "response_time_ms": response_time_ms,
            "discovered_feeds": discovered,
            "recommended_feed": discovered[0]["url"] if discovered else None
        }
    except Exception as e:
        response_time_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "http_status": http_status,
            "response_time_ms": response_time_ms,
            "error": str(e),
            "discovered_feeds": [],
            "recommended_feed": None
        }

def test_source_connection(source: NewsSource) -> Dict[str, Any]:
    target_url = source.rss_feed_url or source.official_website_url
    start_time = time.time()
    try:
        with httpx.Client(timeout=10.0, follow_redirects=True, headers=HEADERS) as client:
            resp = client.get(target_url)
            duration_ms = int((time.time() - start_time) * 1000)
            return {
                "success": resp.status_code == 200,
                "status_code": resp.status_code,
                "response_time_ms": duration_ms,
                "content_type": resp.headers.get("content-type", ""),
                "url_tested": str(resp.url)
            }
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "status_code": None,
            "response_time_ms": duration_ms,
            "error": str(e),
            "url_tested": target_url
        }

def collect_from_source(source_id: str, db: Session) -> Dict[str, Any]:
    """Ingests news items from a single authorized news source, enforcing permission gates and idempotency."""
    source = db.query(NewsSource).filter(NewsSource.id == source_id).first()
    if not source:
        return {"error": "Source not found", "items_collected": 0}

    # 1. Enforce Source Permission Gate
    permissions = source.permissions
    if not permissions or not permissions.can_collect_headlines:
        reason = "Headline collection permission disabled for this source"
        source.last_collection_error = reason
        db.commit()
        return {"error": reason, "items_collected": 0}

    feed_url = source.rss_feed_url
    if not feed_url:
        # Check if we can auto-discover
        disc = discover_feed_url(source.official_website_url)
        if disc.get("recommended_feed"):
            source.rss_feed_url = disc["recommended_feed"]
            feed_url = source.rss_feed_url
            db.commit()
        else:
            reason = f"No RSS feed URL configured or discoverable for {source.publisher_name}"
            source.last_collection_error = reason
            db.commit()
            return {"error": reason, "items_collected": 0}

    start_time = time.time()
    collected_count = 0
    duplicate_count = 0

    try:
        with httpx.Client(timeout=15.0, follow_redirects=True, headers=HEADERS) as client:
            resp = client.get(feed_url)
            resp_time_ms = int((time.time() - start_time) * 1000)

            if resp.status_code != 200:
                raise Exception(f"HTTP {resp.status_code} returned from feed URL: {resp.text[:150]}")

            parsed = feedparser.parse(resp.text)
            if parsed.bozo and not parsed.entries:
                raise Exception(f"Failed to parse XML feed: {getattr(parsed, 'bozo_exception', 'Unknown parse error')}")

            for entry in parsed.entries:
                raw_title = getattr(entry, "title", "").strip()
                raw_link = getattr(entry, "link", "").strip()
                if not raw_title or not raw_link:
                    continue

                canonical_link = normalize_url(raw_link)
                content_hash = compute_content_hash(str(source.id), canonical_link, raw_title)

                # Check idempotency
                existing = db.query(SourceItem).filter(
                    (SourceItem.content_hash == content_hash) | (SourceItem.canonical_url == canonical_link)
                ).first()

                if existing:
                    duplicate_count += 1
                    continue

                # Authorized description and image extraction
                raw_desc = ""
                extracted_image_url = None
                raw_html = getattr(entry, "summary", "") or getattr(entry, "description", "")
                if raw_html:
                    soup = BeautifulSoup(raw_html, "html.parser")
                    if permissions.can_collect_descriptions:
                        raw_desc = soup.get_text(separator=" ", strip=True)
                    # Extract image tag if present
                    img_tag = soup.find("img")
                    if img_tag and img_tag.get("src"):
                        extracted_image_url = img_tag["src"]

                # Check media:content or media:thumbnail or enclosures
                if not extracted_image_url:
                    if hasattr(entry, "media_content") and entry.media_content:
                        extracted_image_url = entry.media_content[0].get("url")
                    elif hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                        extracted_image_url = entry.media_thumbnail[0].get("url")
                    elif hasattr(entry, "enclosures") and entry.enclosures:
                        for enc in entry.enclosures:
                            if "image" in enc.get("type", ""):
                                extracted_image_url = enc.get("href") or enc.get("url")
                                break

                # Cache real photograph locally from source
                cached_image_url = None
                if extracted_image_url:
                    cached_image_url = download_and_cache_image(
                        extracted_image_url,
                        source.publisher_name,
                        raw_title,
                        db
                    )

                # Published date parsing
                pub_date = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                else:
                    pub_date = datetime.now(timezone.utc)

                # Author
                author = getattr(entry, "author", None)

                # Category classification using high-precision word-boundary classifier
                cat_slug, is_reg, reg_state = classify_news(
                    raw_title,
                    raw_desc or "",
                    source_type=source.source_type,
                    publisher_name=source.publisher_name
                )
                category_name = cat_slug.capitalize()

                item = SourceItem(
                    source_id=source.id,
                    original_headline=raw_title,
                    original_url=raw_link,
                    canonical_url=canonical_link,
                    publisher=source.publisher_name,
                    publication_timestamp=pub_date,
                    author=author,
                    authorized_description=raw_desc if permissions.can_collect_descriptions else None,
                    language=source.language,
                    category=category_name,
                    content_hash=content_hash,
                    raw_metadata={
                        "guid": getattr(entry, "id", None),
                        "feed_type": getattr(parsed, "version", "rss"),
                        "source_credibility": source.credibility_score,
                        "image_url": cached_image_url or extracted_image_url,
                        "original_image_url": extracted_image_url
                    },
                    processing_status="PENDING"
                )
                db.add(item)
                collected_count += 1

            # Update source status
            source.last_successful_collection = datetime.now(timezone.utc)
            source.last_collection_error = None
            source.consecutive_failures = 0

            # Health log
            health_log = SourceHealthLog(
                source_id=source.id,
                status="SUCCESS",
                response_time_ms=resp_time_ms,
                http_status=resp.status_code,
                items_collected=collected_count
            )
            db.add(health_log)

            # Audit log
            audit = AuditLog(
                action_type="INGESTION",
                target_type="Source",
                target_id=str(source.id),
                summary=f"Collected {collected_count} items from {source.publisher_name} ({duplicate_count} duplicates skipped)",
                details={"collected": collected_count, "duplicates": duplicate_count, "feed_url": feed_url},
                performed_by="INGESTION_ENGINE"
            )
            db.add(audit)
            db.commit()

            return {
                "source_id": str(source.id),
                "publisher_name": source.publisher_name,
                "items_collected": collected_count,
                "duplicates_skipped": duplicate_count,
                "response_time_ms": resp_time_ms,
                "status": "SUCCESS"
            }

    except Exception as e:
        db.rollback()
        resp_time_ms = int((time.time() - start_time) * 1000)
        source.last_collection_error = str(e)
        source.consecutive_failures += 1

        health_log = SourceHealthLog(
            source_id=source.id,
            status="FAILED",
            response_time_ms=resp_time_ms,
            items_collected=0,
            error_message=str(e)
        )
        db.add(health_log)
        db.commit()

        return {
            "source_id": str(source.id),
            "publisher_name": source.publisher_name,
            "items_collected": 0,
            "error": str(e),
            "status": "FAILED"
        }

def collect_all_enabled_sources(db: Session) -> Dict[str, Any]:
    sources = db.query(NewsSource).filter(NewsSource.enabled == True).all()
    results = []
    total_new_items = 0

    for source in sources:
        res = collect_from_source(str(source.id), db)
        results.append(res)
        total_new_items += res.get("items_collected", 0)

    return {
        "sources_processed": len(sources),
        "total_new_items": total_new_items,
        "details": results
    }
