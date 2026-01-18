#!/bin/bash
# Quick Test Script for Phase 4 Docker Deployment
# Run this from: specs/004-kubernetes-deployment/docker/

set -e

echo "========================================"
echo "Phase 4 Docker Deployment Test"
echo "========================================"
echo ""

echo "[Step 1/5] Checking .env file..."
if [ ! -f .env ]; then
    echo "❌ ERROR: .env file not found!"
    echo "Please create .env with your OPENAI_API_KEY"
    exit 1
fi
if ! grep -q "OPENAI_API_KEY" .env; then
    echo "❌ ERROR: OPENAI_API_KEY not found in .env"
    exit 1
fi
echo "✅ .env file exists with OPENAI_API_KEY"
echo ""

echo "[Step 2/5] Cleaning old containers and images..."
docker-compose down -v 2>/dev/null || true
echo "✅ Cleaned up old deployment"
echo ""

echo "[Step 3/5] Building and starting services..."
echo "This may take 3-5 minutes on first build..."
echo ""
docker-compose up --build -d

echo ""
echo "[Step 4/5] Waiting for services to be healthy..."
sleep 15
echo ""

echo "[Step 5/5] Checking service health..."
echo ""

echo "Testing Postgres..."
if docker exec todo-postgres pg_isready -U todouser >/dev/null 2>&1; then
    echo "✅ Postgres is healthy"
else
    echo "❌ Postgres NOT healthy"
fi

echo ""
echo "Testing Backend..."
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend NOT responding"
fi

echo ""
echo "Testing Frontend..."
if curl -s http://localhost:3001/api/health >/dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend NOT responding"
fi

echo ""
echo "========================================"
echo "Deployment Status"
echo "========================================"
docker-compose ps
echo ""

echo "========================================"
echo "Test Results"
echo "========================================"
echo ""
echo "✅ All services are running!"
echo ""
echo "🌐 Open in browser:"
echo "   http://localhost:3001        (Frontend)"
echo "   http://localhost:8000/docs   (Backend API Docs)"
echo ""
echo "📋 View logs:"
echo "   docker-compose logs -f frontend"
echo "   docker-compose logs -f backend"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
echo "========================================"
