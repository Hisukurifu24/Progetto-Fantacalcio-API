@echo off
REM Fantasy Football API - Local Startup Script
REM This script sets up and runs the API server locally

echo.
echo ========================================
echo  Fantasy Football API - Local Server
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [1/4] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Make sure Python is installed and in your PATH
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
) else (
    echo [1/4] Virtual environment found!
)

echo.
echo [2/4] Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo [3/4] Installing/updating dependencies...
pip install -r Fantasy-Football-API\requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [4/4] Starting server...
echo.
echo ========================================
echo  Server starting on http://localhost:8000
echo  
echo  Interactive Docs: http://localhost:8000/docs
echo  Alternative Docs: http://localhost:8000/redoc
echo.
echo  Press CTRL+C to stop the server
echo ========================================
echo.

cd Fantasy-Football-API
python main.py

REM If server stops, pause so user can see any error messages
echo.
echo Server stopped.
pause
