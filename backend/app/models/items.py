import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import GUID, TimestampMixin

class SourceItem(Base, TimestampMixin):
    __tablename__ = "source_items"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(GUID, ForeignKey("news_sources.id", ondelete="CASCADE"), nullable=False, index=True)

    original_headline = Column(String(512), nullable=False)
    original_url = Column(String(1024), nullable=False)
    canonical_url = Column(String(1024), nullable=False, index=True)
    publisher = Column(String(255), nullable=False)
    publication_timestamp = Column(DateTime(timezone=True), nullable=True)
    author = Column(String(255), nullable=True)
    authorized_description = Column(Text, nullable=True)
    language = Column(String(20), default="en", nullable=False)
    category = Column(String(100), default="General", nullable=False)
    collection_timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    content_hash = Column(String(64), nullable=False, unique=True, index=True)
    raw_metadata = Column(JSON, default=dict, nullable=False)

    processing_status = Column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, CLUSTERED, PROCESSED, DUPLICATE, REJECTED
    rejection_reason = Column(String(255), nullable=True)

    source = relationship("NewsSource", back_populates="items")
    cluster_links = relationship("ClusterItem", back_populates="source_item", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_source_items_canonical", "canonical_url"),
        Index("idx_source_items_status", "processing_status"),
    )
