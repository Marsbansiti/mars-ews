from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.clusters import StoryCluster, ClusterItem
from app.services.publishing import process_cluster_for_publishing
from app.services.clustering import cluster_pending_items

router = APIRouter(prefix="/admin/clusters", tags=["Admin Story Clusters"])

@router.get("")
def list_clusters(status: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    q = db.query(StoryCluster)
    if status:
        q = q.filter(StoryCluster.status == status)

    clusters = q.order_by(StoryCluster.last_updated_at.desc()).limit(limit).all()
    results = []
    for c in clusters:
        items_summary = []
        for ci in c.cluster_items:
            items_summary.append({
                "source_item_id": str(ci.source_item_id),
                "publisher": ci.source_item.publisher if ci.source_item else "Unknown",
                "headline": ci.source_item.original_headline if ci.source_item else "",
                "similarity_score": ci.similarity_score,
                "role": ci.role_in_cluster
            })

        results.append({
            "id": str(c.id),
            "cluster_title": c.cluster_title,
            "slug": c.slug,
            "category": c.category,
            "story_type": c.story_type,
            "status": c.status,
            "item_count": c.item_count,
            "extracted_entities": c.extracted_entities,
            "first_seen_at": c.first_seen_at.isoformat() if c.first_seen_at else None,
            "last_updated_at": c.last_updated_at.isoformat() if c.last_updated_at else None,
            "items": items_summary
        })
    return results

@router.post("/run-clustering")
def run_manual_clustering(threshold: float = 0.45, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    res = cluster_pending_items(db, similarity_threshold=threshold)
    return res

@router.post("/{id}/synthesize")
def trigger_cluster_synthesis(id: str, force_publish: bool = False, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    res = process_cluster_for_publishing(id, db, force_publish=force_publish)
    return res
