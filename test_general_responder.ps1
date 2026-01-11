# PowerShell script to test the general responder
# Run this after starting your services with: docker compose up -d

$BASE_URL = "http://localhost:8001"

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "Testing General Responder with Tools" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Test 1: Quick health check
Write-Host "[Test 1] Checking API health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$BASE_URL/" -Method Get
    Write-Host "SUCCESS: API is running: $($health.message)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: API is not responding. Make sure to run: docker compose up -d" -ForegroundColor Red
    exit 1
}

# Test 2: Automated test endpoint
Write-Host "`n[Test 2] Running automated tests..." -ForegroundColor Yellow
try {
    $testResult = Invoke-RestMethod -Uri "$BASE_URL/chat/test" -Method Get
    Write-Host "SUCCESS: Automated tests completed" -ForegroundColor Green
    
    foreach ($result in $testResult.test_results) {
        Write-Host "`n  Message: $($result.message)" -ForegroundColor White
        Write-Host "  Intent: $($result.intent)" -ForegroundColor Gray
        Write-Host "  Used Tools: $($result.used_tools)" -ForegroundColor Gray
        if ($result.response_preview) {
            Write-Host "  Response: $($result.response_preview)" -ForegroundColor Gray
        }
        if ($result.error) {
            Write-Host "  Error: $($result.error)" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "ERROR: Test failed: $_" -ForegroundColor Red
}

# Test 3: Simple greeting (should NOT use tools)
Write-Host "`n[Test 3] Testing greeting (no tools expected)..." -ForegroundColor Yellow
try {
    $body = @{
        message = "Hello! How are you today?"
        user_id = "test_user_ps1"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$BASE_URL/chat/message" -Method Post -ContentType "application/json" -Body $body

    Write-Host "SUCCESS: Request completed" -ForegroundColor Green
    Write-Host "  Intent: $($response.intent)" -ForegroundColor Gray
    if ($response.used_tools) {
        Write-Host "  Used Tools: $($response.used_tools)" -ForegroundColor Yellow
    } else {
        Write-Host "  Used Tools: $($response.used_tools)" -ForegroundColor Green
    }
    $preview = $response.response.Substring(0, [Math]::Min(150, $response.response.Length))
    Write-Host "  Response: $preview..." -ForegroundColor Gray
} catch {
    Write-Host "ERROR: Test failed: $_" -ForegroundColor Red
}

# Test 4: News search (SHOULD use tools)
Write-Host "`n[Test 4] Testing news search (tools expected)..." -ForegroundColor Yellow
try {
    $body = @{
        message = "Find me the latest news about technology and AI"
        user_id = "test_user_ps2"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$BASE_URL/chat/message" -Method Post -ContentType "application/json" -Body $body

    Write-Host "SUCCESS: Request completed" -ForegroundColor Green
    Write-Host "  Intent: $($response.intent)" -ForegroundColor Gray
    if ($response.used_tools) {
        Write-Host "  Used Tools: $($response.used_tools)" -ForegroundColor Green
    } else {
        Write-Host "  Used Tools: $($response.used_tools)" -ForegroundColor Yellow
    }
    
    if ($response.tool_calls -and $response.tool_calls.Count -gt 0) {
        Write-Host "  Tools Called:" -ForegroundColor Gray
        foreach ($tool in $response.tool_calls) {
            Write-Host "    - $($tool.name)" -ForegroundColor Cyan
        }
    }
    
    $preview = $response.response.Substring(0, [Math]::Min(150, $response.response.Length))
    Write-Host "  Response: $preview..." -ForegroundColor Gray
} catch {
    Write-Host "ERROR: Test failed: $_" -ForegroundColor Red
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "All Tests Completed!" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

Write-Host "Summary: Test 3 should NOT use tools, Test 4 SHOULD use tools" -ForegroundColor White
Write-Host ""
Write-Host "To view detailed logs:" -ForegroundColor Gray
Write-Host "  docker logs research-project-backend-1" -ForegroundColor Yellow
Write-Host ""
