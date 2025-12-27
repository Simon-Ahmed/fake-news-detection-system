from typing import Dict, List
import numpy as np
from .utils import (
    calculate_readability_scores,
    detect_clickbait_patterns,
    analyze_emotional_language,
    detect_bias_indicators,
    analyze_source_citations,
    calculate_vocabulary_diversity,
    analyze_sentence_complexity
)

class FeatureExtractor:
    def __init__(self):
        self.feature_names = [
            # Readability features
            "flesch_reading_ease",
            "flesch_kincaid_grade",
            "automated_readability_index",
            "coleman_liau_index",
            "gunning_fog",
            
            # Clickbait features
            "clickbait_score",
            "has_clickbait",
            
            # Emotional language features
            "positive_emotion_score",
            "negative_emotion_score",
            "fear_emotion_score",
            "anger_emotion_score",
            "total_emotional_words",
            "exclamation_density",
            "caps_density",
            "emotional_intensity",
            
            # Bias indicators
            "absolute_terms_count",
            "loaded_language_count",
            "generalizations_count",
            "total_bias_score",
            "has_bias_indicators",
            
            # Source citations
            "citation_count",
            "url_count",
            "has_sources",
            "source_density",
            
            # Text complexity
            "vocabulary_diversity",
            "avg_sentence_length",
            "sentence_count",
            "max_sentence_length",
            "sentence_length_variance"
        ]
    
    def extract_features(self, text: str) -> Dict[str, float]:
        """Extract all features from text."""
        features = {}
        
        # Readability features
        readability = calculate_readability_scores(text)
        features.update(readability)
        
        # Clickbait features
        clickbait = detect_clickbait_patterns(text)
        features["clickbait_score"] = clickbait["clickbait_score"]
        features["has_clickbait"] = float(clickbait["has_clickbait"])
        
        # Emotional language features
        emotional = analyze_emotional_language(text)
        features["positive_emotion_score"] = emotional["emotion_scores"]["positive"]
        features["negative_emotion_score"] = emotional["emotion_scores"]["negative"]
        features["fear_emotion_score"] = emotional["emotion_scores"]["fear"]
        features["anger_emotion_score"] = emotional["emotion_scores"]["anger"]
        features["total_emotional_words"] = emotional["total_emotional_words"]
        features["exclamation_density"] = emotional["exclamation_density"]
        features["caps_density"] = emotional["caps_density"]
        features["emotional_intensity"] = emotional["emotional_intensity"]
        
        # Bias indicators
        bias = detect_bias_indicators(text)
        features["absolute_terms_count"] = bias["bias_scores"]["absolute_terms"]
        features["loaded_language_count"] = bias["bias_scores"]["loaded_language"]
        features["generalizations_count"] = bias["bias_scores"]["generalizations"]
        features["total_bias_score"] = bias["total_bias_score"]
        features["has_bias_indicators"] = float(bias["has_bias_indicators"])
        
        # Source citations
        sources = analyze_source_citations(text)
        features["citation_count"] = sources["citation_count"]
        features["url_count"] = sources["url_count"]
        features["has_sources"] = float(sources["has_sources"])
        features["source_density"] = sources["source_density"]
        
        # Text complexity
        features["vocabulary_diversity"] = calculate_vocabulary_diversity(text)
        complexity = analyze_sentence_complexity(text)
        features.update(complexity)
        
        return features
    
    def get_feature_vector(self, text: str) -> np.ndarray:
        """Get feature vector as numpy array."""
        features = self.extract_features(text)
        
        # Ensure all features are present and in correct order
        feature_vector = []
        for feature_name in self.feature_names:
            value = features.get(feature_name, 0.0)
            # Handle NaN values
            if np.isnan(value) or np.isinf(value):
                value = 0.0
            feature_vector.append(float(value))
        
        return np.array(feature_vector)
    
    def get_feature_explanations(self, text: str) -> List[Dict[str, any]]:
        """Get human-readable explanations for features."""
        features = self.extract_features(text)
        explanations = []
        
        # Clickbait indicators
        if features.get("clickbait_score", 0) > 30:
            explanations.append({
                "name": "Clickbait Language",
                "score": features["clickbait_score"],
                "impact": "negative",
                "description": f"Contains clickbait phrases (score: {features['clickbait_score']:.1f}/100)"
            })
        
        # Emotional language
        emotional_intensity = features.get("emotional_intensity", 0)
        if emotional_intensity > 0.1:
            explanations.append({
                "name": "Emotional Language",
                "score": emotional_intensity * 100,
                "impact": "negative",
                "description": f"High emotional language intensity ({emotional_intensity:.2%} of words)"
            })
        
        # Excessive punctuation
        exclamation_density = features.get("exclamation_density", 0)
        if exclamation_density > 0.05:
            explanations.append({
                "name": "Excessive Exclamation",
                "score": exclamation_density * 100,
                "impact": "negative",
                "description": f"Uses excessive exclamation marks ({exclamation_density:.2%} density)"
            })
        
        # Bias indicators
        if features.get("has_bias_indicators", 0) > 0:
            explanations.append({
                "name": "Bias Indicators",
                "score": features["total_bias_score"],
                "impact": "negative",
                "description": f"Contains biased language patterns (score: {features['total_bias_score']:.1f}/100)"
            })
        
        # Source citations (positive indicator)
        if features.get("has_sources", 0) > 0:
            explanations.append({
                "name": "Source Citations",
                "score": features["citation_count"] + features["url_count"],
                "impact": "positive",
                "description": f"Contains {features['citation_count']} citations and {features['url_count']} URLs"
            })
        
        # Readability
        flesch_score = features.get("flesch_reading_ease", 50)
        if flesch_score < 30:
            explanations.append({
                "name": "Complex Language",
                "score": 100 - flesch_score,
                "impact": "neutral",
                "description": f"Text is difficult to read (Flesch score: {flesch_score:.1f})"
            })
        elif flesch_score > 90:
            explanations.append({
                "name": "Very Simple Language",
                "score": flesch_score,
                "impact": "neutral",
                "description": f"Text is very easy to read (Flesch score: {flesch_score:.1f})"
            })
        
        return explanations