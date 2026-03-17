@echo off
REM Video Compliance Framework - Quick Start Script (Windows)

echo.
echo ========================================
echo Video Compliance Framework - Quick Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

echo ✓ Python and Node.js found
echo.

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo ✓ Python dependencies installed
echo.

REM Install Frontend dependencies
echo Installing frontend dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)
echo ✓ Frontend dependencies installed
cd ..
echo.

REM Create .env.local for frontend
echo Creating frontend environment configuration...
if not exist frontend\.env.local (
    echo REACT_APP_API_URL=http://localhost:5000 > frontend\.env.local
    echo ✓ Frontend environment configured
) else (
    echo ✓ Frontend environment already configured
)
echo.

REM Create directories
if not exist uploads mkdir uploads
if not exist preprocessed_output mkdir preprocessed_output
echo ✓ Output directories created
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. START BACKEND SERVER (in one terminal):
echo    python app.py
echo.
echo 2. START FRONTEND (in another terminal):
echo    cd frontend
echo    npm start
echo.
echo 3. OPEN BROWSER:
echo    http://localhost:3000
echo.
echo Documentation:
echo   - SETUP_GUIDE.md - Complete setup guide
echo   - BACKEND_API.md - API documentation
echo   - frontend/README.md - Frontend documentation
echo.
pause
