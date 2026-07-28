# Starts the MedAssist backend (FastAPI/uvicorn) and frontend (Vite dev server)
# together in separate windows, and waits for both to come up.
#
# Usage:  powershell -ExecutionPolicy Bypass -File start.ps1
# (or just double-click start.bat)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

$backendDir = Join-Path $root "backend"
$webDir = Join-Path $root "web"

if (-not (Test-Path (Join-Path $backendDir ".env"))) {
    Write-Host "backend/.env is missing. Copy backend/.env.example to backend/.env and set SECRET_KEY first." -ForegroundColor Red
    exit 1
}

Write-Host "Starting backend (FastAPI) on http://127.0.0.1:8000 ..." -ForegroundColor Cyan
$backend = Start-Process powershell -PassThru -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$backendDir'; python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"
)

Write-Host "Waiting for backend health check..." -ForegroundColor DarkGray
$backendUp = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 2
        if ($resp.StatusCode -eq 200) { $backendUp = $true; break }
    } catch {
        Start-Sleep -Seconds 1
    }
}
if ($backendUp) {
    Write-Host "Backend is up." -ForegroundColor Green
} else {
    Write-Host "Backend did not respond within 30s - check the backend window for errors." -ForegroundColor Yellow
}

Write-Host "Starting frontend (Vite) on http://127.0.0.1:5173 ..." -ForegroundColor Cyan
$frontend = Start-Process powershell -PassThru -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$webDir'; npm run dev"
)

Write-Host ""
Write-Host "Backend:  http://127.0.0.1:8000  (docs at /docs)" -ForegroundColor Green
Write-Host "Frontend: http://127.0.0.1:5173" -ForegroundColor Green
Write-Host ""
Write-Host "Each service is running in its own PowerShell window. Close those windows (or Ctrl+C inside them) to stop." -ForegroundColor DarkGray
