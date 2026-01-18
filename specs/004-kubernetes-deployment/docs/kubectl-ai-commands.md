# 🤖 kubectl-ai Command Reference

AI-assisted Kubernetes operations for Todo App deployment.

---

## 🎯 Getting Started

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-your-key-here"

# Test kubectl-ai
kubectl-ai "what pods are running?"

# Get help
kubectl-ai --help
```

---

## 📊 Monitoring & Status

### Pod Status
```bash
kubectl-ai "show me all todo-app pods"
kubectl-ai "are all pods running?"
kubectl-ai "why is the backend pod crashlooping?"
kubectl-ai "show me pods that are not ready"
```

### Resource Usage
```bash
kubectl-ai "show CPU and memory usage for todo-app pods"
kubectl-ai "which pod is using the most memory?"
kubectl-ai "are any pods hitting resource limits?"
```

### Health Checks
```bash
kubectl-ai "check if all health checks are passing"
kubectl-ai "why are readiness probes failing for frontend?"
kubectl-ai "show me the liveness probe configuration"
```

---

## 🔧 Deployment Operations

### Scaling
```bash
kubectl-ai "scale backend to 3 replicas"
kubectl-ai "how many replicas does frontend have?"
kubectl-ai "scale all deployments to 2 replicas"
```

### Rolling Updates
```bash
kubectl-ai "restart the backend deployment"
kubectl-ai "update backend image to todo-backend:v2"
kubectl-ai "rollback frontend deployment to previous version"
```

### Configuration
```bash
kubectl-ai "update backend environment variable DEBUG to true"
kubectl-ai "show me all environment variables for backend"
kubectl-ai "change database password secret"
```

---

## 🐛 Debugging

### Logs
```bash
kubectl-ai "show me backend logs from the last hour"
kubectl-ai "show errors in frontend logs"
kubectl-ai "tail logs from all backend pods"
kubectl-ai "show me logs with keyword 'database connection'"
```

### Events
```bash
kubectl-ai "show me recent events for todo-app"
kubectl-ai "what warnings are there in the cluster?"
kubectl-ai "show me events related to pod failures"
```

### Troubleshooting
```bash
kubectl-ai "why can't my pods pull the image?"
kubectl-ai "why is the service not accessible?"
kubectl-ai "troubleshoot database connection issues"
kubectl-ai "check network connectivity between frontend and backend"
```

---

## 🌐 Networking

### Services
```bash
kubectl-ai "show me all services"
kubectl-ai "what is the external IP of frontend service?"
kubectl-ai "expose backend service on port 8080"
kubectl-ai "create a LoadBalancer service for frontend"
```

### Ingress
```bash
kubectl-ai "create an ingress for todo-app on domain todo.local"
kubectl-ai "show me ingress rules"
kubectl-ai "update ingress to add TLS"
```

---

## 💾 Storage

### Persistent Volumes
```bash
kubectl-ai "show me all persistent volume claims"
kubectl-ai "how much storage is postgres using?"
kubectl-ai "create a 5GB persistent volume for database"
kubectl-ai "resize postgres volume to 10GB"
```

---

## 🔐 Security

### Secrets & ConfigMaps
```bash
kubectl-ai "create a secret for OpenAI API key"
kubectl-ai "show me all secrets (without values)"
kubectl-ai "update database password in secret"
kubectl-ai "create configmap from file app.config"
```

### RBAC
```bash
kubectl-ai "show me service accounts"
kubectl-ai "what permissions does todo-app service account have?"
kubectl-ai "create a role for readonly access to pods"
```

---

## 📦 Helm Integration

```bash
kubectl-ai "show me all helm releases"
kubectl-ai "what version of todo-app is deployed?"
kubectl-ai "upgrade todo-app helm release"
kubectl-ai "rollback todo-app to previous helm revision"
```

---

## 🧪 Testing & Validation

### Connectivity Tests
```bash
kubectl-ai "test if frontend can reach backend"
kubectl-ai "check if pods can access the internet"
kubectl-ai "verify database connectivity from backend"
```

### Performance
```bash
kubectl-ai "show me pod restart counts"
kubectl-ai "which pods have been restarting frequently?"
kubectl-ai "check if any pods are being throttled"
```

---

## 🚀 Advanced Operations

### Cluster Management
```bash
kubectl-ai "show cluster resource utilization"
kubectl-ai "list all namespaces"
kubectl-ai "create namespace for staging environment"
kubectl-ai "move todo-app to namespace production"
```

### Auto-scaling
```bash
kubectl-ai "create horizontal pod autoscaler for backend with target CPU 70%"
kubectl-ai "show current autoscaling status"
kubectl-ai "scale backend between 2 and 10 replicas based on CPU"
```

### Jobs & CronJobs
```bash
kubectl-ai "create a job to run database migration"
kubectl-ai "schedule a cronjob to backup database daily at midnight"
kubectl-ai "show me all completed jobs"
```

---

## 💡 Best Practices

### Resource Management
```bash
kubectl-ai "set resource requests and limits for backend"
kubectl-ai "show pods without resource limits"
kubectl-ai "recommend resource limits based on current usage"
```

### Labels & Annotations
```bash
kubectl-ai "label all todo-app pods with environment=production"
kubectl-ai "show me pods with label app=backend"
kubectl-ai "add annotation to frontend deployment"
```

---

## 🎓 Learning & Documentation

```bash
kubectl-ai "explain what a deployment is"
kubectl-ai "show me best practices for health checks"
kubectl-ai "how do I debug a CrashLoopBackOff pod?"
kubectl-ai "what's the difference between liveness and readiness probes?"
```

---

## 🆘 Emergency Operations

### Quick Fixes
```bash
kubectl-ai "delete all failed pods"
kubectl-ai "restart all crashlooping pods"
kubectl-ai "scale down all deployments to 0"
kubectl-ai "drain node for maintenance"
```

### Disaster Recovery
```bash
kubectl-ai "backup all configmaps and secrets"
kubectl-ai "restore todo-app from backup"
kubectl-ai "force delete stuck pods"
```

---

## 📝 Tips for Effective kubectl-ai Usage

1. **Be Specific**: The more context you provide, the better
   - ❌ "scale pods"
   - ✅ "scale backend deployment to 3 replicas"

2. **Use Natural Language**: No need for exact kubectl syntax
   - "Show me what's wrong with my pods"
   - "Why can't I access the frontend?"

3. **Ask Follow-up Questions**: Build on previous context
   - First: "show me backend pods"
   - Then: "why is the first one failing?"

4. **Request Explanations**: Learn as you go
   - "Explain why this pod is pending"
   - "What does this error mean?"

5. **Combine Operations**: Ask for complete workflows
   - "Create a service and expose it externally for frontend"

---

## 🔗 Related Resources

- **kubectl-ai GitHub**: https://github.com/sozercan/kubectl-ai
- **Kubernetes Docs**: https://kubernetes.io/docs/
- **Helm Docs**: https://helm.sh/docs/

---

**For Judges**: kubectl-ai demonstrates how AI can make Kubernetes more accessible while maintaining production-grade operations.
