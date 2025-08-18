# Chaotic Image Encryption - PowerShell Startup Script
Write-Host "Chaotic Image Encryption - Startup Script" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python is not installed or not in PATH. Please install Python 3.8 or higher." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    Write-Host "Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js is not installed or not in PATH. Please install Node.js 16 or higher." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Prerequisites check passed" -ForegroundColor Green

# Function to start backend
function Start-Backend {
    Write-Host "Starting Backend..." -ForegroundColor Yellow
    Set-Location "chaotic-encryption-app\backend"
    
    # Check if virtual environment exists
    if (-not (Test-Path "venv")) {
        Write-Host "Creating virtual environment..." -ForegroundColor Blue
        python -m venv venv
    }
    
    # Activate virtual environment
    Write-Host "Activating virtual environment..." -ForegroundColor Blue
    & "venv\Scripts\Activate.ps1"
    
    # Install dependencies
    Write-Host "Installing Python dependencies..." -ForegroundColor Blue
    pip install -r requirements.txt
    
    # Start Flask server
    Write-Host "Starting Flask server on http://localhost:5001" -ForegroundColor Green
    Start-Process -FilePath "python" -ArgumentList "app.py" -WindowStyle Minimized
}

# Function to start frontend
function Start-Frontend {
    Write-Host "Starting Frontend..." -ForegroundColor Yellow
    Set-Location "chaotic-encryption-app\frontend"
    
    # Install dependencies
    Write-Host "Installing Node.js dependencies..." -ForegroundColor Blue
    npm install
    
    # Start React development server
    Write-Host "Starting React server on http://localhost:3000" -ForegroundColor Green
    Start-Process -FilePath "npm" -ArgumentList "start" -WindowStyle Minimized
}

# Function to cleanup
function Stop-Servers {
    Write-Host "Stopping servers..." -ForegroundColor Red
    Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "Servers stopped" -ForegroundColor Green
}

# Set up cleanup on script exit
trap {
    Stop-Servers
    break
}

# Start both services
Start-Backend
Start-Sleep -Seconds 3  # Give backend time to start

# Reset location to root directory before starting frontend
Set-Location "C:\Users\Yanly\Monash\FYP\fyp-mds08"
Start-Frontend

Set-Location "C:\Users\Yanly\Monash\FYP\fyp-mds08"

Write-Host ""
Write-Host "Both servers are starting up!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:5001" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Yellow

# Wait for user to stop
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} catch {
    Stop-Servers
}
