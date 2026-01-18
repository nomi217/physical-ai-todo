@echo off
echo ========================================
echo Starting Phase 4 Docker Deployment
echo ========================================
echo.

echo [1/3] Stopping any dev servers on ports 3001 and 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3001 ^| findstr LISTENING') do (
    echo Stopping process on port 3001 (PID %%a)
    taskkill /PID %%a /F 2>nul
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Stopping process on port 8000 (PID %%a)
    taskkill /PID %%a /F 2>nul
)
timeout /t 2 /nobreak >nul
echo ✓ Ports cleared
echo.

echo [2/3] Navigating to Docker directory...
cd specs\004-kubernetes-deployment\docker
if errorlevel 1 (
    echo ERROR: Could not find docker directory!
    echo Make sure you're running this from the project root.
    pause
    exit /b 1
)
echo ✓ In docker directory
echo.

echo [3/3] Starting Docker Compose...
echo This will take 3-5 minutes on first build...
echo.
docker-compose up --build

pause
