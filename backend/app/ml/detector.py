import time
import logging
import os
from typing import Dict, List, Any
from .preprocessor import TextPreprocessor
from .feature_extractor import FeatureExtractor
from .model_loader import ModelLoader

logger = logging.getLogger(__name__)

class FakeNewsDetector:
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.feature_extractor = FeatureExtractor()
        self.model_loader = ModelLoader()
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Initialize the detector with models."""
        try:
            logger.info("Initializing Fake News Detector...")
            
            # Check if we should skip ML initialization for testing
            if os.getenv("SKIP_ML_INIT") == "true":
                logger.info("Skipping ML initialization for testing")
                self.is_initialized = True
                return True
            
            # Skip BERT model loading for now to avoid startup delays
            # Load fallback model only
            fallback_loaded = self.model_loader.load_fallback_model()
            
            if not fallback_loaded:
                logger.error("Failed to load fallback model")
                return False
            
            self.is_initialized = True
            logger.info("Fake News Detector initialized successfully (fallback mode)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize detector: {str(e)}")
            return False
    
    def predict(self, text: str, language: str = "en") -> Dict[str, Any]:
        """Make a prediction on a single text."""
        if not self.is_initialized:
            raise ValueError("Detector not initialized")
        
        start_time = time.time()
        
        try:
            # Validate input
            is_valid, error_msg = self.preprocessor.validate_text(text)
            if not is_valid:
                return {
                    "prediction": "error",
                    "confidence": 0.0,
                    "explanation": f"Input validation failed: {error_msg}",
                    "factors": [],
                    "sources": [],
                    "model_version": self.model_loader.model_version,
                    "processing_time": time.time() - start_time,
                    "error": True
                }
            
            # Preprocess text
            bert_text = self.preprocessor.preprocess_for_bert(text)
            feature_text = self.preprocessor.preprocess_for_features(text)
            
            # Extract features
            features = self.feature_extractor.extract_features(text)
            feature_explanations = self.feature_extractor.get_feature_explanations(text)
            
            # Try BERT prediction first (if available)
            bert_result = None
            if self.model_loader.bert_model:
                try:
                    bert_result = self.model_loader.predict_with_bert(bert_text)
                except Exception as e:
                    logger.warning(f"BERT prediction failed, using fallback: {str(e)}")
            
            # Use fallback model (always available)
            fallback_result = self.model_loader.predict_with_fallback(features)
            
            if bert_result is not None:
                # Combine BERT with feature analysis
                prediction, confidence = self._combine_predictions(bert_result, features)
                model_used = "bert_combined"
            else:
                # Use fallback only
                prediction = fallback_result["prediction"]
                confidence = fallback_result["confidence"]
                model_used = fallback_result["model_used"]
            
            # Generate explanation
            explanation = self._generate_explanation(prediction, confidence, feature_explanations)
            
            # Get suggested sources for fact-checking
            sources = self._get_fact_check_sources()
            
            processing_time = time.time() - start_time
            
            return {
                "prediction": prediction,
                "confidence": round(confidence, 1),
                "explanation": explanation,
                "factors": feature_explanations,
                "sources": sources,
                "model_version": self.model_loader.model_version,
                "processing_time": round(processing_time, 3),
                "model_used": model_used,
                "error": False
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            return {
                "prediction": "error",
                "confidence": 0.0,
                "explanation": f"Prediction failed: {str(e)}",
                "factors": [],
                "sources": [],
                "model_version": self.model_loader.model_version,
                "processing_time": time.time() - start_time,
                "error": True
            }
    
    def batch_predict(self, texts: List[str], language: str = "en") -> List[Dict[str, Any]]:
        """Make predictions on multiple texts."""
        if not self.is_initialized:
            raise ValueError("Detector not initialized")
        
        results = []
        for text in texts:
            result = self.predict(text, language)
            results.append(result)
        
        return results
    
    def _combine_predictions(self, bert_result: Dict[str, Any], features: Dict[str, float]) -> tuple[str, float]:
        """Combine BERT prediction with feature analysis."""
        bert_prediction = bert_result["prediction"]
        bert_confidence = bert_result["confidence"]
        
        # Adjust confidence based on features
        confidence_adjustment = 0
        
        # Strong clickbait indicators reduce confidence in "real" prediction
        if bert_prediction == "real" and features.get("clickbait_score", 0) > 60:
            confidence_adjustment -= 15
        
        # Strong emotional language reduces confidence in "real" prediction
        if bert_prediction == "real" and features.get("emotional_intensity", 0) > 0.2:
            confidence_adjustment -= 10
        
        # Source citations increase confidence in "real" prediction
        if bert_prediction == "real" and features.get("has_sources", 0) > 0:
            confidence_adjustment += 10
        
        # Bias indicators reduce confidence in "real" prediction
        if bert_prediction == "real" and features.get("has_bias_indicators", 0) > 0:
            confidence_adjustment -= 8
        
        # Apply adjustments
        adjusted_confidence = max(50, min(95, bert_confidence + confidence_adjustment))
        
        # If confidence drops too low, change to inconclusive
        if adjusted_confidence < 60 and bert_prediction != "inconclusive":
            return "inconclusive", adjusted_confidence
        
        return bert_prediction, adjusted_confidence
    
    def _generate_explanation(self, prediction: str, confidence: float, factors: List[Dict]) -> str:
        """Generate human-readable explanation."""
        if prediction == "error":
            return "Unable to analyze the text due to an error."
        
        base_explanations = {
            "fake": f"This text appears to be fake news with {confidence:.1f}% confidence.",
            "real": f"This text appears to be legitimate news with {confidence:.1f}% confidence.",
            "inconclusive": f"The analysis is inconclusive with {confidence:.1f}% confidence."
        }
        
        explanation = base_explanations.get(prediction, "Unknown prediction result.")
        
        # Add key factors
        negative_factors = [f for f in factors if f["impact"] == "negative"]
        positive_factors = [f for f in factors if f["impact"] == "positive"]
        
        if negative_factors:
            top_negative = sorted(negative_factors, key=lambda x: x["score"], reverse=True)[:2]
            factor_text = ", ".join([f["name"].lower() for f in top_negative])
            explanation += f" Key concerns include {factor_text}."
        
        if positive_factors:
            top_positive = sorted(positive_factors, key=lambda x: x["score"], reverse=True)[:1]
            factor_text = ", ".join([f["name"].lower() for f in top_positive])
            explanation += f" Positive indicators include {factor_text}."
        
        return explanation
    
    def _get_fact_check_sources(self) -> List[str]:
        """Get list of recommended fact-checking sources."""
        return [
            "https://www.snopes.com",
            "https://www.factcheck.org",
            "https://www.politifact.com",
            "https://www.reuters.com/fact-check",
            "https://apnews.com/hub/ap-fact-check"
        ]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the detector and its models."""
        if not self.is_initialized:
            return {"error": "Detector not initialized"}
        
        model_info = self.model_loader.get_model_info()
        model_info.update({
            "initialized": self.is_initialized,
            "feature_count": len(self.feature_extractor.feature_names),
            "supported_languages": ["en"]  # Currently only English
        })
        
        return model_info
    
    def fine_tune(self, feedback_data: List[Dict]) -> bool:
        """Fine-tune the model with feedback data (placeholder for future implementation)."""
        logger.info(f"Fine-tuning requested with {len(feedback_data)} feedback samples")
        # This would implement online learning in a production system
        # For now, just log the request
        return True
    
    def is_ready(self) -> bool:
        """Check if the detector is ready for predictions."""
        return self.is_initialized and self.model_loader.is_ready()