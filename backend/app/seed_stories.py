from datetime import datetime, timezone, timedelta
from app.core.database import SessionLocal
from app.models.sources import NewsSource
from app.models.items import SourceItem
from app.services.collector import compute_content_hash, normalize_url
from app.services.clustering import cluster_pending_items
from app.services.publishing import process_cluster_for_publishing
from app.models.clusters import StoryCluster

SAMPLE_INGESTION_DATA = [
    # Story 1: ISRO Satellite (Multi-source National / Science story)
    {
        "source_slug": "the-hindu",
        "headline": "ISRO successfully launches next-generation climate observation satellite into geosynchronous orbit",
        "url": "https://www.thehindu.com/sci-tech/science/isro-climate-satellite-launch-2026/article67890.ece",
        "description": "The Indian Space Research Organisation (ISRO) launched its advanced meteorological satellite aboard the GSLV-F14 launch vehicle from Sriharikota, achieving precise orbital injection. Space officials confirmed solar arrays deployed successfully.",
        "category": "Science",
        "hours_ago": 4
    },
    {
        "source_slug": "times-of-india",
        "headline": "ISRO launches state-of-the-art climate satellite from Sriharikota spaceport",
        "url": "https://timesofindia.indiatimes.com/india/isro-gslv-launch-climate-monitoring-satellite/articleshow/998877.cms",
        "description": "India's space agency ISRO accomplished another milestone with the successful lift-off of its climate monitoring spacecraft from the Satish Dhawan Space Centre. The satellite will provide high-resolution atmospheric soundings.",
        "category": "Science",
        "hours_ago": 3
    },
    {
        "source_slug": "pib-india",
        "headline": "Union Minister congratulates ISRO team on flawless launch of climate and weather satellite",
        "url": "https://pib.gov.in/PressReleasePage.aspx?PRID=2012345",
        "description": "Prime Minister and Science & Technology Minister applauded scientists of ISRO for the successful deployment of the indigenous climate observation satellite, calling it a boost for agricultural forecasting and disaster resilience.",
        "category": "Science",
        "hours_ago": 2
    },

    # Story 2: Odisha High-Tech Park (Regional / Technology / Odisha story)
    {
        "source_slug": "deccan-herald",
        "headline": "Odisha approves Rs 4,500 crore Semiconductor and Advanced AI Park in Bhubaneswar",
        "url": "https://www.deccanherald.com/business/odisha-cabinet-clears-semiconductor-ai-park-bhubaneswar-1299.html",
        "description": "The Odisha State Cabinet chaired by the Chief Minister cleared high-level investment proposals including a state-of-the-art semiconductor packaging and AI computing park spread across 200 acres in InfoValley Bhubaneswar.",
        "category": "Odisha",
        "hours_ago": 6
    },
    {
        "source_slug": "the-hindu",
        "headline": "Bhubaneswar to host mega Semiconductor and AI Innovation Cluster with Rs 4,500 cr outlay",
        "url": "https://www.thehindu.com/news/national/other-states/bhubaneswar-semiconductor-ai-hub-approved/article67891.ece",
        "description": "Odisha's semiconductor policy garners key milestone as state approves Rs 4,500 crore facility aiming to generate over 15,000 engineering jobs and position Bhubaneswar as an Eastern electronics design hub.",
        "category": "Odisha",
        "hours_ago": 5
    },

    # Story 3: Financial & Economic story (Business / Markets)
    {
        "source_slug": "the-hindu",
        "headline": "RBI expands Central Bank Digital Currency cross-border settlement pilots with global financial hubs",
        "url": "https://www.thehindu.com/business/Economy/rbi-digital-rupee-cross-border-settlement/article67892.ece",
        "description": "Reserve Bank of India Governor announced new regulatory sandbox frameworks enabling institutional cross-border settlements using wholesale digital rupee (e-INR) across participating ASEAN partner jurisdictions.",
        "category": "Business",
        "hours_ago": 8
    },
    {
        "source_slug": "times-of-india",
        "headline": "RBI expands Digital Rupee wholesale pilot for international trade payments",
        "url": "https://timesofindia.indiatimes.com/business/india-business/rbi-digital-rupee-wholesale-expansion/articleshow/998878.cms",
        "description": "The central bank widened its CBDC pilot project, facilitating bilateral settlements in digital currency to reduce international transaction friction and exchange costs for Indian exporters.",
        "category": "Business",
        "hours_ago": 7
    },

    # Story 4: Sensitive Topic Story (Triggers Fact Validation Auto-Hold!)
    {
        "source_slug": "the-new-indian-express",
        "headline": "Opposition leaders demand parliamentary committee inquiry over election bribery scam allegations",
        "url": "https://www.newindianexpress.com/nation/2026/nov/opposition-election-commission-bribery-allegations.html",
        "description": "Several political parties submitted formal memorandums alleging illicit funding discrepancies during state civic polls and demanding a special investigation team probe into financial allegations.",
        "category": "Politics",
        "hours_ago": 2
    }
]

def seed_sample_news_pipeline():
    db = SessionLocal()
    try:
        print("[PIPELINE SEEDER] Ingesting verified multi-source news items...")
        now = datetime.now(timezone.utc)
        created_items = []

        for item_data in SAMPLE_INGESTION_DATA:
            source = db.query(NewsSource).filter(NewsSource.slug == item_data["source_slug"]).first()
            if not source:
                continue

            canonical = normalize_url(item_data["url"])
            c_hash = compute_content_hash(str(source.id), canonical, item_data["headline"])

            existing = db.query(SourceItem).filter(SourceItem.content_hash == c_hash).first()
            if existing:
                continue

            pub_time = now - timedelta(hours=item_data["hours_ago"])
            item = SourceItem(
                source_id=source.id,
                original_headline=item_data["headline"],
                original_url=item_data["url"],
                canonical_url=canonical,
                publisher=source.publisher_name,
                publication_timestamp=pub_time,
                authorized_description=item_data["description"],
                language=source.language,
                category=item_data["category"],
                content_hash=c_hash,
                raw_metadata={"verified_seed": True, "source_credibility": source.credibility_score},
                processing_status="PENDING"
            )
            db.add(item)
            created_items.append(item)

        db.commit()
        print(f"[PIPELINE SEEDER] Ingested {len(created_items)} items.")

        # Step 2: Story Clustering
        print("[PIPELINE SEEDER] Running multi-signal story clustering...")
        cluster_res = cluster_pending_items(db)
        print(f"[PIPELINE SEEDER] Clustering finished: {cluster_res}")

        # Step 3: Run AI Editorial Synthesis & Publishing
        print("[PIPELINE SEEDER] Running AI Editorial & Validation Engine...")
        clusters = db.query(StoryCluster).filter(StoryCluster.status == "ACTIVE").all()
        for c in clusters:
            res = process_cluster_for_publishing(str(c.id), db)
            print(f"  -> Cluster: '{c.cluster_title[:50]}' => Result: {res.get('status')} [Risk: {res.get('risk_level')}]")

        print("[PIPELINE SEEDER] Successfully populated pipeline!")
    except Exception as e:
        db.rollback()
        print(f"[PIPELINE SEEDER] Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_sample_news_pipeline()
