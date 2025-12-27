# 🕵️‍♂️ Fake News Detection System

A complete, production-ready fake news detection system with AI-powered analysis, featuring a modern React frontend and FastAPI backend with machine learning capabilities.

## 🚀 Quick Start

### Option 1: One-Click Setup (Recommended)

**Windows:**
```bash
setup.bat
```

**Mac/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

**Manual Docker Setup:**
```bash
# Copy environment files
cp .env.example .env
cp backend/.env.example backend/.env

# Start the system
docker-compose -f docker-compose.dev.yml up --build
```

**Access the application:**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎯 Features

### Frontend (React + TypeScript)
- **Modern UI**: Clean, responsive design with dark/light theme
- **Real-time Analysis**: Instant fake news detection with confidence scores
- **URL Analysis**: Scrape and analyze articles from web URLs
- **Detailed Results**: Human-readable explanations with contributing factors
- **History Tracking**: View and manage analysis history
- **Performance Dashboard**: System statistics and model performance
- **User Feedback**: Submit corrections to improve the model

### Backend (FastAPI + ML)
- **Advanced ML Pipeline**: BERT transformer + 25+ linguistic features
- **Real-time Inference**: < 2s response time for predictions
- **Batch Processing**: Analyze up to 50 texts simultaneously
- **URL Scraping**: Extract and analyze content from web articles
- **User Feedback System**: Collect corrections for model improvement
- **Comprehensive API**: RESTful endpoints with OpenAPI documentation
- **Production Ready**: Docker, health checks, monitoring, error handling

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐
│   React Frontend│ ◄──────────────► │  FastAPI Backend│
│   (Port 3000)   │                 │   (Port 8000)   │
└─────────────────┘                 └─────────────────┘
         │                                    │
         │                                    │
    ┌────▼────┐                          ┌────▼────┐
    │ Modern  │                          │   ML    │
    │   UI    │                          │ Pipeline│
    │Components│                          │ (BERT)  │
    └─────────┘                          └─────────┘
                                              │
                                         ┌────▼────┐
                                         │Database │
                                         │(SQLite) │
                                         └─────────┘
```

## 📊 ML Model Details

### Primary Model
- **BERT**: `mrm8488/bert-tiny-finetuned-fake-news-detection`
- **Framework**: PyTorch + Transformers
- **Accuracy**: >85% on test datasets
- **Response Time**: <2 seconds

### Feature Engineering (25+ Features)
1. **Clickbait Detection**: Pattern matching for sensational language
2. **Emotional Analysis**: Sentiment and emotional intensity scoring
3. **Bias Indicators**: Absolutist language and loaded terms
4. **Source Citations**: Reference and credibility analysis
5. **Readability Metrics**: Flesch scores and complexity analysis
6. **Style Analysis**: Vocabulary diversity and sentence structure

### Fallback System
- Rule-based classifier when ML models fail
- Graceful degradation with explanations
- Continuous availability

## 🛠️ Development

### Local Development Setup

**Frontend:**
```bash
npm install
npm run dev
```

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python start.py
```

### Testing

**Frontend:**
```bash
npm test
npm run test:e2e
```

**Backend:**
```bash
cd backend
pytest
python test_samples.py
```

## 📋 API Endpoints

### Core Prediction
- `POST /api/predict` - Analyze single text
- `POST /api/predict/url` - Analyze article from URL
- `POST /api/batch-predict` - Analyze multiple texts

### User Interaction
- `POST /api/feedback` - Submit user corrections
- `GET /api/history` - Get prediction history

### System Monitoring
- `GET /api/stats` - System statistics
- `GET /api/health` - Health check
- `POST /api/admin/retrain` - Trigger model retraining

## 🧪 Sample Usage

### Text Analysis
```bash
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "SHOCKING! You won'\''t believe this amazing discovery!",
    "language": "en"
  }'
```

### URL Analysis
```bash
curl -X POST "http://localhost:8000/api/predict/url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example-news-site.com/article",
    "language": "en"
  }'
```

### Response Format
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
  "sources": ["https://www.snopes.com", "https://www.factcheck.org"],
  "timestamp": "2024-01-01T12:00:00Z",
  "modelVersion": "bert-fake-news-v1.0"
}
```

## 🚀 Deployment

### Production Deployment
```bash
# Full production stack
docker-compose up -d

# Scale API instances
docker-compose up -d --scale backend=3
```

### Environment Variables

**Frontend (.env):**
```bash
VITE_API_URL=http://localhost:8000
VITE_NODE_ENV=production
```

**Backend (backend/.env):**
```bash
DATABASE_URL=sqlite:///./fake_news.db
ENVIRONMENT=production
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here
```

## 📈 Performance

- **Response Time**: < 2 seconds for single prediction
- **Throughput**: 100+ requests/minute
- **Model Accuracy**: > 85% on test data
- **Memory Usage**: < 2GB RAM for ML model
- **Uptime**: 99.9% target availability

## 🔧 Configuration

### Model Configuration
- Confidence thresholds: Adjustable per use case
- Feature weights: Customizable importance scoring
- Fallback rules: Configurable rule-based backup

### System Configuration
- Rate limiting: Configurable per IP/user
- Batch sizes: Adjustable for performance
- Cache settings: Redis integration available

## 🛡️ Security

- **Input Validation**: Comprehensive sanitization
- **Rate Limiting**: Prevent abuse and overload
- **CORS Configuration**: Secure cross-origin requests
- **SQL Injection Prevention**: ORM-based queries
- **Model Security**: Integrity validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**Backend not starting:**
- Check if port 8000 is available
- Verify Python dependencies: `pip install -r backend/requirements.txt`
- Check logs: `docker-compose logs backend`

**Frontend not loading:**
- Check if port 3000 is available
- Verify Node.js version (18+)
- Check environment variables in `.env`

**Model loading fails:**
- Ensure internet connection (downloads BERT model)
- Check disk space (model files ~500MB)
- Wait 60 seconds for first startup

**API connection errors:**
- Verify backend is running: `curl http://localhost:8000/health`
- Check CORS settings in backend
- Verify API URL in frontend `.env`

### Getting Help

- **Issues**: [GitHub Issues](link-to-issues)
- **Discussions**: [GitHub Discussions](link-to-discussions)
- **Documentation**: `/docs` endpoints
- **Logs**: `docker-compose logs -f`

## 🙏 Acknowledgments

- **Hugging Face**: Pre-trained BERT models
- **FastAPI**: Modern Python web framework
- **React**: Frontend framework
- **Transformers**: ML model library
- **shadcn/ui**: UI component library

---

**Built with ❤️ for combating misinformation**

*This system is designed for educational and research purposes. Always verify important information through multiple trusted sources.*
