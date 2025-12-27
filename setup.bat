@echo off
setlocal enabledelayedexpansion

echo 🚀 Fake News Detection System Setup
echo ====================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
) else (
    echo [SUCCESS] Docker is installed
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
) else (
    echo [SUCCESS] Docker Compose is installed
)

echo.
echo [INFO] Setting up environment files...

REM Setup frontend environment
if not exist .env (
    copy .env.example .env >nul
    echo [SUCCESS] Frontend .env file created
) else (
    echo [WARNING] Frontend .env file already exists
)

REM Setup backend environment
if not exist backend\.env (
    copy backend\.env.example backend\.env >nul
    echo [SUCCESS] Backend .env file created
) else (
    echo [WARNING] Backend .env file already exists
)

echo.
echo [INFO] Creating necessary directories...
if not exist backend\logs mkdir backend\logs
if not exist backend\models mkdir backend\models
echo [SUCCESS] Directories created

echo.
echo [INFO] Building Docker images...
docker-compose -f docker-compose.dev.yml build

if %errorlevel% neq 0 (
    echo [ERROR] Failed to build Docker images
    pause
    exit /b 1
)

echo.
echo [INFO] Starting services...
docker-compose -f docker-compose.dev.yml up -d

if %errorlevel% neq 0 (
    echo [ERROR] Failed to start services
    pause
    exit /b 1
)

echo.
echo [INFO] Waiting for services to be ready...
timeout /t 30 /nobreak >nul

echo.
echo [INFO] Testing services...

REM Test backend (using PowerShell for HTTP request)
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing | Out-Null; Write-Host '[SUCCESS] Backend is healthy' } catch { Write-Host '[WARNING] Backend may still be starting up' }"

REM Test frontend
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:3000' -UseBasicParsing | Out-Null; Write-Host '[SUCCESS] Frontend is accessible' } catch { Write-Host '[WARNING] Frontend may still be starting up' }"

echo.
echo ====================================
echo 🎉 Setup complete!
echo.
echo 📋 Next steps:
echo.
echo 🐳 Your services are running:
echo   • Frontend: http://localhost:3000
echo   • Backend API: http://localhost:8000
echo   • API Documentation: http://localhost:8000/docs
echo.
echo 🛠️ Useful commands:
echo   • View logs: docker-compose -f docker-compose.dev.yml logs
echo   • Stop services: docker-compose -f docker-compose.dev.yml down
echo   • Restart services: docker-compose -f docker-compose.dev.yml restart
echo.
echo 🧪 Test the system:
echo   • Open http://localhost:3000 in your browser
echo   • Try analyzing some text for fake news detection
echo   • Check the Dashboard and History tabs
echo.
echo Press any key to open the application in your browser...
pause >nul

REM Open browser
start http://localhost:3000

echo.
echo Happy fake news detecting! 🕵️‍♂️
pause