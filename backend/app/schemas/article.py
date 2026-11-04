from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ArticleSourceResponse(BaseModel):
    id: str
    publisher_name: str
    source_url: str
    original_headline: Optional[str]
    published_date: Optional[datetime]
    attribution_text: str

    model_config = ConfigDict(from_attributes=True)

class ClaimEvidenceResponse(BaseModel):
    id: str
    source_name: str
    source_url: str
    supporting_excerpt: str
    is_direct_match: bool

    model_config = ConfigDict(from_attributes=True)

class ArticleClaimResponse(BaseModel):
    id: str
    claim_text: str
    claim_type: str
    verification_status: str
    confidence_score: float
    verification_notes: Optional[str]
    evidence: List[ClaimEvidenceResponse] = []

    model_config = ConfigDict(from_attributes=True)

class ArticleRevisionResponse(BaseModel):
    id: str
    revision_number: int
    headline: str
    summary: str
    changed_by: str
    change_reason: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CorrectionResponse(BaseModel):
    id: str
    correction_notice: str
    corrected_at: datetime
    editor_name: str
    affected_fields: List[str]

    model_config = ConfigDict(from_attributes=True)

class ArticleListResponse(BaseModel):
    id: str
    slug: str
    headline: str
    summary: str
    category: str
    category_slug: str
    language: str
    status: str
    risk_level: str
    published_at: Optional[datetime]
    is_breaking: bool
    is_featured: bool
    is_regional: bool
    regional_state: Optional[str]
    hero_image_url: Optional[str]
    hero_image_alt: Optional[str]
    hero_image_caption: Optional[str]
    hero_image_license: Optional[str]
    readability_score: float
    reading_time_minutes: int
    version: int
    sources_count: int = 0
    claims_count: int = 0

class ArticleDetailResponse(ArticleListResponse):
    content_body: str
    seo_title: Optional[str]
    seo_description: Optional[str]
    ai_generated: bool
    risk_reasons: List[str] = []
    sources: List[ArticleSourceResponse] = []
    claims: List[ArticleClaimResponse] = []
    revisions: List[ArticleRevisionResponse] = []
    corrections: List[CorrectionResponse] = []
    tags: List[str] = []

class ArticleUpdate(BaseModel):
    headline: Optional[str] = None
    summary: Optional[str] = None
    content_body: Optional[str] = None
    status: Optional[str] = None
    category_id: Optional[str] = None
    is_breaking: Optional[bool] = None
    is_featured: Optional[bool] = None
    hero_image_url: Optional[str] = None
    hero_image_alt: Optional[str] = None
    hero_image_caption: Optional[str] = None
    change_reason: Optional[str] = None

class CorrectionCreate(BaseModel):
    correction_notice: str
    affected_fields: List[str] = ["headline", "content_body"]
    editor_name: Optional[str] = "Editor Desk"
