from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import time

from ..database import get_db
from ..schemas import StatsResponse, HealthResponse, RetrainRequest, RetrainResponse
from .. import crud
from ..ml.detector import FakeNewsDetector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["admin"])

# Global detector instance (shared with predictions router)
detector = None

def get_detector():
    global detector
    if detector is None:
        detector = FakeNewsDetector()
        detector.initialize()
    return detector

@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """Get system statistics."""
    try:
        # Get prediction stats
        stats = crud.get_prediction_stats(db, days=30)
        
        # Get model info
        detector_instance = get_detector()
        model_info = detector_instance.get_model_info()
        
        # Calculate uptime (placeholder - in production, track actual uptime)
        uptime_hours = 24.0  # Placeholder
        
        return StatsResponse(
            total_predictions=stats["total_predictions"],
            fake_predictions=stats["fake_predictions"],
            real_predictions=stats["real_predictions"],
            inconclusive_predictions=stats["inconclusive_predictions"],
            avg_confidence=stats["avg_confidence"],
            model_accuracy=None,  # TODO: Calculate from feedback
            model_version=model_info.get("model_version", "unknown"),
            uptime_hours=uptime_hours
        )
        
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Check database connection
        db_connected = True
        try:
            db.execute("SELECT 1")
        except Exception:
            db_connected = False
        
        # Check ML model
        detector_instance = get_detector()
        ml_model_loaded = detector_instance.is_ready()
        
        # Check Redis (placeholder)
        redis_connected = True  # TODO: Implement Redis check
        
        # Determine overall status
        status = "healthy"
        if not db_connected or not ml_model_loaded:
            status = "unhealthy"
        elif not redis_connected:
            status = "degraded"
        
        model_info = detector_instance.get_model_info()
        
        return HealthResponse(
            status=status,
            ml_model_loaded=ml_model_loaded,
            database_connected=db_connected,
            redis_connected=redis_connected,
            model_version=model_info.get("model_version", "unknown"),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/admin/retrain", response_model=RetrainResponse)
async def trigger_retrain(
    request: RetrainRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger model retraining with feedback data."""
    try:
        # Get feedback data for training
        feedback_data = crud.get_feedback_for_training(db, limit=1000)
        
        if len(feedback_data) < 10:
            raise HTTPException(
                status_code=400, 
                detail="Insufficient feedback data for retraining (minimum 10 samples required)"
            )
        
        # Generate job ID
        import uuid
        job_id = str(uuid.uuid4())
        
        # Start retraining in background
        background_tasks.add_task(
            retrain_model_task,
            job_id,
            feedback_data,
            request.epochs,
            request.learning_rate,
            db
        )
        
        # Estimate training time (placeholder calculation)
        estimated_time = len(feedback_data) * request.epochs // 10  # rough estimate in minutes
        
        logger.info(f"Retraining job {job_id} started with {len(feedback_data)} samples")
        
        return RetrainResponse(
            job_id=job_id,
            status="started",
            message=f"Retraining started with {len(feedback_data)} feedback samples",
            estimated_time=estimated_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trigger retraining: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/admin/retrain/{job_id}")
async def get_retrain_status(job_id: str):
    """Get status of a retraining job."""
    # In a production system, this would check the actual job status
    # For now, return a placeholder response
    return {
        "job_id": job_id,
        "status": "completed",  # or "running", "failed"
        "progress": 100,
        "message": "Retraining completed successfully",
        "started_at": datetime.utcnow() - timedelta(minutes=30),
        "completed_at": datetime.utcnow(),
        "new_model_version": "bert-fake-news-v1.1"
    }

@router.get("/admin/model-info")
async def get_model_info():
    """Get detailed model information."""
    try:
        detector_instance = get_detector()
        model_info = detector_instance.get_model_info()
        
        return {
            **model_info,
            "last_updated": datetime.utcnow(),
            "training_data_size": "Unknown",  # TODO: Track training data
            "performance_metrics": {
                "accuracy": None,  # TODO: Calculate from validation set
                "precision": None,
                "recall": None,
                "f1_score": None
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get model info: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def retrain_model_task(
    job_id: str,
    feedback_data: list,
    epochs: int,
    learning_rate: float,
    db: Session
):
    """Background task for model retraining."""
    try:
        logger.info(f"Starting retraining job {job_id}")
        
        # Simulate retraining process
        # In a real implementation, this would:
        # 1. Prepare training data from feedback
        # 2. Fine-tune the BERT model
        # 3. Validate the new model
        # 4. Update the model version in database
        # 5. Load the new model
        
        # Simulate training time
        await asyncio.sleep(30)  # Simulate 30 seconds of training
        
        # Mark feedback as processed
        feedback_ids = [f.id for f in feedback_data]
        crud.mark_feedback_processed(db, feedback_ids)
        
        # Create new model version record
        new_version_data = {
            "version": f"bert-fake-news-v1.{int(time.time())}",
            "model_path": f"./models/retrained_{job_id}",
            "accuracy": 0.87,  # Placeholder
            "description": f"Retrained with {len(feedback_data)} feedback samples"
        }
        
        crud.create_model_version(db, new_version_data)
        
        logger.info(f"Retraining job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Retraining job {job_id} failed: {str(e)}")

# Import asyncio for the background task
import asyncio