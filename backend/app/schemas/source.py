from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, HttpUrl, ConfigDict

class SourcePermissionSchema(BaseModel):
    can_collect_headlines: bool = True
    can_collect_descriptions: bool = True
    can_create_original_summaries: bool = True
    can_access_full_text: bool = False
    can_reuse_images: bool = False
    can_commercially_redistribute: bool = False
    can_display_attribution: bool = True
    notes: Optional[str] = None

class NewsSourceCreate(BaseModel):
    publisher_name: str
    official_website_url: str
    language: str = "en"
    country: str = "IN"
    coverage_categories: List[str] = []
    source_type: str = "newspaper"
    rss_feed_url: Optional[str] = None
    collection_frequency: int = 15
    enabled: bool = False
    credibility_score: float = 8.5
    content_usage_policy: Optional[str] = None
    permissions: Optional[SourcePermissionSchema] = None

class NewsSourceUpdate(BaseModel):
    publisher_name: Optional[str] = None
    official_website_url: Optional[str] = None
    language: Optional[str] = None
    coverage_categories: Optional[List[str]] = None
    source_type: Optional[str] = None
    rss_feed_url: Optional[str] = None
    permission_status: Optional[str] = None
    collection_frequency: Optional[int] = None
    enabled: Optional[bool] = None
    credibility_score: Optional[float] = None
    content_usage_policy: Optional[str] = None
    permissions: Optional[SourcePermissionSchema] = None

class NewsSourceResponse(BaseModel):
    id: str
    publisher_name: str
    slug: str
    official_website_url: str
    language: str
    country: str
    coverage_categories: List[str]
    source_type: str
    rss_feed_url: Optional[str]
    permission_status: str
    collection_frequency: int
    enabled: bool
    credibility_score: float
    content_usage_policy: Optional[str]
    last_successful_collection: Optional[datetime]
    last_collection_error: Optional[str]
    consecutive_failures: int
    permissions: Optional[SourcePermissionSchema] = None
    items_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)
