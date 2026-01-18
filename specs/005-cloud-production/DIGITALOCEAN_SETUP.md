# DigitalOcean Setup Guide - Phase 5 Production Deployment

## Prerequisites
- DigitalOcean account created
- Payment method added (required for $200 free credit)
- `doctl` CLI installed (optional but recommended)

---

## Step 1: Install doctl CLI (5 minutes)

**Windows:**
```powershell
# Using Chocolatey
choco install doctl

# OR download from: https://github.com/digitalocean/doctl/releases
# Extract doctl.exe to a folder in your PATH
```

**Verify Installation:**
```bash
doctl version
```

---

## Step 2: Authenticate with DigitalOcean (2 minutes)

### A. Create API Token

1. Go to https://cloud.digitalocean.com/account/api/tokens
2. Click **"Generate New Token"**
3. Name: `physical-ai-todo-token`
4. Scopes: **Read & Write** (check both boxes)
5. Click **"Generate Token"**
6. **COPY THE TOKEN** (you won't see it again!)

### B. Authenticate doctl

```bash
doctl auth init
# Paste your API token when prompted
```

**Verify:**
```bash
doctl account get
# Should show your email and account info
```

---

## Step 3: Create Container Registry (3 minutes)

```bash
# Create registry (choose a unique name)
doctl registry create physical-ai-todo-registry

# Login to registry
doctl registry login

# Get registry info
doctl registry get
```

**Your registry URL will be:**
```
registry.digitalocean.com/physical-ai-todo-registry
```

---

## Step 4: Create Kubernetes Cluster (10 minutes)

### A. Create Cluster via CLI

```bash
# Create DOKS cluster (this takes 5-10 minutes)
doctl kubernetes cluster create physical-ai-todo \
  --region nyc1 \
  --version 1.28.2-do.0 \
  --node-pool "name=worker-pool;size=s-2vcpu-4gb;count=2;auto-scale=true;min-nodes=1;max-nodes=3" \
  --wait
```

**Cost Breakdown:**
- 2 nodes × $24/month = $48/month
- Uses your $200 free credit

### B. OR Create via Web UI

1. Go to https://cloud.digitalocean.com/kubernetes/clusters/new
2. **Choose a datacenter:** New York (NYC1) or closest to you
3. **Kubernetes version:** 1.28.x (latest)
4. **Choose cluster capacity:**
   - Node pool name: `worker-pool`
   - Machine type: **Basic nodes** → **$24/mo (2 vCPU, 4GB RAM)**
   - Node count: **2** (enable auto-scaling: min 1, max 3)
5. **Choose a name:** `physical-ai-todo`
6. Click **"Create Cluster"** (takes 5-10 minutes)

---

## Step 5: Configure kubectl (2 minutes)

```bash
# Download cluster config
doctl kubernetes cluster kubeconfig save physical-ai-todo

# Verify connection
kubectl cluster-info
kubectl get nodes
# Should show 2 nodes in "Ready" state
```

---

## Step 6: Install Nginx Ingress Controller (3 minutes)

```bash
# Install nginx ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/do/deploy.yaml

# Wait for LoadBalancer IP (takes 2-3 minutes)
kubectl get service -n ingress-nginx ingress-nginx-controller --watch

# Once EXTERNAL-IP appears (not <pending>), press Ctrl+C
```

**Get your LoadBalancer IP:**
```bash
kubectl get service -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

**Example output:** `157.230.123.45` (your public IP!)

---

## Step 7: Point Domain to LoadBalancer (5 minutes)

### Option A: Use DigitalOcean Domain (Free)

1. Go to https://cloud.digitalocean.com/networking/domains
2. Click **"Add Domain"**
3. Enter your domain (e.g., `yourdomain.com`)
4. Add **A Record:**
   - Hostname: `todo` (creates `todo.yourdomain.com`)
   - Will Direct to: Your LoadBalancer IP from Step 6
   - TTL: 30 seconds

### Option B: No Domain - Use nip.io (Free, No Setup)

If you don't have a domain, use `nip.io`:
```bash
# If LoadBalancer IP is 157.230.123.45
# Your app URL will be: http://157-230-123-45.nip.io
```

**nip.io automatically resolves IP addresses in the hostname!**

---

## Step 8: Create Kubernetes Secrets (2 minutes)

```bash
# Create namespace
kubectl create namespace production

# Create secrets (replace with your actual values)
kubectl create secret generic app-secrets \
  --namespace=production \
  --from-literal=DATABASE_URL="your-neon-postgres-url" \
  --from-literal=JWT_SECRET="your-random-32-char-secret" \
  --from-literal=RESEND_API_KEY="re_72HMJyBA_6kgNsLvKR4T9mWv6oytD5x7X" \
  --from-literal=OPENAI_API_KEY="your-openai-key" \
  --from-literal=GITHUB_OAUTH_CLIENT_ID="your-github-id" \
  --from-literal=GITHUB_OAUTH_CLIENT_SECRET="your-github-secret"
```

---

## Step 9: Build and Push Docker Images (10 minutes)

```bash
# Tag images for DO registry
docker tag todo-frontend:v10 registry.digitalocean.com/physical-ai-todo-registry/frontend:latest
docker tag todo-backend:latest registry.digitalocean.com/physical-ai-todo-registry/backend:latest

# Push to registry
docker push registry.digitalocean.com/physical-ai-todo-registry/frontend:latest
docker push registry.digitalocean.com/physical-ai-todo-registry/backend:latest
```

---

## Step 10: Deploy Application (5 minutes)

I'll create the Kubernetes manifests for you in the next step!

---

## Verification Checklist

- [ ] doctl CLI installed and authenticated
- [ ] Container registry created
- [ ] DOKS cluster running (2 nodes)
- [ ] kubectl connected to cluster
- [ ] Nginx ingress controller installed
- [ ] LoadBalancer has external IP
- [ ] Domain/nip.io configured
- [ ] Secrets created in production namespace
- [ ] Docker images pushed to registry

---

## Cost Tracking

**View your spending:**
```bash
doctl balance get
```

**Or check:** https://cloud.digitalocean.com/account/billing

**With $200 credit, you can run for ~3 months before any charges!**

---

## Cleanup (After Hackathon)

```bash
# Delete cluster (stops all charges)
doctl kubernetes cluster delete physical-ai-todo

# Delete registry
doctl registry delete physical-ai-todo-registry

# Delete LoadBalancer (if still exists)
doctl compute load-balancer list
doctl compute load-balancer delete <load-balancer-id>
```

---

**Next Step:** I'll create the production Kubernetes manifests once email testing is complete!
