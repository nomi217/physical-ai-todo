@echo off
echo ========================================
echo FINAL FRONTEND FIX - Using Image Hash
echo ========================================
echo.

set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml

echo [Step 1] Getting current frontend image digest...
for /f "tokens=*" %%i in ('docker images --digests registry.digitalocean.com/physical-ai-todo-registry/todo-frontend --format "{{.Digest}}"') do set IMAGE_DIGEST=%%i
echo Image digest: %IMAGE_DIGEST%

echo.
echo [Step 2] Updating deployment to use specific image digest...
kubectl set image deployment/todo-frontend -n production frontend=registry.digitalocean.com/physical-ai-todo-registry/todo-frontend@%IMAGE_DIGEST%

echo.
echo [Step 3] Forcing pod recreation...
kubectl delete pod -n production -l app=todo-frontend --force --grace-period=0

echo.
echo [Step 4] Waiting for new pod to be ready (this may take 2-3 minutes)...
kubectl wait --for=condition=ready pod -l app=todo-frontend -n production --timeout=5m

echo.
echo [Step 5] Verifying pod is running...
kubectl get pods -n production -l app=todo-frontend

echo.
echo [Step 6] Testing frontend...
timeout /t 5 /nobreak
curl -s -I http://161-35-250-151.nip.io/auth/signup | findstr "HTTP"

echo.
echo ========================================
echo Frontend Updated!
echo ========================================
echo.
echo IMPORTANT: Clear browser cache completely!
echo Then test: http://161-35-250-151.nip.io/auth/signup
echo.
pause
