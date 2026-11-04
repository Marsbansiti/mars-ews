import re
from app.core.database import SessionLocal
from app.models.articles import Article
from app.models.items import SourceItem
from app.models.audit import AuditLog

def clean_database_boilerplate():
    db = SessionLocal()
    try:
        articles = db.query(Article).all()
        print(f"[CLEANUP] Processing {len(articles)} articles in database...")

        cleaned_count = 0
        for a in articles:
            orig_body = a.content_body or ""
            paras = [p.strip() for p in orig_body.split("\n\n") if p.strip()]
            new_paras = []

            for p in paras:
                if "Verified reporting published by" in p:
                    continue
                if "Cross-source verification indicates" in p:
                    continue
                if "Mars News editorial intelligence" in p:
                    continue
                if "Editorial review indicates consensus" in p:
                    continue
                if "the development represents a significant update in national coverage" in p:
                    continue

                # Clean inline suffixes
                cleaned_p = re.sub(
                    r"\.\s*According to reports cross-verified across [^,.]+, the development represents an active news update in national and regional coverage\.",
                    ".",
                    p,
                    flags=re.I
                )
                cleaned_p = re.sub(
                    r"\.\s*Reporting compiled across verified Indian news desks confirms key developments in this developing story\.",
                    ".",
                    cleaned_p,
                    flags=re.I
                )
                cleaned_p = cleaned_p.strip()
                if cleaned_p and len(cleaned_p) > 3:
                    new_paras.append(cleaned_p)

            # If only lead line remains and we have source items with descriptions, append clean desc
            if len(new_paras) <= 1:
                if a.cluster and a.cluster.cluster_items:
                    primary_item = a.cluster.cluster_items[0].source_item
                    if primary_item and primary_item.authorized_description:
                        desc = primary_item.authorized_description.strip()
                        if "Verified reporting published by" not in desc and desc != a.headline:
                            new_paras.append(desc)

            new_body = "\n\n".join(new_paras)

            # Clean summary if needed
            new_summary = a.summary or ""
            if "Cross-verified across" in new_summary:
                new_summary = re.sub(r"\s*Cross-verified across \d+ leading publications\.", "", new_summary, flags=re.I).strip()

            if new_body != orig_body or new_summary != a.summary:
                a.content_body = new_body
                a.summary = new_summary
                cleaned_count += 1

        db.commit()
        print(f"[CLEANUP] Successfully cleaned {cleaned_count} articles in database!")

        audit = AuditLog(
            action_type="BOILERPLATE_REMOVED",
            target_type="Article",
            summary=f"Cleaned robotic boilerplate sentences from {cleaned_count} articles across database",
            performed_by="EDITORIAL_CLEANUP_SERVICE"
        )
        db.add(audit)
        db.commit()

    except Exception as e:
        db.rollback()
        print(f"[CLEANUP] Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    clean_database_boilerplate()
