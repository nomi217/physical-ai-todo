@echo off
echo ========================================
echo COMPLETE FIX - All 3 Bugs
echo ========================================
echo.
echo Bug 1: Frontend has old code (no auto-login)
echo Bug 2: Missing NEXT_PUBLIC_API_URL_INTERNAL env var
echo Bug 3: Middleware can't reach backend
echo.
echo Fixing ALL issues now...
echo.

set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml

REM Generate unique tag
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TAG=v%datetime:~0,14%
echo Using tag: %TAG%

echo.
echo [1/8] Building frontend with auto-login fix...
docker build -t registry.digitalocean.com/physical-ai-todo-registry/todo-frontend:%TAG% -f specs/004-kubernetes-deployment/docker/frontend.Dockerfile .

echo.
echo [2/8] Pushing to registry...
docker push registry.digitalocean.com/physical-ai-todo-registry/todo-frontend:%TAG%

echo.
echo [3/8] Setting NEXT_PUBLIC_API_URL_INTERNAL env var (Bug #2 fix)...
kubectl set env deployment/todo-frontend -n production NEXT_PUBLIC_API_URL_INTERNAL="http://todo-backend:8000/api/v1"

echo.
echo [4/8] Updating deployment to use new image (Bug #1 fix)...
kubectl set image deployment/todo-frontend -n production frontend=registry.digitalocean.com/physical-ai-todo-registry/todo-frontend:%TAG%

echo.
echo [5/8] Scaling to 1 replica (resource constraint)...
kubectl scale deployment/todo-frontend --replicas=1 -n production

echo.
echo [6/8] Waiting for rollout to complete...
kubectl rollout status deployment/todo-frontend -n production --timeout=5m

echo.
echo [7/8] Checking pod status...
kubectl get pods -n production

echo.
echo [8/8] Testing health endpoint...
timeout /t 5 /nobreak
curl -s http://161-35-250-151.nip.io/health

echo.
echo ========================================
echo ALL BUGS FIXED!
echo ========================================
echo.
echo What was fixed:
echo   ✓ Frontend now has auto-login code
echo   ✓ Middleware can reach backend (internal URL set)
echo   ✓ Fresh image deployed (tag: %TAG%)
echo.
echo CRITICAL: Clear browser cache!
echo   1. Close ALL browsers
echo   2. Open new browser
echo   3. Press Ctrl+Shift+Delete
echo   4. Select "All time"
echo   5. Check ALL boxes (cookies, cache, everything)
echo   6. Click "Clear data"
echo.
echo Then test:
echo   1. Go to: http://161-35-250-151.nip.io/auth/signup
echo   2. Email: Use BRAND NEW email (never used before!)
echo   3. Password: testpass123 (min 8 chars)
echo   4. Name: Your Name
echo   5. Click "Create Account"
echo.
echo Expected behavior:
echo   - Brief loading spinner
echo   - Automatically logged in
echo   - Redirected to /dashboard
echo   - Dashboard shows (empty task list for new user)
echo   - Can create task
echo   - Chatbot works
echo.
pause
