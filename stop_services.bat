@echo off
echo ============================================
echo   Soccer Referee Bias Analysis Platform
echo            STOP SERVICES
echo ============================================
echo.

echo This script will stop all running services
echo.

echo [1/2] Attempting to stop supervisor services...
supervisorctl status >nul 2>&1
if %errorlevel% equ 0 (
    echo 🛑 Stopping supervisor services...
    supervisorctl stop all
    echo ✅ Supervisor services stopped
    echo.
) else (
    echo ℹ️  Supervisor not available, checking for direct processes...
)

echo [2/2] Checking for direct processes...
echo.

echo 🔧 Looking for backend processes on port 8001...
for /f "tokens=5" %%i in ('netstat -ano ^| find ":8001" ^| find "LISTENING"') do (
    echo Found process %%i, attempting to stop...
    taskkill /pid %%i /f >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Backend process stopped
    ) else (
        echo ⚠️  Could not stop backend process %%i
    )
)

echo 🌐 Looking for frontend processes on port 3000...
for /f "tokens=5" %%i in ('netstat -ano ^| find ":3000" ^| find "LISTENING"') do (
    echo Found process %%i, attempting to stop...
    taskkill /pid %%i /f >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Frontend process stopped
    ) else (
        echo ⚠️  Could not stop frontend process %%i
    )
)

echo.
echo 🔍 Looking for any remaining Python/Node processes...
tasklist | find "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Python processes still running. You may need to close them manually.
)

tasklist | find "node.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Node.js processes still running. You may need to close them manually.
)

echo.
echo ============================================
echo          SERVICES STOPPED! 🛑
echo ============================================
echo.
echo All detectable services have been stopped.
echo.
echo If you still see processes running:
echo 1. Check Task Manager for python.exe or node.exe
echo 2. Close any remaining command windows manually
echo 3. Use taskkill commands if needed
echo.
echo Press any key to exit...
pause >nul