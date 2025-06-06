@echo off
echo ============================================
echo    RBS-MatchPredictor-XGBoost Platform
echo            QUICK START
echo ============================================
echo.

echo [1/3] Checking if services are already running...
netstat -an | find "LISTENING" | find ":8001" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Backend server appears to be already running on port 8001
    echo   If you're having issues, close existing instances first
    echo.
)

netstat -an | find "LISTENING" | find ":3000" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Frontend server appears to be already running on port 3000
    echo   If you're having issues, close existing instances first
    echo.
)

echo [2/3] Starting Backend Server...
echo 🔧 Starting FastAPI backend on http://localhost:8001
cd backend
start "Backend Server" cmd /k "python server.py"
cd ..

echo Waiting for backend to initialize...
timeout /t 3 /nobreak >nul
echo.

echo [3/3] Starting Frontend Server...
echo 🌐 Starting React frontend on http://localhost:3000
cd frontend
start "Frontend Server" cmd /k "yarn start"
cd ..

echo.
echo ============================================
echo         APPLICATION STARTING! 🚀
echo ============================================
echo.
echo Your servers are starting up:
echo.
echo 🔧 Backend API: http://localhost:8001/api
echo 🌐 Frontend:    http://localhost:3000
echo.
echo The application will open automatically in your browser.
echo If it doesn't open, navigate to http://localhost:3000
echo.
echo To stop the application:
echo 1. Close both command windows that opened
echo 2. Or press Ctrl+C in each window
echo.
echo ============================================
echo           QUICK START TIPS
echo ============================================
echo.
echo 📊 Upload Data: Use the 'Upload' tab to import CSV files
echo 🔍 Analyze: Use 'Regression Analysis' for statistical insights
echo ⚙️  Optimize: Use 'Formula Optimization' to improve algorithms
echo 🎯 Predict: Use 'Match Prediction' for game outcome forecasts
echo 🚀 XGBoost: Use 'XGBoost + Poisson' for advanced ML predictions
echo.
echo Press any key to continue...
pause >nul
