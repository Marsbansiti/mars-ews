from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel

class DashboardOverviewStats(BaseModel):
    total_sources: int
    active_sources: int
    stories_collected_today: int
    articles_processed: int
    articles_published: int
    duplicate_stories: int
    editorial_holds: int
    failed_tasks: int
    ai_jobs_count: int
    total_tokens_used: int
    estimated_api_cost_usd: float
    average_processing_time_ms: float
    system_health: str
    emergency_pause: bool
    recent_activity: List[Dict[str, Any]] = []

class SystemSettingsSchema(BaseModel):
    emergency_publishing_pause: bool
    auto_collect_interval_minutes: int
    auto_publish_delay_minutes: int
    fact_validation_strict_mode: bool
    openai_model: str
    embedding_model: str
