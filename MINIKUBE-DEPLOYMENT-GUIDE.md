# 🚀 Minikube Deployment Guide - Phase 4

**Status:** Ready to deploy your app to Kubernetes!

---

## 📋 Prerequisites Check

### ✅ Already Installed:
- ✅ Docker (v29.0.1)
- ✅ kubectl (v1.34.1)

### ❌ Need to Install:
- ❌ Minikube

---

## 🔧 Step 1: Install Minikube

### **Option A: Quick Install (Recommended)**

**Run this script:**
```bash
install-minikube.bat
```

**What it does:**
1. Downloads Minikube installer from official GitHub
2. Runs the installer (follow wizard)
3. Verifies installation

### **Option B: Manual Install**

1. **Download:** https://minikube.sigs.k8s.io/docs/start/
2. **Run installer** (follow wizard)
3. **Restart terminal**
4. **Verify:**
   ```bash
   minikube version
   ```

---

## 🚀 Step 2: Start Minikube

Once Minikube is installed:

```bash
# Start Minikube with Docker driver
minikube start --driver=docker --cpus=4 --memory=4096

# Verify it's running
minikube status
```

**Expected output:**
```
✅ minikube
✅ type: Control Plane
✅ host: Running
✅ kubelet: Running
✅ apiserver: Running
✅ kubeconfig: Configured
```

---

## 🐳 Step 3: Build Docker Images

```bash
# Navigate to project root
cd C:\Users\Ahsan\physical-ai-todo

# Build backend image
docker build -t todo-backend:latest ^
  -f specs/004-kubernetes-deployment/docker/backend.Dockerfile ^
  ./backend

# Build frontend image
docker build -t todo-frontend:latest ^
  -f specs/004-kubernetes-deployment/docker/frontend.Dockerfile ^
  ./frontend

# Verify images
docker images | findstr todo
```

**Expected:** Two images listed (todo-backend, todo-frontend)

---

## 📦 Step 4: Load Images into Minikube

```bash
# Load backend image
minikube image load todo-backend:latest

# Load frontend image
minikube image load todo-frontend:latest

# Verify images in Minikube
minikube image ls | findstr todo
```

---

## ⚙️ Step 5: Create Helm Values File

```bash
cd specs/004-kubernetes-deployment/helm

# Create custom values file
cat > custom-values.yaml <<EOF
# OpenAI API Key (REQUIRED - replace with your actual key)
secrets:
  enabled: true
  data:
    openai-api-key: "YOUR_OPENAI_API_KEY_HERE"

# Backend Configuration
backend:
  replicaCount: 1
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: Never  # Use local image (not pull from registry)

# Frontend Configuration
frontend:
  replicaCount: 1
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: Never  # Use local image
  service:
    type: NodePort  # Expose outside Minikube

# PostgreSQL Database
postgres:
  enabled: true
  storage:
    size: 1Gi
EOF
```

---

## 🎯 Step 6: Deploy with Helm

```bash
# Make sure you're in the helm directory
cd specs/004-kubernetes-deployment/helm

# Install the app
helm install todo-app ./todo-app -f custom-values.yaml

# Watch pods start
kubectl get pods -w
```

**Expected output:**
```
NAME                                 READY   STATUS    RESTARTS   AGE
todo-app-backend-xxxxx-xxxxx         1/1     Running   0          30s
todo-app-frontend-xxxxx-xxxxx        1/1     Running   0          30s
todo-app-postgres-0                  1/1     Running   0          30s
```

**Press Ctrl+C to stop watching**

---

## ✅ Step 7: Verify Deployment

```bash
# Check all resources
kubectl get all

# Check pods are healthy
kubectl get pods

# Check services
kubectl get svc

# View logs (if needed)
kubectl logs -l app.kubernetes.io/component=backend
kubectl logs -l app.kubernetes.io/component=frontend
```

---

## 🌐 Step 8: Access Your App

### **Option A: Port Forward (Recommended)**
```bash
# Forward frontend to localhost:3001
kubectl port-forward svc/todo-app-frontend 3001:3000

# Open browser
start http://localhost:3001
```

### **Option B: Minikube Service**
```bash
# Get frontend URL
minikube service todo-app-frontend --url

# Open in browser
minikube service todo-app-frontend
```

---

## 🎬 Step 9: Demo for Judges

Show judges these commands:

```bash
# 1. Show all running pods
kubectl get pods

# 2. Show services
kubectl get svc

# 3. Show deployments
kubectl get deployments

# 4. Use kubectl-ai (if installed)
kubectl-ai "show me my deployments"

# 5. Scale frontend
kubectl scale deployment todo-app-frontend --replicas=3

# 6. Watch auto-scaling
kubectl get pods -w
```

**Judge Reaction:** "Wow, running on Kubernetes with auto-scaling!"

---

## 🔧 Troubleshooting

### Issue: Pods Not Starting
```bash
# Check pod status
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Common fix: Wrong image pull policy
kubectl edit deployment todo-app-frontend
# Change imagePullPolicy to Never
```

### Issue: Database Connection Failed
```bash
# Check postgres pod
kubectl logs todo-app-postgres-0

# Verify secret
kubectl get secret todo-app-secrets -o yaml

# Restart backend
kubectl rollout restart deployment todo-app-backend
```

### Issue: Frontend Can't Reach Backend
```bash
# Test from within cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://todo-app-backend:8000/health

# Should return: {"status":"healthy"}
```

---

## 🧹 Cleanup (After Demo)

```bash
# Uninstall app
helm uninstall todo-app

# Delete all resources
kubectl delete all --all

# Stop Minikube
minikube stop

# Delete Minikube (if needed)
minikube delete
```

---

## 📸 Screenshot Checklist for Demo

Take screenshots of:
- [ ] `minikube status` - showing cluster running
- [ ] `kubectl get pods` - all pods Running
- [ ] `kubectl get svc` - services listed
- [ ] App running in browser (localhost:3001)
- [ ] `kubectl scale deployment` - scaling to 3 replicas
- [ ] `helm list` - showing todo-app installed

---

## 🎓 Talking Points for Judges

1. **"Production-ready Kubernetes deployment"**
   - Show Helm charts
   - Explain multi-stage Docker builds
   - Demonstrate health checks

2. **"Scalable architecture"**
   - Scale frontend: `kubectl scale deployment todo-app-frontend --replicas=5`
   - Show 5 pods running

3. **"Cloud-native design"**
   - Health checks for liveness/readiness
   - Resource limits and requests
   - ConfigMaps and Secrets

4. **"Professional DevOps practices"**
   - Helm for package management
   - kubectl-ai for operations
   - Proper namespacing and labels

---

## 🚀 Next Steps After Minikube

1. **Phase 5A:** Add advanced features (due dates, recurring tasks)
2. **Phase 5B:** Add Dapr components
3. **Phase 5C:** Deploy to DigitalOcean Kubernetes (cloud!)
4. **Phase 5D:** Add CI/CD with GitHub Actions

---

**Ready?** Start with: `install-minikube.bat`

Then come back here for Step 2! 🎉
