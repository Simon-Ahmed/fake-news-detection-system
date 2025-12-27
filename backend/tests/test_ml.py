import pytest
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.preprocessor import TextPreprocessor
from app.ml.feature_extractor import FeatureExtractor
from app.ml.utils import (
    detect_clickbait_patterns,
    analyze_emotional_language,
    detect_bias_indicators,
    analyze_source_citations
)

class TestTextPreprocessor:
    def setup_method(self):
        self.preprocessor = TextPreprocessor()
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        dirty_text = "This   is    a   test!!!   with   extra   spaces."
        cleaned = self.preprocessor.clean_text(dirty_text)
        assert "   " not in cleaned
        assert cleaned.strip() == cleaned
    
    def test_preprocess_for_bert(self):
        """Test BERT preprocessing."""
        text = "This is a test article with some content."
        processed = self.preprocessor.preprocess_for_bert(text)
        assert len(processed) > 0
        assert isinstance(processed, str)
    
    def test_validate_text(self):
        """Test text validation."""
        # Valid text
        valid, msg = self.preprocessor.validate_text("This is a valid news article with enough content.")
        assert valid
        
        # Empty text
        valid, msg = self.preprocessor.validate_text("")
        assert not valid
        
        # Too short
        valid, msg = self.preprocessor.validate_text("short")
        assert not valid
        
        # Too long
        long_text = "a" * 60000
        valid, msg = self.preprocessor.validate_text(long_text)
        assert not valid

class TestFeatureExtractor:
    def setup_method(self):
        self.extractor = FeatureExtractor()
    
    def test_extract_features(self):
        """Test feature extraction."""
        text = "This is a test article. It has multiple sentences and should generate features."
        features = self.extractor.extract_features(text)
        
        assert isinstance(features, dict)
        assert len(features) > 0
        assert "flesch_reading_ease" in features
        assert "clickbait_score" in features
    
    def test_get_feature_vector(self):
        """Test feature vector generation."""
        text = "This is a test article."
        vector = self.extractor.get_feature_vector(text)
        
        assert len(vector) == len(self.extractor.feature_names)
        assert all(isinstance(x, (int, float)) for x in vector)
    
    def test_get_feature_explanations(self):
        """Test feature explanations."""
        clickbait_text = "SHOCKING! You won't believe this amazing trick!"
        explanations = self.extractor.get_feature_explanations(clickbait_text)
        
        assert isinstance(explanations, list)
        # Should detect clickbait
        clickbait_found = any("clickbait" in exp["name"].lower() for exp in explanations)
        assert clickbait_found

class TestMLUtils:
    def test_detect_clickbait_patterns(self):
        """Test clickbait detection."""
        clickbait_text = "You won't believe this shocking discovery!"
        result = detect_clickbait_patterns(clickbait_text)
        
        assert result["clickbait_score"] > 0
        assert result["has_clickbait"]
        assert len(result["clickbait_phrases"]) > 0
    
    def test_analyze_emotional_language(self):
        """Test emotional language analysis."""
        emotional_text = "This is absolutely terrible and disgusting!"
        result = analyze_emotional_language(emotional_text)
        
        assert result["emotion_scores"]["negative"] > 0
        assert result["total_emotional_words"] > 0
    
    def test_detect_bias_indicators(self):
        """Test bias detection."""
        biased_text = "Everyone knows that this is obviously true and always happens."
        result = detect_bias_indicators(biased_text)
        
        assert result["total_bias_score"] > 0
        assert result["has_bias_indicators"]
    
    def test_analyze_source_citations(self):
        """Test source citation analysis."""
        text_with_sources = "According to a study, experts say this is true. https://example.com"
        result = analyze_source_citations(text_with_sources)
        
        assert result["citation_count"] > 0
        assert result["url_count"] > 0
        assert result["has_sources"]
    
    def test_no_clickbait(self):
        """Test normal text without clickbait."""
        normal_text = "The Federal Reserve announced interest rate changes today."
        result = detect_clickbait_patterns(normal_text)
        
        assert result["clickbait_score"] == 0
        assert not result["has_clickbait"]

# Integration test
def test_full_pipeline():
    """Test the full ML pipeline with sample texts."""
    preprocessor = TextPreprocessor()
    extractor = FeatureExtractor()
    
    test_texts = [
        "According to a new study in Nature, coffee consumption may reduce heart disease risk.",
        "SHOCKING! Doctors hate this one weird trick that will change your life forever!",
        "The stock market closed higher today following positive economic indicators."
    ]
    
    for text in test_texts:
        # Validate
        valid, msg = preprocessor.validate_text(text)
        assert valid, f"Text validation failed: {msg}"
        
        # Preprocess
        processed = preprocessor.preprocess_for_bert(text)
        assert len(processed) > 0
        
        # Extract features
        features = extractor.extract_features(text)
        assert len(features) > 0
        
        # Get explanations
        explanations = extractor.get_feature_explanations(text)
        assert isinstance(explanations, list)

if __name__ == "__main__":
    pytest.main([__file__])