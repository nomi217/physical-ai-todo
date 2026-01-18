@echo off
echo ========================================
echo FORCE FRESH IMAGE PULL
echo ========================================
echo.

set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml

echo [1/6] Reapplying frontend deployment YAML...
kubectl apply -f kubernetes/production/deployments/frontend.yaml

echo.
echo [2/6] Deleting frontend pods to force fresh image pull...
kubectl delete pod -n production -l app=todo-frontend --force --grace-period=0

echo.
echo [3/6] Waiting 60 seconds for new pod to start and pull image...
timeout /t 60 /nobreak

echo.
echo [4/6] Checking pod status...
kubectl get pods -n production

echo.
echo [5/6] Checking pod image details...
kubectl get pod -n production -l app=todo-frontend -o jsonpath="{.items[0].spec.containers[0].image}"
echo.
kubectl get pod -n production -l app=todo-frontend -o jsonpath="{.items[0].status.containerStatuses[0].imageID}"
echo.

echo.
echo [6/6] Testing frontend page...
curl -s http://161-35-250-151.nip.io/auth/signup | findstr -i "FlowTask"

echo.
echo ========================================
echo Done! Now test in browser:
echo ========================================
echo.
echo 1. Close ALL browsers
echo 2. Open fresh browser
echo 3. Go to: http://161-35-250-151.nip.io/auth/signup
echo 4. Sign up with NEW email
echo 5. Should auto-login to dashboard!
echo.
echo If "Go to Dashboard" still doesn't work:
echo   - Open browser console (F12)
echo   - Click "Go to Dashboard"
echo   - Check for JavaScript errors
echo   - Take screenshot and show me
echo.
pause
