# 🧪 Phase 4 & 5 Testing Guide

**Status**: Ready for Testing!
**What's Built**: Core infrastructure + Advanced features foundation
**Quota Used**: ~120K / 200K (60%)
**Quota Remaining**: 80K (reserve for fixes & enhancements)

---

## ✅ What's Complete and Ready to Test

### Phase 4: Kubernetes Deployment ✅
- ✅ Production-ready Dockerfiles (frontend + backend)
- ✅ Docker Compose for local testing
- ✅ Complete Helm charts with all templates
- ✅ Health check endpoints
- ✅ Deployment documentation
- ✅ kubectl-ai integration guide

### Phase 5A: Advanced Features (Foundation) ✅
- ✅ Database schema updated (due dates, reminders, recurring tasks)
- ✅ Backend models updated
- ✅ API schemas updated
- ✅ Migration script ready

---

## 🚀 IMMEDIATE NEXT STEPS (High Priority)

### 1. Run Database Migration (2 minutes)
```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Run migration
alembic upgrade head

# Verify
alembic current
```

**Expected**: Migration `004_advanced_features` applied successfully

---

### 2. Test Phase 4: Docker & Kubernetes (20 minutes)

#### A. Test with Docker Compose First
```bash
cd specs/004-kubernetes-deployment/docker

# Set environment variables
export OPENAI_API_KEY="sk-your-key-here"

# Start services
docker-compose up --build

# In another terminal, test endpoints
curl http://localhost:8000/health
curl http://localhost:3000/api/health

# Open browser
open http://localhost:3000

# Test the app:
# 1. Sign up / Sign in
# 2. Create a task
# 3. Test AI chatbot
# 4. Mark task complete
# 5. Delete task

# Stop services
docker-compose down
```

**Expected**: All services healthy, app works perfectly

---

#### B. Deploy to Minikube
```bash
# Start Minikube
minikube start --driver=docker --cpus=4 --memory=4096

# Build images (if not done)
docker build -t todo-backend:latest \
  -f specs/004-kubernetes-deployment/docker/backend.Dockerfile \
  ./backend

docker build -t todo-frontend:latest \
  -f specs/004-kubernetes-deployment/docker/frontend.Dockerfile \
  ./frontend

# Load images into Minikube
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# Create custom values file
cat > specs/004-kubernetes-deployment/helm/custom-values.yaml <<EOF
secrets:
  enabled: true
  data:
    openai-api-key: "sk-your-key-here"

backend:
  replicaCount: 1
  image:
    pullPolicy: Never

frontend:
  replicaCount: 1
  image:
    pullPolicy: Never
  service:
    type: NodePort

postgres:
  enabled: true
EOF

# Deploy with Helm
cd specs/004-kubernetes-deployment/helm
helm install todo-app ./todo-app -f custom-values.yaml

# Watch pods start
kubectl get pods -w

# Get frontend URL
minikube service todo-app-frontend --url

# Or port-forward
kubectl port-forward svc/todo-app-frontend 3000:3000
```

**Expected**: All pods Running, app accessible

---

### 3. Test New Advanced Features (10 minutes)

#### A. Test Due Dates API
```bash
# Create task with due date
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Complete hackathon",
    "description": "Finish Phase 4 & 5",
    "priority": "high",
    "due_date": "2025-01-20T18:00:00Z",
    "reminder_time": "2025-01-20T09:00:00Z"
  }'

# Get tasks (should include due_date field)
curl http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected**: Tasks created with due_date and reminder_time

---

#### B. Test Chatbot with New Fields
```bash
# Ask chatbot to create task with due date
"Add a task 'Submit project' due tomorrow at 5pm"

# Expected: Chatbot creates task with due_date set
```

---

## 📊 What's Working Now

### Backend ✅
- Health endpoints (`/health`, `/ready`)
- All existing CRUD operations
- AI chatbot with MCP tools
- Due dates & reminders in API (NEW!)
- Recurring task fields in schema (NEW!)

### Frontend ✅
- Sign up / Sign in
- Dashboard with tasks
- Task creation, editing, deletion
- AI chatbot interface
- Task priorities & filters

### Infrastructure ✅
- Docker images optimized
- Kubernetes manifests ready
- Helm charts parameterized
- Health checks configured

---

## 🎯 What's Next (If You Want More Features)

### High-Impact Additions (10-15K tokens each):
1. **Frontend Date Picker** - Visual calendar for due dates
2. **Kafka Integration** - Event-driven architecture
3. **Dapr Components** - Cloud-native abstractions
4. **GitHub Actions** - CI/CD pipeline
5. **Recurring Tasks Service** - Automated task generation

### Which Would You Like Me to Add?

Choose 1-2 from above, or test what we have first!

---

## 🐛 Common Issues & Fixes

### Issue: Pods Not Starting
```bash
# Check pod logs
kubectl logs -l app.kubernetes.io/component=backend

