from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.articles import ArticleClaim, ClaimEvidence, Article
from app.models.audit import AuditLog

router = APIRouter(prefix="/admin/validation", tags=["Admin Fact Validation"])

@router.get("/claims")
def list_claims(
    status: Optional[str] = None,
    article_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    q = db.query(ArticleClaim)
    if status:
        q = q.filter(ArticleClaim.verification_status == status)
    if article_id:
        q = q.filter(ArticleClaim.article_id == article_id)

    claims = q.order_by(ArticleClaim.created_at.desc()).limit(limit).all()
    results = []
    for c in claims:
        ev_list = [
            {
                "source_name": ev.source_name,
                "source_url": ev.source_url,
                "supporting_excerpt": ev.supporting_excerpt,
                "is_direct_match": ev.is_direct_match
            }
            for ev in c.evidence
        ]
        results.append({
            "id": str(c.id),
            "article_id": str(c.article_id),
            "article_headline": c.article.headline if c.article else "Unknown",
            "claim_text": c.claim_text,
            "claim_type": c.claim_type,
            "verification_status": c.verification_status,
            "confidence_score": c.confidence_score,
            "verification_notes": c.verification_notes,
            "evidence": ev_list
        })
    return results

@router.patch("/claims/{id}")
def verify_claim(
    id: str,
    status: str,  # VERIFIED, REJECTED, CONTESTED
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    claim = db.query(ArticleClaim).filter(ArticleClaim.id == id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    claim.verification_status = status
    if notes:
        claim.verification_notes = notes

    audit = AuditLog(
        user_id=current_user.id,
        action_type="CLAIM_VERIFIED",
        target_type="Claim",
        target_id=id,
        summary=f"Claim status updated to {status} by {current_user.email}",
        performed_by=current_user.email
    )
    db.add(audit)
    db.commit()
    return {"message": f"Claim status updated to {status}"}

@router.get("/holds")
def list_editorial_holds(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    held_articles = db.query(Article).filter(Article.status == "EDITORIAL_HOLD").order_by(Article.created_at.desc()).all()
    return [
        {
            "id": str(a.id),
            "headline": a.headline,
            "summary": a.summary,
            "risk_level": a.risk_level,
            "risk_reasons": a.risk_reasons,
            "created_at": a.created_at.isoformat(),
            "sources_count": len(a.sources),
            "claims_count": len(a.claims)
        }
        for a in held_articles
    ]
