import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import GUID, TimestampMixin

class PublishingQueueItem(Base, TimestampMixin):
    __tablename__ = "publishing_queue"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(GUID, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    scheduled_for = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    status = Column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, PROCESSING, PUBLISHED, FAILED, HELD
    retry_count = Column(Integer, default=0, nullable=False)
    idempotency_key = Column(String(255), unique=True, nullable=False)
    error_log = Column(Text, nullable=True)

    article = relationship("Article")

    __table_args__ = (
        Index("idx_pub_queue_status_sched", "status", "scheduled_for"),
    )
