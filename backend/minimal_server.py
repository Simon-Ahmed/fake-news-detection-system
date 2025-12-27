#!/usr/bin/env python3
"""
Minimal FastAPI server for testing frontend-backend connection
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn
import uuid

# Create FastAPI app
app = FastAPI(
    title="Fake News Detection API - Minimal",
    description="Minimal API for testing connection",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Fake News Detection API - Minimal Version",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "predict": "/api/predict",
            "health": "/api/health"
        }
    }

@app.get("/health")
async def simple_health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "fake-news-detection-api-minimal"
    }

@app.get("/api/health")
async def api_health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "ml_model_loaded": True,  # Fake for testing
        "database_connected": True,  # Fake for testing
        "redis_connected": False,
        "model_version": "test-v1.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/predict")
async def predict_text(request: dict):
    """Predict if a text is fake news - minimal implementation."""
    
    text = request.get("text", "")
    
    if not text:
        return {
            "error": True,
            "message": "No text provided"
        }
    
    # Simple rule-based prediction for testing
    text_lower = text.lower()
    if any(word in text_lower for word in ["shocking", "unbelievable", "click here", "you won't believe"]):
        prediction = "fake"
        confidence = 85.0
    elif any(word in text_lower for word in ["according to", "study", "research"]):
        prediction = "real"
        confidence = 78.0
    else:
        prediction = "inconclusive"
        confidence = 60.0
    
    return {
        "id": str(uuid.uuid4()),
        "prediction": prediction,
        "confidence": confidence,
        "explanation": f"This text appears to be {prediction} based on simple pattern analysis.",
        "factors": [
            {
                "name": "Pattern Analysis",
                "score": confidence,
                "impact": "negative" if prediction == "fake" else "positive",
                "description": f"Simple keyword-based analysis suggests {prediction} content"
            }
        ],
        "sources": ["https://www.snopes.com", "https://www.factcheck.org"],
        "timestamp": datetime.utcnow().isoformat(),
        "input_text": text[:200] + "..." if len(text) > 200 else text,
        "input_url": None,
        "model_version": "simple-test-v1.0",
        "processing_time": 0.1
    }

@app.get("/api/stats")
async def get_stats():
    """Get system statistics - minimal implementation."""
    return {
        "total_predictions": 42,
        "fake_predictions": 15,
        "real_predictions": 20,
        "inconclusive_predictions": 7,
        "avg_confidence": 75.5,
        "model_accuracy": 87.2,
        "model_version": "simple-test-v1.0",
        "uptime_hours": 1.0
    }

@app.get("/api/history")
async def get_history(limit: int = 50, offset: int = 0):
    """Get prediction history - minimal implementation."""
    return {
        "predictions": [],
        "total": 0,
        "page": 1,
        "per_page": limit
    }

if __name__ == "__main__":
    print("🚀 Starting Minimal Fake News Detection API...")
    print("📍 Server: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🔍 Health: http://localhost:8000/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )