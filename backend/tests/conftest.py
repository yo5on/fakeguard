import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.database import Base, get_db, make_engine, normalize_database_url
from app.main import app
from app.rate_limit import limiter
from app.security import create_token, hash_password

# By default: in-memory SQLite shared across connections; nothing touches disk.
# Set FAKEGUARD_TEST_DATABASE_URL to run the suite against another server
# (e.g. PostgreSQL). Tables are dropped after every test, so only databases
# whose name starts with "fakeguard_test" are accepted.
TEST_DATABASE_URL = os.getenv("FAKEGUARD_TEST_DATABASE_URL")
if TEST_DATABASE_URL:
    _db_name = make_url(normalize_database_url(TEST_DATABASE_URL)).database or ""
    if not _db_name.startswith("fakeguard_test"):
        raise RuntimeError("FAKEGUARD_TEST_DATABASE_URL must name a database starting with 'fakeguard_test'")
    engine = make_engine(TEST_DATABASE_URL)
else:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

TEST_USERNAME = "reviewer"
TEST_PASSWORD = "correct horse battery staple"
TEST_SECRET = "test-secret-key-that-is-long-enough-0123456789"
# Hashed once per session: scrypt is deliberately slow.
TEST_PASSWORD_HASH = hash_password(TEST_PASSWORD)


def make_settings(**overrides) -> Settings:
    """Settings with authentication configured and rate limiting off."""
    values = dict(
        auth_username=TEST_USERNAME,
        auth_password_hash=TEST_PASSWORD_HASH,
        auth_secret_key=TEST_SECRET,
        rate_limit_enabled=False,
    )
    values.update(overrides)
    return Settings(**values)


def auth_headers(subject: str = TEST_USERNAME, secret: str = TEST_SECRET, ttl: int = 3600) -> dict:
    token, _ = create_token(subject, secret, ttl)
    return {"Authorization": f"Bearer {token}"}


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


@pytest.fixture(autouse=True)
def reset_state():
    limiter.reset()
    app.dependency_overrides[get_db] = override_get_db
    default_settings = make_settings()
    app.dependency_overrides[get_settings] = lambda: default_settings
    yield
    app.dependency_overrides.clear()
    limiter.reset()


@pytest.fixture
def use_settings():
    """Replace the active settings for the current test: use_settings(rate_limit_enabled=True)."""
    def _use(**overrides):
        settings = make_settings(**overrides)
        app.dependency_overrides[get_settings] = lambda: settings
        return settings
    return _use


@pytest.fixture
def anon_client():
    """Client without credentials."""
    return TestClient(app)


@pytest.fixture
def client():
    """Client authenticated with a valid bearer token."""
    return TestClient(app, headers=auth_headers())


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
