@echo off
echo ========================================
echo Diagnostic Report
echo ========================================
echo.

set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml

echo [1/5] Checking pod status...
kubectl get pods -n production

echo.
echo [2/5] Checking backend logs (last 30 lines)...
kubectl logs -n production deployment/todo-backend --tail=30

echo.
echo [3/5] Checking ingress configuration...
kubectl get ingress -n production

echo.
echo [4/5] Describing backend service...
kubectl describe svc todo-backend -n production

echo.
echo [5/5] Testing backend directly from within cluster...
kubectl exec -n production deployment/todo-backend -- curl -s http://localhost:8000/health

echo.
echo ========================================
echo Diagnostic Complete!
echo ========================================
pause
