Write-Host "🧪 Testing Fake News Detection System Services" -ForegroundColor Green
Write-Host "=" * 50

# Test Backend
Write-Host "`n🔧 Testing Backend (http://localhost:8000)..." -ForegroundColor Yellow
try {
    $backendResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Backend is running! Status: $($backendResponse.StatusCode)" -ForegroundColor Green
    Write-Host "   Response: $($backendResponse.Content.Substring(0, [Math]::Min(100, $backendResponse.Content.Length)))..."
} catch {
    Write-Host "❌ Backend not responding: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Frontend
Write-Host "`n🎨 Testing Frontend (http://localhost:5173)..." -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Frontend is running! Status: $($frontendResponse.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend not responding: $($_.Exception.Message)" -ForegroundColor Red
}

# Test API Endpoint
Write-Host "`n🤖 Testing API Prediction Endpoint..." -ForegroundColor Yellow
try {
    $testData = @{
        text = "This is a test news article to check if the API is working properly."
        language = "en"
    } | ConvertTo-Json

    $apiResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/predict" -Method POST -Body $testData -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
    Write-Host "✅ API is working! Status: $($apiResponse.StatusCode)" -ForegroundColor Green
    
    $result = $apiResponse.Content | ConvertFrom-Json
    $confidence = $result.confidence
    Write-Host "   Prediction: $($result.prediction) ($confidence% confidence)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ API not responding: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 Service Test Complete!" -ForegroundColor Green
Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
Write-Host "   • Open http://localhost:5173 in your browser"
Write-Host "   • Try the fake news detection interface"
Write-Host "   • Check API docs at http://localhost:8000/docs"