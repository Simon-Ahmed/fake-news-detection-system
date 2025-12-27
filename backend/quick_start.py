#!/usr/bin/env python3
"""
Quick startup script for testing backend connection
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Start the server quickly for testing"""
    print("🚀 Quick starting Fake News Detection API for testing...")
    
    # Set environment to avoid heavy ML loading
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["SKIP_ML_INIT"] = "true"
    
    # Start the server
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()