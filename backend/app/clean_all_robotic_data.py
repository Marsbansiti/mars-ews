import re
import sys
from app.core.database import SessionLocal
from app.models.articles import Article
from app.models.clusters import StoryCluster, ClusterItem
from app.models.items import SourceItem

def clean_database():
    db = SessionLocal()
    try:
        articles = db.query(Article).all()
        print(f"Inspecting and cleaning {len(articles)} articles...")

        updated_count = 0
        cleaned_summaries = 0
        cleaned_bodies = 0
        cleaned_headlines = 0

        for a in articles:
            dirty = False

            # 1. Clean headline
            orig_h = a.headline or ""
            new_h = re.sub(r"^Report:\s*", "", orig_h, flags=re.IGNORECASE).strip()
            if new_h != orig_h:
                a.headline = new_h
                dirty = True
                cleaned_headlines += 1

            # 2. Clean summary
            orig_s = a.summary or ""
            if "Key developments regarding" in orig_s or "Cross-verified across" in orig_s or "Verified reporting published by" in orig_s or not orig_s.strip():
                # Attempt to get real description from source item
                best_desc = ""
                if a.cluster_id:
                    cluster_item = db.query(ClusterItem).filter(ClusterItem.cluster_id == a.cluster_id).first()
                    if cluster_item:
                        si = db.query(SourceItem).filter(SourceItem.id == cluster_item.source_item_id).first()
                        if si and si.authorized_description:
                            candidate = si.authorized_description.strip()
                            if "Verified reporting published by" not in candidate and candidate != a.headline:
                                best_desc = candidate

                # Fallback to content body paragraph
                if not best_desc and a.content_body:
                    paras = [p.strip() for p in a.content_body.split("\n\n") if p.strip()]
                    for p in paras:
                        # strip bureau lead
                        clean_p = re.sub(r"^\*\*.*?\*\*\s*—\s*", "", p).strip()
                        if clean_p and clean_p != a.headline and "According to reports" not in clean_p and "Cross-source" not in clean_p:
                            best_desc = clean_p
                            break

                if not best_desc:
                    best_desc = a.headline

                # Final formatting
                new_s = best_desc[:280].strip()
                if not new_s.endswith((".", "!", "?")) and len(best_desc) > 280:
                    new_s = new_s.rstrip(" ,;") + "..."

                a.summary = new_s
                dirty = True
                cleaned_summaries += 1

            # 3. Clean content body
            if a.content_body:
                orig_body = a.content_body
                body = orig_body

                # Remove inline robotic patterns
                body = re.sub(
                    r"\.\s*According to reports (?:cross-verified|compiled) across [^,.]+, the development represents (?:an active|a significant) (?:news )?update in national (?:and regional )?coverage\.",
                    ".",
                    body,
                    flags=re.IGNORECASE
                )
                body = re.sub(
                    r"\.\s*According to reports compiled from verified publications including [^,.]+, the development represents a significant update in national coverage\.",
                    ".",
                    body,
                    flags=re.IGNORECASE
                )
                body = re.sub(
                    r"\.\s*Reporting compiled across verified Indian news desks confirms key developments in this developing story\.",
                    ".",
                    body,
                    flags=re.IGNORECASE
                )

                # Filter out whole robotic paragraphs
                paras = body.split("\n\n")
                filtered = []
                for p in paras:
                    pt = p.strip()
                    if not pt:
                        continue
                    if "Verified reporting published by" in pt:
                        continue
                    if "Cross-source verification indicates" in pt:
                        continue
                    if "Mars News editorial intelligence" in pt:
                        continue
                    if "Editorial review indicates consensus" in pt:
                        continue
                    filtered.append(pt)

                new_body = "\n\n".join(filtered)
                if new_body != orig_body:
                    a.content_body = new_body
                    dirty = True
                    cleaned_bodies += 1

            # 4. Clean bad media captions / alt
            if a.hero_image_alt and "Space rocket launching" in a.hero_image_alt and a.category and a.category.slug not in ["science", "technology"]:
                a.hero_image_alt = a.headline
                dirty = True
            if a.hero_image_caption and "Space Exploration Archive" in a.hero_image_caption and a.category and a.category.slug not in ["science", "technology"]:
                a.hero_image_caption = f"Photo courtesy of {a.sources[0].publisher_name}" if a.sources else "Mars News Visual"
                dirty = True

            if dirty:
                updated_count += 1

        db.commit()
        print(f"Cleanup finished successfully!")
        print(f"  - Total articles updated: {updated_count}")
        print(f"  - Headlines cleaned: {cleaned_headlines}")
        print(f"  - Summaries cleaned: {cleaned_summaries}")
        print(f"  - Bodies cleaned: {cleaned_bodies}")

    except Exception as e:
        db.rollback()
        print(f"Error during cleanup: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    clean_database()
