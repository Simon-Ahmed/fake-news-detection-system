"""
Lightweight Fake News Detection Server for Railway Deployment
Simplified version without heavy ML dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import json
import os
from datetime import datetime
import random
import re
import textstat

app = FastAPI(title="Fake News Detection API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "fake_news.db"

def init_db():
    """Initialize the database"""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL NOT NULL,
            analysis_type TEXT DEFAULT 'text',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            features TEXT
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

class PredictionRequest(BaseModel):
    text: str
    analysis_type: str = "text"

class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    explanation: str
    features: dict

def extract_simple_features(text: str) -> dict:
    """Extract simple linguistic features without heavy ML"""
    
    # Basic text statistics
    word_count = len(text.split())
    char_count = len(text)
    sentence_count = len([s for s in text.split('.') if s.strip()])
    
    # Readability
    try:
        flesch_score = textstat.flesch_reading_ease(text)
    except:
        flesch_score = 50.0
    
    # Emotional indicators
    emotional_words = ['shocking', 'unbelievable', 'amazing', 'incredible', 'must', 'urgent', 
                      'breaking', 'secret', 'exposed', 'revealed', 'scandal', 'outrageous']
    emotional_count = sum(1 for word in emotional_words if word.lower() in text.lower())
    
    # Capitalization
    caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
    
    # Exclamation marks
    exclamation_count = text.count('!')
    
    # Question marks
    question_count = text.count('?')
    
    return {
        'word_count': word_count,
        'char_count': char_count,
        'sentence_count': sentence_count,
        'avg_word_length': char_count / word_count if word_count > 0 else 0,
        'flesch_reading_ease': flesch_score,
        'emotional_words': emotional_count,
        'caps_ratio': caps_ratio,
        'exclamation_count': exclamation_count,
        'question_count': question_count
    }

def simple_fake_news_detection(text: str) -> tuple:
    """Enhanced fake news detection with better accuracy"""
    
    features = extract_simple_features(text)
    
    # Enhanced scoring system
    fake_score = 0
    explanation_parts = []
    
    # Strong fake indicators (high weight)
    strong_fake_words = ['shocking', 'unbelievable', 'you won\'t believe', 'incredible', 
                        'amazing discovery', 'secret', 'they don\'t want you to know',
                        'click here', 'before it\'s too late', 'government cover', 'breakthrough']
    
    strong_fake_count = sum(1 for word in strong_fake_words if word.lower() in text.lower())
    if strong_fake_count > 0:
        fake_score += 0.4 + (strong_fake_count * 0.15)
        explanation_parts.append(f"Contains {strong_fake_count} strong sensationalist phrases")
    
    # Clickbait patterns
    clickbait_patterns = ['you won\'t believe', 'this will change everything', 
                         'what happens next', 'the truth about', 'doctors hate']
    clickbait_count = sum(1 for pattern in clickbait_patterns if pattern.lower() in text.lower())
    if clickbait_count > 0:
        fake_score += 0.3 + (clickbait_count * 0.1)
        explanation_parts.append("Uses clickbait language patterns")
    
    # Excessive punctuation
    if features['exclamation_count'] > 2:
        fake_score += 0.2 + (features['exclamation_count'] * 0.05)
        explanation_parts.append(f"Excessive exclamation marks ({features['exclamation_count']})")
    
    # ALL CAPS usage
    if features['caps_ratio'] > 0.15:
        fake_score += 0.25
        explanation_parts.append("Excessive capitalization detected")
    
    # Emotional manipulation words
    emotional_words = ['shocking', 'terrifying', 'outrageous', 'scandal', 'exposed', 
                      'revealed', 'hidden truth', 'conspiracy', 'urgent', 'breaking']
    emotional_count = sum(1 for word in emotional_words if word.lower() in text.lower())
    if emotional_count > 1:
        fake_score += 0.2 + (emotional_count * 0.08)
        explanation_parts.append(f"High emotional manipulation language ({emotional_count} indicators)")
    
    # Credible source indicators (reduce fake score)
    credible_indicators = ['according to', 'study shows', 'research indicates', 'university',
                          'published in', 'peer reviewed', 'data shows', 'statistics reveal',
                          'experts say', 'official statement']
    
    credible_count = sum(1 for indicator in credible_indicators if indicator.lower() in text.lower())
    if credible_count > 0:
        fake_score -= 0.3 + (credible_count * 0.1)
        explanation_parts.append(f"Contains {credible_count} credible source indicators")
    
    # Length analysis
    if features['word_count'] < 20:
        fake_score += 0.1
        explanation_parts.append("Very short content (often misleading)")
    elif features['word_count'] > 500:
        fake_score -= 0.1
        explanation_parts.append("Detailed content (typically more credible)")
    
    # Readability analysis
    if features['flesch_reading_ease'] > 80:  # Very easy to read (often clickbait)
        fake_score += 0.15
        explanation_parts.append("Overly simplified language (clickbait indicator)")
    elif features['flesch_reading_ease'] < 30:  # Very hard to read
        fake_score += 0.1
        explanation_parts.append("Unnecessarily complex language")
    
    # Ensure score is between 0 and 1
    fake_score = max(0, min(1, fake_score))
    
    # Determine prediction with better thresholds
    if fake_score > 0.6:
        prediction = "FAKE"
        confidence = fake_score
    elif fake_score < 0.3:
        prediction = "REAL"
        confidence = 1 - fake_score
    else:
        prediction = "REAL"  # Default to real for borderline cases
        confidence = 1 - fake_score
    
    # Ensure minimum confidence
    confidence = max(0.6, confidence)
    
    return prediction, confidence, features

@app.get("/")
async def root():
    return {"message": "Fake News Detection API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Predict if news is fake or real"""
    
    try:
        text = request.text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Get prediction
        prediction, confidence, features = simple_fake_news_detection(text)
        
        # Create explanation
        if not explanation_parts:
            if prediction == "FAKE":
                explanation_parts.append("Text shows patterns commonly associated with misinformation")
            else:
                explanation_parts.append("Text appears to follow standard informational patterns")
        
        explanation = ". ".join(explanation_parts) + "."
        
        # Save to database
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO predictions (text, prediction, confidence, analysis_type, features)
            VALUES (?, ?, ?, ?, ?)
        """, (text, prediction, confidence, request.analysis_type, json.dumps(features)))
        
        conn.commit()
        conn.close()
        
        return PredictionResponse(
            prediction=prediction,
            confidence=round(confidence, 3),
            explanation=explanation,
            features=features
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/history")
async def get_history():
    """Get prediction history"""
    
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, text, prediction, confidence, analysis_type, created_at, features
            FROM predictions
            ORDER BY created_at DESC
            LIMIT 100
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        history = []
        for row in results:
            try:
                features = json.loads(row[6]) if row[6] else {}
            except:
                features = {}
                
            history.append({
                "id": row[0],
                "text": row[1],
                "prediction": row[2],
                "confidence": row[3],
                "analysis_type": row[4],
                "created_at": row[5],
                "features": features
            })
        
        return {"history": history}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get prediction statistics"""
    
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Total predictions
        cursor.execute("SELECT COUNT(*) FROM predictions")
        total = cursor.fetchone()[0]
        
        # By prediction type
        cursor.execute("SELECT prediction, COUNT(*) FROM predictions GROUP BY prediction")
        by_prediction = dict(cursor.fetchall())
        
        # By analysis type
        cursor.execute("SELECT analysis_type, COUNT(*) FROM predictions GROUP BY analysis_type")
        by_type = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "total_predictions": total,
            "by_prediction": by_prediction,
            "by_analysis_type": by_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)