import time
import logging
from datetime import datetime, timezone
from app.core.database import SessionLocal
from app.services.collector import collect_all_enabled_sources
from app.services.clustering import cluster_pending_items
from app.services.publishing import auto_publish_ready_clusters
from app.core.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("mars_news_scheduler")

def run_standalone_scheduler(single_run: bool = False):
    """Zero-dependency local background scheduler that can run on Windows without Redis/Docker."""
    logger.info("MARS NEWS Standalone Newsroom Worker Started")
    iteration = 1

    while True:
        logger.info(f"--- Pipeline Execution Loop #{iteration} ---")
        db = SessionLocal()
        try:
            # Step 1: Ingestion
            logger.info("Executing news ingestion from authorized enabled sources...")
            ingest_result = collect_all_enabled_sources(db)
            logger.info(f"Ingestion complete: {ingest_result.get('total_new_items', 0)} new items collected.")

            # Step 2: Clustering
            logger.info("Clustering pending reports...")
            cluster_result = cluster_pending_items(db)
            logger.info(f"Clustering complete: {cluster_result.get('clusters_created', 0)} created, {cluster_result.get('clusters_updated', 0)} updated.")

            # Step 3: Publishing
            if not settings.EMERGENCY_PUBLISHING_PAUSE:
                logger.info("Processing editorial publishing queue...")
                pub_result = auto_publish_ready_clusters(db, max_articles=5)
                logger.info(f"Publishing complete: {pub_result.get('processed', 0)} stories processed.")
            else:
                logger.warning("Publishing paused: Global emergency publishing pause switch is active.")

        except Exception as e:
            logger.error(f"Scheduler execution error: {e}", exc_info=True)
        finally:
            db.close()

        if single_run:
            logger.info("Single run completed.")
            break

        interval = settings.AUTO_COLLECT_INTERVAL_MINUTES * 60
        logger.info(f"Sleeping for {interval} seconds until next scheduled run...")
        time.sleep(interval)
        iteration += 1

if __name__ == "__main__":
    import sys
    is_once = "--once" in sys.argv
    run_standalone_scheduler(single_run=is_once)
