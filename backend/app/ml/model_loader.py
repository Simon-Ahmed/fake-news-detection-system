import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Optional, Dict, Any
import logging
import pickle
from sklearn.ensemble import RandomForestClassifier
import numpy as np

logger = logging.getLogger(__name__)

class ModelLoader:
    def __init__(self):
        self.bert_model = None
        self.bert_tokenizer = None
        self.fallback_model = None
        self.model_version = "bert-fake-news-v1.0"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    def load_bert_model(self, model_name: str = "mrm8488/bert-tiny-finetuned-fake-news-detection") -> bool:
        """Load pre-trained BERT model for fake news detection."""
        try:
            logger.info(f"Loading BERT model: {model_name}")
            
            # Skip BERT loading for now to avoid startup delays
            logger.info("Skipping BERT model loading for faster startup")
            return False
            
        except Exception as e:
            logger.error(f"Failed to load BERT model: {str(e)}")
            return False
    
    def load_fallback_model(self) -> bool:
        """Load or create a simple fallback model."""
        try:
            fallback_path = "models/fallback_model.pkl"
            
            if os.path.exists(fallback_path):
                with open(fallback_path, 'rb') as f:
                    self.fallback_model = pickle.load(f)
                logger.info("Fallback model loaded from file")
            else:
                # Create a simple rule-based fallback
                self.fallback_model = self._create_rule_based_model()
                logger.info("Created rule-based fallback model")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load fallback model: {str(e)}")
            return False
    
    def _create_rule_based_model(self) -> Dict[str, Any]:
        """Create a simple rule-based model as fallback."""
        return {
            "type": "rule_based",
            "rules": {
                "clickbait_threshold": 50,
                "emotional_threshold": 0.15,
                "bias_threshold": 30,
                "source_bonus": 20
            }
        }
    
    def predict_with_bert(self, text: str) -> Dict[str, Any]:
        """Make prediction using BERT model."""
        if not self.bert_model or not self.bert_tokenizer:
            raise ValueError("BERT model not loaded")
        
        try:
            # Tokenize input
            inputs = self.bert_tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Make prediction
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)
            
            # Convert to numpy
            probs = probabilities.cpu().numpy()[0]
            
            # Assuming binary classification: [REAL, FAKE]
            fake_prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
            real_prob = float(probs[0]) if len(probs) > 1 else 1.0 - float(probs[0])
            
            # Determine prediction
            if fake_prob > 0.7:
                prediction = "fake"
                confidence = fake_prob * 100
            elif real_prob > 0.7:
                prediction = "real"
                confidence = real_prob * 100
            else:
                prediction = "inconclusive"
                confidence = max(fake_prob, real_prob) * 100
            
            return {
                "prediction": prediction,
                "confidence": confidence,
                "fake_probability": fake_prob,
                "real_probability": real_prob,
                "model_used": "bert"
            }
            
        except Exception as e:
            logger.error(f"BERT prediction failed: {str(e)}")
            raise
    
    def predict_with_fallback(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Make prediction using fallback model."""
        if not self.fallback_model:
            raise ValueError("Fallback model not loaded")
        
        try:
            if self.fallback_model["type"] == "rule_based":
                return self._rule_based_prediction(features)
            else:
                # If we have a trained sklearn model
                feature_vector = np.array(list(features.values())).reshape(1, -1)
                prediction = self.fallback_model.predict(feature_vector)[0]
                confidence = max(self.fallback_model.predict_proba(feature_vector)[0]) * 100
                
                return {
                    "prediction": prediction,
                    "confidence": confidence,
                    "model_used": "fallback_ml"
                }
                
        except Exception as e:
            logger.error(f"Fallback prediction failed: {str(e)}")
            raise
    
    def _rule_based_prediction(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Simple rule-based prediction."""
        rules = self.fallback_model["rules"]
        
        fake_score = 0
        real_score = 0
        
        # Clickbait indicators
        if features.get("clickbait_score", 0) > rules["clickbait_threshold"]:
            fake_score += 30
        
        # Emotional language
        if features.get("emotional_intensity", 0) > rules["emotional_threshold"]:
            fake_score += 25
        
        # Bias indicators
        if features.get("total_bias_score", 0) > rules["bias_threshold"]:
            fake_score += 20
        
        # Source citations (positive indicator)
        if features.get("has_sources", 0) > 0:
            real_score += rules["source_bonus"]
        
        # Readability (very low or very high can be suspicious)
        flesch_score = features.get("flesch_reading_ease", 50)
        if flesch_score < 20 or flesch_score > 95:
            fake_score += 15
        
        # Determine prediction
        total_score = fake_score - real_score
        
        if total_score > 40:
            prediction = "fake"
            confidence = min(60 + (total_score - 40) * 0.5, 95)
        elif total_score < -20:
            prediction = "real"
            confidence = min(60 + abs(total_score + 20) * 0.5, 95)
        else:
            prediction = "inconclusive"
            confidence = 50 + abs(total_score) * 0.5
        
        return {
            "prediction": prediction,
            "confidence": confidence,
            "fake_score": fake_score,
            "real_score": real_score,
            "model_used": "rule_based"
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models."""
        return {
            "model_version": self.model_version,
            "bert_loaded": self.bert_model is not None,
            "fallback_loaded": self.fallback_model is not None,
            "device": str(self.device),
            "bert_model_name": "mrm8488/bert-tiny-finetuned-fake-news-detection" if self.bert_model else None
        }
    
    def is_ready(self) -> bool:
        """Check if at least one model is ready for predictions."""
        return self.bert_model is not None or self.fallback_model is not None