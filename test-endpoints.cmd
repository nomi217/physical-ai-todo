@echo off
echo ========================================
echo Testing All Endpoints
echo ========================================
echo.

echo [1/8] Testing Health Endpoint...
echo URL: http://161-35-250-151.nip.io/health
curl -s http://161-35-250-151.nip.io/health
echo.
echo.

echo [2/8] Testing API Root...
echo URL: http://161-35-250-151.nip.io/api/v1/
curl -s http://161-35-250-151.nip.io/api/v1/
echo.
echo.

echo [3/8] Testing Frontend Root...
echo URL: http://161-35-250-151.nip.io/
curl -s -I http://161-35-250-151.nip.io/
echo.

echo [4/8] Testing Auth Endpoints (Should return 405 or 422)...
echo URL: http://161-35-250-151.nip.io/api/v1/auth/register
curl -s -X GET http://161-35-250-151.nip.io/api/v1/auth/register
echo.
echo.

echo [5/8] Testing CORS Headers...
echo URL: http://161-35-250-151.nip.io/api/v1/
curl -s -I -H "Origin: http://161-35-250-151.nip.io" http://161-35-250-151.nip.io/api/v1/
echo.

echo [6/8] Checking Frontend Pod Logs...
set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml
kubectl logs -n production deployment/todo-frontend --tail=20
echo.

echo [7/8] Checking if Frontend Image is Updated...
kubectl get pod -n production -l app=todo-frontend -o jsonpath="{.items[0].spec.containers[0].image}"
echo.
echo.

echo [8/8] Checking if Backend Image is Updated...
kubectl get pod -n production -l app=todo-backend -o jsonpath="{.items[0].spec.containers[0].image}"
echo.
echo.

echo ========================================
echo Test Complete!
echo ========================================
pause
