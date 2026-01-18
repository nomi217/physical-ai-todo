@echo off
echo Stopping development servers...
echo.

echo Stopping frontend (Port 3001 - PID 10560)...
taskkill /PID 10560 /F 2>nul
if errorlevel 1 (
    echo Frontend already stopped or PID changed
) else (
    echo ✓ Frontend dev server stopped
)

echo.
echo Stopping backend (Port 8000 - PID 4796)...
taskkill /PID 4796 /F 2>nul
if errorlevel 1 (
    echo Backend already stopped or PID changed
) else (
    echo ✓ Backend dev server stopped
)

echo.
echo ========================================
echo Dev servers stopped!
echo Now you can run Docker deployment.
echo ========================================
echo.
echo Next steps:
echo   cd specs\004-kubernetes-deployment\docker
echo   docker-compose up --build
echo.
