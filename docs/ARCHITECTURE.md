# MARS NEWS — Complete System Architecture & Pipeline Specification

## 1. System Philosophy
MARS NEWS is designed as an autonomous, multi-source digital newsroom intelligence engine. It avoids simple RSS scraping or verbatim republication; instead, it enforces copyright and publisher boundaries, matches related stories into clusters, extracts verifiable factual assertions, validates those claims across consensus reports, and produces independently authored journalistic summaries with full attribution and an explicit claim-evidence trail.

## 2. Ingestion & Source Management
- **Directory**: Prepopulated with top 10 Indian national dailies (*The Hindu*, *The Times of India*, *Hindustan Times*, *The Indian Express*, *The Telegraph*, *Deccan Herald*, *The New Indian Express*, *The Tribune*, *Deccan Chronicle*, *The Statesman*), official government releases (*PIB*, *DD News*), and regional outlets (*Odisha TV*, *Sambad English*).
- **Discovery**: HTML `<link rel="alternate" type="application/rss+xml">` parser automatically discovers official syndication feeds from publisher homepages.
- **Granular Permissions Gate**: `can_collect_headlines`, `can_collect_descriptions`, `can_create_original_summaries`, `can_access_full_text`, `can_reuse_images`, `can_display_attribution`.
- **Idempotency**: Prevents repeated ingestion using normalized canonical URLs and SHA-256 content hashes.

## 3. Deduplication & Clustering Engine
Groups related reports through a weighted composite similarity score:
1. **Headline Token Jaccard Similarity** (40% weight)
2. **Levenshtein Distance Ratio** (30% weight)
3. **Named Entity Set Overlap** (30% weight) — extracts People, Organizations (*ISRO*, *RBI*, *DRDO*, *SEBI*, etc.), Locations (*Bhubaneswar*, *New Delhi*, *Mumbai*, etc.).
4. **Time Proximity Decay** — penalizes stories published more than 36–48 hours apart.

## 4. AI Editorial & Zero-Hallucination Guardrails
- Integrates OpenAI API (`gpt-4o`) with Pydantic JSON validation schema (`AIEditorialOutput`).
- Deterministic journalistic synthesis fallback when offline or no API key is set.
- Strictly prohibited from inventing quotes, financial figures, dates, or official statements.
- Preserves differing reporting angles in `divergent_points`.

## 5. Fact Validation & Automatic Editorial Holds
- Maps every factual assertion to supporting publisher excerpts.
- Automatic Hold Triggers: Elections and political allegations, communal conflicts, crime allegations, unverified medical claims, financial allegations, death reports, national security incidents.
- Stories categorized as High or Critical risk are automatically placed on `EDITORIAL_HOLD` until newsroom editors review and manually release them.

## 6. Public Delivery & SEO
- Next.js 14 App Router, Tailwind CSS, high-impact typography.
- JSON-LD Structured Data: `NewsArticle`, `Organization`, `BreadcrumbList`.
- Automatic XML Sitemap (`/api/v1/sitemap.xml`), Google News Sitemap (`/api/v1/news-sitemap.xml`), and RSS 2.0 (`/api/v1/rss.xml`).
