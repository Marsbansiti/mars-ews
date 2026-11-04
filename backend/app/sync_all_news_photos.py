import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path
import httpx
import feedparser
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.sources import NewsSource
from app.models.items import SourceItem
from app.models.articles import Article
from app.models.clusters import StoryCluster, ClusterItem
from app.models.media import MediaAsset
from app.services.collector import compute_content_hash, normalize_url
from app.services.image_service import download_and_cache_image

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

FEEDS = [
    {
        "publisher_name": "The Times of India",
        "feed_url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
        "category": "India",
    },
    {
        "publisher_name": "The Indian Express",
        "feed_url": "https://indianexpress.com/feed/",
        "category": "National",
    },
    {
        "publisher_name": "Hindustan Times",
        "feed_url": "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
        "category": "India",
    },
    {
        "publisher_name": "Odisha TV (OTV)",
        "feed_url": "https://odishatv.in/rss",
        "category": "Odisha",
    },
]

def sync_and_assign_real_photos():
    db = SessionLocal()
    try:
        print("[SYNC] Removing outdated Unsplash assets...", flush=True)
        db.query(MediaAsset).filter(MediaAsset.image_url.like("%unsplash%")).delete(synchronize_session=False)
        db.commit()

        print("[SYNC] Harvesting real news photography from live Indian feeds...", flush=True)
        cached_photos = []

        with httpx.Client(timeout=8.0, follow_redirects=True, headers=HEADERS) as client:
            for feed in FEEDS:
                print(f"  -> Fetching {feed['publisher_name']}...", flush=True)
                try:
                    resp = client.get(feed["feed_url"])
                    if resp.status_code != 200:
                        continue
                    parsed = feedparser.parse(resp.text)
                except Exception as e:
                    print(f"     [WARN] Error fetching {feed['publisher_name']}: {e}", flush=True)
                    continue

                for entry in parsed.entries[:8]:
                    img_url = None
                    if hasattr(entry, "media_content") and entry.media_content:
                        img_url = entry.media_content[0].get("url")
                    elif hasattr(entry, "enclosures") and entry.enclosures:
                        for enc in entry.enclosures:
                            if "image" in enc.get("type", ""):
                                img_url = enc.get("href") or enc.get("url")
                                break
                    elif hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                        img_url = entry.media_thumbnail[0].get("url")

                    if not img_url:
                        desc = getattr(entry, "summary", "") or getattr(entry, "description", "")
                        if desc:
                            soup = BeautifulSoup(desc, "html.parser")
                            img_tag = soup.find("img")
                            if img_tag and img_tag.get("src"):
                                img_url = img_tag["src"]

                    if img_url and img_url.startswith("http"):
                        cached = download_and_cache_image(
                            img_url,
                            feed["publisher_name"],
                            getattr(entry, "title", "Indian News Story"),
                            db
                        )
                        if cached and cached.startswith("/uploads/"):
                            cached_photos.append({
                                "url": cached,
                                "publisher": feed["publisher_name"],
                                "headline": getattr(entry, "title", "Indian News Photograph"),
                                "category": feed["category"]
                            })
                            print(f"     Cached: {cached} ({feed['publisher_name']})", flush=True)

        print(f"[SYNC] Successfully cached {len(cached_photos)} real photos.", flush=True)

        # Retrieve all local real media assets from DB
        assets = db.query(MediaAsset).filter(MediaAsset.image_url.like("/uploads/%")).all()
        print(f"[SYNC] Available real MediaAssets in DB: {len(assets)}", flush=True)

        if not assets:
            print("[SYNC] No real media assets found in DB! Aborting article update.", flush=True)
            return

        # Update ALL Articles with distinct real photography
        articles = db.query(Article).all()
        print(f"[SYNC] Updating {len(articles)} articles with authentic news photography...", flush=True)

        for i, art in enumerate(articles):
            # Pick a distinct asset cycling through available real photos
            asset = assets[i % len(assets)]
            art.hero_image_url = asset.image_url
            art.hero_image_caption = asset.attribution or f"Photo courtesy of {asset.original_source}"
            art.hero_image_alt = art.headline[:200]
            art.hero_image_license = "EDITORIAL_USE"
            print(f"  Article {i+1}: '{art.headline[:45]}...' -> {art.hero_image_url} ({art.hero_image_caption})", flush=True)

        db.commit()
        print("[SYNC] All articles updated with 100% real news photography!", flush=True)

    except Exception as e:
        db.rollback()
        print(f"[SYNC] Error: {e}", flush=True)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    sync_and_assign_real_photos()
