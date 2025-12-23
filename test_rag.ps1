$body = @{
    message = "What are the latest news about technology?"
    user_id = "test_user"
    include_sources = $true
    context_limit = 3
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8001/news-chat/ask" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing

$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
