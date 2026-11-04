from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.media import MediaAsset
from app.models.audit import AuditLog

router = APIRouter(prefix="/admin/media", tags=["Admin Media Library"])

class MediaAssetCreate(BaseModel):
    filename: str
    image_url: str
    original_source: str
    license: str = "CC-BY-4.0"
    attribution: str
    usage_permission: bool = True
    alt_text: str
    copyright_information: Optional[str] = None
    media_type: str = "image/jpeg"

@router.get("")
def list_media(limit: int = 50, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    assets = db.query(MediaAsset).order_by(MediaAsset.created_at.desc()).limit(limit).all()
    return [
        {
            "id": str(m.id),
            "filename": m.filename,
            "image_url": m.image_url,
            "original_source": m.original_source,
            "license": m.license,
            "attribution": m.attribution,
            "usage_permission": m.usage_permission,
            "alt_text": m.alt_text,
            "copyright_information": m.copyright_information,
            "created_at": m.created_at.isoformat()
        }
        for m in assets
    ]

@router.post("")
def add_media_asset(payload: MediaAssetCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    asset = MediaAsset(
        filename=payload.filename,
        image_url=payload.image_url,
        original_source=payload.original_source,
        license=payload.license,
        attribution=payload.attribution,
        usage_permission=payload.usage_permission,
        alt_text=payload.alt_text,
        copyright_information=payload.copyright_information,
        media_type=payload.media_type
    )
    db.add(asset)

    audit = AuditLog(
        user_id=current_user.id,
        action_type="MEDIA_ADDED",
        target_type="Media",
        target_id=str(asset.id),
        summary=f"Added verified media asset: {asset.filename} ({asset.license})",
        performed_by=current_user.email
    )
    db.add(audit)
    db.commit()
    db.refresh(asset)
    return {"message": "Media asset registered successfully", "id": str(asset.id)}
