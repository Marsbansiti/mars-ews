import asyncio
import json
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import engine, Base
from app.db_seed import seed_database
from app.services.autonomous_engine import autonomous_background_loop, ENGINE_METRICS

# Import API Routers
from app.api.v1.auth import router as auth_router
from app.api.v1.public import router as public_router
from app.api.v1.admin_dashboard import router as admin_dashboard_router
from app.api.v1.admin_sources import router as admin_sources_router
from app.api.v1.admin_collector import router as admin_collector_router
from app.api.v1.admin_clusters import router as admin_clusters_router
from app.api.v1.admin_articles import router as admin_articles_router
from app.api.v1.admin_validation import router as admin_validation_router
from app.api.v1.admin_media import router as admin_media_router
from app.api.v1.admin_settings import router as admin_settings_router
from app.api.v1.admin_analytics import router as admin_analytics_router
from app.api.v1.admin_users import router as admin_users_router
from app.api.v1.admin_audit import router as admin_audit_router
from app.api.v1.admin_categories import router as admin_categories_router
from app.api.v1.admin_queue import router as admin_queue_router
from app.api.v1.admin_jobs import router as admin_jobs_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize schema and seed database
    Base.metadata.create_all(bind=engine)
    seed_database()

    # 2. Launch autonomous background newsroom collector loop (zero button clicks needed)
    bg_task = asyncio.create_task(autonomous_background_loop(interval_seconds=90))
    yield
    # Graceful shutdown
    bg_task.cancel()
    try:
        await bg_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="MARS NEWS API",
    description="Automated Indian Digital Newspaper & News Intelligence Platform API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(public_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(admin_dashboard_router, prefix="/api/v1")
app.include_router(admin_sources_router, prefix="/api/v1")
app.include_router(admin_collector_router, prefix="/api/v1")
app.include_router(admin_clusters_router, prefix="/api/v1")
app.include_router(admin_articles_router, prefix="/api/v1")
app.include_router(admin_validation_router, prefix="/api/v1")
app.include_router(admin_media_router, prefix="/api/v1")
app.include_router(admin_settings_router, prefix="/api/v1")
app.include_router(admin_analytics_router, prefix="/api/v1")
app.include_router(admin_users_router, prefix="/api/v1")
app.include_router(admin_audit_router, prefix="/api/v1")
app.include_router(admin_categories_router, prefix="/api/v1")
app.include_router(admin_queue_router, prefix="/api/v1")
app.include_router(admin_jobs_router, prefix="/api/v1")

# Mount Static Uploads for Local News Photography
media_dir = Path(__file__).resolve().parent.parent / "media_uploads"
media_dir.mkdir(parents=True, exist_ok=True)
frontend_uploads = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "uploads"
frontend_uploads.mkdir(parents=True, exist_ok=True)

# Mount primary uploads path
app.mount("/uploads", StaticFiles(directory=str(frontend_uploads)), name="uploads")

@app.get("/health", tags=["System"])
def health_check(request: Request = None):
    db_status = "CONNECTED"
    db_stats = {}
    try:
        from app.core.database import SessionLocal
        from app.models.articles import Article
        from app.models.sources import NewsSource
        from app.models.clusters import StoryCluster
        db = SessionLocal()
        total_arts = db.query(Article).count()
        total_srcs = db.query(NewsSource).count()
        active_srcs = db.query(NewsSource).filter(NewsSource.enabled == True).count()
        total_clusters = db.query(StoryCluster).count()
        db_stats = {
            "total_articles_published": total_arts,
            "total_news_sources": total_srcs,
            "active_monitored_sources": active_srcs,
            "story_clusters": total_clusters
        }
        ENGINE_METRICS["sources_monitored"] = active_srcs
        db.close()
    except Exception as e:
        db_status = f"ERROR: {str(e)}"

    payload = {
        "status": "HEALTHY",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database": db_status,
        "database_metrics": db_stats,
        "autonomous_engine": {
            **ENGINE_METRICS,
            "is_running": True,
            "status": "ACTIVE" if ENGINE_METRICS.get("loop_active", True) else "PAUSED"
        },
        "emergency_pause": settings.EMERGENCY_PUBLISHING_PAUSE,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return Response(
        content=json.dumps(payload, indent=2),
        media_type="application/json"
    )
