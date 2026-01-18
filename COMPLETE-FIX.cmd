@echo off
echo ========================================
echo COMPLETE FIX - Frontend and Backend
echo ========================================
echo.

set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml

echo [1/7] Scaling deployments to 1 replica...
kubectl scale deployment/todo-backend --replicas=1 -n production
kubectl scale deployment/todo-frontend --replicas=1 -n production

echo.
echo [2/7] Deleting ALL frontend pods (force new image pull)...
kubectl delete pod -n production -l app=todo-frontend --force --grace-period=0

echo.
echo [3/7] Deleting ALL backend pods (force new image pull)...
kubectl delete pod -n production -l app=todo-backend --force --grace-period=0

echo.
echo [4/7] Waiting 45 seconds for pods to start...
timeout /t 45 /nobreak

echo.
echo [5/7] Checking pod status...
kubectl get pods -n production

echo.
echo [6/7] Testing backend health...
curl -s http://161-35-250-151.nip.io/health
echo.

echo.
echo [7/7] Testing frontend...
curl -s -I http://161-35-250-151.nip.io/ | findstr "HTTP location"

echo.
echo ========================================
echo FIX COMPLETE!
echo ========================================
echo.
echo CRITICAL: Clear browser completely before testing!
echo.
echo 1. Close ALL browser windows
echo 2. Open new browser
echo 3. Press Ctrl+Shift+Delete
echo 4. Clear: Cookies, Cache, ALL data, "All time"
echo 5. Click "Clear data"
echo.
echo Then test:
echo   - Sign Up: http://161-35-250-151.nip.io/auth/signup
echo   - Use BRAND NEW email (never used before)
echo   - Should AUTO-LOGIN to dashboard!
echo.
echo If dashboard loads but is empty:
echo   - Create a task manually
echo   - Open chat and ask "What tasks do I have?"
echo   - Chat will show your tasks!
echo.
pause
