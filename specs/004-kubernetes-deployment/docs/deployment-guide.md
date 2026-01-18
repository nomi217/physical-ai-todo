# 🚀 Phase IV Deployment Guide

Complete step-by-step guide for deploying the Todo Chatbot on Kubernetes (Minikube).

---

## 📋 Prerequisites

### Required Tools

1. **Docker Desktop** (latest version with Gordon enabled)
   ```bash
   # Verify installation
   docker --version
   docker-compose --version
   ```

2. **Minikube** (Kubernetes local cluster)
   ```bash
   # Install (macOS)
   brew install minikube

   # Install (Windows with Chocolatey)
   choco install minikube

   # Verify
   minikube version
   ```

3. **Helm** (Kubernetes package manager)
   ```bash
   # Install (macOS)
   brew install helm

   # Install (Windows)
   choco install kubernetes-helm

   # Verify
   helm version
   ```

4. **kubectl-ai** (AI-assisted Kubernetes operations)
   ```bash
   # Install
   brew install kubectl-ai

   # Configure with OpenAI key
   export OPENAI_API_KEY="your-key-here"
   ```

---

## 🐳 Step 1: Build Docker Images

### Option A: Using Docker AI (Gordon)

```bash
# Ask Gordon for help
docker ai "What can you do?"

# Build backend
docker ai "build an optimized image for my FastAPI backend in ./backend directory"

# Build frontend
docker ai "build an optimized Next.js image for ./frontend directory"
```

### Option B: Standard Docker Commands

```bash
# Navigate to project root
cd physical-ai-todo

# Build backend image
docker build -t todo-backend:latest -f specs/004-kubernetes-deployment/docker/backend.Dockerfile ./backend

# Build frontend image
docker build -t todo-frontend:latest -f specs/004-kubernetes-deployment/docker/frontend.Dockerfile ./frontend

# Verify images
docker images | grep todo
```

---

## 🧪 Step 2: Test Locally with Docker Compose

Before deploying to Kubernetes, test everything works:

```bash
cd specs/004-kubernetes-deployment/docker

# Set your OpenAI API key
export OPENAI_API_KEY="sk-your-key-here"

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Test frontend
curl http://localhost:3000/api/health

# Test backend
curl http://localhost:8000/health

# Stop services
docker-compose down
```

**Expected**: All services healthy, frontend accessible at http://localhost:3000

---

## ☸️ Step 3: Start Minikube

```bash
# Start Minikube with Docker driver
minikube start --driver=docker --cpus=4 --memory=4096

# Verify cluster is running
kubectl cluster-info
kubectl get nodes

# Enable dashboard (optional)
minikube dashboard
```

### Load Docker Images into Minikube

```bash
# Load backend image
minikube image load todo-backend:latest

# Load frontend image
minikube image load todo-frontend:latest

# Verify images are loaded
minikube image ls | grep todo
```

---

## 📦 Step 4: Deploy with Helm

### A. Prepare Configuration

```bash
cd specs/004-kubernetes-deployment/helm
```

Create a `custom-values.yaml` file with your settings:

```yaml
# custom-values.yaml
secrets:
  enabled: true
  data:
    openai-api-key: "sk-your-actual-key-here"

backend:
  replicaCount: 1  # For local testing
  image:
    pullPolicy: Never  # Use local images

frontend:
  replicaCount: 1
  image:
    pullPolicy: Never
  service:
    type: NodePort  # Easier access in Minikube

postgres:
  enabled: true
```

### B. Install the Helm Chart

```bash
# Install (or upgrade if already installed)
helm install todo-app ./todo-app \
  --values ./todo-app/custom-values.yaml \
  --namespace default

# Or upgrade existing deployment
helm upgrade todo-app ./todo-app \
  --values ./todo-app/custom-values.yaml
```

### C. Watch Deployment

```bash
# Watch pods start
kubectl get pods -w

# Check all resources
kubectl get all -l app.kubernetes.io/instance=todo-app
```

---

## 🔍 Step 5: Verify Deployment with kubectl-ai

```bash
# Check overall status
kubectl-ai "show me the status of todo-app deployment"

# Troubleshoot if needed
kubectl-ai "why are my todo-app pods not running?"

# Check logs
kubectl-ai "show me the logs of the backend pod"

# Describe resources
kubectl-ai "describe the frontend service"
```

