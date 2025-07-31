@echo off
echo Starting Core Model Frontend...
echo.

cd /d "%~dp0frontend\core_model"

echo Installing Node.js dependencies...
npm install

echo.
echo Starting Angular development server...
echo Frontend will be available at: http://localhost:4200
echo.

ng serve --open --port 4200
