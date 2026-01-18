# Quick Start Guide for Judges Demo

## After Restarting Your PC

### Step 1: Open Command Prompt
1. Press `Win + R`
2. Type `cmd` and press Enter

### Step 2: Navigate to Project
```cmd
cd C:\Users\Ahsan\physical-ai-todo
```

### Step 3: Check App Status (Optional)
```cmd
set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml
kubectl get pods -n production
kubectl get svc -n production
kubectl get ingress -n production
```

### Step 4: Access Your App
Your app is live at: **http://161-35-250-151.nip.io**

That's it! The app is running on DigitalOcean cloud, so you don't need to start anything after reboot.

---

## If You Made Code Changes

### Rebuild and Redeploy Frontend:
```cmd
REM 1. Rebuild frontend image
docker build -t registry.digitalocean.com/physical-ai-todo-registry/todo-frontend:latest -f specs/004-kubernetes-deployment/docker/frontend.Dockerfile .

REM 2. Push to registry
docker push registry.digitalocean.com/physical-ai-todo-registry/todo-frontend:latest

REM 3. Restart frontend pods
set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml
kubectl rollout restart deployment/todo-frontend -n production
kubectl rollout status deployment/todo-frontend -n production
```

### Rebuild and Redeploy Backend:
```cmd
REM 1. Rebuild backend image
docker build -t registry.digitalocean.com/physical-ai-todo-registry/todo-frontend:backend -f backend/Dockerfile backend

REM 2. Push to registry
docker push registry.digitalocean.com/physical-ai-todo-registry/todo-frontend:backend

REM 3. Restart backend pods
set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml
kubectl rollout restart deployment/todo-backend -n production
kubectl rollout status deployment/todo-backend -n production
```

---

## Testing Checklist for Judges

### 1. Landing Page
- [ ] Visit http://161-35-250-151.nip.io
- [ ] Check that landing page loads properly
- [ ] Verify gradient background and animations work

### 2. Email Sign Up (Auto-verified for demo)
- [ ] Click "Get Started" or "Sign Up"
- [ ] Enter email, password, full name
- [ ] Click "Create Account"
- [ ] **Should automatically log you in and redirect to dashboard** (no email verification needed)

### 3. Dashboard
- [ ] Verify you're on dashboard after signup
- [ ] Check that task list loads
- [ ] Try creating a new task
- [ ] Try marking task as complete
- [ ] Try editing a task
- [ ] Try deleting a task
- [ ] Test dark mode toggle
- [ ] Test language switch (English/Urdu)

### 4. AI Chatbot
- [ ] Click chatbot icon or navigate to /chat
- [ ] Send a message to AI assistant
- [ ] Verify AI responds correctly
- [ ] Test follow-up questions
- [ ] Check conversation history

### 5. GitHub OAuth (Optional)
- [ ] Click "Continue with GitHub"
- [ ] Authorize the app
- [ ] Verify redirect back to dashboard

### 6. Logout
- [ ] Click logout button
- [ ] Verify redirected to landing page
- [ ] Verify can't access /dashboard without login

---

## Troubleshooting

### If pods aren't running:
```cmd
set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml
kubectl get pods -n production
kubectl describe pod <pod-name> -n production
kubectl logs -n production deployment/todo-backend --tail=50
kubectl logs -n production deployment/todo-frontend --tail=50
```

### If app doesn't load:
```cmd
REM Check ingress
kubectl get ingress -n production
kubectl describe ingress todo-app-ingress -n production

REM Check LoadBalancer IP
kubectl get svc -n ingress-nginx
```

### Force pull latest images:
```cmd
set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml
kubectl delete pod -n production -l app=todo-frontend
kubectl delete pod -n production -l app=todo-backend
```

---

## Important URLs

- **Production App**: http://161-35-250-151.nip.io
- **Landing Page**: http://161-35-250-151.nip.io/landing
- **Sign Up**: http://161-35-250-151.nip.io/auth/signup
- **Sign In**: http://161-35-250-151.nip.io/auth/signin
- **Dashboard**: http://161-35-250-151.nip.io/dashboard
- **Chatbot**: http://161-35-250-151.nip.io/chat
- **API Health**: http://161-35-250-151.nip.io/api/v1/health

---

## Demo Account (for judges)

You can either:
1. **Sign up** with any email (instant access, no verification needed)
2. **Use GitHub OAuth** (one-click signup)

Both methods work instantly for the hackathon demo!
