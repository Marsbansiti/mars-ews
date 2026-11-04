import sys
from collections import Counter
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.articles import Article
from app.models.clusters import StoryCluster
from app.models.items import SourceItem
from app.models.taxonomy import Category
from app.models.audit import AuditLog
from app.services.classifier import classify_news

CATEGORY_DEFAULT_SVGS = {
    "science": "/images/science-isro.svg",
    "technology": "/images/science-isro.svg",
    "business": "/images/business-economy.svg",
    "economy": "/images/business-economy.svg",
    "odisha": "/images/odisha-tech.svg",
    "india": "/images/governance-parliament.svg",
    "politics": "/images/governance-parliament.svg",
    "default": "/images/news-default.svg"
}

def reclassify_everything():
    db = SessionLocal()
    try:
        print("[RECLASSIFY] Loading categories from database...")
        cats_by_slug = {c.slug: c for c in db.query(Category).all()}
        india_cat = cats_by_slug.get("india")
        if not india_cat:
            print("[ERROR] India category not found in DB!")
            return

        articles = db.query(Article).all()
        print(f"[RECLASSIFY] Processing {len(articles)} articles...")

        stats = Counter()
        for art in articles:
            # Determine source info
            pub_name = None
            if art.sources and len(art.sources) > 0:
                pub_name = art.sources[0].publisher_name

            cat_slug, is_reg, reg_state = classify_news(
                art.headline,
                art.summary or "",
                source_type=None,
                publisher_name=pub_name
            )

            target_cat = cats_by_slug.get(cat_slug, india_cat)
            art.category_id = target_cat.id
            art.is_regional = is_reg
            art.regional_state = reg_state

            # If hero image is an SVG visual marker, ensure it matches the new category
            if art.hero_image_url and art.hero_image_url.startswith("/images/"):
                new_svg = CATEGORY_DEFAULT_SVGS.get(cat_slug, CATEGORY_DEFAULT_SVGS["default"])
                art.hero_image_url = new_svg

            stats[target_cat.name] += 1

        print("[RECLASSIFY] Reclassifying story clusters...")
        clusters = db.query(StoryCluster).all()
        for cl in clusters:
            cat_slug, _, _ = classify_news(cl.cluster_title or "")
            target_cat = cats_by_slug.get(cat_slug, india_cat)
            cl.category = target_cat.name

        print("[RECLASSIFY] Reclassifying source items...")
        items = db.query(SourceItem).all()
        for it in items:
            cat_slug, _, _ = classify_news(
                it.original_headline,
                it.authorized_description or "",
                publisher_name=it.publisher
            )
            target_cat = cats_by_slug.get(cat_slug, india_cat)
            it.category = target_cat.name

        audit = AuditLog(
            action_type="CATEGORIES_RECLASSIFIED",
            target_type="Article",
            summary=f"Reclassified {len(articles)} articles and clusters using high-precision word-boundary classifier",
            details=dict(stats),
            performed_by="CLASSIFIER_SERVICE"
        )
        db.add(audit)
        db.commit()

        print("[RECLASSIFY] Database re-classification complete!")
        print("Updated Category Distribution:")
        for cat_name, cnt in stats.most_common():
            print(f"  - {cat_name:18}: {cnt} articles")

    except Exception as e:
        db.rollback()
        print(f"[RECLASSIFY] Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    reclassify_everything()
