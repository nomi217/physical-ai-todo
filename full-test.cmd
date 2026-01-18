@echo off
echo ========================================
echo Full Application Test
echo ========================================
echo.

set BASE_URL=http://161-35-250-151.nip.io
set TEST_EMAIL=test_%RANDOM%@example.com
set TEST_PASSWORD=testpass123
set TEST_NAME=Test User

echo Using test email: %TEST_EMAIL%
echo.

echo [1/7] Testing user registration...
curl -s -X POST "%BASE_URL%/api/v1/auth/register" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"%TEST_EMAIL%\",\"password\":\"%TEST_PASSWORD%\",\"full_name\":\"%TEST_NAME%\"}" ^
  -c cookies.txt
echo.
echo.

echo [2/7] Testing user login...
curl -s -X POST "%BASE_URL%/api/v1/auth/login" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"%TEST_EMAIL%\",\"password\":\"%TEST_PASSWORD%\"}" ^
  -c cookies.txt -b cookies.txt
echo.
echo.

echo [3/7] Testing get current user (auth/me)...
curl -s "%BASE_URL%/api/v1/auth/me" -b cookies.txt
echo.
echo.

echo [4/7] Testing get tasks...
curl -s "%BASE_URL%/api/v1/tasks" -b cookies.txt
echo.
echo.

echo [5/7] Testing create task...
curl -s -X POST "%BASE_URL%/api/v1/tasks" ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Test Task\",\"description\":\"Testing API\",\"priority\":\"medium\"}" ^
  -b cookies.txt
echo.
echo.

echo [6/7] Testing chat message...
curl -s -X POST "%BASE_URL%/api/v1/chat/messages" ^
  -H "Content-Type: application/json" ^
  -d "{\"message\":\"Hello AI\"}" ^
  -b cookies.txt
echo.
echo.

echo [7/7] Checking backend logs for errors...
set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml
kubectl logs -n production deployment/todo-backend --tail=50 | findstr -i "error exception traceback"

echo.
echo ========================================
echo Test Complete!
echo ========================================
echo.
echo If you see errors above, that's the issue!
echo If you see "Not Found" for tasks/chat, those endpoints might not exist.
echo.
pause
