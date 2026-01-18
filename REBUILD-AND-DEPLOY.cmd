@echo off
echo ========================================
echo REBUILD FRONTEND WITH UNIQUE TAG
echo ========================================
echo.

REM Get timestamp for unique tag
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TAG=%datetime:~0,8%-%datetime:~8,6%
echo Using tag: %TAG%

echo.
echo [1/6] Building frontend with tag: %TAG%...
docker build -t registry.digitalocean.com/physical-ai-todo-registry/todo-frontend:%TAG% -f specs/004-kubernetes-deployment/docker/frontend.Dockerfile .

echo.
echo [2/6] Pushing image to registry...
docker push registry.digitalocean.com/physical-ai-todo-registry/todo-frontend:%TAG%

echo.
echo [3/6] Updating deployment to use new tag...
set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml
kubectl set image deployment/todo-frontend -n production frontend=registry.digitalocean.com/physical-ai-todo-registry/todo-frontend:%TAG%

echo.
echo [4/6] Waiting for rollout to complete...
kubectl rollout status deployment/todo-frontend -n production --timeout=5m

echo.
echo [5/6] Checking pod status...
kubectl get pods -n production

echo.
echo [6/6] Testing frontend...
timeout /t 5 /nobreak
curl -s http://161-35-250-151.nip.io/health

echo.
echo ========================================
echo DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Frontend is now running with code that includes:
echo   - Auto-login after signup (no email verification)
echo   - Correct API URL: http://161-35-250-151.nip.io/api/v1
echo.
echo NOW TEST:
echo   1. Clear browser cache (Ctrl+Shift+Delete, All time, ALL boxes)
echo   2. Go to: http://161-35-250-151.nip.io/auth/signup
echo   3. Use NEW email you've never used
echo   4. After clicking "Create Account", you should:
echo      - See a brief loading spinner
echo      - Be automatically logged in
echo      - Land on dashboard page
echo.
echo If still not working:
echo   - Open browser console (F12)
echo   - Try signup again
echo   - Screenshot any errors
echo   - Show me the screenshot
echo.
pause
