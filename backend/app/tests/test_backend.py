import pytest
from datetime import datetime, timezone
from app.models.sources import NewsSource, SourcePermission
from app.models.items import SourceItem
from app.models.clusters import StoryCluster, ClusterItem
from app.models.articles import Article
from app.services.collector import normalize_url, compute_content_hash
from app.services.clustering import (
    jaccard_similarity, levenshtein_ratio, extract_key_entities, compute_story_similarity, cluster_pending_items
)
from app.services.ai_editorial import analyze_risk_factors, synthesize_fallback
from app.services.validation import validate_and_assess_risk
from app.schemas.ai import AIEditorialOutput, ExtractedClaim

def test_url_normalization_and_idempotency():
    raw_url = "https://timesofindia.indiatimes.com/india/story-123.cms?utm_source=twitter&utm_medium=social&ref=feed"
    clean = normalize_url(raw_url)
    assert "utm_source" not in clean
    assert "utm_medium" not in clean
    assert clean == "https://timesofindia.indiatimes.com/india/story-123.cms"

    hash1 = compute_content_hash("source-1", clean, "ISRO launches climate satellite")
    hash2 = compute_content_hash("source-1", clean, "ISRO launches climate satellite")
    hash3 = compute_content_hash("source-1", clean, "Different headline")

    assert hash1 == hash2
    assert hash1 != hash3

def test_string_similarity_and_levenshtein():
    s1 = "ISRO successfully launches navigation satellite"
    s2 = "ISRO successfully launches new navigation satellite"
    ratio = levenshtein_ratio(s1, s2)
    assert ratio > 0.85

    tokens_a = {"isro", "launches", "satellite"}
    tokens_b = {"isro", "launches", "satellite", "orbit"}
    jacc = jaccard_similarity(tokens_a, tokens_b)
    assert jacc == 0.75

def test_entity_extraction():
    sample = "ISRO and DRDO announce joint test from Bhubaneswar, Odisha with PM Narendra Modi."
    entities = extract_key_entities(sample)
    assert "ISRO" in entities["organizations"]
    assert "DRDO" in entities["organizations"]
    assert "Bhubaneswar" in entities["locations"]
    assert "Odisha" in entities["locations"]

def test_risk_analysis_sensitive_topics():
    # Regular story
    risk_low, detected_low = analyze_risk_factors(
        "ISRO conducts successful static fire test",
        "The space agency conducted tests at the propulsion complex."
    )
    assert risk_low == "LOW"
    assert len(detected_low) == 0

    # Sensitive topic story
    risk_crit, detected_crit = analyze_risk_factors(
        "Three dead in communal clash following election results",
        "Police reported casualties and imposed restrictions."
    )
    assert risk_crit == "CRITICAL"
    assert any("Death" in d for d in detected_crit)
    assert any("Communal" in d for d in detected_crit)

def test_fact_validation_auto_hold():
    editorial_data = AIEditorialOutput(
        original_headline="Election Commission issues notification on bribery scam allegations",
        original_summary="New notifications issued regarding financial inquiries.",
        article_body="Detailed reporting on allegations.",
        category="Politics",
        tags=["Politics", "Elections"],
        seo_title="EC Issues Notice",
        seo_description="EC notification details",
        claims=[
            ExtractedClaim(
                claim_text="Commission issued notification on Tuesday",
                claim_type="OFFICIAL_STATEMENT",
                supporting_source_publisher="The Hindu",
                supporting_quote_or_context="Official notice published Tuesday",
                confidence=0.9
            )
        ],
        divergent_points=[],
        detected_risk_topics=["Elections and political allegations", "Financial allegations"],
        suggested_risk_level="HIGH",
        editorial_rationale="Tested"
    )

    sources = [{"publisher_name": "The Hindu", "source_url": "https://thehindu.com/test"}]
    result = validate_and_assess_risk(editorial_data, sources, strict_mode=True)

    # Must NOT auto-publish high-risk stories
    assert result["can_auto_publish"] is False
    assert result["triggers_auto_hold"] is True
    assert "Elections And Political Allegations" in result["hold_reasons"]
