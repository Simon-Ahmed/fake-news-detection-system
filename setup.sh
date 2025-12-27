#!/bin/bash

# Fake News Detection System Setup Script
# This script sets up both frontend and backend components

set -e

echo "🚀 Fake News Detection System Setup"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if command -v docker &> /dev/null; then
        print_success "Docker is installed"
        return 0
    else
        print_error "Docker is not installed. Please install Docker first."
        return 1
    fi
}

# Check if Docker Compose is installed
check_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose is installed"
        return 0
    else
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        return 1
    fi
}

# Check if Node.js is installed (for local development)
check_node() {
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js is installed: $NODE_VERSION"
        return 0
    else
        print_warning "Node.js is not installed. Required for local development."
        return 1
    fi
}

# Check if Python is installed (for local development)
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python is installed: $PYTHON_VERSION"
        return 0
    else
        print_warning "Python 3 is not installed. Required for local development."
        return 1
    fi
}

# Setup environment files
setup_env_files() {
    print_status "Setting up environment files..."
    
    # Frontend environment
    if [ ! -f .env ]; then
        cp .env.example .env
        print_success "Frontend .env file created"
    else
        print_warning "Frontend .env file already exists"
    fi
    
    # Backend environment
    if [ ! -f backend/.env ]; then
        cp backend/.env.example backend/.env
        print_success "Backend .env file created"
    else
        print_warning "Backend .env file already exists"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p backend/logs
    mkdir -p backend/models
    
    print_success "Directories created"
}

# Docker setup
setup_docker() {
    print_status "Setting up with Docker..."
    
    # Build and start services
    print_status "Building Docker images..."
    docker-compose -f docker-compose.dev.yml build
    
    print_status "Starting services..."
    docker-compose -f docker-compose.dev.yml up -d
    
    print_success "Docker services started"
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Check backend health
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_success "Backend is healthy"
    else
        print_warning "Backend may still be starting up. Check logs with: docker-compose -f docker-compose.dev.yml logs backend"
    fi
    
    # Check frontend
    if curl -f http://localhost:3000 &> /dev/null; then
        print_success "Frontend is accessible"
    else
        print_warning "Frontend may still be starting up. Check logs with: docker-compose -f docker-compose.dev.yml logs frontend"
    fi
}

# Local development setup
setup_local() {
    print_status "Setting up for local development..."
    
    # Frontend setup
    print_status "Installing frontend dependencies..."
    npm install
    
    # Backend setup
    print_status "Setting up backend..."
    cd backend
    
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    print_status "Activating virtual environment and installing dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    cd ..
    
    print_success "Local development setup complete"
}

# Test the system
test_system() {
    print_status "Testing the system..."
    
    # Test backend
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_success "Backend API is responding"
    else
        print_error "Backend API is not responding"
        return 1
    fi
    
    # Test frontend
    if curl -f http://localhost:3000 &> /dev/null; then
        print_success "Frontend is responding"
    else
        print_error "Frontend is not responding"
        return 1
    fi
    
    print_success "System test passed"
}

# Main setup function
main() {
    echo
    print_status "Checking system requirements..."
    
    # Check requirements
    DOCKER_OK=false
    NODE_OK=false
    PYTHON_OK=false
    
    if check_docker && check_docker_compose; then
        DOCKER_OK=true
    fi
    
    if check_node; then
        NODE_OK=true
    fi
    
    if check_python; then
        PYTHON_OK=true
    fi
    
    echo
    print_status "Setting up environment..."
    setup_env_files
    create_directories
    
    echo
    print_status "Choose setup method:"
    echo "1. Docker (Recommended - requires Docker)"
    echo "2. Local Development (requires Node.js and Python)"
    echo "3. Both"
    
    read -p "Enter your choice (1-3): " choice
    
    case $choice in
        1)
            if [ "$DOCKER_OK" = true ]; then
                setup_docker
            else
                print_error "Docker is not available. Please install Docker first."
                exit 1
            fi
            ;;
        2)
            if [ "$NODE_OK" = true ] && [ "$PYTHON_OK" = true ]; then
                setup_local
            else
                print_error "Node.js and Python are required for local development."
                exit 1
            fi
            ;;
        3)
            if [ "$DOCKER_OK" = true ]; then
                setup_docker
            fi
            if [ "$NODE_OK" = true ] && [ "$PYTHON_OK" = true ]; then
                setup_local
            fi
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
    
    echo
    print_status "Setup complete! 🎉"
    echo
    echo "📋 Next steps:"
    echo
    
    if [ "$choice" = "1" ] || [ "$choice" = "3" ]; then
        echo "🐳 Docker setup:"
        echo "  • Frontend: http://localhost:3000"
        echo "  • Backend API: http://localhost:8000"
        echo "  • API Documentation: http://localhost:8000/docs"
        echo "  • View logs: docker-compose -f docker-compose.dev.yml logs"
        echo "  • Stop services: docker-compose -f docker-compose.dev.yml down"
        echo
    fi
    
    if [ "$choice" = "2" ] || [ "$choice" = "3" ]; then
        echo "💻 Local development:"
        echo "  • Start frontend: npm run dev"
        echo "  • Start backend: cd backend && source venv/bin/activate && python start.py"
        echo "  • Test backend: cd backend && python test_samples.py"
        echo
    fi
    
    echo "🧪 Test the system:"
    echo "  • Open http://localhost:3000 in your browser"
    echo "  • Try analyzing some text for fake news detection"
    echo "  • Check the Dashboard and History tabs"
    echo
    echo "📚 Documentation:"
    echo "  • API Docs: http://localhost:8000/docs"
    echo "  • README: ./README.md"
    echo "  • Backend README: ./backend/README.md"
}

# Run main function
main "$@"