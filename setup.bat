@echo off
echo Data Analysis Platform - Complete Setup
echo.

echo This script will set up both frontend and backend...
echo.

echo Step 1: Setting up Python Backend...
cd /d "%~dp0backend"

if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    echo.
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Step 2: Setting up Angular Frontend...
cd /d "%~dp0frontend\data-analysis-app"

echo Installing Node.js dependencies...
npm install

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo To start the application:
echo 1. Run 'start-backend.bat' in one terminal
echo 2. Run 'start-frontend.bat' in another terminal
echo 3. Open http://localhost:4200 in your browser
echo.
echo Don't forget to:
echo - Add your OpenAI API key to backend\.env
echo - Check that both Node.js and Python are installed
echo.
pause
