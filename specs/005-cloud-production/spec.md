# Feature Specification: Phase V - Production Cloud Deployment

**Feature Branch**: `005-cloud-production`
**Created**: 2025-12-21
**Status**: In Progress
**Priority**: P0 (Hackathon Deadline)

## Overview

Deploy the Physical AI Todo application to DigitalOcean Kubernetes (DOKS) with production-grade infrastructure, CI/CD pipeline, and basic observability for hackathon submission.

**Scope**: Production deployment with minimal viable observability
**Timeline**: Complete today (2025-12-21)
**Success Metric**: Application accessible via public URL with HTTPS, auto-deploys on git push

## User Story

As a hackathon judge, I want to access a production-deployed todo application at a public URL, so I can evaluate the project's completeness and production readiness without setting up local infrastructure.

## Phase V Components (MVP for Hackathon)

### ✅ Must Have (P0 - Deploy Today)

1. **DigitalOcean Kubernetes Cluster**
   - DOKS cluster (1-2 nodes, $10-20/month budget)
   - Managed Postgres database (or Neon Serverless)
   - LoadBalancer service for ingress

2. **GitHub Actions CI/CD**
   - Build Docker images on push to main
   - Push to DigitalOcean Container Registry
   - Auto-deploy to DOKS
   - Secrets management via GitHub Secrets

3. **Production Configuration**
   - Environment variables via Kubernetes Secrets/ConfigMaps
   - HTTPS/TLS via DigitalOcean LoadBalancer or cert-manager
   - Health checks and readiness probes
   - Resource limits (CPU/memory)

4. **Basic Observability**
   - Kubernetes Dashboard (built-in)
   - Pod logs via kubectl
   - Basic metrics (optional: Prometheus if time permits)

### 🎯 Nice to Have (P1 - If Time Permits)

5. **Event Streaming (Kafka)**
   - Apache Kafka for task events
   - Event-driven architecture for real-time updates

6. **Microservices Runtime (Dapr)**
   - Dapr sidecars for pub/sub
   - State management
   - Secrets management

7. **Advanced Observability**
   - Prometheus + Grafana dashboards
   - Jaeger distributed tracing
   - Centralized logging (Loki)

## Architecture

### Phase V Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  DigitalOcean Cloud                     │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │         DOKS Cluster (Kubernetes)                │  │
│  │                                                  │  │
│  │  ┌────────────┐      ┌────────────┐            │  │
│  │  │  Frontend  │      │  Backend   │            │  │
│  │  │  (Next.js) │      │  (FastAPI) │            │  │
│  │  │  Pod x2    │      │  Pod x2    │            │  │
│  │  └─────┬──────┘      └─────┬──────┘            │  │
│  │        │                   │                    │  │
│  │        └───────┬───────────┘                    │  │
│  │                │                                 │  │
│  │         ┌──────▼──────┐                         │  │
│  │         │  LoadBalancer│                        │  │
│  │         │   (Public IP)│                        │  │
│  │         └──────┬───────┘                        │  │
│  └────────────────┼──────────────────────────────┘  │
│                   │                                  │
│  ┌────────────────▼──────────────┐                  │
│  │   Managed Postgres / Neon     │                  │
│  │   (Database)                  │                  │
│  └───────────────────────────────┘                  │
│                                                      │
└──────────────────────────────────────────────────────┘
                   ▲
                   │ HTTPS (TLS)
                   │
            ┌──────┴──────┐
            │   Users /   │
            │   Judges    │
            └─────────────┘

┌─────────────────────────────────────────────────────────┐
│                 GitHub Actions CI/CD                    │
│                                                         │
│  Git Push ──► Build Images ──► Push to Registry ──►   │
│               Test Suite       Deploy to DOKS           │
└─────────────────────────────────────────────────────────┘
```

## Deployment Strategy

### 1. DigitalOcean Setup

**DOKS Cluster Configuration:**
```yaml
name: physical-ai-todo-cluster
region: nyc1 (or closest to judges)
version: 1.28.x (latest stable)
node_pools:
  - name: worker-pool
    size: s-2vcpu-4gb ($24/month per node)
    count: 2
    auto_scale: true
    min_nodes: 1
    max_nodes: 3
