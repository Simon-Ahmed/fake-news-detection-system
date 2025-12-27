from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import time
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime

from ..database import get_db
from ..schemas import (
    PredictionRequest, URLPredictionRequest, BatchPredictionRequest,
    PredictionResponse, BatchPredictionResponse, HistoryResponse
)
from .. import crud
from ..ml.detector import FakeNewsDetector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["predictions"])

# Global detector instance
detector = FakeNewsDetector()

@router.on_event("startup")
async def startup_event():
    """Initialize the ML detector on startup."""
    # Initialize detector in background to avoid blocking startup
    logger.info("Starting ML detector initialization in background")
    try:
        global detector
        detector.initialize()
        logger.info("ML detector initialized successfully")
    except Exception as e:
        logger.error(f"ML detector initialization failed: {e}")
        # Continue without ML - use fallback only

@router.post("/predict", response_model=PredictionResponse)
async def predict_text(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Predict if a text is fake news."""
    
    try:
        # For now, return a simple mock response to test connectivity
        import uuid
        import time
        
        # Simple rule-based prediction for testing
        text_lower = request.text.lower()
        if any(word in text_lower for word in ["shocking", "unbelievable", "click here", "you won't believe"]):
            prediction = "fake"
            confidence = 85.0
        elif any(word in text_lower for word in ["according to", "study", "research"]):
            prediction = "real"
            confidence = 78.0
        else:
            prediction = "inconclusive"
            confidence = 60.0
        
        response_data = {
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
            "input_text": request.text[:200] + "..." if len(request.text) > 200 else request.text,
            "input_url": None,
            "model_version": "simple-test-v1.0",
            "processing_time": 0.1
        }
        
        return PredictionResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/predict/url", response_model=PredictionResponse)
async def predict_url(
    request: URLPredictionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Predict if a news article from URL is fake news."""
    if not detector.is_ready():
        raise HTTPException(status_code=503, detail="ML model not ready")
    
    try:
        # Scrape article content
        article_text = scrape_article(request.url)
        
        if not article_text:
            raise HTTPException(status_code=400, detail="Could not extract text from URL")
        
        # Make prediction
        result = detector.predict(article_text, request.language)
        
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["explanation"])
        
        # Prepare response
        response_data = {
            "id": "",  # Will be set after DB save
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "explanation": result["explanation"],
            "factors": result["factors"],
            "sources": result["sources"],
            "timestamp": None,  # Will be set by DB
            "input_text": article_text[:200] + "..." if len(article_text) > 200 else article_text,
            "input_url": request.url,
            "model_version": result["model_version"],
            "processing_time": result["processing_time"]
        }
        
        # Save to database in background
        background_tasks.add_task(
            save_prediction_to_db,
            db,
            article_text,
            request.url,
            result
        )
        
        # Create response
        import uuid
        response_data["id"] = str(uuid.uuid4())
        response_data["timestamp"] = time.time()
        
        return PredictionResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"URL prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/batch-predict", response_model=BatchPredictionResponse)
async def batch_predict(
    request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Predict multiple texts for fake news."""
    if not detector.is_ready():
        raise HTTPException(status_code=503, detail="ML model not ready")
    
    if len(request.texts) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 texts allowed per batch")
    
    try:
        start_time = time.time()
        
        # Make batch predictions
        results = detector.batch_predict(request.texts, request.language)
        
        predictions = []
        for i, (text, result) in enumerate(zip(request.texts, results)):
            if result.get("error"):
                continue  # Skip failed predictions
            
            response_data = {
                "id": f"batch_{i}_{int(time.time())}",
                "prediction": result["prediction"],
                "confidence": result["confidence"],
                "explanation": result["explanation"],
                "factors": result["factors"],
                "sources": result["sources"],
                "timestamp": time.time(),
                "input_text": text[:200] + "..." if len(text) > 200 else text,
                "input_url": None,
                "model_version": result["model_version"],
                "processing_time": result["processing_time"]
            }
            
            predictions.append(PredictionResponse(**response_data))
            
            # Save to database in background
            background_tasks.add_task(
                save_prediction_to_db,
                db,
                text,
                None,
                result
            )
        
        total_time = time.time() - start_time
        
        return BatchPredictionResponse(
            predictions=predictions,
            total_processed=len(predictions),
            processing_time=round(total_time, 3)
        )
        
    except Exception as e:
        logger.error(f"Batch prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/history", response_model=HistoryResponse)
async def get_prediction_history(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get prediction history."""
    try:
        predictions = crud.get_predictions(db, skip=offset, limit=limit)
        total = crud.get_predictions_count(db)
        
        prediction_responses = []
        for pred in predictions:
            response_data = {
                "id": pred.id,
                "prediction": pred.prediction,
                "confidence": pred.confidence,
                "explanation": pred.explanation or "",
                "factors": pred.factors or [],
                "sources": pred.sources or [],
                "timestamp": pred.created_at,
                "input_text": pred.input_text[:200] + "..." if len(pred.input_text) > 200 else pred.input_text,
                "input_url": pred.input_url,
                "model_version": pred.model_version,
                "processing_time": pred.processing_time
            }
            prediction_responses.append(PredictionResponse(**response_data))
        
        return HistoryResponse(
            predictions=prediction_responses,
            total=total,
            page=offset // limit + 1,
            per_page=limit
        )
        
    except Exception as e:
        logger.error(f"Failed to get history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

def scrape_article(url: str) -> str:
    """Scrape article content from URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to find article content
        article_selectors = [
            'article',
            '[role="main"]',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content',
            'main'
        ]
        
        article_text = ""
        for selector in article_selectors:
            elements = soup.select(selector)
            if elements:
                article_text = elements[0].get_text()
                break
        
        # Fallback to body if no article found
        if not article_text:
            article_text = soup.body.get_text() if soup.body else soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in article_text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        article_text = ' '.join(chunk for chunk in chunks if chunk)
        
        return article_text[:10000]  # Limit to 10k characters
        
    except Exception as e:
        logger.error(f"Failed to scrape URL {url}: {str(e)}")
        return ""

def save_prediction_to_db(db: Session, text: str, url: str, result: dict):
    """Save prediction to database (background task)."""
    try:
        prediction_data = {
            "input_text": text,
            "input_url": url,
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "explanation": result["explanation"],
            "factors": result["factors"],
            "sources": result["sources"],
            "model_version": result["model_version"],
            "processing_time": result["processing_time"]
        }
        
        crud.create_prediction(db, prediction_data)
        logger.debug("Prediction saved to database")
        
    except Exception as e:
        logger.error(f"Failed to save prediction to database: {str(e)}")