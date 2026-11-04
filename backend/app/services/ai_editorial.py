import json
import time
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.clusters import StoryCluster, ClusterItem
from app.models.items import SourceItem
from app.models.ai import AIJob
from app.schemas.ai import AIEditorialOutput, ExtractedClaim, DivergentPerspective
from app.services.classifier import classify_news

AUTO_HOLD_KEYWORDS = {
    "election": "Elections and political allegations",
    "bribe": "Corruption and financial allegations",
    "scam": "Financial allegations",
    "kill": "Death reports and violence",
    "murder": "Crime allegations",
    "dead": "Death reports",
    "lynch": "Communal and violence incidents",
    "communal": "Communal and religious conflicts",
    "riot": "Communal and public order incidents",
    "terror": "National security incidents",
    "suicide": "Sensitive death reports",
    "cancer cure": "Unverified medical/health claims",
    "covid cure": "Medical and public health claims"
}

def analyze_risk_factors(title: str, text: str) -> Tuple[str, List[str]]:
    combined = (title + " " + text).lower()
    detected = []
    for kw, topic in AUTO_HOLD_KEYWORDS.items():
        if re.search(r"\b" + re.escape(kw) + r"\b", combined):
            detected.append(topic)

    detected = list(set(detected))
    if any(d in ["National security incidents", "Death reports", "Communal and religious conflicts"] for d in detected):
        risk_level = "CRITICAL"
    elif detected:
        risk_level = "HIGH"
    elif len(text.split()) < 5:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return risk_level, detected

def synthesize_fallback(cluster: StoryCluster, items: List[SourceItem]) -> AIEditorialOutput:
    """Deterministic journalistic synthesis fallback when OpenAI API key is not configured."""
    primary_item = items[0]
    headline = primary_item.original_headline
    desc = primary_item.authorized_description or "Official announcements and detailed reports confirm the development."

    cat_slug, is_reg, reg_state = classify_news(
        headline,
        desc,
        source_type=primary_item.source.source_type if primary_item.source else None,
        publisher_name=primary_item.publisher
    )
    category = cat_slug.capitalize()

    # Build coherent article body
    body_paras = [
        f"**NEW DELHI / REGIONAL BUREAU** — {headline}.",
        f"{desc}"
    ]

    claims = []
    for item in items:
        claims.append(ExtractedClaim(
            claim_text=item.original_headline,
            claim_type="OFFICIAL_STATEMENT" if "pib" in item.publisher.lower() else "FACT",
            supporting_source_publisher=item.publisher,
            supporting_quote_or_context=item.authorized_description[:120] if item.authorized_description else item.original_headline,
            confidence=0.95
        ))

    risk_level, detected_topics = analyze_risk_factors(headline, desc)

    clean_headline = re.sub(r"^Report:\s*", "", headline, flags=re.IGNORECASE).strip()
    clean_summary = desc[:280] if desc and len(desc.strip()) > 15 else clean_headline

    return AIEditorialOutput(
        original_headline=clean_headline,
        original_summary=clean_summary,
        article_body="\n\n".join(body_paras),
        category=category,
        tags=["India", category] + ([ "Odisha" ] if is_odisha else []),
        is_regional=is_odisha,
        regional_state="Odisha" if is_odisha else None,
        readability_score=75.0,
        reading_time_minutes=2,
        seo_title=f"{headline[:55]} | Mars News",
        seo_description=f"Detailed briefing on {headline.rstrip('.')}. Verified Indian news coverage on Mars News.",
        claims=claims,
        divergent_points=[],
        detected_risk_topics=detected_topics,
        suggested_risk_level=risk_level,
        editorial_rationale="Compiled strictly from authorized publisher headlines and metadata without speculative additions."
    )