```

**Managed Database** (Alternative: Use existing Neon Serverless):
- Option A: DO Managed Postgres ($15/month minimum)
- Option B: Keep Neon Serverless (RECOMMENDED for cost)

### 2. GitHub Actions Workflow

**Trigger**: Push to `main` branch
**Steps**:
1. Run tests (pytest, npm test)
2. Build Docker images (backend, frontend)
3. Push to DigitalOcean Container Registry
4. Deploy to DOKS via kubectl
5. Run smoke tests
6. Notify on Discord/Slack (optional)

### 3. Kubernetes Resources

**Deployments:**
- `frontend-deployment.yaml` (2 replicas)
- `backend-deployment.yaml` (2 replicas)

**Services:**
- `frontend-service` (ClusterIP)
- `backend-service` (ClusterIP)
- `ingress-nginx` (LoadBalancer - public IP)

**Configuration:**
- `app-secrets.yaml` (DATABASE_URL, RESEND_API_KEY, JWT_SECRET, OPENAI_API_KEY)
- `app-configmap.yaml` (FRONTEND_URL, environment settings)

**Ingress:**
- Domain: `todo.yourdomain.com` (or DO provided domain)
- TLS: Let's Encrypt via cert-manager
- Routes: `/api` → backend, `/` → frontend

## Acceptance Criteria

### P0 - Must Complete Today

- [ ] DOKS cluster created and accessible
- [ ] Container registry configured (DigitalOcean or DockerHub)
- [ ] GitHub Actions workflow building and pushing images
- [ ] Application deployed to DOKS
- [ ] Public URL accessible via HTTPS
- [ ] Database migrations applied
- [ ] All existing features working in production
- [ ] Health checks passing
- [ ] GitHub repo README updated with production URL

### P1 - Nice to Have

- [ ] Prometheus metrics collection
- [ ] Grafana dashboards
- [ ] Auto-scaling configured
- [ ] Backup strategy documented
- [ ] Kafka event streaming
- [ ] Dapr integration

## Technical Requirements

### Infrastructure as Code

**Kubernetes Manifests:** `kubernetes/production/`
```
kubernetes/production/
├── namespace.yaml
├── deployments/
│   ├── frontend.yaml
│   └── backend.yaml
├── services/
│   ├── frontend.yaml
│   └── backend.yaml
├── configmaps/
│   └── app-config.yaml
├── secrets/
│   └── app-secrets.yaml (template, actual values from GitHub Secrets)
├── ingress/
│   └── nginx-ingress.yaml
└── cert-manager/
    └── letsencrypt-issuer.yaml
```

**GitHub Actions:** `.github/workflows/deploy-production.yml`

### Environment Variables (Production)

**Secrets** (stored in GitHub Secrets, injected as K8s Secrets):
- `DATABASE_URL` - Neon or DO Postgres connection string
- `JWT_SECRET` - Random 32-char string
- `RESEND_API_KEY` - Email service API key
- `OPENAI_API_KEY` - AI chatbot API key
- `GITHUB_OAUTH_CLIENT_ID` - OAuth app ID
- `GITHUB_OAUTH_CLIENT_SECRET` - OAuth app secret

**ConfigMap** (non-sensitive):
- `FRONTEND_URL` - `https://todo.yourdomain.com`
- `NODE_ENV` - `production`
- `LOG_LEVEL` - `info`

### Docker Images

**Frontend:**
- Registry: `registry.digitalocean.com/your-registry/todo-frontend:latest`
- Multi-stage build (Node.js 20 Alpine)
- Size: ~200MB
- Healthcheck: `GET /` returns 200

**Backend:**
- Registry: `registry.digitalocean.com/your-registry/todo-backend:latest`
- Multi-stage build (Python 3.12 Alpine)
- Size: ~150MB
- Healthcheck: `GET /health` returns 200

### CI/CD Pipeline

**Build Stage** (5-10 minutes):
```yaml
- Run tests (backend + frontend)
- Build Docker images
- Tag with git SHA and 'latest'
- Push to registry
```

