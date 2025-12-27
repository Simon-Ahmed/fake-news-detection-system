from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime

from .database import engine, Base
from .routes import predictions, feedback, admin
from .schemas import ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Fake News Detection API")
    yield
    # Shutdown
    logger.info("Shutting down Fake News Detection API")

# Create FastAPI app
app = FastAPI(
    title="Fake News Detection API",
    description="A comprehensive API for detecting fake news using machine learning",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predictions.router)
app.include_router(feedback.router)
app.include_router(admin.router)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Fake News Detection API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "predict": "/api/predict",
            "predict_url": "/api/predict/url",
            "batch_predict": "/api/batch-predict",
            "feedback": "/api/feedback",
            "history": "/api/history",
            "stats": "/api/stats",
            "health": "/api/health"
        },
        "documentation": "/docs"
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=True,
            message=exc.detail,
            code=f"HTTP_{exc.status_code}",
            timestamp=datetime.utcnow(),
            suggestion="Check the API documentation at /docs for correct usage"
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=True,
            message="Internal server error",
            code="INTERNAL_ERROR",
            timestamp=datetime.utcnow(),
            suggestion="Please try again later or contact support"
        ).dict()
    )

# Health check endpoint (duplicate for convenience)
@app.get("/health")
async def simple_health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "fake-news-detection-api"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )