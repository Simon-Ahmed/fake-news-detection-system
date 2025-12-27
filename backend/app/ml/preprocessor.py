import re
import nltk
from typing import Tuple
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class TextPreprocessor:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text for processing."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation for sentence structure
        text = re.sub(r'[^\w\s\.\!\?\,\;\:\-\(\)]', '', text)
        
        # Normalize quotes
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r'['']', "'", text)
        
        # Remove excessive punctuation (more than 3 consecutive)
        text = re.sub(r'([.!?]){4,}', r'\1\1\1', text)
        
        return text.strip()
    
    def preprocess_for_bert(self, text: str) -> str:
        """Preprocess text specifically for BERT model."""
        # Clean the text
        cleaned_text = self.clean_text(text)
        
        # BERT can handle most text as-is, but we'll do minimal preprocessing
        # Truncate to reasonable length (BERT has 512 token limit)
        words = cleaned_text.split()
        if len(words) > 400:  # Leave room for special tokens
            cleaned_text = ' '.join(words[:400])
        
        return cleaned_text
    
    def preprocess_for_features(self, text: str) -> str:
        """Preprocess text for feature extraction."""
        # More aggressive preprocessing for traditional ML features
        cleaned_text = self.clean_text(text)
        
        # Convert to lowercase for feature extraction
        cleaned_text = cleaned_text.lower()
        
        # Tokenize
        tokens = word_tokenize(cleaned_text)
        
        # Remove stopwords for some features (but keep original for others)
        filtered_tokens = [token for token in tokens if token not in self.stop_words]
        
        return ' '.join(filtered_tokens)
    
    def extract_metadata(self, text: str) -> dict:
        """Extract metadata about the text."""
        return {
            "original_length": len(text),
            "word_count": len(text.split()),
            "sentence_count": len(re.findall(r'[.!?]+', text)),
            "paragraph_count": len([p for p in text.split('\n\n') if p.strip()]),
            "has_urls": bool(re.search(r'https?://[^\s]+', text)),
            "has_email": bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)),
            "exclamation_count": text.count('!'),
            "question_count": text.count('?'),
            "caps_ratio": sum(1 for c in text if c.isupper()) / max(len(text), 1)
        }
    
    def validate_text(self, text: str) -> Tuple[bool, str]:
        """Validate if text is suitable for analysis."""
        if not text or not text.strip():
            return False, "Text is empty"
        
        if len(text.strip()) < 10:
            return False, "Text is too short (minimum 10 characters)"
        
        if len(text) > 50000:
            return False, "Text is too long (maximum 50,000 characters)"
        
        # Check if text is mostly non-alphabetic
        alpha_ratio = sum(1 for c in text if c.isalpha()) / len(text)
        if alpha_ratio < 0.3:
            return False, "Text contains too few alphabetic characters"
        
        return True, "Text is valid"