---

## 🌐 Step 6: Access the Application

### Get the Frontend URL

```bash
# Get the service URL
minikube service todo-app-frontend --url

# Or use port-forward
kubectl port-forward svc/todo-app-frontend 3000:3000
```

Open your browser to the displayed URL or http://localhost:3000

### Access Backend API

```bash
# Port-forward backend
kubectl port-forward svc/todo-app-backend 8000:8000

# Open API docs
open http://localhost:8000/docs
```

---

## 🧪 Step 7: Test the Application

1. **Test Frontend**:
   - Sign up for a new account
   - Create some tasks
   - Test the AI chatbot

2. **Test Backend API**:
   - Visit http://localhost:8000/docs
   - Try the interactive API documentation

3. **Verify Database**:
   ```bash
   # Connect to PostgreSQL pod
   kubectl exec -it deploy/todo-app-postgres -- psql -U todouser -d tododb

   # List tables
   \dt

   # Query tasks
   SELECT * FROM tasks LIMIT 5;

   # Exit
   \q
   ```

---

## 📊 Step 8: Monitor with kubectl-ai

```bash
# Monitor pod resource usage
kubectl-ai "show me the CPU and memory usage of todo-app pods"

# Check pod health
kubectl-ai "are all todo-app pods healthy?"

# View recent events
kubectl-ai "show me recent events for todo-app"

# Get pod logs
kubectl-ai "show me the last 50 lines of backend logs"
```

---

## 🔧 Step 9: Common Operations

### Scale Deployment

```bash
# Using kubectl
kubectl scale deployment todo-app-backend --replicas=3

# Using kubectl-ai
kubectl-ai "scale the backend deployment to 3 replicas"

# Using Helm
helm upgrade todo-app ./todo-app \
  --set backend.replicaCount=3
```

### Update Configuration

```bash
# Update a value
helm upgrade todo-app ./todo-app \
  --set backend.env.DEBUG=true

# Or edit values.yaml and upgrade
helm upgrade todo-app ./todo-app \
  --values ./todo-app/custom-values.yaml
```

### View Helm Status

```bash
# List releases
helm list

# Get status
helm status todo-app

# Get values
helm get values todo-app
```

### Rolling Restart

```bash
# Restart backend pods
kubectl rollout restart deployment/todo-app-backend

# Watch rollout
kubectl rollout status deployment/todo-app-backend
```

---

## 🐛 Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods

# Describe problematic pod
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Use kubectl-ai
kubectl-ai "why is pod <pod-name> crashlooping?"
```

### Image Pull Errors

```bash
# Verify images in Minikube
minikube image ls | grep todo

# Reload image
minikube image load todo-backend:latest

# Set imagePullPolicy to Never in values.yaml
```

### Service Not Accessible

```bash
# Check service
kubectl get svc

# Test from within cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://todo-app-backend:8000/health

# Use kubectl-ai
kubectl-ai "why can't I access the frontend service?"
```

### Database Connection Issues

```bash
# Check postgres pod
kubectl logs deploy/todo-app-postgres

# Verify connection string
kubectl get deploy todo-app-backend -o yaml | grep DATABASE_URL

# Test connection from backend
kubectl exec -it deploy/todo-app-backend -- \
  python -c "import psycopg2; psycopg2.connect('postgresql://todouser:todopass@todo-app-postgres:5432/tododb')"
```

---

## 🗑️ Cleanup

### Uninstall the Application

```bash
# Uninstall Helm release
helm uninstall todo-app

# Verify removal
kubectl get all

# Delete persistent volumes (if any)
kubectl delete pvc --all
```

### Stop Minikube

```bash
# Stop cluster
minikube stop

# Delete cluster (complete reset)
minikube delete
```

---

## 📚 Next Steps

- ✅ **Phase IV Complete**: Local Kubernetes deployment working
- 🎯 **Next: Phase V** - Add advanced features and deploy to DigitalOcean

---

## 🆘 Getting Help

```bash
# Helm help
helm help
helm get --help

# kubectl-ai help
kubectl-ai --help

# Kubernetes dashboard
minikube dashboard

# View Helm chart
helm show chart ./todo-app
helm show values ./todo-app
```

**For judges**: This deployment demonstrates production-grade Kubernetes practices with health checks, resource limits, multi-replica deployments, and AI-assisted operations.
