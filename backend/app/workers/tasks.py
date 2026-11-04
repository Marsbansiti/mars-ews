from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.collector import collect_all_enabled_sources
from app.services.clustering import cluster_pending_items
from app.services.publishing import auto_publish_ready_clusters

@celery_app.task(name="app.workers.tasks.task_collect_all_news")
def task_collect_all_news():
    db = SessionLocal()
    try:
        return collect_all_enabled_sources(db)
    finally:
        db.close()

@celery_app.task(name="app.workers.tasks.task_cluster_items")
def task_cluster_items():
    db = SessionLocal()
    try:
        return cluster_pending_items(db)
    finally:
        db.close()

@celery_app.task(name="app.workers.tasks.task_publish_stories")
def task_publish_stories():
    db = SessionLocal()
    try:
        return auto_publish_ready_clusters(db, max_articles=5)
    finally:
        db.close()
