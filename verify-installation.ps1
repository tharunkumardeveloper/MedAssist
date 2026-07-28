# MedAssist Installation Verification Script
# Checks if everything is properly installed and configured

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MedAssist Installation Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$errors = 0
$warnings = 0

# Function to check command
function Test-Command {
    param($command)
    try {
        Get-Command $command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Check Python
Write-Host "1. Checking Python..." -ForegroundColor Yellow
if (Test-Command python) {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✓ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   ✗ Python not found" -ForegroundColor Red
    $errors++
}

# Check pip
Write-Host "2. Checking pip..." -ForegroundColor Yellow
if (Test-Command pip) {
    $pipVersion = pip --version 2>&1 | Select-Object -First 1
    Write-Host "   ✓ $pipVersion" -ForegroundColor Green
} else {
    Write-Host "   ✗ pip not found" -ForegroundColor Red
    $errors++
}

# Check Node.js
Write-Host "3. Checking Node.js..." -ForegroundColor Yellow
if (Test-Command node) {
    $nodeVersion = node --version 2>&1
    Write-Host "   ✓ Node.js $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "   ✗ Node.js not found" -ForegroundColor Red
    $errors++
}

# Check npm
Write-Host "4. Checking npm..." -ForegroundColor Yellow
if (Test-Command npm) {
    $npmVersion = npm --version 2>&1
    Write-Host "   ✓ npm $npmVersion" -ForegroundColor Green
} else {
    Write-Host "   ✗ npm not found" -ForegroundColor Red
    $errors++
}

# Check backend virtual environment
Write-Host "5. Checking backend virtual environment..." -ForegroundColor Yellow
if (Test-Path "backend\venv") {
    Write-Host "   ✓ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "   ! Virtual environment not found (run setup.ps1)" -ForegroundColor Yellow
    $warnings++
}

# Check backend dependencies
Write-Host "6. Checking backend dependencies..." -ForegroundColor Yellow
if (Test-Path "backend\venv\Lib\site-packages\fastapi") {
    Write-Host "   ✓ Backend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "   ! Backend dependencies not installed (run setup.ps1)" -ForegroundColor Yellow
    $warnings++
}

# Check backend .env
Write-Host "7. Checking backend configuration..." -ForegroundColor Yellow
if (Test-Path "backend\.env") {
    $envContent = Get-Content "backend\.env" -Raw
    if ($envContent -match "SECRET_KEY=.{64}") {
        Write-Host "   ✓ Backend .env file configured" -ForegroundColor Green
    } else {
        Write-Host "   ! SECRET_KEY may not be properly configured" -ForegroundColor Yellow
        $warnings++
    }
} else {
    Write-Host "   ! Backend .env file missing (run setup.ps1)" -ForegroundColor Yellow
    $warnings++
}

# Check frontend dependencies
Write-Host "8. Checking frontend dependencies..." -ForegroundColor Yellow
if (Test-Path "web\node_modules") {
    Write-Host "   ✓ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "   ! Frontend dependencies not installed (run setup.ps1)" -ForegroundColor Yellow
    $warnings++
}

# Check frontend .env
Write-Host "9. Checking frontend configuration..." -ForegroundColor Yellow
if (Test-Path "web\.env") {
    Write-Host "   ✓ Frontend .env file exists" -ForegroundColor Green
} else {
    Write-Host "   ! Frontend .env file missing (run setup.ps1)" -ForegroundColor Yellow
    $warnings++
}

# Check model files
Write-Host "10. Checking ML model files..." -ForegroundColor Yellow
$modelFiles = @(
    "model\model1_outcome_classifier.pkl",
    "model\model1_symptom_binarizer.pkl",
    "model\model2_brfss_risk_models.pkl",
    "model\model3_tfidf_vectorizer.pkl"
)
$missingModels = 0
foreach ($file in $modelFiles) {
    if (-Not (Test-Path $file)) {
        $missingModels++
    }
}
if ($missingModels -eq 0) {
    Write-Host "   ✓ All ML model files present" -ForegroundColor Green
} else {
    Write-Host "   ✗ $missingModels model files missing" -ForegroundColor Red
    $errors++
}

# Check README and SETUP
Write-Host "11. Checking documentation..." -ForegroundColor Yellow
if ((Test-Path "README.md") -and (Test-Path "SETUP.md")) {
    Write-Host "   ✓ Documentation files present" -ForegroundColor Green
} else {
    Write-Host "   ! Some documentation files missing" -ForegroundColor Yellow
    $warnings++
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Verification Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($errors -eq 0 -and $warnings -eq 0) {
    Write-Host "✓ All checks passed! Your installation is ready." -ForegroundColor Green
    Write-Host ""
    Write-Host "To start the application, run:" -ForegroundColor Cyan
    Write-Host "  .\start.ps1" -ForegroundColor White
} elseif ($errors -eq 0) {
    Write-Host "! $warnings warning(s) found." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Run the setup script to complete installation:" -ForegroundColor Cyan
    Write-Host "  .\setup.ps1" -ForegroundColor White
} else {
    Write-Host "✗ $errors error(s) and $warnings warning(s) found." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install missing dependencies and run:" -ForegroundColor Cyan
    Write-Host "  .\setup.ps1" -ForegroundColor White
}

Write-Host ""
