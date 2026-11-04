# MARS NEWS — AI-Powered Automated Indian Digital Newspaper & Newsroom

**MARS NEWS** is a production-grade, automated digital newspaper and news intelligence platform built for the Indian media ecosystem. It continuously monitors authorized public feeds from major Indian dailies, regional media, and government agencies, deduplicates and clusters multi-source stories, uses OpenAI structured outputs to draft original journalistic summaries, validates factual claims against verified sources, manages editorial risk with automatic hold gates, and publishes eligible articles to a modern public newspaper while giving editors an advanced administrative newsroom dashboard.

---

## 🌟 Key Features

1. **Prepopulated Indian News Directory**:
   - 10 National Dailies: *The Times of India*, *The Hindu*, *Hindustan Times*, *The Indian Express*, *The Telegraph*, *Deccan Herald*, *The New Indian Express*, *The Tribune*, *Deccan Chronicle*, *The Statesman*.
   - Official Government Releases: *Press Information Bureau (PIB)*, *DD News*.
   - Regional & Odisha Bureaus: *Odisha TV*, *Sambad English*.
2. **Server-Enforced Source Permission Gates**: Granular permissions for headlines, descriptions, full-text access, image reuse, and attribution.
3. **Multi-Signal Deduplication & Story Clustering**: Combines normalized headline Jaccard similarity, Levenshtein distance, named entity recognition (People, Organizations, Locations), and time-decay proximity.
4. **AI Editorial Engine with Zero Hallucination**: Strict OpenAI structured JSON schemas (`AIEditorialOutput`) with factual claim extraction. Never invents quotes, dates, or statistics.
5. **Fact Validation & Automatic Editorial Holds**: Factual claims mapped to source evidence. Automatically holds sensitive topics (elections, corruption, crime allegations, communal disputes, national security, death reports).
6. **Modern Public Digital Newspaper**: Classical masthead, live breaking ticker, featured lead stories, regional & Odisha desk spotlight, category sections, claims-evidence drawers, search, RSS 2.0 (`/rss.xml`), and Google News XML sitemaps.
7. **Dark-Glass Newsroom Control Suite**: 16 functional tabs (Overview, Source Manager, Incoming News, Collector, Clusters, AI Editorial, Fact Validation, Article Manager, Media Library, Categories, Queue, Automation, Analytics, Users, Audit Logs, Settings) with emergency pause switch.
8. **Production-Ready & Dual Run Mode**: Runs seamlessly on Windows standalone (SQLite/PostgreSQL fallback + standalone async scheduler) and via Docker Compose (PostgreSQL 16 + pgvector, Redis 7.2, Meilisearch 1.8, Celery Workers, Next.js, and Nginx).

---

## 🚀 Quick Start (Windows Standalone)

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 1. Backend Setup
```powershell
cd backend
# Create and activate virtual environment
python -m uv venv .venv
# Install dependencies
python -m uv pip install -r requirements.txt --python .venv\Scripts\python.exe
# Run Alembic migrations
.venv\Scripts\python.exe -m alembic upgrade head
# Seed prepopulated sources, categories, and admin account
.venv\Scripts\python.exe -m app.db_seed
# (Optional) Seed sample pipeline to see stories immediately
.venv\Scripts\python.exe -m app.seed_stories
# Start FastAPI backend server
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Setup
```powershell
cd frontend
# Install dependencies (already completed)
npm install
# Run development server
npm run dev
```

### 3. Access URLs
- **Public Newspaper**: [http://localhost:3000](http://localhost:3000)
- **Newsroom Control Suite (Admin)**: [http://localhost:3000/admin](http://localhost:3000/admin)
- **Backend API Docs (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Public RSS Feed**: [http://localhost:3000/api/v1/rss.xml](http://localhost:3000/api/v1/rss.xml)
- **Google News Sitemap**: [http://localhost:3000/api/v1/news-sitemap.xml](http://localhost:3000/api/v1/news-sitemap.xml)

### 4. Default Admin Credentials
- **Email**: `admin@marsnews.in`
- **Password**: `MarsNewsSuperAdmin2026!`

---

## 🐳 Production Deployment (Docker Compose)

```bash
cd infrastructure
docker-compose up --build -d
```
Services started:
- `mars_postgres` (pgvector/pgvector:pg16)
- `mars_redis` (redis:7.2-alpine)
- `mars_meilisearch` (getmeili/meilisearch:v1.8)
- `mars_backend` (FastAPI REST API)
- `mars_celery_worker` (Background Ingestion & AI task runner)
- `mars_celery_beat` (Scheduled collection scheduler)
- `mars_frontend` (Next.js 14 App)
- `mars_nginx` (Reverse Proxy on Port 80)

---

## 🧪 Automated Test Suite

Run the full pytest suite:
```powershell
cd backend
.venv\Scripts\python.exe -m pytest -v
```
All 11 tests covering normalization, Levenshtein similarity, entity extraction, sensitive risk detection, claim validation, auto-hold logic, public API endpoints, RSS, and sitemaps will execute.

---

## 📁 Project Structure

```
mars-news/
├── frontend/                 # Next.js 14 App Router, Tailwind CSS, Lucide icons
│   ├── app/
│   │   ├── (public)/         # Newspaper pages (/, /[category], /article/[slug], /search, /about...)
│   │   ├── admin/            # Dark-glass newsroom control suite
│   │   └── layout.tsx        # Root HTML shell
│   ├── components/           # Masthead, Navbar, BreakingTicker, ArticleCard, StructuredData
│   └── lib/                  # API client & formatting utilities
├── backend/                  # FastAPI, SQLAlchemy 2.0, Alembic, Celery, Pydantic
│   ├── app/
│   │   ├── api/v1/           # Public & Admin REST endpoints
│   │   ├── core/             # Database connection, Config, JWT Security
│   │   ├── models/           # 24 Database tables with UUID primary keys
│   │   ├── schemas/          # Pydantic v2 validation models
│   │   ├── services/         # Collector, Deduplication, Clustering, AI, Validation, Publishing
│   │   └── workers/          # Celery tasks & standalone Windows background scheduler
│   ├── alembic/              # Database migrations
│   ├── requirements.txt      # Pinned Python dependencies
│   └── Dockerfile
├── infrastructure/           # Docker Compose & Nginx configuration
├── scripts/                  # One-click Windows batch runners
├── docs/                     # Architecture & Editorial standards specification
└── README.md
```

---

## 📜 Intellectual Property & Fair Discovery Notice
MARS NEWS operates in strict compliance with intellectual property boundaries. Original publisher headlines and metadata are indexed solely for synthesis and discovery. Published reports link directly to canonical publisher sources with complete attribution.
