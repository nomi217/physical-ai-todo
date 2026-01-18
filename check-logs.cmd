@echo off
set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml

echo ========================================
echo Backend Logs (Last 100 lines)
echo ========================================
kubectl logs -n production deployment/todo-backend --tail=100

echo.
echo ========================================
echo Frontend Logs (Last 50 lines)
echo ========================================
kubectl logs -n production deployment/todo-frontend --tail=50

pause
