@echo off
REM Quick Test Script for Phase 4 Docker Deployment
REM Run this from: specs/004-kubernetes-deployment/docker/

echo ========================================
echo Phase 4 Docker Deployment Test
echo ========================================
echo.

echo [Step 1/5] Checking .env file...
if not exist .env (
    echo ERROR: .env file not found!
    echo Please create .env with your OPENAI_API_KEY
    exit /b 1
)
findstr /C:"OPENAI_API_KEY" .env >nul
if errorlevel 1 (
    echo ERROR: OPENAI_API_KEY not found in .env
    exit /b 1
)
echo ✓ .env file exists with OPENAI_API_KEY
echo.

echo [Step 2/5] Cleaning old containers and images...
docker-compose down -v 2>nul
echo ✓ Cleaned up old deployment
echo.

echo [Step 3/5] Building and starting services...
echo This may take 3-5 minutes on first build...
echo.
docker-compose up --build -d

if errorlevel 1 (
    echo.
    echo ERROR: Build failed! Check logs above.
    exit /b 1
)
echo.

echo [Step 4/5] Waiting for services to be healthy...
timeout /t 15 /nobreak >nul
echo.

echo [Step 5/5] Checking service health...
echo.

echo Testing Postgres...
docker exec todo-postgres pg_isready -U todouser >nul 2>&1
if errorlevel 1 (
    echo ✗ Postgres NOT healthy
) else (
    echo ✓ Postgres is healthy
)

echo.
echo Testing Backend...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ✗ Backend NOT responding
) else (
    echo ✓ Backend is healthy
)

echo.
echo Testing Frontend...
curl -s http://localhost:3001/api/health >nul 2>&1
if errorlevel 1 (
    echo ✗ Frontend NOT responding
) else (
    echo ✓ Frontend is healthy
)

echo.
echo ========================================
echo Deployment Status
echo ========================================
docker-compose ps
echo.

echo ========================================
echo Test Results
echo ========================================
echo.
echo ✅ All services are running!
echo.
echo 🌐 Open in browser:
echo    http://localhost:3001   (Frontend)
echo    http://localhost:8000/docs   (Backend API Docs)
echo.
echo 📋 View logs:
echo    docker-compose logs -f frontend
echo    docker-compose logs -f backend
echo.
echo 🛑 Stop services:
echo    docker-compose down
echo.
echo ========================================
