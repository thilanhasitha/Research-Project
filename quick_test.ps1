# Quick one-liner tests for general responder

Write-Host "`n=== Quick Test Commands ===" -ForegroundColor Cyan

Write-Host "`n1. Health Check:" -ForegroundColor Yellow
Write-Host '   Invoke-RestMethod -Uri "http://localhost:8001/"' -ForegroundColor White

Write-Host "`n2. Test Greeting:" -ForegroundColor Yellow
Write-Host '   Invoke-RestMethod -Uri "http://localhost:8001/chat/message" -Method Post -ContentType "application/json" -Body (@{message="Hello!"; user_id="test"} | ConvertTo-Json)' -ForegroundColor White

Write-Host "`n3. Test News Search:" -ForegroundColor Yellow
Write-Host '   Invoke-RestMethod -Uri "http://localhost:8001/chat/message" -Method Post -ContentType "application/json" -Body (@{message="Show me news"; user_id="test"} | ConvertTo-Json)' -ForegroundColor White

Write-Host "`n4. View Logs:" -ForegroundColor Yellow
Write-Host '   docker logs research_backend --tail 30' -ForegroundColor White

Write-Host "`n5. Check Services:" -ForegroundColor Yellow
Write-Host '   docker ps --format "table {{.Names}}\t{{.Status}}"' -ForegroundColor White

Write-Host "`n=== Run Tests Now ===" -ForegroundColor Cyan

# Execute tests if -Run parameter is passed
if ($args -contains "-Run") {
    Write-Host "`nRunning tests..." -ForegroundColor Green
    
    try {
        Write-Host "`nTest 1: Health Check"
        $health = Invoke-RestMethod -Uri "http://localhost:8001/"
        Write-Host "✓ $($health.message)" -ForegroundColor Green
        
        Write-Host "`nTest 2: Greeting"
        $response = Invoke-RestMethod -Uri "http://localhost:8001/chat/message" -Method Post -ContentType "application/json" -Body (@{message="Hello!"; user_id="test"} | ConvertTo-Json) -TimeoutSec 30
        Write-Host "✓ Response: $($response.response.Substring(0, [Math]::Min(100, $response.response.Length)))" -ForegroundColor Green
        
        Write-Host "`nAll tests passed!" -ForegroundColor Green
    } catch {
        Write-Host "✗ Error: $_" -ForegroundColor Red
    }
} else {
    Write-Host "`nTo run tests automatically, use: .\quick_test.ps1 -Run" -ForegroundColor Gray
}
