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
import uuid
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
    
    # Drop existing table to recreate with proper schema
    cursor.execute("DROP TABLE IF EXISTS predictions")
    
    cursor.execute("""
        CREATE TABLE predictions (
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
    print("✅ Database initialized successfully")

# Initialize database on startup
init_db()

class PredictionRequest(BaseModel):
    text: str
    analysis_type: str = "text"

class PredictionResponse(BaseModel):
    id: str
    prediction: str
    confidence: float
    explanation: str
    factors: list
    sources: list
    timestamp: str
    input_text: str
    input_url: str = None
    analysis_type: str
    model_version: str
    processing_time: float = 0.1

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
    factors = []
    
    # Strong fake indicators (high weight)
    strong_fake_words = ['shocking', 'unbelievable', 'you won\'t believe', 'incredible', 
                        'amazing discovery', 'secret', 'they don\'t want you to know',
                        'click here', 'before it\'s too late', 'government cover', 'breakthrough']
    
    strong_fake_count = sum(1 for word in strong_fake_words if word.lower() in text.lower())
    if strong_fake_count > 0:
        fake_score += 0.4 + (strong_fake_count * 0.15)
        explanation_parts.append(f"Contains {strong_fake_count} strong sensationalist phrases")
        factors.append({
            "name": "Sensationalist Language",
            "score": min(100, strong_fake_count * 25),
            "impact": "negative",
            "description": f"Found {strong_fake_count} sensationalist phrases"
        })
    
    # Clickbait patterns
    clickbait_patterns = ['you won\'t believe', 'this will change everything', 
                         'what happens next', 'the truth about', 'doctors hate']
    clickbait_count = sum(1 for pattern in clickbait_patterns if pattern.lower() in text.lower())
    if clickbait_count > 0:
        fake_score += 0.3 + (clickbait_count * 0.1)
        explanation_parts.append("Uses clickbait language patterns")
        factors.append({
            "name": "Clickbait Patterns",
            "score": min(100, clickbait_count * 30),
            "impact": "negative",
            "description": f"Found {clickbait_count} clickbait patterns"
        })
    
    # Excessive punctuation
    if features['exclamation_count'] > 2:
        fake_score += 0.2 + (features['exclamation_count'] * 0.05)
        explanation_parts.append(f"Excessive exclamation marks ({features['exclamation_count']})")
        factors.append({
            "name": "Excessive Punctuation",
            "score": min(100, features['exclamation_count'] * 15),
            "impact": "negative",
            "description": f"{features['exclamation_count']} exclamation marks detected"
        })
    
    # ALL CAPS usage
    if features['caps_ratio'] > 0.15:
        fake_score += 0.25
        explanation_parts.append("Excessive capitalization detected")
        factors.append({
            "name": "Excessive Capitalization",
            "score": min(100, features['caps_ratio'] * 200),
            "impact": "negative",
            "description": f"{features['caps_ratio']:.1%} of text is capitalized"
        })
    
    # Emotional manipulation words
    emotional_words = ['shocking', 'terrifying', 'outrageous', 'scandal', 'exposed', 
                      'revealed', 'hidden truth', 'conspiracy', 'urgent', 'breaking']
    emotional_count = sum(1 for word in emotional_words if word.lower() in text.lower())
    if emotional_count > 1:
        fake_score += 0.2 + (emotional_count * 0.08)
        explanation_parts.append(f"High emotional manipulation language ({emotional_count} indicators)")
        factors.append({
            "name": "Emotional Manipulation",
            "score": min(100, emotional_count * 20),
            "impact": "negative",
            "description": f"Found {emotional_count} emotional manipulation words"
        })
    
    # Credible source indicators (reduce fake score)
    credible_indicators = ['according to', 'study shows', 'research indicates', 'university',
                          'published in', 'peer reviewed', 'data shows', 'statistics reveal',
                          'experts say', 'official statement']
    
    credible_count = sum(1 for indicator in credible_indicators if indicator.lower() in text.lower())
    if credible_count > 0:
        fake_score -= 0.3 + (credible_count * 0.1)
        explanation_parts.append(f"Contains {credible_count} credible source indicators")
        factors.append({
            "name": "Credible Sources",
            "score": min(100, credible_count * 25),
            "impact": "positive",
            "description": f"Found {credible_count} credible source indicators"
        })
    
    # Length analysis - improved for short texts
    if features['word_count'] < 5:
        fake_score += 0.2
        explanation_parts.append("Extremely short content (often misleading or incomplete)")
        factors.append({
            "name": "Content Length",
            "score": 80,
            "impact": "negative",
            "description": "Extremely short content"
        })
    elif features['word_count'] < 15:
        fake_score += 0.1
        explanation_parts.append("Very short content (may lack context)")
        factors.append({
            "name": "Content Length",
            "score": 60,
            "impact": "negative",
            "description": "Very short content"
        })
    elif features['word_count'] > 500:
        fake_score -= 0.1
        explanation_parts.append("Detailed content (typically more credible)")
        factors.append({
            "name": "Content Length",
            "score": 70,
            "impact": "positive",
            "description": "Detailed, comprehensive content"
        })
    
    # Readability analysis
    if features['flesch_reading_ease'] > 80:  # Very easy to read (often clickbait)
        fake_score += 0.15
        explanation_parts.append("Overly simplified language (clickbait indicator)")
        factors.append({
            "name": "Readability",
            "score": 75,
            "impact": "negative",
            "description": "Overly simplified language"
        })
    elif features['flesch_reading_ease'] < 30:  # Very hard to read
        fake_score += 0.1
        explanation_parts.append("Unnecessarily complex language")
        factors.append({
            "name": "Readability",
            "score": 60,
            "impact": "negative",
            "description": "Unnecessarily complex language"
        })
    
    # Ensure score is between 0 and 1
    fake_score = max(0, min(1, fake_score))
    
    # Determine prediction with better thresholds and confidence
    if fake_score > 0.6:
        prediction = "fake"
        confidence = max(0.65, min(0.95, fake_score))  # Ensure reasonable confidence range
    elif fake_score < 0.3:
        prediction = "real"  
        confidence = max(0.65, min(0.95, 1 - fake_score))  # Ensure reasonable confidence range
    else:
        # Borderline cases - lean towards real but with lower confidence
        prediction = "real"
        confidence = max(0.55, min(0.75, 1 - fake_score))
    
    return prediction, confidence, features, explanation_parts, factors

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
        
        print(f"🔍 Analyzing: '{text[:50]}...'")
        
        # Get prediction with detailed explanation and factors
        prediction, confidence, features, explanation_parts, factors = simple_fake_news_detection(text)
        
        # Create explanation from detection results
        if not explanation_parts:
            if prediction == "fake":
                explanation_parts.append("Text shows patterns commonly associated with misinformation")
            else:
                explanation_parts.append("Text appears to follow standard informational patterns")
        
        explanation = ". ".join(explanation_parts) + "."
        
        # Create prediction ID
        prediction_id = str(uuid.uuid4())
        
        # Prepare sources
        sources = ["https://www.snopes.com", "https://www.factcheck.org", "https://www.politifact.com"]
        
        print(f"📊 Result: {prediction} ({confidence:.3f})")
        
        # Create full response structure
        response_data = {
            "id": prediction_id,
            "prediction": prediction,
            "confidence": round(confidence, 3),
            "explanation": explanation,
            "factors": factors,
            "sources": sources,
            "timestamp": datetime.now().isoformat(),
            "input_text": text[:200] + "..." if len(text) > 200 else text,
            "input_url": None,
            "analysis_type": getattr(request, 'analysis_type', 'text'),
            "model_version": "enhanced-v2.0",
            "processing_time": 0.1
        }
        
        # Save to database with error handling
        try:
            conn = sqlite3.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            analysis_type = getattr(request, 'analysis_type', 'text')
            
            cursor.execute("""
                INSERT INTO predictions (text, prediction, confidence, analysis_type, features)
                VALUES (?, ?, ?, ?, ?)
            """, (text, prediction, confidence, analysis_type, json.dumps({
                "features": features,
                "factors": factors,
                "explanation_parts": explanation_parts
            })))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Saved to database: {prediction} for '{text[:30]}...'")
            
        except Exception as db_error:
            print(f"❌ Database error: {db_error}")
        
        return PredictionResponse(**response_data)
        
    except Exception as e:
        print(f"❌ Prediction error: {str(e)}")
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
                "text": row[1][:100] + "..." if len(row[1]) > 100 else row[1],  # Truncate long text
                "prediction": row[2],
                "confidence": row[3],
                "analysis_type": row[4] or 'text',
                "created_at": row[5],
                "features": features,
                "timestamp": row[5]  # Add timestamp field for frontend compatibility
            })
        
        print(f"📊 Returning {len(history)} history items")
        return {"history": history}
        
    except Exception as e:
        print(f"❌ History error: {str(e)}")
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
        by_prediction_results = cursor.fetchall()
        by_prediction = {}
        for pred, count in by_prediction_results:
            by_prediction[pred.upper()] = count  # Ensure uppercase for consistency
        
        # By analysis type
        cursor.execute("SELECT analysis_type, COUNT(*) FROM predictions GROUP BY analysis_type")
        by_type_results = cursor.fetchall()
        by_analysis_type = {}
        for atype, count in by_type_results:
            by_analysis_type[atype or 'text'] = count
        
        conn.close()
        
        stats = {
            "total_predictions": total,
            "by_prediction": by_prediction,
            "by_analysis_type": by_analysis_type
        }
        
        print(f"📊 Stats: {stats}")
        return stats
        
    except Exception as e:
        print(f"❌ Stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/test-db")
async def test_database():
    """Test database connection and add sample data"""
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Add a test record
        cursor.execute("""
            INSERT INTO predictions (text, prediction, confidence, analysis_type, features)
            VALUES (?, ?, ?, ?, ?)
        """, ("Test news article", "FAKE", 0.85, "text", "{}"))
        
        conn.commit()
        
        # Check if it was saved
        cursor.execute("SELECT COUNT(*) FROM predictions")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        return {"status": "success", "total_records": count, "message": "Database is working"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)