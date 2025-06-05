@echo off
echo ============================================
echo   Soccer Referee Bias Analysis Platform
echo        INITIAL SETUP AND START
echo ============================================
echo.

echo [1/6] Checking Python and Node.js installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 16+ and add it to your PATH
    pause
    exit /b 1
)

yarn --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Yarn is not installed
    echo Please install Yarn package manager
    echo Run: npm install -g yarn
    pause
    exit /b 1
)

echo ✅ Python and Node.js are installed
echo.

echo [2/6] Installing Backend Dependencies...
cd backend
if not exist requirements.txt (
    echo ERROR: requirements.txt not found in backend directory
    pause
    exit /b 1
)

echo Installing Python packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)

echo ✅ Backend dependencies installed
cd ..
echo.

echo [3/6] Installing Frontend Dependencies...
cd frontend
if not exist package.json (
    echo ERROR: package.json not found in frontend directory
    pause
    exit /b 1
)

echo Installing Node.js packages with Yarn...
yarn install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)

echo ✅ Frontend dependencies installed
cd ..
echo.

echo [4/6] Checking Environment Configuration...
if not exist backend\.env (
    echo WARNING: backend\.env file not found
    echo The application may not work properly without environment configuration
    echo Please ensure MongoDB connection string is properly configured
)

if not exist frontend\.env (
    echo WARNING: frontend\.env file not found
    echo The application may not work properly without environment configuration
    echo Please ensure REACT_APP_BACKEND_URL is properly configured
)

echo ✅ Environment check completed
echo.

echo [5/6] Starting Backend Server...
echo Starting FastAPI backend on http://localhost:8001
cd backend
start "Backend Server" cmd /k "python server.py"
cd ..

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul
echo.

echo [6/6] Starting Frontend Server...
echo Starting React frontend on http://localhost:3000
cd frontend
start "Frontend Server" cmd /k "yarn start"
cd ..

echo.
echo ============================================
echo           SETUP COMPLETED! 🚀
echo ============================================
echo.
echo Your application is starting up:
echo.
echo 🔧 Backend API: http://localhost:8001
echo 🌐 Frontend:    http://localhost:3000
echo.
echo The application will open automatically in your browser.
echo If it doesn't open, navigate to http://localhost:3000
echo.
echo For future starts, use quick_start.bat
echo.
echo Press any key to continue...
pause >nul