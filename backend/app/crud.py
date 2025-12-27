from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from . import models, schemas
from typing import List, Optional
from datetime import datetime, timedelta

def create_prediction(db: Session, prediction_data: dict) -> models.Prediction:
    db_prediction = models.Prediction(**prediction_data)
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

def get_prediction(db: Session, prediction_id: str) -> Optional[models.Prediction]:
    return db.query(models.Prediction).filter(models.Prediction.id == prediction_id).first()

def get_predictions(db: Session, skip: int = 0, limit: int = 50) -> List[models.Prediction]:
    return db.query(models.Prediction).order_by(desc(models.Prediction.created_at)).offset(skip).limit(limit).all()

def get_predictions_count(db: Session) -> int:
    return db.query(models.Prediction).count()

def create_feedback(db: Session, feedback_data: dict) -> models.Feedback:
    db_feedback = models.Feedback(**feedback_data)
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def get_feedback_for_training(db: Session, limit: int = 1000) -> List[models.Feedback]:
    return db.query(models.Feedback).filter(models.Feedback.is_processed == False).limit(limit).all()

def mark_feedback_processed(db: Session, feedback_ids: List[str]):
    db.query(models.Feedback).filter(models.Feedback.id.in_(feedback_ids)).update(
        {models.Feedback.is_processed: True}, synchronize_session=False
    )
    db.commit()

def get_active_model_version(db: Session) -> Optional[models.ModelVersion]:
    return db.query(models.ModelVersion).filter(models.ModelVersion.is_active == True).first()

def create_model_version(db: Session, model_data: dict) -> models.ModelVersion:
    # Deactivate current active model
    db.query(models.ModelVersion).filter(models.ModelVersion.is_active == True).update(
        {models.ModelVersion.is_active: False}, synchronize_session=False
    )
    
    # Create new active model
    model_data["is_active"] = True
    db_model = models.ModelVersion(**model_data)
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

def get_prediction_stats(db: Session, days: int = 30) -> dict:
    start_date = datetime.utcnow() - timedelta(days=days)
    
    total = db.query(models.Prediction).filter(models.Prediction.created_at >= start_date).count()
    fake = db.query(models.Prediction).filter(
        models.Prediction.created_at >= start_date,
        models.Prediction.prediction == "fake"
    ).count()
    real = db.query(models.Prediction).filter(
        models.Prediction.created_at >= start_date,
        models.Prediction.prediction == "real"
    ).count()
    inconclusive = db.query(models.Prediction).filter(
        models.Prediction.created_at >= start_date,
        models.Prediction.prediction == "inconclusive"
    ).count()
    
    avg_confidence = db.query(func.avg(models.Prediction.confidence)).filter(
        models.Prediction.created_at >= start_date
    ).scalar() or 0.0
    
    return {
        "total_predictions": total,
        "fake_predictions": fake,
        "real_predictions": real,
        "inconclusive_predictions": inconclusive,
        "avg_confidence": round(avg_confidence, 2)
    }

def update_analytics(db: Session):
    today = datetime.utcnow().date()
    
    # Check if analytics for today already exist
    existing = db.query(models.PredictionAnalytics).filter(
        func.date(models.PredictionAnalytics.date) == today
    ).first()
    
    if existing:
        return existing
    
    # Calculate today's stats
    stats = get_prediction_stats(db, days=1)
    
    analytics = models.PredictionAnalytics(
        date=datetime.utcnow(),
        **stats
    )
    
    db.add(analytics)
    db.commit()
    db.refresh(analytics)
    return analytics