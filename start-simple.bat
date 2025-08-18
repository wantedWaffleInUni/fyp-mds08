@echo off
echo Chaotic Image Encryption - Simple Startup Script
echo ================================================

echo Starting Backend...
cd chaotic-encryption-app\backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Start Flask server in background
echo Starting Flask server on http://localhost:5001
start "Backend Server" python app.py

cd ..\..

echo.
echo Starting Frontend...
cd chaotic-encryption-app\frontend

REM Install dependencies
echo Installing Node.js dependencies...
npm install

REM Start React development server in background
echo Starting React server on http://localhost:3000
start "Frontend Server" npm start

cd ..\..

echo.
echo Both servers are starting up!
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:5001
echo.
echo Press any key to stop both servers...
pause

REM Kill the background processes
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

echo Servers stopped
pause
