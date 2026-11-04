from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.models.articles import Article, ArticleClaim, ClaimEvidence
from app.models.audit import AuditLog, Notification
from app.schemas.ai import AIEditorialOutput

SENSITIVE_TOPIC_CRITERIA = [
    "elections and political allegations",
    "communal and religious conflicts",
    "crime allegations",
    "medical and public health claims",
    "financial allegations",
    "death reports",
    "national security incidents",
    "unverified breaking news"
]

def validate_and_assess_risk(
    editorial_output: AIEditorialOutput,
    article_sources: List[Dict[str, Any]],
    strict_mode: bool = True
) -> Dict[str, Any]:
    """Validates claims against source evidence and determines publication eligibility."""
    claims_verified = 0
    claims_unverified = 0
    claims_conflicting = 0
    issues_found = []

    # 1. Claim Validation Check
    for claim in editorial_output.claims:
        # Check if source publisher matches one of the ingested article sources
        matched_source = next(
            (s for s in article_sources if s["publisher_name"].lower() in claim.supporting_source_publisher.lower() or claim.supporting_source_publisher.lower() in s["publisher_name"].lower()),
            None
        )

        if not matched_source:
            issues_found.append(f"Claim '{claim.claim_text[:60]}...' lacks verified publisher mapping.")
            claims_unverified += 1
        elif len(claim.supporting_quote_or_context.strip()) < 5:
            issues_found.append(f"Claim '{claim.claim_text[:60]}...' lacks supporting context/excerpt.")
            claims_unverified += 1
        else:
            claims_verified += 1

    # 2. Risk Topic Evaluation
    detected_risk_topics = [t.lower() for t in editorial_output.detected_risk_topics]
    triggers_auto_hold = False
    hold_reasons = []

    for sensitive_topic in SENSITIVE_TOPIC_CRITERIA:
        if any(sensitive_topic in t or t in sensitive_topic for t in detected_risk_topics):
            triggers_auto_hold = True
            hold_reasons.append(sensitive_topic.title())

    # 3. Conflict / Divergence Check
    if editorial_output.divergent_points:
        issues_found.append(f"Disagreement detected across reporting perspectives: {len(editorial_output.divergent_points)} divergent points.")
        if strict_mode and len(editorial_output.divergent_points) > 1:
            triggers_auto_hold = True
            hold_reasons.append("Conflicting source accounts")

    # 4. Final Risk Level Calculation
    if triggers_auto_hold or editorial_output.suggested_risk_level in ["HIGH", "CRITICAL"]:
        final_risk = "CRITICAL" if any("death" in h.lower() or "security" in h.lower() for h in hold_reasons) else "HIGH"
        can_auto_publish = False
    elif editorial_output.suggested_risk_level == "MEDIUM" or claims_unverified > 0:
        final_risk = "MEDIUM"
        can_auto_publish = not strict_mode if claims_unverified == 0 else False
    else:
        final_risk = "LOW"
        can_auto_publish = True

    return {
        "can_auto_publish": can_auto_publish,
        "final_risk_level": final_risk,
        "triggers_auto_hold": triggers_auto_hold,
        "hold_reasons": hold_reasons,
        "claims_total": len(editorial_output.claims),
        "claims_verified": claims_verified,
        "claims_unverified": claims_unverified,
        "validation_issues": issues_found,
        "confidence_score": 1.0 if not claims_unverified else round(claims_verified / (claims_verified + claims_unverified), 2)
    }

def process_article_validation(article_id: str, db: Session) -> Dict[str, Any]:
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        return {"error": "Article not found"}

    claims = db.query(ArticleClaim).filter(ArticleClaim.article_id == article_id).all()
    verified_count = sum(1 for c in claims if c.verification_status == "VERIFIED")
    unverified_count = sum(1 for c in claims if c.verification_status != "VERIFIED")

    # If article is held, check if editor can release
    is_held = article.status == "EDITORIAL_HOLD"

    return {
        "article_id": str(article.id),
        "headline": article.headline,
        "status": article.status,
        "risk_level": article.risk_level,
        "risk_reasons": article.risk_reasons,
        "total_claims": len(claims),
        "verified_claims": verified_count,
        "unverified_claims": unverified_count,
        "is_held": is_held
    }
