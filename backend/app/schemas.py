from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class PredictionRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=10000, description="News text to analyze")
    language: str = Field(default="en", description="Language code")

class URLPredictionRequest(BaseModel):
    url: str = Field(..., description="URL of news article to analyze")
    language: str = Field(default="en", description="Language code")

class BatchPredictionRequest(BaseModel):
    texts: List[str] = Field(..., max_items=50, description="List of news texts to analyze")
    language: str = Field(default="en", description="Language code")

class Factor(BaseModel):
    name: str
    score: float
    impact: str  # positive/negative/neutral
    description: str

class PredictionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    id: str
    prediction: str  # real/fake/inconclusive
    confidence: float
    explanation: str
    factors: List[Factor]
    sources: List[str]
    timestamp: datetime
    input_text: str
    input_url: Optional[str] = None
    model_version: str
    processing_time: Optional[float] = None

class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]
    total_processed: int
    processing_time: float

class FeedbackRequest(BaseModel):
    prediction_id: str
    user_correction: str = Field(..., pattern="^(real|fake)$")
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: str
    message: str
    timestamp: datetime

class HistoryResponse(BaseModel):
    predictions: List[PredictionResponse]
    total: int
    page: int
    per_page: int

class StatsResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    total_predictions: int
    fake_predictions: int
    real_predictions: int
    inconclusive_predictions: int
    avg_confidence: float
    model_accuracy: Optional[float]
    model_version: str
    uptime_hours: float

class HealthResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    status: str
    ml_model_loaded: bool
    database_connected: bool
    redis_connected: bool
    model_version: str
    timestamp: datetime

class ErrorResponse(BaseModel):
    error: bool = True
    message: str
    code: str
    timestamp: datetime
    suggestion: Optional[str] = None

class RetrainRequest(BaseModel):
    trigger: str = Field(default="manual")
    epochs: int = Field(default=3, ge=1, le=10)
    learning_rate: float = Field(default=2e-5, gt=0, lt=1)

class RetrainResponse(BaseModel):
    job_id: str
    status: str
    message: str
    estimated_time: int  # minutes