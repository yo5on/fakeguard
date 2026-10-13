import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# In-memory SQLite shared across connections; nothing is written to disk.
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_database():
    """Create a fresh schema before each test and drop it afterwards."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


VALID_ACCOUNT = {
    "username": "test_user",
    "age_days": 100,
    "followers": 500,
    "following": 400,
    "posts_per_day": 3.0,
    "profile_completeness": 80.0,
    "avg_likes": 25.0,
    "avg_comments": 2.5,
}


@pytest.fixture
def make_account(client):
    """Create an account through the API and return its JSON."""
    def _make(**overrides):
        response = client.post("/api/accounts", json={**VALID_ACCOUNT, **overrides})
        assert response.status_code == 201, response.text
        return response.json()
    return _make
