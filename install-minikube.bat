@echo off
echo ========================================
echo Installing Minikube for Windows
echo ========================================
echo.

echo [1/3] Downloading Minikube installer...
curl -Lo minikube-installer.exe https://github.com/kubernetes/minikube/releases/latest/download/minikube-installer.exe

if errorlevel 1 (
    echo ERROR: Failed to download Minikube
    echo Please download manually from: https://minikube.sigs.k8s.io/docs/start/
    pause
    exit /b 1
)

echo.
echo [2/3] Running Minikube installer...
echo Please follow the installation wizard...
start /wait minikube-installer.exe

echo.
echo [3/3] Verifying installation...
timeout /t 2 /nobreak >nul
minikube version

if errorlevel 1 (
    echo.
    echo WARNING: Minikube not found in PATH
    echo Please restart your terminal and try again
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ Minikube installed successfully!
echo ========================================
echo.
echo Next steps:
echo   1. Close this terminal
echo   2. Open a NEW terminal (to refresh PATH)
echo   3. Run: cd C:\Users\Ahsan\physical-ai-todo
echo   4. Run: minikube start --driver=docker
echo.
pause
