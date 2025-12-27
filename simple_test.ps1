Write-Host "Testing Services..." -ForegroundColor Green

# Test Backend Health
Write-Host "Testing Backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "Backend OK - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "Backend Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Frontend
Write-Host "Testing Frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -TimeoutSec 5
    Write-Host "Frontend OK - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "Frontend Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Test Complete!" -ForegroundColor Green