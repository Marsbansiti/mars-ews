import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import GUID, TimestampMixin
from app.models.taxonomy import article_tags, article_entities

class Article(Base, TimestampMixin):
    __tablename__ = "articles"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    cluster_id = Column(GUID, ForeignKey("story_clusters.id", ondelete="SET NULL"), nullable=True, index=True)
    category_id = Column(GUID, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)

    slug = Column(String(512), unique=True, nullable=False, index=True)
    headline = Column(String(512), nullable=False)
    summary = Column(Text, nullable=False)
    content_body = Column(Text, nullable=False)
    language = Column(String(20), default="en", nullable=False)

    status = Column(String(50), default="DRAFT", nullable=False, index=True)  # DRAFT, IN_REVIEW, EDITORIAL_HOLD, PUBLISHED, ARCHIVED
    risk_level = Column(String(50), default="LOW", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    risk_reasons = Column(JSON, default=list, nullable=False)

    readability_score = Column(Float, default=70.0, nullable=False)
    reading_time_minutes = Column(Integer, default=2, nullable=False)

    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    is_breaking = Column(Boolean, default=False, nullable=False, index=True)
    is_featured = Column(Boolean, default=False, nullable=False, index=True)
    is_regional = Column(Boolean, default=False, nullable=False, index=True)
    regional_state = Column(String(100), nullable=True, index=True)  # e.g., "Odisha", "Maharashtra"

    hero_image_url = Column(String(1024), nullable=True)
    hero_image_alt = Column(String(255), nullable=True)
    hero_image_caption = Column(String(255), nullable=True)
    hero_image_license = Column(String(100), nullable=True)

    seo_title = Column(String(255), nullable=True)
    seo_description = Column(String(512), nullable=True)
    ai_generated = Column(Boolean, default=True, nullable=False)
    version = Column(Integer, default=1, nullable=False)

    # Relationships
    cluster = relationship("StoryCluster", back_populates="articles")
    category_rel = relationship("Category", back_populates="articles")
    tags = relationship("Tag", secondary=article_tags, back_populates="articles")
    entities = relationship("Entity", secondary=article_entities, back_populates="articles")
    sources = relationship("ArticleSource", back_populates="article", cascade="all, delete-orphan")
    revisions = relationship("ArticleRevision", back_populates="article", cascade="all, delete-orphan")
    claims = relationship("ArticleClaim", back_populates="article", cascade="all, delete-orphan")
    corrections = relationship("Correction", back_populates="article", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_articles_status_published", "status", "published_at"),
    )

class ArticleSource(Base, TimestampMixin):
    __tablename__ = "article_sources"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(GUID, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    publisher_name = Column(String(255), nullable=False)
    source_url = Column(String(1024), nullable=False)
    original_headline = Column(String(512), nullable=True)
    published_date = Column(DateTime(timezone=True), nullable=True)
    attribution_text = Column(String(255), nullable=False)
    source_item_id = Column(GUID, ForeignKey("source_items.id", ondelete="SET NULL"), nullable=True)

    article = relationship("Article", back_populates="sources")

class ArticleRevision(Base, TimestampMixin):
    __tablename__ = "article_revisions"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(GUID, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    revision_number = Column(Integer, nullable=False)
    headline = Column(String(512), nullable=False)
    summary = Column(Text, nullable=False)
    content_body = Column(Text, nullable=False)
    changed_by = Column(String(255), default="AI_EDITORIAL", nullable=False)
    change_reason = Column(String(512), nullable=True)

    article = relationship("Article", back_populates="revisions")

class ArticleClaim(Base, TimestampMixin):
    __tablename__ = "article_claims"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(GUID, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_text = Column(Text, nullable=False)
    claim_type = Column(String(50), default="FACT", nullable=False)  # STATISTIC, DATE, QUOTE, OFFICIAL_STATEMENT, FACT
    verification_status = Column(String(50), default="VERIFIED", nullable=False)  # VERIFIED, UNVERIFIED, CONFLICTING, REJECTED
    confidence_score = Column(Float, default=1.0, nullable=False)
    verification_notes = Column(Text, nullable=True)

    article = relationship("Article", back_populates="claims")
    evidence = relationship("ClaimEvidence", back_populates="claim", cascade="all, delete-orphan")

class ClaimEvidence(Base, TimestampMixin):
    __tablename__ = "claim_evidence"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id = Column(GUID, ForeignKey("article_claims.id", ondelete="CASCADE"), nullable=False, index=True)
    source_name = Column(String(255), nullable=False)
    source_url = Column(String(1024), nullable=False)
    supporting_excerpt = Column(Text, nullable=False)
    is_direct_match = Column(Boolean, default=True, nullable=False)

    claim = relationship("ArticleClaim", back_populates="evidence")

class Correction(Base, TimestampMixin):
    __tablename__ = "corrections"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(GUID, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    correction_notice = Column(Text, nullable=False)
    corrected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    editor_name = Column(String(255), default="Editor-in-Chief", nullable=False)
    affected_fields = Column(JSON, default=list, nullable=False)

    article = relationship("Article", back_populates="corrections")
