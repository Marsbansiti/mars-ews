import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import GUID, TimestampMixin

class StoryCluster(Base, TimestampMixin):
    __tablename__ = "story_clusters"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    cluster_title = Column(String(512), nullable=False)
    slug = Column(String(512), nullable=False, unique=True, index=True)
    category = Column(String(100), default="General", nullable=False)
    story_type = Column(String(50), default="NEW", nullable=False)  # NEW, DEVELOPING, UPDATED, RELATED, DUPLICATE, CORRECTION
    status = Column(String(50), default="ACTIVE", nullable=False, index=True)  # ACTIVE, SYNTHESIZING, READY_TO_PUBLISH, PUBLISHED, ARCHIVED

    extracted_entities = Column(JSON, default=dict, nullable=False)  # { "people": [], "orgs": [], "locations": [] }
    synthesized_notes = Column(Text, nullable=True)
    divergent_points = Column(JSON, default=list, nullable=False)

    first_seen_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    item_count = Column(Float, default=1, nullable=False)

    cluster_items = relationship("ClusterItem", back_populates="cluster", cascade="all, delete-orphan")
    articles = relationship("Article", back_populates="cluster")

class ClusterItem(Base, TimestampMixin):
    __tablename__ = "cluster_items"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    cluster_id = Column(GUID, ForeignKey("story_clusters.id", ondelete="CASCADE"), nullable=False, index=True)
    source_item_id = Column(GUID, ForeignKey("source_items.id", ondelete="CASCADE"), nullable=False, index=True)

    similarity_score = Column(Float, default=1.0, nullable=False)
    role_in_cluster = Column(String(50), default="SUPPORTING", nullable=False)  # PRIMARY, SUPPORTING, CONFLICTING
    notes = Column(String(255), nullable=True)

    cluster = relationship("StoryCluster", back_populates="cluster_items")
    source_item = relationship("SourceItem", back_populates="cluster_links")
