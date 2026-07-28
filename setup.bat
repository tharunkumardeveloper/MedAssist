@echo off
REM MedAssist Quick Setup Script for Windows CMD
REM This script sets up both backend and frontend dependencies

echo ========================================
echo   MedAssist Setup Script
echo ========================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.12+ from https://www.python.org/
    pause
    exit /b 1
)
echo [OK] Python found
echo.

REM Check Node.js
echo Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js found
echo.

echo ========================================
echo   Setting up Backend
echo ========================================
echo.

cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

REM Install dependencies
echo Installing Python dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)
echo [OK] Python dependencies installed

REM Setup .env file
if not exist ".env" (
    echo Setting up environment variables...
    copy .env.example .env >nul
    
    REM Generate SECRET_KEY
    for /f "delims=" %%i in ('python -c "import secrets; print(secrets.token_hex(32))"') do set SECRET_KEY=%%i
    powershell -Command "(gc .env) -replace 'SECRET_KEY=your-secret-key-here', 'SECRET_KEY=%SECRET_KEY%' | Out-File -encoding ASCII .env"
    
    echo [OK] Environment file created with secure SECRET_KEY
) else (
    echo [OK] Environment file already exists
)

cd ..

echo.
echo ========================================
echo   Setting up Frontend
echo ========================================
echo.

cd web

REM Install Node dependencies
if not exist "node_modules" (
    echo Installing Node.js dependencies (this may take a few minutes)...
    call npm install
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install Node.js dependencies
        pause
        exit /b 1
    )
    echo [OK] Node.js dependencies installed
) else (
    echo [OK] Node.js dependencies already installed
)

REM Setup .env file
if not exist ".env" (
    echo Setting up frontend environment...
    copy .env.example .env >nul
    echo [OK] Frontend environment file created
) else (
    echo [OK] Frontend environment file already exists
)

cd ..

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo To start the application, run:
echo   start.bat
echo.
echo Or start services manually:
echo   Backend:  cd backend ^&^& python -m uvicorn main:app --reload
echo   Frontend: cd web ^&^& npm run dev
echo.
echo Default admin credentials:
echo   Email:    admin@medassist.local
echo   Password: ChangeMe123!
echo.
pause
