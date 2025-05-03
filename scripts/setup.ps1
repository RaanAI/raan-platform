# Setup.ps1 - RAAN AI Stack Launcher (Windows)

Write-Host "🔍 Checking Docker installation..."

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "❌ Docker is not installed. Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
}

Write-Host "✅ Docker found"

# Copy .env.example to .env if not exists
if (-not (Test-Path "../.env")) {
    Copy-Item ../.env.example ../.env
    Write-Host "📄 .env created from .env.example"
}

# Navigate to infra
Set-Location ../infra

# Build and run Docker Compose
Write-Host "🚀 Launching Docker stack..."
docker compose -f docker-compose.yml up -d --build

Write-Host "`n✅ All services started:"
Write-Host "📦 Postgres: localhost:5432"
Write-Host "🧠 vLLM:     http://localhost:8000/v1"
Write-Host "🧠 Dify UI:  http://localhost:8080"
