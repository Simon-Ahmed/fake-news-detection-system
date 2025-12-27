from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from ..database import get_db
from ..schemas import FeedbackRequest, FeedbackResponse
from .. import crud

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["feedback"])

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """Submit user feedback for a prediction."""
    try:
        # Verify prediction exists
        prediction = crud.get_prediction(db, request.prediction_id)
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        # Create feedback record
        feedback_data = {
            "prediction_id": request.prediction_id,
            "user_correction": request.user_correction,
            "comment": request.comment,
            "user_id": None,  # TODO: Add user authentication
            "is_processed": False
        }
        
        feedback = crud.create_feedback(db, feedback_data)
        
        logger.info(f"Feedback submitted for prediction {request.prediction_id}")
        
        return FeedbackResponse(
            id=feedback.id,
            message="Thank you for your feedback! It will help improve our model.",
            timestamp=feedback.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/feedback/stats")
async def get_feedback_stats(db: Session = Depends(get_db)):
    """Get feedback statistics for model improvement."""
    try:
        # Get unprocessed feedback count
        unprocessed_feedback = crud.get_feedback_for_training(db, limit=10000)
        
        # Calculate accuracy from feedback
        total_feedback = len(unprocessed_feedback)
        if total_feedback == 0:
            return {
                "total_feedback": 0,
                "accuracy_from_feedback": None,
                "corrections_needed": 0
            }
        
        # Compare predictions with user corrections
        correct_predictions = 0
        for feedback in unprocessed_feedback:
            prediction = crud.get_prediction(db, feedback.prediction_id)
            if prediction and prediction.prediction == feedback.user_correction:
                correct_predictions += 1
        
        accuracy = (correct_predictions / total_feedback) * 100 if total_feedback > 0 else 0
        
        return {
            "total_feedback": total_feedback,
            "accuracy_from_feedback": round(accuracy, 2),
            "corrections_needed": total_feedback - correct_predictions,
            "correct_predictions": correct_predictions
        }
        
    except Exception as e:
        logger.error(f"Failed to get feedback stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")