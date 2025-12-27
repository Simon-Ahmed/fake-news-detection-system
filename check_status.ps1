Write-Host "🔍 Checking System Status..." -ForegroundColor Green

# Check if processes are running
Write-Host "`n📊 Process Status:" -ForegroundColor Yellow
$frontendProcess = Get-Process -Name "node" -ErrorAction SilentlyContinue
$backendProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue

if ($frontendProcess) {
    Write-Host "✅ Frontend process running (Node.js)" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend process not found" -ForegroundColor Red
}

if ($backendProcess) {
    Write-Host "✅ Backend process running (Python)" -ForegroundColor Green
} else {
    Write-Host "❌ Backend process not found" -ForegroundColor Red
}

# Check ports
Write-Host "`n🌐 Port Status:" -ForegroundColor Yellow
$frontend = Test-NetConnection -ComputerName localhost -Port 5173 -InformationLevel Quiet -WarningAction SilentlyContinue
$backend = Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet -WarningAction SilentlyContinue

if ($frontend) {
    Write-Host "✅ Frontend port 5173 is open" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend port 5173 is not accessible" -ForegroundColor Red
}

if ($backend) {
    Write-Host "✅ Backend port 8000 is open" -ForegroundColor Green
} else {
    Write-Host "❌ Backend port 8000 is not accessible" -ForegroundColor Red
}

Write-Host "`n🎯 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Open http://localhost:5173 in your browser"
Write-Host "2. Try analyzing some text"
Write-Host "3. If it still doesn't work, open test_connection.html in your browser"