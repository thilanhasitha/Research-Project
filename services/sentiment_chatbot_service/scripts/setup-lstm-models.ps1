# LSTM Multi-Model Training Quick Start
# =======================================

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "LSTM Multi-Model Training & Deployment" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "  Virtual environment not activated. Activating..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
}

# Step 1: Check datasets
Write-Host "`n Step 1: Checking datasets..." -ForegroundColor Green
$dataPath = "backend\lstm_stock_prediction\data\processed"

if (Test-Path $dataPath) {
    $csvFiles = Get-ChildItem -Path $dataPath -Filter "*.csv"
    
    if ($csvFiles.Count -gt 0) {
        Write-Host "    Found $($csvFiles.Count) dataset(s):" -ForegroundColor Green
        foreach ($file in $csvFiles) {
            Write-Host "      - $($file.Name)" -ForegroundColor White
        }
    } else {
        Write-Host "   No CSV files found in $dataPath" -ForegroundColor Red
        Write-Host "   Please add your datasets to the processed folder first." -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "   Data directory not found!" -ForegroundColor Red
    exit 1
}

# Step 2: Train models
Write-Host "`n Step 2: Training LSTM models..." -ForegroundColor Green
Write-Host "   This may take 10-30 minutes depending on data size..." -ForegroundColor Yellow

Push-Location backend\lstm_stock_prediction

try {
    python train_multi_models.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n    Training completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "`n    Training failed!" -ForegroundColor Red
        Pop-Location
        exit 1
    }
} catch {
    Write-Host "`n    Error during training: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}

Pop-Location

# Step 3: Verify models
Write-Host "`n📦 Step 3: Verifying trained models..." -ForegroundColor Green
$modelsPath = "backend\lstm_stock_prediction\models"

if (Test-Path "$modelsPath\models_metadata.json") {
    Write-Host "   ✅ Models metadata found" -ForegroundColor Green
    
    $modelFiles = Get-ChildItem -Path $modelsPath -Filter "*.h5"
    Write-Host "   ✅ Found $($modelFiles.Count) trained model(s)" -ForegroundColor Green
    
    foreach ($model in $modelFiles) {
        Write-Host "      - $($model.Name)" -ForegroundColor White
    }
} else {
    Write-Host "   ❌ Models metadata not found!" -ForegroundColor Red
    exit 1
}

# Step 4: Build and start Docker service
Write-Host "`n Step 4: Building and starting LSTM Docker service..." -ForegroundColor Green

$dockerRunning = docker ps 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "    Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

Write-Host "   Building LSTM service container..." -ForegroundColor Yellow
docker-compose build lstm-predictor

if ($LASTEXITCODE -eq 0) {
    Write-Host "    Build successful" -ForegroundColor Green
} else {
    Write-Host "    Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "   Starting LSTM service..." -ForegroundColor Yellow
docker-compose up -d lstm-predictor

if ($LASTEXITCODE -eq 0) {
    Write-Host "    Service started successfully" -ForegroundColor Green
} else {
    Write-Host "    Failed to start service!" -ForegroundColor Red
    exit 1
}

# Step 5: Wait for service to be ready
Write-Host "`n Step 5: Waiting for service to be ready..." -ForegroundColor Green

$maxAttempts = 30
$attempt = 0
$serviceReady = $false

while ($attempt -lt $maxAttempts -and -not $serviceReady) {
    Start-Sleep -Seconds 2
    $attempt++
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8002/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        
        if ($response.StatusCode -eq 200) {
            $serviceReady = $true
            Write-Host "    LSTM service is ready!" -ForegroundColor Green
        }
    } catch {
        Write-Host "    Waiting... (attempt $attempt/$maxAttempts)" -ForegroundColor Yellow
    }
}

if (-not $serviceReady) {
    Write-Host "     Service did not respond in time. Check logs with: docker logs LSTM_model" -ForegroundColor Red
}

# Step 6: Test the service
Write-Host "`n Step 6: Testing the service..." -ForegroundColor Green

try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8002/health" -Method GET
    Write-Host "    Health check passed" -ForegroundColor Green
    Write-Host "      Status: $($healthResponse.status)" -ForegroundColor White
    Write-Host "      Models loaded: $($healthResponse.model_loaded)" -ForegroundColor White
    
    # Try to get ensemble info
    $ensembleResponse = Invoke-RestMethod -Uri "http://localhost:8002/ensemble/info" -Method GET -ErrorAction SilentlyContinue
    
    if ($ensembleResponse) {
        Write-Host "    Ensemble info retrieved" -ForegroundColor Green
        Write-Host "      Number of models: $($ensembleResponse.num_models)" -ForegroundColor White
        Write-Host "      Models: $($ensembleResponse.model_names -join ', ')" -ForegroundColor White
    }
} catch {
    Write-Host "    Could not retrieve service info. Service may still be initializing." -ForegroundColor Yellow
}

# Summary
Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host " Setup Complete!" -ForegroundColor Green
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""
Write-Host "LSTM Service Information:" -ForegroundColor Cyan
Write-Host "  • Service URL: http://localhost:8002" -ForegroundColor White
Write-Host "  • API Documentation: http://localhost:8002/docs" -ForegroundColor White
Write-Host "  • Container Name: LSTM_model" -ForegroundColor White
Write-Host ""
Write-Host "Available Endpoints:" -ForegroundColor Cyan
Write-Host "  • GET  /health                - Health check" -ForegroundColor White
Write-Host "  • GET  /ensemble/info         - Ensemble information" -ForegroundColor White
Write-Host "  • GET  /ensemble/models       - List all models" -ForegroundColor White
Write-Host "  • POST /predict/ensemble      - Make ensemble predictions" -ForegroundColor White
Write-Host "  • POST /query/predict         - Natural language queries" -ForegroundColor White
Write-Host ""
Write-Host "Backend Integration:" -ForegroundColor Cyan
Write-Host "  • GET  /api/lstm/health       - Check LSTM service" -ForegroundColor White
Write-Host "  • GET  /api/lstm/models       - List available models" -ForegroundColor White
Write-Host "  • POST /api/lstm/predict      - Stock predictions" -ForegroundColor White
Write-Host "  • POST /api/lstm/query        - User queries" -ForegroundColor White
Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Cyan
Write-Host "  • View logs:    docker logs LSTM_model" -ForegroundColor White
Write-Host "  • Stop service: docker-compose stop lstm-predictor" -ForegroundColor White
Write-Host "  • Restart:      docker-compose restart lstm-predictor" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Test predictions using the API endpoints" -ForegroundColor White
Write-Host "  2. Integrate with your frontend/chatbot" -ForegroundColor White
Write-Host "  3. Monitor model performance" -ForegroundColor White
Write-Host "  4. Retrain periodically with new data" -ForegroundColor White
Write-Host ""
Write-Host " For detailed documentation, see: README files\LSTM_MULTI_MODEL_GUIDE.md" -ForegroundColor Yellow
Write-Host ""
