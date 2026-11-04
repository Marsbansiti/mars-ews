import uuid
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import GUID, TimestampMixin

article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", GUID, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", GUID, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)

article_entities = Table(
    "article_entities",
    Base.metadata,
    Column("article_id", GUID, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("entity_id", GUID, ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True)
)

class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    display_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    articles = relationship("Article", back_populates="category_rel")

class Tag(Base, TimestampMixin):
    __tablename__ = "tags"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    usage_count = Column(Integer, default=0, nullable=False)

    articles = relationship("Article", secondary=article_tags, back_populates="tags")

class Entity(Base, TimestampMixin):
    __tablename__ = "entities"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)  # PERSON, ORG, GPE, LOCATION, EVENT
    description = Column(Text, nullable=True)
    metadata_json = Column(JSON, default=dict, nullable=False)

    articles = relationship("Article", secondary=article_entities, back_populates="entities")
