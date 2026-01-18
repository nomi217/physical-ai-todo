# Phase 4: Kubernetes Deployment Guide

## 🔧 Permanent Fix for "Failed to Fetch" Issues

### Problem
Minikube service tunnels use dynamic ports that change on every restart, breaking the frontend.

### Solution
Use Kubernetes Ingress with a fixed hostname (`todo.local`)

## Setup Instructions

### 1. Add Domain to Hosts File

**Windows** (Run as Administrator):
```cmd
notepad C:\Windows\System32\drivers\etc\hosts
```

Add this line:
```
127.0.0.1 todo.local
```

**Linux/Mac**:
```bash
sudo echo "127.0.0.1 todo.local" >> /etc/hosts
```

### 2. Enable Ingress (One-time setup)
```bash
minikube addons enable ingress
```

### 3. Apply Ingress Configuration
```bash
kubectl apply -f specs/004-kubernetes-deployment/kubernetes/ingress.yaml
```

### 4. Build and Deploy Frontend
```bash
# Build with fixed URL
docker build -f specs/004-kubernetes-deployment/docker/frontend.Dockerfile -t todo-frontend:v9 .

# Load into Minikube
minikube image load todo-frontend:v9

# Deploy
kubectl set image deployment/todo-app-frontend frontend=todo-frontend:v9
```

### 5. Start Minikube Tunnel
```bash
minikube tunnel
```

**Keep this terminal open!** The tunnel must stay running.

### 6. Access Your Application

- **Frontend**: http://todo.local
- **Backend API**: http://todo.local/api/v1

URLs never change - even after Minikube restarts! 🎉

## Daily Usage

After Minikube restart, just run:
```bash
minikube start
minikube tunnel  # Keep this running
```

Then access: **http://todo.local**

No rebuilding needed!

## Troubleshooting

### "This site can't be reached"
- Check `minikube tunnel` is running
- Verify hosts file has `127.0.0.1 todo.local`
- Run: `kubectl get ingress` to verify ingress exists

### GitHub OAuth Issues
Update callback URL to: `http://todo.local/auth/callback/github`

### Still getting "Failed to Fetch"
```bash
# Check backend is running
kubectl get pods

# Check ingress
kubectl describe ingress todo-app-ingress
```
