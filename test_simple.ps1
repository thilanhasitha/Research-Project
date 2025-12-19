# Simple test script for the general responder
Write-Host "`n=== Testing General Responder ===" -ForegroundColor Cyan

# 1. Test basic API health
Write-Host "`n[1] Testing API health..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/" -Method Get -TimeoutSec 5
    Write-Host "SUCCESS: $($response.message)" -ForegroundColor Green
} catch {
    Write-Host "FAILED: API not responding on port 8001" -ForegroundColor Red
    Write-Host "Run: docker compose up -d" -ForegroundColor Yellow
    exit 1
}

# 2. Test simple message (greeting)
Write-Host "`n[2] Testing simple greeting..." -ForegroundColor Yellow
try {
    $body = @{
        message = "Hello!"
        user_id = "test_user"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:8001/chat/message" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body `
        -TimeoutSec 30
    
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host "  Intent: $($response.intent)" -ForegroundColor Gray
    Write-Host "  Response: $($response.response.Substring(0, [Math]::Min(200, $response.response.Length)))" -ForegroundColor Gray
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Test news search
Write-Host "`n[3] Testing news search..." -ForegroundColor Yellow
try {
    $body = @{
        message = "Show me recent news"
        user_id = "test_user"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:8001/chat/message" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body `
        -TimeoutSec 30
    
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host "  Intent: $($response.intent)" -ForegroundColor Gray
    Write-Host "  Used Tools: $($response.used_tools)" -ForegroundColor Gray
    Write-Host "  Response: $($response.response.Substring(0, [Math]::Min(200, $response.response.Length)))" -ForegroundColor Gray
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
Write-Host "`nTo view detailed logs:" -ForegroundColor Gray
Write-Host "  docker logs research_backend --tail 50" -ForegroundColor Yellow
