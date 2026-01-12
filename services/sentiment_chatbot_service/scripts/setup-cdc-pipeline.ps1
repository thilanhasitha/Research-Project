# Setup script for MongoDB CDC to Weaviate pipeline
# This script registers the Debezium connector and verifies the setup

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "MongoDB CDC to Weaviate Setup" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Wait for Kafka Connect to be ready
Write-Host "Waiting for Kafka Connect to be ready..." -ForegroundColor Yellow
$maxRetries = 30
$retry = 0

while ($retry -lt $maxRetries) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8083/" -Method Get -ErrorAction Stop
        Write-Host "Kafka Connect is ready!" -ForegroundColor Green
        break
    }
    catch {
        $retry++
        Write-Host "Waiting for Kafka Connect... ($retry/$maxRetries)" -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
}

if ($retry -eq $maxRetries) {
    Write-Host "ERROR: Kafka Connect is not ready after $maxRetries attempts" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check if connector already exists
Write-Host "Checking if connector already exists..." -ForegroundColor Yellow
try {
    $existingConnector = Invoke-RestMethod -Uri "http://localhost:8083/connectors/research-mongo-source-connector" -Method Get -ErrorAction Stop
    Write-Host "Connector already exists. Deleting..." -ForegroundColor Yellow
    Invoke-RestMethod -Uri "http://localhost:8083/connectors/research-mongo-source-connector" -Method Delete -ErrorAction Stop
    Write-Host "Existing connector deleted" -ForegroundColor Green
    Start-Sleep -Seconds 2
}
catch {
    Write-Host "No existing connector found" -ForegroundColor Yellow
}

Write-Host ""

# Register the Debezium MongoDB connector
Write-Host "Registering Debezium MongoDB connector..." -ForegroundColor Yellow

$connectorConfig = Get-Content ".\connectors\mongo-source.json" -Raw | ConvertFrom-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8083/connectors" `
        -Method Post `
        -ContentType "application/json" `
        -Body ($connectorConfig | ConvertTo-Json -Depth 10) `
        -ErrorAction Stop
    
    Write-Host "Connector registered successfully!" -ForegroundColor Green
    Write-Host "Connector Name: $($response.name)" -ForegroundColor Cyan
    Write-Host ""
}
catch {
    Write-Host "ERROR: Failed to register connector" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Wait a moment for connector to initialize
Start-Sleep -Seconds 3

# Check connector status
Write-Host "Checking connector status..." -ForegroundColor Yellow
try {
    $status = Invoke-RestMethod -Uri "http://localhost:8083/connectors/research-mongo-source-connector/status" -Method Get -ErrorAction Stop
    
    Write-Host "Connector Status:" -ForegroundColor Cyan
    Write-Host "  State: $($status.connector.state)" -ForegroundColor $(if ($status.connector.state -eq "RUNNING") { "Green" } else { "Red" })
    Write-Host "  Worker: $($status.connector.worker_id)" -ForegroundColor Cyan
    
    if ($status.tasks) {
        Write-Host "  Tasks:" -ForegroundColor Cyan
        foreach ($task in $status.tasks) {
            Write-Host "    - Task $($task.id): $($task.state)" -ForegroundColor $(if ($task.state -eq "RUNNING") { "Green" } else { "Red" })
        }
    }
}
catch {
    Write-Host "ERROR: Failed to get connector status" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host ""

# List all connectors
Write-Host "All registered connectors:" -ForegroundColor Cyan
try {
    $connectors = Invoke-RestMethod -Uri "http://localhost:8083/connectors" -Method Get
    foreach ($connector in $connectors) {
        Write-Host "  - $connector" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Failed to list connectors" -ForegroundColor Red
}

Write-Host ""

# Check Kafka topics
Write-Host "Checking Kafka topics..." -ForegroundColor Yellow
Write-Host "Expected topic: research_db.research_db.rss_news" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can verify Kafka topics by running:" -ForegroundColor Yellow
Write-Host "  docker exec -it kafka_new kafka-topics.sh --bootstrap-server localhost:9092 --list" -ForegroundColor Cyan
Write-Host ""

# Check Weaviate
Write-Host "Checking Weaviate..." -ForegroundColor Yellow
try {
    $weaviateResponse = Invoke-RestMethod -Uri "http://localhost:8080/v1/meta" -Method Get -ErrorAction Stop
    Write-Host "Weaviate is ready!" -ForegroundColor Green
    Write-Host "  Version: $($weaviateResponse.version)" -ForegroundColor Cyan
}
catch {
    Write-Host "WARNING: Weaviate is not accessible" -ForegroundColor Red
}

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Insert/Update/Delete documents in MongoDB rss_news collection" -ForegroundColor White
Write-Host "2. Changes will automatically flow through Kafka to Weaviate" -ForegroundColor White
Write-Host "3. Check consumer logs: docker logs research_consumer -f" -ForegroundColor White
Write-Host "4. Verify vectors in Weaviate using the backend API" -ForegroundColor White
Write-Host ""
