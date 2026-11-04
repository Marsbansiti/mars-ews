import uuid
from sqlalchemy import Column, String, Integer, Float, Text, JSON, Index
from app.core.database import Base
from app.models.base import GUID, TimestampMixin

class AIJob(Base, TimestampMixin):
    __tablename__ = "ai_jobs"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_type = Column(String(50), nullable=False, index=True)  # EDITORIAL_GENERATION, FACT_VALIDATION, CLUSTERING, EMBEDDING
    model_name = Column(String(100), nullable=False)
    target_id = Column(String(36), nullable=True, index=True)  # cluster_id or article_id

    status = Column(String(50), default="RUNNING", nullable=False, index=True)  # RUNNING, SUCCESS, FAILED
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    estimated_cost_usd = Column(Float, default=0.0, nullable=False)
    execution_time_ms = Column(Integer, default=0, nullable=False)

    error_message = Column(Text, nullable=True)
    raw_prompt = Column(Text, nullable=True)
    response_payload = Column(JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("idx_ai_jobs_status_type", "status", "job_type"),
    )
