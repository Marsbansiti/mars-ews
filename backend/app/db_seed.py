import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.core.config import settings
from app.models import (
    User, Role, Permission, NewsSource, SourcePermission,
    Category, Tag, MediaAsset, AuditLog
)

from app.seed_all_sources import ALL_INDIAN_SOURCES

PREPOPULATED_SOURCES = ALL_INDIAN_SOURCES


CATEGORIES = [
    {"name": "India", "slug": "india", "description": "National news, governance, public policy, and key developments across India.", "display_order": 1},
    {"name": "Politics", "slug": "politics", "description": "Parliamentary affairs, electoral analysis, state politics, and policy debates.", "display_order": 2},
    {"name": "Business", "slug": "business", "description": "Indian economy, markets, startups, corporate developments, and finance.", "display_order": 3},
    {"name": "Technology", "slug": "technology", "description": "AI, space research, cybersecurity, digital infrastructure, and consumer tech.", "display_order": 4},
    {"name": "Sports", "slug": "sports", "description": "Cricket, badminton, hockey, Olympics, athletics, and regional sporting events.", "display_order": 5},
    {"name": "Entertainment", "slug": "entertainment", "description": "Cinema, arts, literature, OTT streaming, and cultural festivals.", "display_order": 6},
    {"name": "Education", "slug": "education", "description": "Universities, competitive exams, EdTech, skill development, and policy.", "display_order": 7},
    {"name": "Science", "slug": "science", "description": "ISRO space missions, biotechnology, climate research, and innovations.", "display_order": 8},
    {"name": "Lifestyle", "slug": "lifestyle", "description": "Health, wellness, travel, heritage, cuisine, and environment.", "display_order": 9},
    {"name": "Regional", "slug": "regional", "description": "In-depth grassroots reporting and regional perspectives across Indian states.", "display_order": 10},
    {"name": "Odisha", "slug": "odisha", "description": "Dedicated regional coverage of Odisha governance, heritage, industry, and coast.", "display_order": 11},
]

MEDIA_ASSETS = [
    {
        "filename": "science-isro.svg",
        "image_url": "/images/science-isro.svg",
        "original_source": "ISRO / Space Research Documentation Archive",
        "license": "CC-BY-4.0",
        "attribution": "Space Exploration Archive (CC-BY-4.0)",
        "usage_permission": True,
        "alt_text": "Space rocket launching into the night sky representing technological progress",
        "copyright_information": "Approved for editorial use with attribution",
        "media_type": "image/svg+xml"
    },
    {
        "filename": "business-economy.svg",
        "image_url": "/images/business-economy.svg",
        "original_source": "Reserve Bank of India / Financial Documentation",
        "license": "CC-BY-4.0",
        "attribution": "Financial Market Visuals (Editorial)",
        "usage_permission": True,
        "alt_text": "Financial market indices and economic growth analytics visualization",
        "copyright_information": "Editorial use permitted with citation",
        "media_type": "image/svg+xml"
    },
    {
        "filename": "odisha-tech.svg",
        "image_url": "/images/odisha-tech.svg",
        "original_source": "Odisha High-Tech Infrastructure Bureau",
        "license": "CC-BY-4.0",
        "attribution": "Heritage & Tech Documentation (CC-BY-4.0)",
        "usage_permission": True,
        "alt_text": "Semiconductor microchip wafer and Bhubaneswar tech park",
        "copyright_information": "Licensed under Creative Commons Attribution 4.0",
        "media_type": "image/svg+xml"
    },
    {
        "filename": "governance-parliament.svg",
        "image_url": "/images/governance-parliament.svg",
        "original_source": "Official Public Domain / Governance Repository",
        "license": "PUBLIC_DOMAIN",
        "attribution": "Government of India / Public Domain Archive",
        "usage_permission": True,
        "alt_text": "Architectural view representing democratic governance and parliament",
        "copyright_information": "Public Domain - Free for editorial citation",
        "media_type": "image/svg+xml"
    }
]

