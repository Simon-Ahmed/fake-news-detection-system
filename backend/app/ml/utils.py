import re
import nltk
import textstat
from typing import Dict, List
import numpy as np
from collections import Counter

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def calculate_readability_scores(text: str) -> Dict[str, float]:
    """Calculate various readability scores for the text."""
    return {
        "flesch_reading_ease": textstat.flesch_reading_ease(text),
        "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
        "automated_readability_index": textstat.automated_readability_index(text),
        "coleman_liau_index": textstat.coleman_liau_index(text),
        "gunning_fog": textstat.gunning_fog(text)
    }

def detect_clickbait_patterns(text: str) -> Dict[str, any]:
    """Detect clickbait patterns in text."""
    clickbait_patterns = [
        r'\b(shocking|amazing|incredible|unbelievable|you won\'t believe)\b',
        r'\b(this one trick|doctors hate|secret)\b',
        r'\b(click here|find out|discover)\b',
        r'\b(number \d+ will|what happens next)\b'
    ]
    
    matches = []
    total_score = 0
    
    for pattern in clickbait_patterns:
        pattern_matches = re.findall(pattern, text.lower())
        if pattern_matches:
            matches.extend(pattern_matches)
            total_score += len(pattern_matches) * 10
    
    return {
        "clickbait_score": min(total_score, 100),
        "clickbait_phrases": matches,
        "has_clickbait": total_score > 20
    }

def analyze_emotional_language(text: str) -> Dict[str, any]:
    """Analyze emotional language in text."""
    emotional_words = {
        "positive": ["amazing", "incredible", "fantastic", "wonderful", "excellent", "perfect"],
        "negative": ["terrible", "awful", "horrible", "disgusting", "outrageous", "shocking"],
        "fear": ["dangerous", "threat", "crisis", "disaster", "panic", "terror"],
        "anger": ["furious", "outraged", "angry", "mad", "hate", "disgusted"]
    }
    
    text_lower = text.lower()
    word_counts = Counter(text_lower.split())
    
    emotion_scores = {}
    total_emotional_words = 0
    
    for emotion, words in emotional_words.items():
        count = sum(word_counts.get(word, 0) for word in words)
        emotion_scores[emotion] = count
        total_emotional_words += count
    
    # Calculate exclamation and caps density
    exclamation_count = text.count('!')
    caps_words = len([word for word in text.split() if word.isupper() and len(word) > 1])
    
    return {
        "emotion_scores": emotion_scores,
        "total_emotional_words": total_emotional_words,
        "exclamation_density": exclamation_count / max(len(text.split()), 1),
        "caps_density": caps_words / max(len(text.split()), 1),
        "emotional_intensity": total_emotional_words / max(len(text.split()), 1)
    }

def detect_bias_indicators(text: str) -> Dict[str, any]:
    """Detect potential bias indicators in text."""
    bias_patterns = {
        "absolute_terms": r'\b(always|never|all|none|every|completely|totally)\b',
        "loaded_language": r'\b(obviously|clearly|undoubtedly|certainly|definitely)\b',
        "generalizations": r'\b(everyone knows|it\'s common knowledge|studies show)\b'
    }
    
    bias_scores = {}
    total_bias_score = 0
    
    for bias_type, pattern in bias_patterns.items():
        matches = len(re.findall(pattern, text.lower()))
        bias_scores[bias_type] = matches
        total_bias_score += matches * 5
    
    return {
        "bias_scores": bias_scores,
        "total_bias_score": min(total_bias_score, 100),
        "has_bias_indicators": total_bias_score > 15
    }

def analyze_source_citations(text: str) -> Dict[str, any]:
    """Analyze source citations and references in text."""
    citation_patterns = [
        r'according to',
        r'study shows?',
        r'research indicates?',
        r'experts? say',
        r'officials? said',
        r'reports? suggest',
        r'data shows?'
    ]
    
    url_pattern = r'https?://[^\s]+'
    
    citation_count = 0
    for pattern in citation_patterns:
        citation_count += len(re.findall(pattern, text.lower()))
    
    url_count = len(re.findall(url_pattern, text))
    
    return {
        "citation_count": citation_count,
        "url_count": url_count,
        "has_sources": citation_count > 0 or url_count > 0,
        "source_density": (citation_count + url_count) / max(len(text.split()), 1)
    }

def calculate_vocabulary_diversity(text: str) -> float:
    """Calculate vocabulary diversity (Type-Token Ratio)."""
    words = text.lower().split()
    if not words:
        return 0.0
    
    unique_words = set(words)
    return len(unique_words) / len(words)

def analyze_sentence_complexity(text: str) -> Dict[str, float]:
    """Analyze sentence complexity metrics."""
    sentences = nltk.sent_tokenize(text)
    if not sentences:
        return {"avg_sentence_length": 0.0, "sentence_count": 0}
    
    sentence_lengths = [len(sentence.split()) for sentence in sentences]
    
    return {
        "avg_sentence_length": np.mean(sentence_lengths),
        "sentence_count": len(sentences),
        "max_sentence_length": max(sentence_lengths) if sentence_lengths else 0,
        "sentence_length_variance": np.var(sentence_lengths) if len(sentence_lengths) > 1 else 0
    }