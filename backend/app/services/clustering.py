import re
import math
import difflib
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple, Optional
import uuid
from sqlalchemy.orm import Session
from app.models.items import SourceItem
from app.models.clusters import StoryCluster, ClusterItem
from app.models.audit import AuditLog

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't",
    "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him",
    "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't",
    "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor",
    "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out",
    "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some",
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through",
    "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've",
    "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who",
    "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll",
    "you're", "you've", "your", "yours", "yourself", "yourselves", "says", "said", "new", "delhi", "india"
}

def tokenize(text: str) -> List[str]:
    clean = re.sub(r"[^\w\s]", " ", text.lower())
    tokens = [t.strip() for t in clean.split() if len(t.strip()) > 2 and t.strip() not in STOPWORDS]
    return tokens

def jaccard_similarity(set_a: set, set_b: set) -> float:
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union if union > 0 else 0.0

def levenshtein_ratio(s1: str, s2: str) -> float:
    """Calculates normalized similarity between two strings."""
    s1, s2 = s1.lower(), s2.lower()
    if s1 == s2:
        return 1.0
    return difflib.SequenceMatcher(None, s1, s2).ratio()

def extract_key_entities(text: str) -> Dict[str, List[str]]:
    """Heuristic named entity extractor for key Indian institutions, locations, and high-frequency capitalized terms."""
    entities = {"organizations": [], "locations": [], "people": [], "events": []}

    known_orgs = ["ISRO", "RBI", "SEBI", "BCCI", "Supreme Court", "High Court", "DRDO", "AIIMS", "IIT", "CBI", "ED", "Parliament", "Lok Sabha", "Rajya Sabha", "PIB", "ECI"]
    known_locs = ["New Delhi", "Delhi", "Odisha", "Bhubaneswar", "Mumbai", "Bengaluru", "Chennai", "Kolkata", "Hyderabad", "Punjab", "Kashmir", "Gujarat", "Assam", "Kerala"]

    text_upper = text
    for org in known_orgs:
        if re.search(r"\b" + re.escape(org) + r"\b", text_upper, re.IGNORECASE):
            entities["organizations"].append(org)

    for loc in known_locs:
        if re.search(r"\b" + re.escape(loc) + r"\b", text_upper, re.IGNORECASE):
            entities["locations"].append(loc)

    # Capitalized multi-word proper nouns
    caps = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b", text)
    for cap in caps:
        if cap not in entities["organizations"] and cap not in entities["locations"]:
            entities["people"].append(cap)

    return entities

def compute_story_similarity(item: SourceItem, cluster: StoryCluster) -> float:
    """Multi-signal similarity metric between an incoming SourceItem and a StoryCluster:
    - Normalized headline Jaccard & Levenshtein
    - Named entity intersection
    - Time proximity decay (24h window)
    """
    item_tokens = set(tokenize(item.original_headline + " " + (item.authorized_description or "")))
    cluster_tokens = set(tokenize(cluster.cluster_title + " " + (cluster.synthesized_notes or "")))

    # 1. Headline token Jaccard
    jaccard = jaccard_similarity(item_tokens, cluster_tokens)

    # 2. Levenshtein ratio on headlines
    lev = levenshtein_ratio(item.original_headline, cluster.cluster_title)

    # 3. Entity overlap
    item_entities = extract_key_entities(item.original_headline + " " + (item.authorized_description or ""))
    cluster_entities = cluster.extracted_entities or {}

    item_entity_set = set(item_entities.get("organizations", []) + item_entities.get("locations", []) + item_entities.get("people", []))
    cluster_entity_set = set(cluster_entities.get("organizations", []) + cluster_entities.get("locations", []) + cluster_entities.get("people", []))

    entity_sim = jaccard_similarity(item_entity_set, cluster_entity_set) if item_entity_set and cluster_entity_set else 0.0

    # 4. Time decay: penalize if published more than 36 hours apart
    time_sim = 1.0
    if item.publication_timestamp and cluster.first_seen_at:
        hours_diff = abs((item.publication_timestamp - cluster.first_seen_at).total_seconds()) / 3600.0
        if hours_diff > 48:
            time_sim = 0.2
        elif hours_diff > 24:
            time_sim = 0.6
        elif hours_diff > 12:
            time_sim = 0.85

    # Composite weighted similarity score
    composite_score = (jaccard * 0.40 + lev * 0.30 + entity_sim * 0.30) * time_sim
    return composite_score

def cluster_pending_items(db: Session, similarity_threshold: float = 0.45, max_items: int = 50) -> Dict[str, Any]:
    """Scans pending source items and clusters them into existing or newly formed story clusters."""
    pending_items = db.query(SourceItem).filter(SourceItem.processing_status == "PENDING").limit(max_items).all()
    if not pending_items:
        return {"processed": 0, "clusters_created": 0, "clusters_updated": 0}

    # Fetch active clusters created in the last 72 hours
    cutoff = datetime.now(timezone.utc) - timedelta(hours=72)
    active_clusters = db.query(StoryCluster).filter(
        StoryCluster.status.in_(["ACTIVE", "READY_TO_PUBLISH"]),
        StoryCluster.last_updated_at >= cutoff
    ).all()

    clusters_created = 0
    clusters_updated = 0

    for item in pending_items:
        best_cluster = None
        best_score = 0.0

        for cluster in active_clusters:
            score = compute_story_similarity(item, cluster)
            if score > best_score:
                best_score = score
                best_cluster = cluster

        if best_cluster and best_score >= similarity_threshold:
            # Determine role: if score is very high (> 0.88), item is DUPLICATE or SUPPORTING
            role = "SUPPORTING"
            if best_score > 0.85:
                role = "PRIMARY" if best_cluster.item_count == 1 else "SUPPORTING"

            cluster_link = ClusterItem(
                cluster_id=best_cluster.id,
                source_item_id=item.id,
                similarity_score=round(best_score, 3),
                role_in_cluster=role,
                notes=f"Matched cluster with confidence {best_score:.2f}"
            )
            db.add(cluster_link)

            # Update cluster metadata
            best_cluster.item_count += 1
            best_cluster.last_updated_at = datetime.now(timezone.utc)
            if best_cluster.story_type == "NEW" and best_cluster.item_count >= 2:
                best_cluster.story_type = "DEVELOPING"

            item.processing_status = "CLUSTERED"
            clusters_updated += 1
        else:
            # Create a new StoryCluster
            slug_base = re.sub(r"[^\w\s-]", "", item.original_headline.lower())
            slug = "-".join(slug_base.split()[:8]) + f"-{str(uuid.uuid4())[:6]}"
            entities = extract_key_entities(item.original_headline + " " + (item.authorized_description or ""))

            new_cluster = StoryCluster(
                cluster_title=item.original_headline,
                slug=slug,
                category=item.category or "General",
                story_type="NEW",
                status="ACTIVE",
                extracted_entities=entities,
                synthesized_notes=item.authorized_description or "",
                first_seen_at=item.publication_timestamp or datetime.now(timezone.utc),
                last_updated_at=datetime.now(timezone.utc),
                item_count=1
            )
            db.add(new_cluster)
            db.flush()

            cluster_link = ClusterItem(
                cluster_id=new_cluster.id,
                source_item_id=item.id,
                similarity_score=1.0,
                role_in_cluster="PRIMARY",
                notes="Initial seeding report for cluster"
            )
            db.add(cluster_link)

            item.processing_status = "CLUSTERED"
            active_clusters.append(new_cluster)
            clusters_created += 1

    db.commit()
    return {
        "processed": len(pending_items),
        "clusters_created": clusters_created,
        "clusters_updated": clusters_updated
    }
