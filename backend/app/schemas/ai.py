from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class ExtractedClaim(BaseModel):
    claim_text: str = Field(description="Exact factual assertion made in the report.")
    claim_type: str = Field(description="STATISTIC, DATE, QUOTE, OFFICIAL_STATEMENT, or FACT.")
    supporting_source_publisher: str = Field(description="Publisher that reported this claim.")
    supporting_quote_or_context: str = Field(description="Direct sentence or excerpt from the authorized source text.")
    confidence: float = Field(default=1.0, description="Verification confidence score (0.0 to 1.0).")

class DivergentPerspective(BaseModel):
    topic: str
    perspective_a: str
    source_a: str
    perspective_b: str
    source_b: str

class AIEditorialOutput(BaseModel):
    original_headline: str = Field(description="Original, journalistic headline accurately reflecting the verified facts.")
    original_summary: str = Field(description="Concise 2-3 sentence executive editorial summary.")
    article_body: str = Field(description="Multi-paragraph, independently composed journalistic article adhering to strict factual bounds.")
    category: str = Field(description="Category name (India, Politics, Business, Technology, Sports, Entertainment, Education, Science, Lifestyle, Regional, Odisha).")
    tags: List[str] = Field(default_factory=list, description="Relevant news tags.")
    is_regional: bool = Field(default=False)
    regional_state: Optional[str] = Field(default=None, description="E.g. Odisha, Karnataka, etc.")
    readability_score: float = Field(default=70.0, description="Readability score (0-100).")
    reading_time_minutes: int = Field(default=2)
    seo_title: str = Field(description="SEO-optimized title under 60 characters.")
    seo_description: str = Field(description="SEO meta description under 155 characters.")
    claims: List[ExtractedClaim] = Field(default_factory=list, description="Extracted factual claims with source mapping.")
    divergent_points: List[DivergentPerspective] = Field(default_factory=list, description="Conflicting or differing perspectives across sources.")
    detected_risk_topics: List[str] = Field(default_factory=list, description="E.g. elections, crime, communal, financial allegations, death reports, national security.")
    suggested_risk_level: str = Field(default="LOW", description="LOW, MEDIUM, HIGH, or CRITICAL.")
    editorial_rationale: str = Field(description="Brief note from AI explaining the synthesis and safety checks.")
