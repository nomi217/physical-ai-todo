# Production Deployment to DigitalOcean Kubernetes (DOKS)

## Prerequisites
- [ ] DigitalOcean account with $200 credit
- [ ] `doctl` CLI installed and authenticated
- [ ] DOKS cluster created (2 nodes, s-2vcpu-4gb)
- [ ] Container registry created
- [ ] `kubectl` configured to access DOKS cluster
- [ ] Nginx Ingress Controller installed

## Quick Deploy Steps

### 1. Get LoadBalancer IP
```bash
kubectl get service -n ingress-nginx ingress-nginx-controller

# Copy the EXTERNAL-IP (e.g., 157.230.123.45)
```

### 2. Update Configuration Files

**Update `configmaps/app-config.yaml`:**
```yaml
FRONTEND_URL: "http://157-230-123-45.nip.io"  # Replace with your LoadBalancer IP
```

**Update `ingress/nginx-ingress.yaml`:**
```yaml
- host: 157-230-123-45.nip.io  # Replace with your LoadBalancer IP
```

**Update `deployments/backend.yaml` and `deployments/frontend.yaml`:**
```yaml
image: registry.digitalocean.com/YOUR_REGISTRY_NAME/todo-backend:latest
# Replace YOUR_REGISTRY_NAME with your actual registry name
```

### 3. Create Secrets

**Option A: From template (edit values first)**
```bash
# Edit configmaps/secrets-template.yaml with real values
kubectl apply -f configmaps/secrets-template.yaml
```

**Option B: From command line (recommended)**
```bash
kubectl create secret generic app-secrets \
  --namespace=production \
  --from-literal=DATABASE_URL="your-neon-postgres-url" \
  --from-literal=JWT_SECRET="$(openssl rand -hex 32)" \
  --from-literal=RESEND_API_KEY="re_72HMJyBA_6kgNsLvKR4T9mWv6oytD5x7X" \
  --from-literal=OPENAI_API_KEY="your-openai-key" \
  --from-literal=GITHUB_CLIENT_ID="your-github-id" \
  --from-literal=GITHUB_CLIENT_SECRET="your-github-secret"
```

### 4. Build and Push Docker Images

```bash
# Build images
docker build -f specs/004-kubernetes-deployment/docker/frontend.Dockerfile -t todo-frontend:prod .
docker build -f backend/Dockerfile -t todo-backend:prod .

# Tag for DO registry
docker tag todo-frontend:prod registry.digitalocean.com/YOUR_REGISTRY_NAME/todo-frontend:latest
docker tag todo-backend:prod registry.digitalocean.com/YOUR_REGISTRY_NAME/todo-backend:latest

# Login to registry
doctl registry login

# Push images
docker push registry.digitalocean.com/YOUR_REGISTRY_NAME/todo-frontend:latest
docker push registry.digitalocean.com/YOUR_REGISTRY_NAME/todo-backend:latest
```

### 5. Deploy to Kubernetes

```bash
# Apply in order
kubectl apply -f namespace.yaml
kubectl apply -f configmaps/app-config.yaml
# (Secrets already created in step 3)
kubectl apply -f deployments/backend.yaml
kubectl apply -f deployments/frontend.yaml
kubectl apply -f ingress/nginx-ingress.yaml

# Watch deployment
kubectl get pods -n production --watch
```

### 6. Verify Deployment

```bash
# Check pods
kubectl get pods -n production

# Check services
kubectl get svc -n production

# Check ingress
kubectl get ingress -n production

# View logs
kubectl logs -n production deployment/todo-backend
kubectl logs -n production deployment/todo-frontend

# Test health endpoint
curl http://YOUR_IP.nip.io/health
curl http://YOUR_IP.nip.io/api/v1/health
```

### 7. Access Your App

Open browser: **http://YOUR_LOADBALANCER_IP.nip.io**

Example: `http://157-230-123-45.nip.io`

---

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod -n production POD_NAME
kubectl logs -n production POD_NAME
```

### ImagePullBackOff error
```bash
# Verify registry access
doctl registry login

# Check image exists
doctl registry repository list-v2

# Update deployment with correct image name
kubectl edit deployment -n production todo-backend
```

### Ingress not working
```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress resource
kubectl describe ingress -n production todo-app-ingress

# Verify LoadBalancer IP
kubectl get svc -n ingress-nginx ingress-nginx-controller
```

### Database connection issues
```bash
# Check secrets
kubectl get secret -n production app-secrets -o yaml

# Test database connection from pod
kubectl exec -n production deployment/todo-backend -- python -c "from app.database import engine; print('Connected!' if engine else 'Failed')"
```

---

## Update Deployment

```bash
# Build new images
docker build -f specs/004-kubernetes-deployment/docker/frontend.Dockerfile -t todo-frontend:prod .
docker tag todo-frontend:prod registry.digitalocean.com/YOUR_REGISTRY_NAME/todo-frontend:latest
docker push registry.digitalocean.com/YOUR_REGISTRY_NAME/todo-frontend:latest

# Force pods to pull new image
kubectl rollout restart deployment/todo-frontend -n production
kubectl rollout restart deployment/todo-backend -n production

# Watch rollout
kubectl rollout status deployment/todo-frontend -n production
```

---

## Cleanup

```bash
# Delete all resources in production namespace
kubectl delete namespace production

# Delete cluster (stops all charges)
doctl kubernetes cluster delete physical-ai-todo

# Delete registry
doctl registry delete YOUR_REGISTRY_NAME
```

---

## Costs

**Running:**
- 2 nodes × $24/month = $48/month
- LoadBalancer = $12/month
- Registry = $5/month
- **Total: ~$65/month** (covered by $200 credit for ~3 months)

**After Hackathon:**
- Scale down to 1 node: ~$41/month
- Or delete cluster: $0/month
