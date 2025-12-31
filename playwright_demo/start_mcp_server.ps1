# Set timeouts to 5 minutes (300000ms = 300 seconds)
$env:PLAYWRIGHT_MCP_TIMEOUT_ACTION = "300000"
$env:PLAYWRIGHT_MCP_TIMEOUT_NAVIGATION = "300000"

Write-Host "🚀 Starting MCP Server with extended timeouts..."
Write-Host "   Action timeout: 300 seconds"
Write-Host "   Navigation timeout: 300 seconds"
Write-Host ""

npx @playwright/mcp --port 3000