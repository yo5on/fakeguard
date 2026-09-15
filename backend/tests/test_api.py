import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import Account

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override database dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Create test database before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_analyze_account():
    """Test account analysis endpoint."""
    account_data = {
        "username": "test_user",
        "age_days": 100,
        "followers": 1000,
        "following": 800,
        "posts_per_day": 5.0,
        "profile_completeness": 75.0,
        "avg_likes": 50.0,
        "avg_comments": 5.0
    }
    
    response = client.post("/api/analyze", json=account_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "account" in data
    assert "analysis" in data
    assert "timestamp" in data
    assert "risk_score" in data["analysis"]
    assert "category" in data["analysis"]
    assert "features" in data["analysis"]

def test_analyze_invalid_data():
    """Test analysis with invalid data."""
    # Negative age
    response = client.post("/api/analyze", json={
        "username": "test",
        "age_days": -1,
        "followers": 100,
        "following": 100,
        "posts_per_day": 5.0,
        "profile_completeness": 75.0,
        "avg_likes": 10.0,
        "avg_comments": 1.0
    })
    assert response.status_code == 422
    
    # Profile completeness > 100
    response = client.post("/api/analyze", json={
        "username": "test",
        "age_days": 100,
        "followers": 100,
        "following": 100,
        "posts_per_day": 5.0,
        "profile_completeness": 150.0,
        "avg_likes": 10.0,
        "avg_comments": 1.0
    })
    assert response.status_code == 422

def test_create_account():
    """Test account creation."""
    account_data = {
        "username": "new_user",
        "age_days": 100,
        "followers": 500,
        "following": 400,
        "posts_per_day": 3.0,
        "profile_completeness": 80.0,
        "avg_likes": 25.0,
        "avg_comments": 2.5
    }
    
    response = client.post("/api/accounts", json=account_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["username"] == "new_user"
    assert "id" in data

def test_get_accounts():
    """Test getting accounts with pagination."""
    # Create test accounts
    for i in range(5):
        client.post("/api/accounts", json={
            "username": f"user_{i}",
            "age_days": 100 + i,
            "followers": 500,
            "following": 400,
            "posts_per_day": 3.0,
            "profile_completeness": 80.0,
            "avg_likes": 25.0,
            "avg_comments": 2.5
        })
    
    response = client.get("/api/accounts?skip=0&limit=3")
    assert response.status_code == 200
    
    data = response.json()
    assert "accounts" in data
    assert "total" in data
    assert len(data["accounts"]) == 3
    assert data["total"] == 5

def test_get_account_by_id():
    """Test getting a specific account."""
    # Create account
    create_response = client.post("/api/accounts", json={
        "username": "specific_user",
        "age_days": 100,
        "followers": 500,
        "following": 400,
        "posts_per_day": 3.0,
        "profile_completeness": 80.0,
        "avg_likes": 25.0,
        "avg_comments": 2.5
    })
    account_id = create_response.json()["id"]
    
    response = client.get(f"/api/accounts/{account_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["username"] == "specific_user"

def test_analyze_existing_account():
    """Test analyzing an existing account."""
    # Create account
    create_response = client.post("/api/accounts", json={
        "username": "analyze_me",
        "age_days": 50,
        "followers": 200,
        "following": 1000,
        "posts_per_day": 25.0,
        "profile_completeness": 40.0,
        "avg_likes": 5.0,
        "avg_comments": 0.5
    })
    account_id = create_response.json()["id"]
    
    response = client.post(f"/api/accounts/{account_id}/analyze")
    assert response.status_code == 200
    
    data = response.json()
    assert "analysis" in data
    assert data["analysis"]["risk_score"] > 0

def test_dashboard_summary():
    """Test dashboard summary endpoint."""
    # Create and analyze some accounts
    for i in range(3):
        create_response = client.post("/api/accounts", json={
            "username": f"dashboard_user_{i}",
            "age_days": 100 * (i + 1),
            "followers": 500,
            "following": 400,
            "posts_per_day": 3.0,
            "profile_completeness": 80.0,
            "avg_likes": 25.0,
            "avg_comments": 2.5
        })
        account_id = create_response.json()["id"]
        client.post(f"/api/accounts/{account_id}/analyze")
    
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_accounts" in data
    assert "low_risk" in data
    assert "average_risk_score" in data

def test_scoring_config():
    """Test scoring configuration endpoint."""
    response = client.get("/api/config/scoring")
    assert response.status_code == 200
    
    data = response.json()
    assert "features" in data
    assert "categories" in data
    assert "reason_codes" in data
    assert "disclaimer" in data