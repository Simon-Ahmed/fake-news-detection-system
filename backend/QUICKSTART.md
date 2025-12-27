# 🚀 Quick Start Guide

## Fastest Setup (Docker)

```bash
cd backend
cp .env.example .env
docker-compose -f docker-compose.dev.yml up --build
```

**API will be available at: http://localhost:8000**

## Local Development Setup

```bash
cd backend

# Run setup script
python setup.py

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Start server
python start.py
```

## Test the API

```bash
# Run test suite
python test_samples.py

# Or test manually
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "SHOCKING! You won'\''t believe this amazing discovery!"}'
```

## Key Endpoints

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Predict Text**: `POST /api/predict`
- **Predict URL**: `POST /api/predict/url`
- **Batch Predict**: `POST /api/batch-predict`
- **Submit Feedback**: `POST /api/feedback`
- **View History**: `GET /api/history`
- **System Stats**: `GET /api/stats`

## Sample Request

```json
{
  "text": "According to a new study, coffee reduces heart disease risk by 15%.",
  "language": "en"
}
```

## Sample Response

```json
{
  "id": "uuid-here",
  "prediction": "real",
  "confidence": 78.5,
  "explanation": "This text appears to be legitimate news with 78.5% confidence. Positive indicators include source citations.",
  "factors": [
    {
      "name": "Source Citations",
      "score": 1,
      "impact": "positive",
      "description": "Contains 1 citations and 0 URLs"
    }
  ],
  "sources": ["https://www.snopes.com", "https://www.factcheck.org"],
  "timestamp": "2024-01-01T12:00:00Z",
  "model_version": "bert-fake-news-v1.0"
}
```

## Troubleshooting

**Model not loading?**
- Check internet connection (downloads BERT model)
- Wait 30-60 seconds for first startup
- Check logs: `docker-compose logs api`

**Connection refused?**
- Ensure port 8000 is available
- Check if server started: `curl http://localhost:8000/health`

**Dependencies issues?**
- Use Python 3.8+
- Run: `pip install -r requirements.txt`

## Production Deployment

```bash
# Full production stack
docker-compose up -d

# Scale API instances
docker-compose up -d --scale api=3
```

---

**Ready to detect fake news! 🕵️‍♂️**