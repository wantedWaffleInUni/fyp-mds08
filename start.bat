@echo off
echo 🔐 Chaotic Image Encryption - Startup Script
echo ==============================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH. Please install Node.js 16 or higher.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Start backend
echo 🚀 Starting Backend...
cd chaotic-encryption-app\backend

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing Python dependencies...
pip install -r requirements.txt

REM Start Flask server
echo 🌐 Starting Flask server on http://localhost:5001
start "Backend Server" python app.py

cd ..\..

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo 🚀 Starting Frontend...
cd chaotic-encryption-app\frontend

REM Install dependencies
echo 📥 Installing Node.js dependencies...
npm install

REM Start React development server
echo 🌐 Starting React server on http://localhost:3000
start "Frontend Server" npm start

cd ..\..

echo.
echo 🎉 Both servers are starting up!
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend:  http://localhost:5001
echo.
echo Press any key to stop both servers...
pause

REM Kill the background processes
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

echo ✅ Servers stopped
pause
