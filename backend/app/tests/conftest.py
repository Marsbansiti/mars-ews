import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base, get_db
from app.main import app
from app.core.security import get_password_hash, create_access_token
from app.models.users import User, Role
from app.models.sources import NewsSource, SourcePermission
from app.models.taxonomy import Category
from app.models.articles import Article

TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()

    # Seed Admin Role & User
    admin_role = Role(name="Admin", description="Administrator")
    session.add(admin_role)
    session.flush()

    user = User(
        email="testadmin@marsnews.in",
        hashed_password=get_password_hash("TestPass123!"),
        full_name="Test Admin",
        role_id=admin_role.id,
        is_active=True,
        is_verified=True
    )
    session.add(user)

    # Seed Sample Categories
    cat1 = Category(name="India", slug="india", description="National news", display_order=1, is_active=True)
    cat2 = Category(name="Technology", slug="technology", description="Tech & AI", display_order=2, is_active=True)
    session.add_all([cat1, cat2])
    session.flush()

    # Seed Sample Sources
    s1 = NewsSource(
        publisher_name="The Hindu",
        slug="the-hindu",
        official_website_url="https://www.thehindu.com",
        rss_feed_url="https://www.thehindu.com/news/national/feeder/default.rss",
        source_type="newspaper",
        credibility_score=9.5,
        enabled=True,
        permission_status="VERIFIED"
    )
    s2 = NewsSource(
        publisher_name="The Times of India",
        slug="the-times-of-india",
        official_website_url="https://timesofindia.indiatimes.com",
        rss_feed_url="https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
        source_type="newspaper",
        credibility_score=9.2,
        enabled=True,
        permission_status="VERIFIED"
    )
    session.add_all([s1, s2])
    session.flush()

    # Seed Sample Published Article for RSS and Sitemap
    art = Article(
        slug="isro-launches-satellite-test",
        headline="ISRO Successfully Launches New Earth Observation Satellite",
        summary="India's space agency ISRO has launched its latest satellite from Sriharikota.",
        content_body="ISRO marked another milestone on Thursday with the successful launch of its satellite.",
        status="PUBLISHED",
        published_at=datetime.now(timezone.utc),
        is_breaking=True,
        is_featured=True,
        category_id=cat1.id
    )
    session.add(art)

    session.commit()
    session.close()

    yield

    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def admin_token(db_session):
    user = db_session.query(User).filter(User.email == "testadmin@marsnews.in").first()
    token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": "Admin"})
    return token
