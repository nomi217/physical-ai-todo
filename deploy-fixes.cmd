@echo off
echo ========================================
echo Deploying Auto-Login and CORS Fixes
echo ========================================
echo.

set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml

echo [1/4] Restarting backend deployment (CORS fix)...
kubectl rollout restart deployment/todo-backend -n production

echo.
echo [2/4] Waiting for backend to be ready...
kubectl rollout status deployment/todo-backend -n production --timeout=3m

echo.
echo [3/4] Restarting frontend deployment (Auto-login fix)...
kubectl rollout restart deployment/todo-frontend -n production

echo.
echo [4/4] Waiting for frontend to be ready...
kubectl rollout status deployment/todo-frontend -n production --timeout=3m

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Fixes Applied:
echo   ✓ Frontend: Auto-login after signup (no email verification)
echo   ✓ Backend: CORS now allows production domain
echo.
echo Your app is ready at: http://161-35-250-151.nip.io
echo.
echo Testing URLs:
echo   - Landing: http://161-35-250-151.nip.io/landing
echo   - Sign Up: http://161-35-250-151.nip.io/auth/signup
echo   - Health: http://161-35-250-151.nip.io/api/v1/health
echo.
echo What to test:
echo   1. Sign up with NEW email - should auto-login
echo   2. Access dashboard - should work now
echo   3. Test chatbot - should work now
echo   4. Health endpoint - should show status
echo.
pause
