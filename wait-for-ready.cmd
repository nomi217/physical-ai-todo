@echo off
echo ========================================
echo Waiting for Pods to be Ready
echo ========================================
echo.

set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml

echo Checking current status...
kubectl get pods -n production

echo.
echo Waiting for backend to be ready...
kubectl wait --for=condition=ready pod -l app=todo-backend -n production --timeout=5m

echo.
echo Waiting for frontend to be ready...
kubectl wait --for=condition=ready pod -l app=todo-frontend -n production --timeout=5m

echo.
echo All pods ready! Checking status...
kubectl get pods -n production

echo.
echo Testing health endpoint...
curl -s http://161-35-250-151.nip.io/health
echo.

echo.
echo Testing frontend...
curl -s -I http://161-35-250-151.nip.io/
echo.

echo ========================================
echo Pods are ready! Test now:
echo   http://161-35-250-151.nip.io
echo ========================================
pause
