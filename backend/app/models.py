from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from .database import Base
import uuid

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    input_text = Column(Text, nullable=False)
    input_url = Column(String, nullable=True)
    prediction = Column(String, nullable=False)  # real/fake/inconclusive
    confidence = Column(Float, nullable=False)
    explanation = Column(Text, nullable=True)
    factors = Column(JSON, nullable=True)
    sources = Column(JSON, nullable=True)
    model_version = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processing_time = Column(Float, nullable=True)

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    prediction_id = Column(String, nullable=False)
    user_correction = Column(String, nullable=False)  # real/fake
    comment = Column(Text, nullable=True)
    user_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_processed = Column(Boolean, default=False)

class ModelVersion(Base):
    __tablename__ = "model_versions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    version = Column(String, nullable=False, unique=True)
    model_path = Column(String, nullable=False)
    accuracy = Column(Float, nullable=True)
    training_date = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=False)
    description = Column(Text, nullable=True)

class PredictionAnalytics(Base):
    __tablename__ = "prediction_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    total_predictions = Column(Integer, default=0)
    fake_predictions = Column(Integer, default=0)
    real_predictions = Column(Integer, default=0)
    inconclusive_predictions = Column(Integer, default=0)
    avg_confidence = Column(Float, default=0.0)
    avg_processing_time = Column(Float, default=0.0)