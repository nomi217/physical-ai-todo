@echo off
echo ========================================
echo Updating Frontend with Auto-Login Fix
echo ========================================
echo.

set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml

echo [1/2] Restarting frontend deployment...
kubectl rollout restart deployment/todo-frontend -n production

echo.
echo [2/2] Waiting for new pods to be ready...
kubectl rollout status deployment/todo-frontend -n production --timeout=3m

echo.
echo ========================================
echo Frontend Updated Successfully!
echo ========================================
echo.
echo Your app is ready at: http://161-35-250-151.nip.io
echo.
echo Test signup now - you should be auto-logged in after creating account!
echo.
pause
