# Phase 5 Production Deployment Checklist

## ⏱️ Estimated Time: 2-3 hours

---

## Part 1: DigitalOcean Setup (30 minutes)

### Step 1: Install doctl CLI

- [ ] Download from: https://github.com/digitalocean/doctl/releases
- [ ] Extract and add to PATH
- [ ] Verify: `doctl version`

### Step 2: Create API Token

- [ ] Go to: https://cloud.digitalocean.com/account/api/tokens
- [ ] Click "Generate New Token"
- [ ] Name: `physical-ai-todo`
- [ ] Scopes: Read + Write
- [ ] Copy token (save it!)

### Step 3: Authenticate doctl

```bash
doctl auth init
# Paste your API token
```

- [ ] Verify: `doctl account get`

### Step 4: Create Container Registry

```bash
doctl registry create physical-ai-todo-registry
doctl registry login
```

- [ ] Registry created
- [ ] Logged in successfully

### Step 5: Create DOKS Cluster

**Option A: Via CLI (5-10 minutes)**
```bash
doctl kubernetes cluster create physical-ai-todo \
  --region nyc1 \
  --version 1.28.2-do.0 \
  --node-pool "name=worker-pool;size=s-2vcpu-4gb;count=2" \
  --wait
```

**Option B: Via Web UI**
1. Go to: https://cloud.digitalocean.com/kubernetes/clusters/new
2. Region: New York (NYC1)
3. Version: 1.28.x
4. Nodes: 2 × Basic ($24/mo)
5. Name: `physical-ai-todo`
6. Create (wait 5-10 min)

- [ ] Cluster created and running

### Step 6: Configure kubectl

```bash
doctl kubernetes cluster kubeconfig save physical-ai-todo
kubectl get nodes
```

- [ ] 2 nodes in "Ready" state

### Step 7: Install Nginx Ingress

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/do/deploy.yaml

# Wait for LoadBalancer IP (2-3 minutes)
kubectl get svc -n ingress-nginx ingress-nginx-controller --watch
```

- [ ] LoadBalancer has EXTERNAL-IP (not `<pending>`)
- [ ] Save LoadBalancer IP: `_________________`

---

## Part 2: Configuration (15 minutes)

### Step 8: Update Kubernetes Manifests

**File: `kubernetes/production/configmaps/app-config.yaml`**
```yaml
FRONTEND_URL: "http://YOUR_IP.nip.io"  # Replace YOUR_IP
```

- [ ] Updated with LoadBalancer IP (format: `157-230-123-45.nip.io`)

**File: `kubernetes/production/ingress/nginx-ingress.yaml`**
```yaml
- host: YOUR_IP.nip.io  # Replace YOUR_IP
```

- [ ] Updated with LoadBalancer IP

**File: `kubernetes/production/deployments/backend.yaml`**
```yaml
image: registry.digitalocean.com/physical-ai-todo-registry/todo-backend:latest
```

- [ ] Updated registry name

**File: `kubernetes/production/deployments/frontend.yaml`**
```yaml
image: registry.digitalocean.com/physical-ai-todo-registry/todo-frontend:latest
```

- [ ] Updated registry name

### Step 9: Update Frontend Dockerfile

**File: `specs/004-kubernetes-deployment/docker/frontend.Dockerfile`**
```dockerfile
ENV NEXT_PUBLIC_API_URL=http://YOUR_IP.nip.io/api/v1
```

- [ ] Updated with production API URL

### Step 10: Create Kubernetes Secrets

Get your Neon database URL from: https://console.neon.tech/

```bash
kubectl create secret generic app-secrets \
  --namespace=production \
  --from-literal=DATABASE_URL="postgresql://user:pass@host/db?sslmode=require" \
  --from-literal=JWT_SECRET="$(openssl rand -hex 32)" \
  --from-literal=RESEND_API_KEY="re_72HMJyBA_6kgNsLvKR4T9mWv6oytD5x7X" \
  --from-literal=OPENAI_API_KEY="your-openai-key-here" \
  --from-literal=GITHUB_CLIENT_ID="your-github-oauth-id" \
  --from-literal=GITHUB_CLIENT_SECRET="your-github-oauth-secret"
```

- [ ] Secrets created
- [ ] Verify: `kubectl get secret -n production app-secrets`

---

## Part 3: Build & Deploy (45 minutes)

### Step 11: Build Docker Images

```bash
# Build backend
cd backend
docker build -t todo-backend:prod .
cd ..

# Build frontend
docker build -f specs/004-kubernetes-deployment/docker/frontend.Dockerfile -t todo-frontend:prod .
```

- [ ] Backend image built
- [ ] Frontend image built

### Step 12: Tag & Push Images

```bash
# Tag images
docker tag todo-backend:prod registry.digitalocean.com/physical-ai-todo-registry/todo-backend:latest
docker tag todo-frontend:prod registry.digitalocean.com/physical-ai-todo-registry/todo-frontend:latest

