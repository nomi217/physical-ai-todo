@echo off
REM Restart frontend deployment with new image
set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml

echo Restarting frontend deployment...
kubectl rollout restart deployment/todo-frontend -n production

echo Waiting for rollout to complete...
kubectl rollout status deployment/todo-frontend -n production --timeout=3m

echo.
echo Frontend restarted successfully!
echo Check status: kubectl get pods -n production
