#!/usr/bin/env python3
"""
Startup script for the Fake News Detection API
This script handles initialization and starts the server
"""

import os
import sys
import logging
import uvicorn
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def setup_logging():
    """Setup logging configuration"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/app.log') if os.path.exists('logs') else logging.NullHandler()
        ]
    )

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'models']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Directory '{directory}' ready")

def check_environment():
    """Check environment setup"""
    print("🔍 Checking environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check required packages
    try:
        import fastapi
        import transformers
        import torch
        import sqlalchemy
        print("✅ Required packages installed")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Check environment file
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found, using defaults")
        print("   Copy .env.example to .env for custom configuration")
    else:
        print("✅ Environment file found")

def main():
    """Main startup function"""
    print("🚀 Starting Fake News Detection API")
    print("=" * 50)
    
    # Setup
    check_environment()
    create_directories()
    setup_logging()
    
    # Get configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    
    print(f"🌐 Server will start on http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔄 Auto-reload: {'enabled' if reload else 'disabled'}")
    print("=" * 50)
    
    # Start the server
    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=os.getenv("LOG_LEVEL", "info").lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()