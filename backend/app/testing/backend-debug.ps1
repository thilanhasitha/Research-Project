# Backend Startup Troubleshooting Script
# Run this with: docker-compose restart backend && docker-compose logs -f backend

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host " Backend Service Troubleshooting" -ForegroundColor Yellow
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if container exists
Write-Host "1️  Checking backend container..." -ForegroundColor Yellow
$container = docker ps -a --filter "name=research_backend" --format "{{.Status}}"
if ($container) {
    Write-Host "   Container status: $container" -ForegroundColor Gray
    if ($container -like "*Up*") {
        Write-Host "    Container is running" -ForegroundColor Green
    } else {
        Write-Host "     Container exists but not running" -ForegroundColor Yellow
    }
} else {
    Write-Host "    Container doesn't exist" -ForegroundColor Red
    Write-Host "   Run: docker-compose up -d" -ForegroundColor Gray
    exit
}

# Step 2: Check logs for errors
Write-Host ""
Write-Host "2️  Checking recent logs..." -ForegroundColor Yellow
$logs = docker logs research_backend --tail 30 2>&1
$hasError = $false

if ($logs -match "error|Error|ERROR|failed|Failed|FAILED|exception|Exception") {
    Write-Host "     Errors found in logs:" -ForegroundColor Red
    $logs -split "`n" | Where-Object { $_ -match "error|Error|ERROR|failed|Failed|exception|Exception" } | ForEach-Object {
        Write-Host "      $_" -ForegroundColor Red
    }
    $hasError = $true
} else {
    Write-Host "    No obvious errors in recent logs" -ForegroundColor Green
}

# Step 3: Check if FastAPI is responding
Write-Host ""
Write-Host "3️  Testing backend API..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "    Backend is responding!" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "    Backend not responding" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 4: Run diagnostic inside container
Write-Host ""
Write-Host "4️  Running internal diagnostics..." -ForegroundColor Yellow
Write-Host "   (This checks Python imports and configuration)" -ForegroundColor Gray
Write-Host ""
docker exec research_backend python diagnose.py 2>&1

# Step 5: Check dependencies
Write-Host ""
Write-Host "5️  Checking MongoDB connection..." -ForegroundColor Yellow
$mongoStatus = docker ps --filter "name=research_mongo" --format "{{.Status}}"
if ($mongoStatus -like "*Up*") {
    Write-Host "    MongoDB container is running" -ForegroundColor Green
} else {
    Write-Host "    MongoDB container is not running" -ForegroundColor Red
}

Write-Host ""
Write-Host "6️  Checking Ollama connection..." -ForegroundColor Yellow
$ollamaStatus = docker ps --filter "name=ollama" --format "{{.Status}}"
if ($ollamaStatus -like "*Up*") {
    Write-Host "    Ollama container is running" -ForegroundColor Green
    
    # Check if model is pulled
    $models = docker exec ollama_new ollama list 2>&1
    if ($models -match "llama3") {
        Write-Host "    Ollama model is available" -ForegroundColor Green
    } else {
        Write-Host "     Ollama model may not be pulled" -ForegroundColor Yellow
        Write-Host "   Run: docker exec ollama_new ollama pull llama3.2" -ForegroundColor Gray
    }
} else {
    Write-Host "    Ollama container is not running" -ForegroundColor Red
}

# Summary and recommendations
Write-Host ""
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host " Summary & Next Steps" -ForegroundColor Green
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

if (-not $hasError) {
    Write-Host " No major issues detected!" -ForegroundColor Green
    Write-Host ""
    Write-Host "If backend still not working, try:" -ForegroundColor Yellow
    Write-Host "   1. View full logs:    docker-compose logs backend" -ForegroundColor Cyan
    Write-Host "   2. Restart service:   docker-compose restart backend" -ForegroundColor Cyan
    Write-Host "   3. Rebuild:           docker-compose up --build -d backend" -ForegroundColor Cyan
} else {
    Write-Host "  Issues detected. Common fixes:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host " Fix #1: Missing Dependencies" -ForegroundColor Yellow
    Write-Host "   docker-compose exec backend pip install -r requirements.txt" -ForegroundColor Cyan
    Write-Host "   docker-compose restart backend" -ForegroundColor Cyan
    Write-Host ""
    Write-Host " Fix #2: Rebuild Container" -ForegroundColor Yellow
    Write-Host "   docker-compose down" -ForegroundColor Cyan
    Write-Host "   docker-compose up --build -d" -ForegroundColor Cyan
    Write-Host ""
    Write-Host " Fix #3: Check Environment Variables" -ForegroundColor Yellow
    Write-Host "   docker-compose exec backend printenv | Select-String MONGO" -ForegroundColor Cyan
    Write-Host "   docker-compose exec backend printenv | Select-String OLLAMA" -ForegroundColor Cyan
    Write-Host ""
    Write-Host " Fix #4: Clean Restart" -ForegroundColor Yellow
    Write-Host "   docker-compose down -v" -ForegroundColor Cyan
    Write-Host "   docker-compose up --build -d" -ForegroundColor Cyan
}

Write-Host ""
Write-Host " View detailed logs:" -ForegroundColor Gray
Write-Host "   docker-compose logs -f backend" -ForegroundColor Cyan
Write-Host ""
