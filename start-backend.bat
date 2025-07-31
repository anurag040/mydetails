@echo off
echo Starting Data Analysis Platform Backend...
echo.

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
echo Starting FastAPI server...
echo Backend will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
