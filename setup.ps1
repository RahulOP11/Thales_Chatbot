# Quick Setup Script for Windows
# Run this after activating virtual environment

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Thales Chatbot - Quick Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠ Virtual environment not detected!" -ForegroundColor Yellow
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    Write-Host "Then activate: venv\Scripts\activate" -ForegroundColor Yellow
    Write-Host ""
    exit
}

Write-Host "✓ Virtual environment detected" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
pip install --upgrade pip
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠ IMPORTANT: Edit .env and add your GOOGLE_API_KEY" -ForegroundColor Yellow
    Write-Host "Get free key from: https://makersuite.google.com/app/apikey" -ForegroundColor Yellow
    Write-Host ""
    
    # Ask if user wants to open .env
    $response = Read-Host "Open .env file now? (y/n)"
    if ($response -eq "y") {
        notepad .env
    }
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Add your Gemini API key to .env file" -ForegroundColor White
Write-Host "2. Download textbooks: python src/utils/download_textbooks.py" -ForegroundColor White
Write-Host "3. Build vector store: python build_vectorstore.py" -ForegroundColor White
Write-Host "4. Start API server: python main.py" -ForegroundColor White
Write-Host ""
Write-Host "Full documentation: README.md" -ForegroundColor White
Write-Host ""
