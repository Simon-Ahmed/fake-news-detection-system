#!/usr/bin/env python3
"""
Setup script for the Fake News Detection Backend
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def setup_virtual_environment():
    """Setup Python virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("🔄 Creating virtual environment...")
    if run_command(f"{sys.executable} -m venv venv", "Virtual environment creation"):
        print("✅ Virtual environment created")
        return True
    return False

def install_dependencies():
    """Install Python dependencies"""
    # Determine pip command based on OS
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/Mac
        pip_cmd = "venv/bin/pip"
    
    commands = [
        (f"{pip_cmd} install --upgrade pip", "Upgrading pip"),
        (f"{pip_cmd} install -r requirements.txt", "Installing dependencies")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = ["logs", "models", "tests"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Directory '{directory}' created")

def setup_environment_file():
    """Setup environment configuration"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ .env file created from .env.example")
        print("   Edit .env file to customize configuration")
    else:
        print("⚠️  .env.example not found, creating basic .env file")
        with open(env_file, 'w') as f:
            f.write("""DATABASE_URL=sqlite:///./fake_news.db
ENVIRONMENT=development
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
""")
        print("✅ Basic .env file created")

def run_tests():
    """Run basic tests to verify setup"""
    print("🧪 Running basic tests...")
    
    # Determine python command for virtual environment
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/Mac
        python_cmd = "venv/bin/python"
    
    # Test imports
    test_command = f'{python_cmd} -c "import fastapi, transformers, torch, sqlalchemy; print(\\"All imports successful\\")"'
    
    if run_command(test_command, "Testing package imports"):
        print("✅ All required packages are working")
        return True
    else:
        print("⚠️  Some packages may not be working correctly")
        return False

def main():
    """Main setup function"""
    print("🚀 Fake News Detection Backend Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("Virtual Environment", setup_virtual_environment),
        ("Dependencies", install_dependencies),
        ("Directories", create_directories),
        ("Environment File", setup_environment_file),
        ("Package Tests", run_tests)
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        print(f"\n📋 Setting up {step_name}...")
        if not step_function():
            failed_steps.append(step_name)
    
    print("\n" + "=" * 50)
    
    if failed_steps:
        print("⚠️  Setup completed with some issues:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nYou may need to fix these issues manually.")
    else:
        print("🎉 Setup completed successfully!")
    
    print("\n📋 Next steps:")
    print("1. Activate virtual environment:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix/Linux/Mac
        print("   source venv/bin/activate")
    
    print("2. Start the server:")
    print("   python start.py")
    print("   # or")
    print("   uvicorn app.main:app --reload")
    
    print("3. Test the API:")
    print("   python test_samples.py")
    
    print("4. View documentation:")
    print("   http://localhost:8000/docs")
    
    print("\n🐳 Docker alternative:")
    print("   docker-compose -f docker-compose.dev.yml up --build")

if __name__ == "__main__":
    main()