# 🤖 Fake News Detection Backend

A comprehensive, production-ready backend system for fake news detection using machine learning with FastAPI, BERT, and advanced feature engineering.

## 🚀 Features

- **Advanced ML Pipeline**: Pre-trained BERT model + feature engineering
- **Real-time Predictions**: < 2s response time for single predictions
- **Batch Processing**: Handle up to 50 texts simultaneously
- **URL Analysis**: Scrape and analyze news articles from URLs
- **User Feedback**: Collect feedback for model improvement
- **Comprehensive API**: RESTful endpoints with OpenAPI documentation
- **Production Ready**: Docker, health checks, monitoring, error handling
- **Fallback System**: Rule-based fallback when ML models fail

## 📋 API Endpoints

### Core Prediction Endpoints
- `POST /api/predict` - Analyze single text
- `POST /api/predict/url` - Analyze article from URL
- `POST /api/batch-predict` - Analyze multiple texts

### Feedback & History
- `POST /api/feedback` - Submit user corrections
- `GET /api/history` - Get prediction history (paginated)

### Monitoring & Admin
- `GET /api/stats` - System statistics
- `GET /api/health` - Health check
- `POST /api/admin/retrain` - Trigger model retraining

## 🛠️ Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone and setup
git clone <repository>
cd backend

# Copy environment file
cp .env.example .env

# Run with Docker Compose (Production)
docker-compose up --build

# Or run development version
docker-compose -f docker-compose.dev.yml up --build
```

### Option 2: Local Development

```bash
# Setup Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Test the API

```bash
# Health check
curl http://localhost:8000/health

# Test prediction
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Breaking: Aliens land in New York City! Government hiding truth!",
    "language": "en"
  }'

# Test URL prediction
curl -X POST "http://localhost:8000/api/predict/url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example-news-site.com/article",
    "language": "en"
  }'

# Submit feedback
curl -X POST "http://localhost:8000/api/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "prediction_id": "your-prediction-id",
    "user_correction": "real",
    "comment": "This is actually legitimate news"
  }'
```

## 📊 Sample Response

```json
{
  "id": "uuid-here",
  "prediction": "fake",
  "confidence": 87.5,
  "explanation": "This text appears to be fake news with 87.5% confidence. Key concerns include clickbait language, excessive exclamation.",
  "factors": [
    {
      "name": "Clickbait Language",
      "score": 75.0,
      "impact": "negative",
      "description": "Contains clickbait phrases (score: 75.0/100)"
    }
  ],
  "sources": [
    "https://www.snopes.com",
    "https://www.factcheck.org"
  ],
  "timestamp": "2024-01-01T12:00:00Z",
  "input_text": "Breaking: Aliens land in New York...",
  "model_version": "bert-fake-news-v1.0",
  "processing_time": 1.234
}
```

## 🏗️ Architecture

### ML Pipeline
1. **Text Preprocessing**: Cleaning, validation, BERT tokenization
2. **Feature Extraction**: 25+ linguistic and statistical features
3. **BERT Inference**: Pre-trained model for semantic analysis
4. **Feature Combination**: Combine BERT + traditional ML features
5. **Explanation Generation**: Human-readable explanations

### Key Components
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: Database ORM with SQLite/PostgreSQL support
- **Transformers**: Hugging Face BERT model
- **NLTK**: Natural language processing
- **BeautifulSoup**: Web scraping for URL analysis
- **Docker**: Containerization and deployment

## 🔧 Configuration

### Environment Variables

```bash
DATABASE_URL=sqlite:///./fake_news.db  # or PostgreSQL URL
REDIS_URL=redis://localhost:6379
MODEL_PATH=./ml_models/bert_fake_news
HUGGINGFACE_TOKEN=your_token_here
API_KEY=your_api_key_here
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Database Schema

- **predictions**: Store all predictions with features and results
- **feedback**: User corrections for model improvement
- **model_versions**: Track different ML model versions
- **prediction_analytics**: Usage statistics

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_api.py
pytest tests/test_ml.py

# Run with coverage
pytest --cov=app tests/
```

## 📈 Performance

- **Response Time**: < 2 seconds for single prediction
- **Throughput**: 100+ requests/minute
- **Model Accuracy**: > 85% on test data
- **Memory Usage**: < 2GB RAM for ML model
- **CPU Optimized**: No GPU required

## 🔍 ML Model Details

### Primary Model
- **BERT**: `mrm8488/bert-tiny-finetuned-fake-news-detection`
- **Framework**: PyTorch + Transformers
- **Input**: Max 512 tokens
- **Output**: Binary classification (Real/Fake)

### Feature Engineering (25+ Features)
1. **Readability**: Flesch scores, complexity metrics
2. **Clickbait**: Pattern detection, emotional triggers
3. **Bias Indicators**: Absolute terms, loaded language
4. **Source Citations**: References, URLs, credibility
5. **Style Analysis**: Vocabulary diversity, sentence structure

### Fallback System
- Rule-based classifier when BERT fails
- Feature-based scoring system
- Graceful degradation

## 🚀 Deployment

### Production Deployment

```bash
# Build and deploy with Docker
docker-compose up -d

# Scale the API service
docker-compose up -d --scale api=3

# View logs
docker-compose logs -f api
```

### Health Monitoring

- **Health Endpoint**: `/api/health`
- **Metrics**: Response times, error rates, model status
- **Alerts**: Configurable for model drift, high error rates
- **Logging**: Structured JSON logs

## 🔄 Model Retraining

The system supports online learning through user feedback:

```bash
# Trigger retraining
curl -X POST "http://localhost:8000/api/admin/retrain" \
  -H "Content-Type: application/json" \
  -d '{
    "trigger": "manual",
    "epochs": 3,
    "learning_rate": 0.00002
  }'
```

## 📚 API Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **ReDoc**: http://localhost:8000/redoc

## 🛡️ Security

- Input validation and sanitization
- Rate limiting (configurable)
- SQL injection prevention via ORM
- Model integrity validation
- CORS configuration for frontend integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

1. **Model Loading Fails**
   - Check internet connection for Hugging Face downloads
   - Verify disk space for model files
   - Check logs: `docker-compose logs api`

2. **Database Connection Issues**
   - Verify DATABASE_URL in .env
   - Check PostgreSQL service: `docker-compose ps`
   - Reset database: `docker-compose down -v && docker-compose up`

3. **High Memory Usage**
   - Monitor with: `docker stats`
   - Adjust batch sizes in code
   - Consider using BERT-tiny model

4. **Slow Predictions**
   - Check CPU usage
   - Verify model is using CPU (not waiting for GPU)
   - Monitor with `/api/stats` endpoint

### Support

- Check the [Issues](link-to-issues) page
- Review logs: `docker-compose logs -f`
- Enable debug logging: Set `LOG_LEVEL=DEBUG`

---

**Built with ❤️ for accurate news detection**