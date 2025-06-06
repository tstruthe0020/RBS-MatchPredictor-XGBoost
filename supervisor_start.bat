@echo off
echo ============================================
echo    RBS-MatchPredictor-XGBoost Platform
echo        PRODUCTION QUICK START
echo ============================================
echo.

echo This script works with supervisor-managed services
echo.

echo [1/2] Checking supervisor status...
supervisorctl status >nul 2>&1
if %errorlevel% neq 0 (
    echo Supervisor not available, falling back to direct start...
    echo Calling quick_start.bat...
    call quick_start.bat
    exit /b
)

echo ✅ Supervisor is available
echo.

echo [2/2] Starting all services with supervisor...
echo.

echo 🔧 Starting backend service (with XGBoost)...
supervisorctl start backend
if %errorlevel% neq 0 (
    echo ❌ Failed to start backend service
    pause
    exit /b 1
)

echo 🌐 Starting frontend service...
supervisorctl start frontend
if %errorlevel% neq 0 (
    echo ❌ Failed to start frontend service
    pause
    exit /b 1
)

echo.
echo Checking service status...
supervisorctl status

echo.
echo ============================================
echo         SERVICES STARTED! 🚀
echo ============================================
echo.
echo Your RBS-MatchPredictor-XGBoost application is now running:
echo.
echo 🔧 Backend API: Available on configured port
echo 🌐 Frontend:    Available on configured port
echo.
echo To check service status: supervisorctl status
echo To restart services: supervisorctl restart all
echo To stop services: supervisorctl stop all
echo.
echo Press any key to continue...
pause >nul
