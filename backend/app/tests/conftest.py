import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import app
from app.core.security import get_password_hash, create_access_token
from app.models.users import User, Role
from app.models.sources import NewsSource, SourcePermission
from app.models.taxonomy import Category

TEST_DATABASE_URL = "sqlite:///./test_mars_news.db"

test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
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
    role = db_session.query(Role).filter(Role.name == "Admin").first()
    if not role:
        role = Role(name="Admin", description="Administrator")
        db_session.add(role)
        db_session.flush()

    user = db_session.query(User).filter(User.email == "testadmin@marsnews.in").first()
    if not user:
        user = User(
            email="testadmin@marsnews.in",
            hashed_password=get_password_hash("TestPass123!"),
            full_name="Test Admin",
            role_id=role.id,
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": "Admin"})
    return token
