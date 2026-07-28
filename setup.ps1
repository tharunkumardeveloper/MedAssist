# MedAssist Quick Setup Script for Windows PowerShell
# This script sets up both backend and frontend dependencies

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MedAssist Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion found" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.12+ from https://www.python.org/" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js $nodeVersion found" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 18+ from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setting up Backend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Backend setup
Set-Location backend

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment and install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}

# Setup .env file if it doesn't exist
if (-Not (Test-Path ".env")) {
    Write-Host "Setting up environment variables..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    
    # Generate SECRET_KEY
    $secretKey = python -c "import secrets; print(secrets.token_hex(32))"
    (Get-Content .env) -replace 'SECRET_KEY=your-secret-key-here', "SECRET_KEY=$secretKey" | Set-Content .env
    
    Write-Host "✓ Environment file created with secure SECRET_KEY" -ForegroundColor Green
} else {
    Write-Host "✓ Environment file already exists" -ForegroundColor Green
}

# Return to root directory
Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setting up Frontend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Frontend setup
Set-Location web

# Check if node_modules exists
if (-Not (Test-Path "node_modules")) {
    Write-Host "Installing Node.js dependencies (this may take a few minutes)..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Node.js dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to install Node.js dependencies" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ Node.js dependencies already installed" -ForegroundColor Green
}

# Setup .env file if it doesn't exist
if (-Not (Test-Path ".env")) {
    Write-Host "Setting up frontend environment..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✓ Frontend environment file created" -ForegroundColor Green
} else {
    Write-Host "✓ Frontend environment file already exists" -ForegroundColor Green
}

# Return to root directory
Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application, run:" -ForegroundColor Cyan
Write-Host "  .\start.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Or start services manually:" -ForegroundColor Cyan
Write-Host "  Backend:  cd backend && python -m uvicorn main:app --reload" -ForegroundColor White
Write-Host "  Frontend: cd web && npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Default admin credentials:" -ForegroundColor Yellow
Write-Host "  Email:    admin@medassist.local" -ForegroundColor White
Write-Host "  Password: ChangeMe123!" -ForegroundColor White
Write-Host ""
