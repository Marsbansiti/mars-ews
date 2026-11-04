import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.taxonomy import Category
from app.models.audit import AuditLog

router = APIRouter(prefix="/admin/categories", tags=["Admin Categories"])

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    display_order: int = 10

@router.get("")
def list_admin_categories(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cats = db.query(Category).order_by(Category.display_order.asc()).all()
    return [
        {
            "id": str(c.id),
            "name": c.name,
            "slug": c.slug,
            "description": c.description,
            "display_order": c.display_order,
            "articles_count": len(c.articles)
        }
        for c in cats
    ]

@router.post("")
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    slug = re.sub(r"[^\w-]", "", payload.name.lower().replace(" ", "-"))
    existing = db.query(Category).filter(Category.slug == slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    cat = Category(
        name=payload.name,
        slug=slug,
        description=payload.description,
        display_order=payload.display_order,
        is_active=True
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return {"message": "Category created", "id": str(cat.id), "slug": cat.slug}
