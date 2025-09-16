@echo off
echo Starting Fantasy Football API server...

REM Check if dependencies are installed
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Error: FastAPI not found. Please run install.bat first.
    pause
    exit /b 1
)

echo.
echo Starting server on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.

REM Start the server
python main.py

pause