def generate_editorial_article(cluster_id: str, db: Session) -> AIEditorialOutput:
    """Processes a StoryCluster through the AI Editorial Engine with OpenAI structured JSON output."""
    cluster = db.query(StoryCluster).filter(StoryCluster.id == cluster_id).first()
    if not cluster:
        raise ValueError(f"Cluster {cluster_id} not found")

    cluster_links = db.query(ClusterItem).filter(ClusterItem.cluster_id == cluster_id).all()
    item_ids = [cl.source_item_id for cl in cluster_links]
    items = db.query(SourceItem).filter(SourceItem.id.in_(item_ids)).all()

    if not items:
        raise ValueError(f"No source items associated with cluster {cluster_id}")

    start_time = time.time()
    ai_job = AIJob(
        job_type="EDITORIAL_GENERATION",
        model_name=settings.OPENAI_MODEL,
        target_id=str(cluster.id),
        status="RUNNING"
    )
    db.add(ai_job)
    db.flush()

    # If OpenAI API Key is present, call OpenAI API
    if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("your-"):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            source_summaries = []
            for it in items:
                source_summaries.append(
                    f"Publisher: {it.publisher}\nOriginal Headline: {it.original_headline}\nTimestamp: {it.publication_timestamp}\nDescription: {it.authorized_description or 'N/A'}\n"
                )
            context_block = "\n---\n".join(source_summaries)

            system_prompt = (
                "You are the Chief AI Editorial Writer for MARS NEWS, a premier Indian digital newspaper. "
                "Your objective is to generate an authoritative, independently phrased, balanced news article "
                "based SOLELY on the authorized facts from the provided source reports.\n"
                "STRICT RULES:\n"
                "1. NEVER copy complete articles or verbatim phrasing.\n"
                "2. NEVER invent quotes, numbers, dates, locations, or official statements.\n"
                "3. If reports conflict, explicitly describe the divergence.\n"
                "4. Extract verifiable claims and map each claim to its reporting publisher.\n"
                "5. Classify editorial risk level (LOW, MEDIUM, HIGH, CRITICAL). Identify if topic involves elections, crime allegations, communal conflict, financial scam, or death reports.\n"
                "Output MUST be a valid JSON object matching the requested schema."
            )

            prompt_text = (
                f"Cluster Topic: {cluster.cluster_title}\n"
                f"Coverage Category: {cluster.category}\n\n"
                f"Source Reports:\n{context_block}\n\n"
                f"Please synthesize and return the JSON according to the AIEditorialOutput schema."
            )

            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt_text}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )

            elapsed_ms = int((time.time() - start_time) * 1000)
            raw_output = response.choices[0].message.content
            parsed_data = json.loads(raw_output)
            editorial_output = AIEditorialOutput(**parsed_data)

            # Record AI Job metrics
            ai_job.status = "SUCCESS"
            ai_job.execution_time_ms = elapsed_ms
            ai_job.prompt_tokens = response.usage.prompt_tokens if response.usage else 0
            ai_job.completion_tokens = response.usage.completion_tokens if response.usage else 0
            ai_job.total_tokens = response.usage.total_tokens if response.usage else 0
            ai_job.estimated_cost_usd = (ai_job.prompt_tokens * 0.000005) + (ai_job.completion_tokens * 0.000015)
            ai_job.response_payload = editorial_output.model_dump()
            db.commit()

            return editorial_output

        except Exception as e:
            # Fallback on API failure
            elapsed_ms = int((time.time() - start_time) * 1000)
            ai_job.status = "FAILED"
            ai_job.error_message = str(e)
            ai_job.execution_time_ms = elapsed_ms
            db.commit()
            return synthesize_fallback(cluster, items)

    # Deterministic fallback when no API key configured
    editorial_output = synthesize_fallback(cluster, items)
    elapsed_ms = int((time.time() - start_time) * 1000)
    ai_job.status = "SUCCESS"
    ai_job.execution_time_ms = elapsed_ms
    ai_job.response_payload = editorial_output.model_dump()
    db.commit()

    return editorial_output