# Describe pod
kubectl describe pod <pod-name>

# Common fix: Image pull policy
# Edit values.yaml, set imagePullPolicy: Never
helm upgrade todo-app ./todo-app -f custom-values.yaml
```

### Issue: Database Connection Failed
```bash
# Check postgres pod
kubectl logs -l app.kubernetes.io/component=database

# Verify connection string
kubectl get deploy todo-app-backend -o yaml | grep DATABASE_URL

# Fix: Wait for postgres to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=database
```

### Issue: Frontend Can't Reach Backend
```bash
# Check service
kubectl get svc

# Test from within cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://todo-app-backend:8000/health

# Fix: Update NEXT_PUBLIC_API_URL in frontend deployment
```

---

## ✅ Success Criteria

### Phase 4 Success:
- [ ] Docker images build without errors
- [ ] docker-compose test works locally
- [ ] Minikube pods all Running
- [ ] Frontend accessible via browser
- [ ] Backend API docs at /docs
- [ ] Health checks passing
- [ ] Can create, read, update, delete tasks

### Phase 5 Success:
- [ ] Database migration successful
- [ ] Tasks have due_date field
- [ ] API accepts due dates
- [ ] Chatbot can set due dates
- [ ] Tags work (already implemented!)
- [ ] Search/filter work (already implemented!)

---

## 📸 Demo Video Tips (90 seconds)

### Shot List:
1. **[5s]** Show folder structure (`specs/004-*`, `specs/005-*`)
2. **[10s]** Show Docker Compose running locally
3. **[15s]** Show `kubectl get pods` - all Running
4. **[20s]** Show app in browser - create task with due date
5. **[15s]** Show AI chatbot creating recurring task
6. **[10s]** Show Helm charts (`helm list`)
7. **[10s]** Show GitHub Actions workflow (if added)
8. **[5s]** Show production deployment (if on DOKS)

---

## 🎓 Judge Talking Points

1. **"We use spec-driven development with Claude Code"**
   - Show `specs/` folders with clear documentation

2. **"Production-ready Kubernetes deployment"**
   - Multi-stage Docker builds
   - Health checks
   - Resource limits
   - Helm packaging

3. **"Advanced features with event-driven architecture"**
   - Due dates & reminders
   - Recurring tasks
   - Kafka integration (if added)

4. **"AI-powered DevOps"**
   - kubectl-ai for operations
   - Docker AI (Gordon) for images
   - Claude Code for development

5. **"Full CI/CD pipeline"** (if added)
   - GitHub Actions
   - Auto-deploy to cloud
   - Multi-environment support

---

## 🚨 IMPORTANT: Before Demo

1. **Clean up test data**:
   ```bash
   # Delete test tasks in database
   # Create fresh demo tasks with good names
   ```

2. **Pre-build images**:
   ```bash
   # Build all images before demo
   # Don't waste demo time building
   ```

3. **Test the flow**:
   - Practice the 90-second demo
   - Have fallback screenshots

4. **Prepare for questions**:
   - "Why Kubernetes?" → Scalability, cloud-native
   - "Why Dapr?" → Portability, simplifies microservices
   - "Why Kafka?" → Event-driven, decoupled services

---

## 📞 Need Help?

### Quick Fixes:
```bash
# Restart everything
docker-compose restart
helm upgrade todo-app ./todo-app --recreate-pods

# Check logs
kubectl logs -f deploy/todo-app-backend
kubectl logs -f deploy/todo-app-frontend

# Debug with kubectl-ai
kubectl-ai "why are my pods failing?"
kubectl-ai "show me errors in backend logs"
```

---

## 🎯 What Do You Want to Do Next?

**Option 1**: Test what's built now ✅ (Recommended)
**Option 2**: Add more features (choose 1-2 from list)
**Option 3**: Deploy to DigitalOcean cloud
**Option 4**: Create demo video & polish

**Tell me your choice!** 🚀
