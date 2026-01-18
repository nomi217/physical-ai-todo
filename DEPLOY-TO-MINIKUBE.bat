@echo off
echo ========================================
echo Deploying Todo App to Minikube
echo ========================================
echo.

REM Step 1: Verify Minikube
echo [1/8] Verifying Minikube installation...
minikube version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Minikube not found in PATH
    echo Please restart your terminal and try again
    pause
    exit /b 1
)
echo ✓ Minikube is installed
echo.

REM Step 2: Start Minikube
echo [2/8] Starting Minikube cluster...
echo This may take 2-3 minutes on first start...
minikube start --driver=docker --cpus=4 --memory=4096
if errorlevel 1 (
    echo ERROR: Failed to start Minikube
    echo Make sure Docker Desktop is running
    pause
    exit /b 1
)
echo ✓ Minikube cluster started
echo.

REM Step 3: Verify Minikube status
echo [3/8] Verifying cluster status...
minikube status
echo.

REM Step 4: Build Docker images
echo [4/8] Building Docker images...
echo Building backend...
docker build -t todo-backend:latest -f specs/004-kubernetes-deployment/docker/backend.Dockerfile ./backend
if errorlevel 1 (
    echo ERROR: Backend build failed
    pause
    exit /b 1
)
echo ✓ Backend image built

echo Building frontend...
docker build -t todo-frontend:latest -f specs/004-kubernetes-deployment/docker/frontend.Dockerfile ./frontend
if errorlevel 1 (
    echo ERROR: Frontend build failed
    pause
    exit /b 1
)
echo ✓ Frontend image built
echo.

REM Step 5: Load images into Minikube
echo [5/8] Loading images into Minikube...
echo Loading backend...
minikube image load todo-backend:latest
echo ✓ Backend image loaded

echo Loading frontend...
minikube image load todo-frontend:latest
echo ✓ Frontend image loaded
echo.

REM Step 6: Verify images
echo [6/8] Verifying images in Minikube...
minikube image ls | findstr todo
echo.

REM Step 7: Create Helm values file
echo [7/8] Creating Helm values file...
cd specs\004-kubernetes-deployment\helm
if not exist "todo-app" (
    echo ERROR: Helm chart not found at specs/004-kubernetes-deployment/helm/todo-app
    pause
    exit /b 1
)

echo Creating custom-values.yaml...
(
echo # Minikube Custom Values
echo secrets:
echo   enabled: true
echo   data:
echo     openai-api-key: "%OPENAI_API_KEY%"
echo.
echo backend:
echo   replicaCount: 1
echo   image:
echo     repository: todo-backend
echo     tag: latest
echo     pullPolicy: Never
echo.
echo frontend:
echo   replicaCount: 1
echo   image:
echo     repository: todo-frontend
echo     tag: latest
echo     pullPolicy: Never
echo   service:
echo     type: NodePort
echo.
echo postgres:
echo   enabled: true
echo   storage:
echo     size: 1Gi
) > custom-values.yaml
echo ✓ Helm values created
echo.

REM Step 8: Deploy with Helm
echo [8/8] Deploying with Helm...
helm install todo-app ./todo-app -f custom-values.yaml
if errorlevel 1 (
    echo ERROR: Helm install failed
    echo Trying to upgrade instead...
    helm upgrade todo-app ./todo-app -f custom-values.yaml
)
echo ✓ App deployed to Kubernetes
echo.

echo ========================================
echo Waiting for pods to start...
echo ========================================
echo This may take 1-2 minutes...
echo.
timeout /t 10 /nobreak >nul

echo Checking pod status...
kubectl get pods
echo.

echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo 📋 View all resources:
echo    kubectl get all
echo.
echo 📊 Check pod status:
echo    kubectl get pods
echo.
echo 📝 View logs:
echo    kubectl logs -l app.kubernetes.io/component=backend
echo    kubectl logs -l app.kubernetes.io/component=frontend
echo.
echo 🌐 Access your app:
echo    kubectl port-forward svc/todo-app-frontend 3001:3000
echo    Then open: http://localhost:3001
echo.
echo OR use Minikube service:
echo    minikube service todo-app-frontend
echo.
echo ========================================
pause
