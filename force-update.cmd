@echo off
echo ========================================
echo Force Updating Frontend and Backend
echo ========================================
echo.

set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml

echo [1/4] Deleting frontend pods (will force pull new image)...
kubectl delete pod -n production -l app=todo-frontend

echo.
echo [2/4] Deleting backend pods (will force pull new image)...
kubectl delete pod -n production -l app=todo-backend

echo.
echo [3/4] Waiting for new pods to start...
timeout /t 30 /nobreak

echo.
echo [4/4] Checking pod status...
kubectl get pods -n production

echo.
echo ========================================
echo Update Complete!
echo ========================================
echo.
echo Test now:
echo   1. Clear browser cookies (Ctrl+Shift+Delete)
echo   2. Go to: http://161-35-250-151.nip.io/auth/signup
echo   3. Use NEW email (not alishbafatima73@gmail.com)
echo   4. Should auto-login to dashboard!
echo.
pause
