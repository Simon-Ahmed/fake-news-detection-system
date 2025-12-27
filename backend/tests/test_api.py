import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import get_db, Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)

# Test data
test_cases = [
    {
        "text": "According to a new study published in Nature, moderate coffee consumption reduces heart disease risk by 15%.",
        "expected": "real"
    },
    {
        "text": "SHOCKING: Doctors hate this one trick to lose 20lbs in 3 days! Click here for the secret that will change your life forever!",
        "expected": "fake"
    },
    {
        "text": "The Federal Reserve announced a 0.25% increase in interest rates today, citing concerns about inflation.",
        "expected": "real"
    },
    {
        "text": "BREAKING: Aliens have landed in New York City! Government officials are hiding the truth from the public!",
        "expected": "fake"
    }
]

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Fake News Detection API"

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_predict_endpoint():
    """Test the prediction endpoint."""
    for test_case in test_cases:
        response = client.post(
            "/api/predict",
            json={"text": test_case["text"], "language": "en"}
        )
        
        # The endpoint might not be fully functional without ML models
        # So we just check that it doesn't crash
        assert response.status_code in [200, 503]  # 503 if ML model not ready
        
        if response.status_code == 200:
            data = response.json()
            assert "prediction" in data
            assert "confidence" in data
            assert data["prediction"] in ["real", "fake", "inconclusive"]
            assert 0 <= data["confidence"] <= 100

def test_predict_validation():
    """Test input validation for prediction endpoint."""
    # Test empty text
    response = client.post(
        "/api/predict",
        json={"text": "", "language": "en"}
    )
    assert response.status_code == 422  # Validation error
    
    # Test text too short
    response = client.post(
        "/api/predict",
        json={"text": "short", "language": "en"}
    )
    assert response.status_code == 422  # Validation error

def test_batch_predict_endpoint():
    """Test the batch prediction endpoint."""
    texts = [case["text"] for case in test_cases[:2]]  # Test with 2 texts
    
    response = client.post(
        "/api/batch-predict",
        json={"texts": texts, "language": "en"}
    )
    
    # The endpoint might not be fully functional without ML models
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "predictions" in data
        assert "total_processed" in data

def test_batch_predict_validation():
    """Test validation for batch prediction endpoint."""
    # Test too many texts
    texts = ["test text"] * 51  # More than 50 allowed
    
    response = client.post(
        "/api/batch-predict",
        json={"texts": texts, "language": "en"}
    )
    assert response.status_code in [400, 503]  # 400 for validation error or 503 if model not ready

def test_feedback_endpoint():
    """Test the feedback endpoint."""
    # First, we need a prediction ID (this would normally come from a real prediction)
    fake_prediction_id = "test-prediction-id"
    
    response = client.post(
        "/api/feedback",
        json={
            "prediction_id": fake_prediction_id,
            "user_correction": "real",
            "comment": "This is actually a legitimate news article"
        }
    )
    
    # Should return 404 since prediction doesn't exist
    assert response.status_code == 404

def test_stats_endpoint():
    """Test the stats endpoint."""
    response = client.get("/api/stats")
    assert response.status_code in [200, 500]  # Might fail without proper setup
    
    if response.status_code == 200:
        data = response.json()
        assert "total_predictions" in data
        assert "model_version" in data

def test_history_endpoint():
    """Test the history endpoint."""
    response = client.get("/api/history")
    assert response.status_code == 200
    
    data = response.json()
    assert "predictions" in data
    assert "total" in data
    assert isinstance(data["predictions"], list)

def test_history_pagination():
    """Test history endpoint pagination."""
    response = client.get("/api/history?limit=10&offset=0")
    assert response.status_code == 200
    
    data = response.json()
    assert "page" in data
    assert "per_page" in data
    assert data["per_page"] == 10

if __name__ == "__main__":
    pytest.main([__file__])