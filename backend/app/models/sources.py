import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import GUID, TimestampMixin

class NewsSource(Base, TimestampMixin):
    __tablename__ = "news_sources"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    publisher_name = Column(String(255), nullable=False, unique=True, index=True)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    official_website_url = Column(String(1024), nullable=False)
    language = Column(String(20), default="en", nullable=False)
    country = Column(String(10), default="IN", nullable=False)
    coverage_categories = Column(JSON, default=list, nullable=False)  # e.g. ["National", "Politics", "Business"]
    source_type = Column(String(50), default="newspaper", nullable=False)  # newspaper, digital_media, government, regional
    rss_feed_url = Column(String(1024), nullable=True)
    api_endpoint = Column(String(1024), nullable=True)
    api_key_configured = Column(Boolean, default=False, nullable=False)

    permission_status = Column(String(50), default="UNVERIFIED", nullable=False)  # UNVERIFIED, DISCOVERY_PENDING, VERIFIED, REJECTED
    content_usage_policy = Column(Text, nullable=True)
    collection_frequency = Column(Integer, default=15, nullable=False)  # in minutes
    enabled = Column(Boolean, default=False, nullable=False)
    credibility_score = Column(Float, default=8.5, nullable=False)

    last_successful_collection = Column(DateTime(timezone=True), nullable=True)
    last_collection_error = Column(Text, nullable=True)
    consecutive_failures = Column(Integer, default=0, nullable=False)

    permissions = relationship("SourcePermission", back_populates="source", uselist=False, cascade="all, delete-orphan")
    items = relationship("SourceItem", back_populates="source", cascade="all, delete-orphan")
    health_logs = relationship("SourceHealthLog", back_populates="source", cascade="all, delete-orphan")

class SourcePermission(Base, TimestampMixin):
    __tablename__ = "source_permissions"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(GUID, ForeignKey("news_sources.id", ondelete="CASCADE"), nullable=False, unique=True)

    can_collect_headlines = Column(Boolean, default=True, nullable=False)
    can_collect_descriptions = Column(Boolean, default=True, nullable=False)
    can_create_original_summaries = Column(Boolean, default=True, nullable=False)
    can_access_full_text = Column(Boolean, default=False, nullable=False)
    can_reuse_images = Column(Boolean, default=False, nullable=False)
    can_commercially_redistribute = Column(Boolean, default=False, nullable=False)
    can_display_attribution = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)

    source = relationship("NewsSource", back_populates="permissions")

class SourceHealthLog(Base, TimestampMixin):
    __tablename__ = "source_health_logs"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(GUID, ForeignKey("news_sources.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False)  # SUCCESS, FAILED, TIMEOUT, DISCOVERY_RUN
    response_time_ms = Column(Integer, nullable=True)
    http_status = Column(Integer, nullable=True)
    items_collected = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)

    source = relationship("NewsSource", back_populates="health_logs")
