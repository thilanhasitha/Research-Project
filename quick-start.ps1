# Quick Start Script for Windows PowerShell
# Run this to set up and test the RSS news system

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host " RSS News Collection System - Quick Start" -ForegroundColor Green
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Docker
Write-Host "1️  Checking Docker..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    Write-Host "    Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "    Docker not found. Please install Docker Desktop" -ForegroundColor Red
    exit 1
}

# Step 2: Start services
Write-Host ""
Write-Host "2️  Starting services..." -ForegroundColor Yellow
Write-Host "   This may take a few minutes on first run..." -ForegroundColor Gray
docker-compose up -d

Start-Sleep -Seconds 5

# Step 3: Check services
Write-Host ""
Write-Host "3️  Checking service status..." -ForegroundColor Yellow
$services = docker-compose ps --format json | ConvertFrom-Json
foreach ($service in $services) {
    if ($service.State -eq "running") {
        Write-Host "    $($service.Service)" -ForegroundColor Green
    } else {
        Write-Host "    $($service.Service) - $($service.State)" -ForegroundColor Red
    }
}

# Step 4: Wait for services to be ready
Write-Host ""
Write-Host "4️  Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Step 5: Pull Ollama model
Write-Host ""
Write-Host "5️  Checking Ollama model..." -ForegroundColor Yellow
$modelName = "llama3.2"

try {
    $models = docker exec ollama_new ollama list 2>&1
    if ($models -match $modelName) {
        Write-Host "    Model $modelName is available" -ForegroundColor Green
    } else {
        Write-Host "    Pulling model $modelName (this will take several minutes)..." -ForegroundColor Yellow
        docker exec ollama_new ollama pull $modelName
        Write-Host "    Model downloaded successfully" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠️  Could not check Ollama model: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "   You may need to pull it manually: docker exec ollama_new ollama pull $modelName" -ForegroundColor Gray
}

# Step 6: Test backend
Write-Host ""
Write-Host "6️  Testing backend API..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "    Backend is responding" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠️  Backend not ready yet, waiting..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8001/" -TimeoutSec 5
        Write-Host "    Backend is now responding" -ForegroundColor Green
    } catch {
        Write-Host "    Backend not responding. Check logs: docker-compose logs backend" -ForegroundColor Red
    }
}

# Step 7: Run test
Write-Host ""
Write-Host "7️⃣  Running system test..." -ForegroundColor Yellow
Write-Host "   This will test MongoDB, Ollama, and RSS processing..." -ForegroundColor Gray
Write-Host ""

docker exec -it research_backend python test_rss_flow.py

# Summary
Write-Host ""
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host " Next Steps" -ForegroundColor Green
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""
Write-Host " Services are running! You can now:" -ForegroundColor Green
Write-Host ""
Write-Host "   • Test API:          " -NoNewline; Write-Host "Invoke-WebRequest http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host "   • Collect news:      " -NoNewline; Write-Host "Invoke-WebRequest http://localhost:8001/rss/collect" -ForegroundColor Cyan
Write-Host "   • Get latest news:   " -NoNewline; Write-Host "Invoke-WebRequest http://localhost:8001/rss/latest" -ForegroundColor Cyan
Write-Host "   • View logs:         " -NoNewline; Write-Host "docker-compose logs -f backend" -ForegroundColor Cyan
Write-Host "   • Stop services:     " -NoNewline; Write-Host "docker-compose down" -ForegroundColor Cyan
Write-Host ""
Write-Host " Documentation: See SETUP_GUIDE.md for detailed instructions" -ForegroundColor Gray
Write-Host ""
