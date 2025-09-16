@echo off
echo Installing Fantasy Football API dependencies...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Install dependencies
echo Installing required packages...
pip install -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Installation completed successfully!
echo.
echo To start the API server, run:
echo   python main.py
echo.
echo Then visit http://localhost:8000/docs for the API documentation
echo.
pause