# Push to registry
docker push registry.digitalocean.com/physical-ai-todo-registry/todo-backend:latest
docker push registry.digitalocean.com/physical-ai-todo-registry/todo-frontend:latest
```

- [ ] Backend pushed to registry
- [ ] Frontend pushed to registry
- [ ] Verify: `doctl registry repository list-v2`

### Step 13: Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f kubernetes/production/namespace.yaml
kubectl apply -f kubernetes/production/configmaps/app-config.yaml
kubectl apply -f kubernetes/production/deployments/backend.yaml
kubectl apply -f kubernetes/production/deployments/frontend.yaml
kubectl apply -f kubernetes/production/ingress/nginx-ingress.yaml

# Watch deployment
kubectl get pods -n production --watch
```

- [ ] Namespace created
- [ ] ConfigMap created
- [ ] Backend pods running (2/2)
- [ ] Frontend pods running (2/2)
- [ ] Ingress created

---

## Part 4: Verification (20 minutes)

### Step 14: Check Deployment Status

```bash
# Check pods
kubectl get pods -n production

# Check services
kubectl get svc -n production

# Check ingress
kubectl get ingress -n production

# View backend logs
kubectl logs -n production deployment/todo-backend --tail=50

# View frontend logs
kubectl logs -n production deployment/todo-frontend --tail=50
```

- [ ] All pods in "Running" state
- [ ] Services have ClusterIPs
- [ ] Ingress has host configured
- [ ] No error logs

### Step 15: Test Health Endpoints

```bash
# Replace YOUR_IP with your LoadBalancer IP
curl http://YOUR_IP.nip.io/health
curl http://YOUR_IP.nip.io/api/v1/health
```

- [ ] Backend health returns: `{"status":"healthy"}`
- [ ] Frontend loads successfully

### Step 16: Full Application Testing

Open browser: **http://YOUR_IP.nip.io**

- [ ] Landing page loads
- [ ] Sign up new account (no email needed - auto-verified!)
- [ ] Login works
- [ ] Dashboard shows
- [ ] Create task works
- [ ] AI chatbot works
- [ ] Multi-language switcher works
- [ ] Dark mode toggle works
- [ ] Logout redirects to landing

---

## Part 5: GitHub Actions Setup (Optional - 20 minutes)

### Step 17: Add GitHub Secrets

Go to: https://github.com/YOUR_USERNAME/physical-ai-todo/settings/secrets/actions

Add these secrets:
- [ ] `DO_API_TOKEN` - Your DigitalOcean API token
- [ ] `DO_REGISTRY_NAME` - `physical-ai-todo-registry`
- [ ] `DO_CLUSTER_NAME` - `physical-ai-todo`

### Step 18: Commit & Push

```bash
git add -A
git commit -m "feat(phase-5): production deployment to DigitalOcean DOKS"
git push origin 004-ai-chatbot

# Merge to main to trigger auto-deploy
git checkout main
git merge 004-ai-chatbot
git push origin main
```

- [ ] Committed to Git
- [ ] Pushed to GitHub
- [ ] GitHub Actions workflow running
- [ ] Auto-deployment successful

---

## Part 6: Documentation (10 minutes)

### Step 19: Update README

Add to README.md:
```markdown
## Production Deployment

🚀 **Live Demo**: http://YOUR_IP.nip.io

### Tech Stack
- Frontend: Next.js 14 (TypeScript)
- Backend: FastAPI (Python)
- Database: Neon Serverless Postgres
- Deployment: DigitalOcean Kubernetes (DOKS)
- CI/CD: GitHub Actions
```

- [ ] README updated with production URL
- [ ] Architecture diagram added
- [ ] Committed and pushed

---

## Success Metrics ✅

- [ ] Application accessible via public URL
- [ ] All features working (auth, tasks, chatbot, i18n)
- [ ] Auto-deploys on git push to main
- [ ] Zero downtime deployments
- [ ] Health checks passing
- [ ] Logs accessible via kubectl
- [ ] Cost within budget ($15-20 for hackathon)

---

## After Hackathon

### Cleanup to Stop Charges

```bash
# Delete cluster (stops all charges)
doctl kubernetes cluster delete physical-ai-todo

# Delete registry
doctl registry delete physical-ai-todo-registry

# Verify no resources running
doctl compute load-balancer list
doctl kubernetes cluster list
```

---

## Troubleshooting

### Pods stuck in "Pending"
```bash
kubectl describe pod -n production POD_NAME
# Check for resource limits or scheduling issues
```

### ImagePullBackOff
```bash
doctl registry login
# Verify images exist
doctl registry repository list-v2
```

### Can't access application
```bash
# Check LoadBalancer
kubectl get svc -n ingress-nginx

# Check ingress
kubectl describe ingress -n production

# Test from inside cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- sh
curl http://todo-backend.production:8000/health
```

### Database connection errors
```bash
# Test connection
kubectl exec -n production deployment/todo-backend -- \
  python -c "from app.database import engine; print('Connected!')"
```

---

**Total Time**: ~2-3 hours
**Cost**: $15-20 for hackathon week
**Result**: Fully deployed production app with CI/CD! 🎉
