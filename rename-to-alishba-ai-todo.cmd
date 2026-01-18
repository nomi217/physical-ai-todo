@echo off
echo ========================================
echo Rename App to alishba-ai-todo
echo ========================================
echo.
echo New URL: http://alishba-ai-todo.161-35-250-151.nip.io
echo.

set NEW_HOST=alishba-ai-todo.161-35-250-151.nip.io
set NEW_URL=http://alishba-ai-todo.161-35-250-151.nip.io
set NEW_API_URL=http://alishba-ai-todo.161-35-250-151.nip.io/api/v1

REM Generate unique tag
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TAG=v%datetime:~0,14%

echo [1/9] Updating Kubernetes Ingress...
set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml

REM Create temporary ingress file with new hostname
(
echo apiVersion: networking.k8s.io/v1
echo kind: Ingress
echo metadata:
echo   name: todo-app-ingress
echo   namespace: production
echo   annotations:
echo     nginx.ingress.kubernetes.io/rewrite-target: /
echo spec:
echo   ingressClassName: nginx
echo   rules:
echo   - host: %NEW_HOST%
echo     http:
echo       paths:
echo       - path: /api
echo         pathType: Prefix
echo         backend:
echo           service:
echo             name: todo-backend
echo             port:
echo               number: 8000
echo       - path: /health
echo         pathType: Prefix
echo         backend:
echo           service:
echo             name: todo-backend
echo             port:
echo               number: 8000
echo       - path: /
echo         pathType: Prefix
echo         backend:
echo           service:
echo             name: todo-frontend
echo             port:
echo               number: 3000
) > temp-ingress.yaml

kubectl apply -f temp-ingress.yaml
del temp-ingress.yaml

echo.
echo [2/9] Updating Frontend Dockerfile with new API URL...
REM This step is just informational - we'll set env var in build command

echo.
echo [3/9] Updating ConfigMap with new frontend URL...
(
echo apiVersion: v1
echo kind: ConfigMap
echo metadata:
echo   name: app-config
echo   namespace: production
echo data:
echo   FRONTEND_URL: "%NEW_URL%"
echo   BACKEND_URL: "http://todo-backend:8000"
echo   NODE_ENV: "production"
echo   LOG_LEVEL: "info"
echo   CORS_ORIGINS: "%NEW_URL%,https://your-domain.com"
) > temp-configmap.yaml

kubectl apply -f temp-configmap.yaml
del temp-configmap.yaml

echo.
echo [4/9] Restarting backend to pick up new CORS origins...
kubectl rollout restart deployment/todo-backend -n production

echo.
echo [5/9] Building frontend with new URL (tag: %TAG%)...
docker build ^
  --build-arg NEXT_PUBLIC_API_URL=%NEW_API_URL% ^
  -t registry.digitalocean.com/physical-ai-todo-registry/todo-frontend:%TAG% ^
  -f specs/004-kubernetes-deployment/docker/frontend.Dockerfile .

echo.
echo [6/9] Pushing to registry...
docker push registry.digitalocean.com/physical-ai-todo-registry/todo-frontend:%TAG%

echo.
echo [7/9] Updating frontend deployment...
kubectl set env deployment/todo-frontend -n production NEXT_PUBLIC_API_URL_INTERNAL="http://todo-backend:8000/api/v1"
kubectl set image deployment/todo-frontend -n production frontend=registry.digitalocean.com/physical-ai-todo-registry/todo-frontend:%TAG%

echo.
echo [8/9] Waiting for rollout...
kubectl rollout status deployment/todo-frontend -n production --timeout=5m
kubectl rollout status deployment/todo-backend -n production --timeout=5m

echo.
echo [9/9] Testing new URL...
timeout /t 10 /nobreak
curl -s http://%NEW_HOST%/health
echo.

echo.
echo ========================================
echo RENAME COMPLETE!
echo ========================================
echo.
echo Your new URLs:
echo   Landing:   http://%NEW_HOST%
echo   Sign Up:   http://%NEW_HOST%/auth/signup
echo   Dashboard: http://%NEW_HOST%/dashboard
echo   Chat:      http://%NEW_HOST%/chat
echo   API:       http://%NEW_HOST%/api/v1/
echo   Health:    http://%NEW_HOST%/health
echo.
echo IMPORTANT: Clear browser cache before testing!
echo   1. Close all browsers
echo   2. Open new browser
echo   3. Ctrl+Shift+Delete -^> All time -^> Clear all
echo.
echo Then test:
echo   http://%NEW_HOST%/auth/signup
echo.
echo Share with judges:
echo   "Try my AI-powered task manager at:"
echo   "http://%NEW_HOST%"
echo   "No setup required - just sign up and explore!"
echo.
pause