**Deploy Stage** (2-5 minutes):
```yaml
- Install doctl CLI
- Authenticate with DOKS
- Apply Kubernetes manifests
- Wait for rollout completion
- Run smoke tests
```

**Smoke Tests**:
```bash
curl https://todo.yourdomain.com/health
curl https://todo.yourdomain.com/api/v1/health
```

## Cost Estimate (DigitalOcean)

**Monthly Costs:**
- DOKS Cluster: 2 nodes x $24/month = $48/month
- LoadBalancer: $12/month
- Container Registry: $5/month (1GB included)
- **Total**: ~$65/month

**Hackathon Budget** (1 week):
- ~$15-20 for testing and demo

**Free Tier Options:**
- Neon Serverless Postgres: Free tier sufficient
- Cert-manager: Free (Let's Encrypt)
- GitHub Actions: 2000 minutes/month free

## Security Checklist

- [ ] All secrets stored in GitHub Secrets (never committed)
- [ ] Database connection uses SSL/TLS
- [ ] HTTPS enforced via Ingress
- [ ] CORS properly configured (only allow production domain)
- [ ] Rate limiting on API endpoints
- [ ] JWT tokens httpOnly cookies
- [ ] No debug logs in production
- [ ] Resource limits prevent DoS

## Rollback Strategy

**If deployment fails:**
1. GitHub Actions automatically reverts on test failure
2. Manual rollback: `kubectl rollout undo deployment/frontend`
3. Database migrations: Manual rollback script

**Monitoring:**
- Watch deployment: `kubectl rollout status deployment/frontend`
- Check logs: `kubectl logs -f deployment/backend`

## Testing Strategy

### Pre-Deployment Tests (CI)
- Unit tests: `pytest` (backend), `npm test` (frontend)
- Integration tests: API endpoint tests
- Coverage: >80% required

### Post-Deployment Tests (CD)
- Health checks: All pods healthy
- Smoke tests: Critical paths working
- Manual QA: Full user flow (signup → login → create task → chatbot)

## Success Metrics

**Deployment Success:**
- ✅ Application accessible at public URL within 30 minutes of git push
- ✅ All critical features working (auth, tasks, chatbot, multi-language)
- ✅ Zero downtime on subsequent deploys
- ✅ Logs accessible via kubectl

**Performance:**
- API response time: <500ms p95
- Frontend load time: <3s
- Uptime: >99% during hackathon evaluation

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| DO credit card verification delays | High | Use existing account or DockerHub + K8s provider |
| Build failures in CI | Medium | Test locally first, cache dependencies |
| Database migration failures | High | Test migrations on staging, backup before deploy |
| DNS propagation delays | Low | Use DO provided domain initially |
| Cost overruns | Medium | Set budget alerts, use smallest node sizes |

## Next Steps (Execution Order)

1. **Setup DigitalOcean Account** (15 min)
   - Create DOKS cluster
   - Create container registry
   - Get kubeconfig

2. **Configure GitHub Actions** (30 min)
   - Add GitHub Secrets
   - Create workflow file
   - Test build

3. **Prepare Kubernetes Manifests** (45 min)
   - Create production YAMLs
   - Configure Ingress
   - Setup cert-manager

4. **Deploy to DOKS** (30 min)
   - Apply manifests
   - Verify pods running
   - Test public URL

5. **Verify All Features** (30 min)
   - Test signup/login
   - Test task CRUD
   - Test AI chatbot
   - Test multi-language

**Total Estimated Time**: 2.5 hours (with buffer: 3-4 hours)

## Documentation Updates

**README.md:**
- Add "Production Deployment" section
- Include public URL
- Document architecture
- Add cost breakdown

**DEPLOYMENT.md:**
- Step-by-step DO setup
- GitHub Actions setup
- Secrets configuration
- Troubleshooting guide

## Definition of Done

- [ ] Application accessible at `https://todo.yourdomain.com`
- [ ] GitHub Actions deploys on push to main
- [ ] All Phase 1-4 features working
- [ ] No manual deployment steps required
- [ ] Documentation complete
- [ ] Demo video recorded (optional)
- [ ] Hackathon submission ready

---

**Last Updated**: 2025-12-21
**Next Review**: After deployment completion
