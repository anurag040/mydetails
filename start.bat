@echo off
REM Payments Hub Dashboard - Startup Script for Windows

echo.
echo ====================================================
echo   ^! Payments Hub Dashboard - Startup Script
echo ====================================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [X] Node.js is not installed.
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Node.js version: 
node --version

echo [OK] npm version:
npm --version
echo.

REM Step 1: Install dependencies
echo [*] Step 1: Installing dependencies...
echo This may take a few minutes...
call npm install

if errorlevel 1 (
    echo [X] Installation failed. Please check your npm connection.
    pause
    exit /b 1
)

echo [OK] Dependencies installed successfully!
echo.

REM Step 2: Start development server
echo [*] Step 2: Starting development server...
echo The application will open automatically in your browser...
echo.
echo Opening at http://localhost:4200
echo Press Ctrl+C to stop the server
echo.

call npm start

REM If we get here, the app has stopped
echo.
echo [OK] Application stopped.
pause