def seed_database():
    db = SessionLocal()
    try:
        print("[SEED] Starting database initialization...")

        # 1. Roles
        roles_dict = {}
        for role_name, desc in [
            ("Admin", "Full newsroom administrative privileges and system controls"),
            ("Editor", "Editorial review, publishing approval, and risk management"),
            ("Journalist", "Content drafting, review, and verification notes"),
            ("Reviewer", "Read-only access to audit logs and fact validation"),
        ]:
            role = db.query(Role).filter(Role.name == role_name).first()
            if not role:
                role = Role(name=role_name, description=desc)
                db.add(role)
                db.flush()
                print(f"  + Added Role: {role_name}")
            roles_dict[role_name] = role

        # 2. Permissions
        permissions = [
            ("manage_sources", "Manage News Sources", "Can add, edit, toggle, and configure sources"),
            ("collect_news", "Trigger News Collector", "Can manually trigger ingestion jobs"),
            ("edit_articles", "Edit Articles", "Can edit, summarize, and revise articles"),
            ("publish_articles", "Publish Articles", "Can publish articles or lift editorial holds"),
            ("hold_articles", "Editorial Hold", "Can place stories on editorial hold"),
            ("manage_users", "User Management", "Can create and assign roles to users"),
            ("view_audit_logs", "View Audit Logs", "Can view immutable system logs"),
            ("manage_settings", "System Settings", "Can toggle emergency pause and update intervals")
        ]
        for code, name, desc in permissions:
            perm = db.query(Permission).filter(Permission.code == code).first()
            if not perm:
                perm = Permission(code=code, name=name, description=desc)
                db.add(perm)
                db.flush()
                # attach to Admin role
                if roles_dict.get("Admin") and perm not in roles_dict["Admin"].permissions:
                    roles_dict["Admin"].permissions.append(perm)

        # 3. SuperAdmin User
        admin_user = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if not admin_user:
            admin_user = User(
                email=settings.ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                full_name="Mars News Chief Editor",
                role_id=roles_dict["Admin"].id,
                is_active=True,
                is_verified=True
            )
            db.add(admin_user)
            db.flush()
            print(f"  + Added SuperAdmin user: {settings.ADMIN_EMAIL}")

        # 4. Categories
        for cat_data in CATEGORIES:
            cat = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
            if not cat:
                cat = Category(
                    name=cat_data["name"],
                    slug=cat_data["slug"],
                    description=cat_data["description"],
                    display_order=cat_data["display_order"],
                    is_active=True
                )
                db.add(cat)
                print(f"  + Added Category: {cat_data['name']}")

        # 5. News Sources
        for src_data in PREPOPULATED_SOURCES:
            src = db.query(NewsSource).filter(NewsSource.slug == src_data["slug"]).first()
            if not src:
                src = NewsSource(
                    publisher_name=src_data["publisher_name"],
                    slug=src_data["slug"],
                    official_website_url=src_data["official_website_url"],
                    language=src_data["language"],
                    country=src_data["country"],
                    coverage_categories=src_data["coverage_categories"],
                    source_type=src_data["source_type"],
                    rss_feed_url=src_data["rss_feed_url"],
                    permission_status=src_data["permission_status"],
                    content_usage_policy=src_data["content_usage_policy"],
                    collection_frequency=src_data["collection_frequency"],
                    enabled=src_data["enabled"],
                    credibility_score=src_data["credibility_score"]
                )
                db.add(src)
                db.flush()

                # Granular permissions for the source
                is_gov = src_data["source_type"] == "government"
                src_perm = SourcePermission(
                    source_id=src.id,
                    can_collect_headlines=True,
                    can_collect_descriptions=True,
                    can_create_original_summaries=True,
                    can_access_full_text=is_gov,
                    can_reuse_images=is_gov,
                    can_commercially_redistribute=False,
                    can_display_attribution=True,
                    notes="Configured per Section 4 publisher policy and copyright boundaries."
                )
                db.add(src_perm)
                print(f"  + Added Source: {src_data['publisher_name']} [{src_data['permission_status']}]")

        # 6. Media Assets
        for media_data in MEDIA_ASSETS:
            asset = db.query(MediaAsset).filter(MediaAsset.filename == media_data["filename"]).first()
            if not asset:
                asset = MediaAsset(
                    filename=media_data["filename"],
                    image_url=media_data["image_url"],
                    original_source=media_data["original_source"],
                    license=media_data["license"],
                    attribution=media_data["attribution"],
                    usage_permission=media_data["usage_permission"],
                    alt_text=media_data["alt_text"],
                    copyright_information=media_data["copyright_information"],
                    media_type=media_data["media_type"]
                )
                db.add(asset)
                print(f"  + Added Media Asset: {media_data['filename']}")

        # 7. Initial Audit Log
        audit = AuditLog(
            action_type="SYSTEM_INITIALIZED",
            target_type="System",
            summary="MARS NEWS system database seeded with prepopulated Indian sources, roles, and categories",
            details={"sources_seeded": len(PREPOPULATED_SOURCES), "categories_seeded": len(CATEGORIES)},
            performed_by="SYSTEM_SEEDER"
        )
        db.add(audit)

        db.commit()
        print("[SEED] Completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"[SEED] Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
