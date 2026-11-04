import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON
from app.core.database import Base
from app.models.base import GUID, TimestampMixin

class MediaAsset(Base, TimestampMixin):
    __tablename__ = "media_assets"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    image_url = Column(String(1024), nullable=False)
    original_source = Column(String(255), nullable=False)
    license = Column(String(100), default="CC-BY-4.0", nullable=False)  # CC-BY-4.0, PUBLIC_DOMAIN, EDITORIAL_USE, LICENSED_PUBLISHER, AI_GENERATED
    attribution = Column(String(255), nullable=False)
    usage_permission = Column(Boolean, default=True, nullable=False)
    alt_text = Column(String(512), nullable=False)
    copyright_information = Column(String(512), nullable=True)
    media_type = Column(String(50), default="image/jpeg", nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    metadata_json = Column(JSON, default=dict, nullable=False)
