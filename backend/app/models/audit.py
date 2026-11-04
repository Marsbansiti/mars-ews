import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import GUID, TimestampMixin

class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action_type = Column(String(100), nullable=False, index=True)  # INGESTION, CLUSTER_CREATED, AI_GENERATION, FACT_CHECK, EDITORIAL_HOLD, ARTICLE_PUBLISHED, EMERGENCY_PAUSE, SOURCE_MODIFIED
    target_type = Column(String(100), nullable=True)  # Source, Article, Cluster, Queue, System
    target_id = Column(String(36), nullable=True)

    summary = Column(String(512), nullable=False)
    details = Column(JSON, default=dict, nullable=False)
    ip_address = Column(String(45), nullable=True)
    performed_by = Column(String(100), default="SYSTEM_AUTOMATION", nullable=False)

    user = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("idx_audit_logs_action_created", "action_type", "created_at"),
    )

class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    level = Column(String(50), default="INFO", nullable=False)  # INFO, WARNING, ERROR, CRITICAL
    category = Column(String(50), default="EDITORIAL", nullable=False)  # EDITORIAL, HARVESTER, SYSTEM, SECURITY
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    action_link = Column(String(512), nullable=True)
    metadata_json = Column(JSON, default=dict, nullable=False)

class AnalyticsEvent(Base, TimestampMixin):
    __tablename__ = "analytics_events"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(50), nullable=False, index=True)  # ARTICLE_VIEW, CATEGORY_CLICK, SEARCH_QUERY, SHARE_CLICK
    article_id = Column(GUID, ForeignKey("articles.id", ondelete="SET NULL"), nullable=True, index=True)
    category_slug = Column(String(100), nullable=True)
    search_query = Column(String(255), nullable=True)
    client_ip_hash = Column(String(64), nullable=True)
    user_agent = Column(String(255), nullable=True)
    metadata_json = Column(JSON, default=dict, nullable=False)
