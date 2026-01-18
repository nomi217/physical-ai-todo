# Testing Guide - Production Deployment

## Fixes Applied
✅ **Frontend**: Auto-login after signup (no email verification needed)
✅ **Backend**: CORS configured to allow production domain
✅ **Images**: Built and pushed to DigitalOcean registry

## Deploy the Fixes

### Run this command first:
```cmd
deploy-fixes.cmd
```

This will:
1. Restart backend with CORS fix
2. Restart frontend with auto-login fix
3. Wait for both to be ready
4. Show you the testing URLs

---

## Testing Checklist

### 1. Health Check (Backend Connectivity)
**URL**: http://161-35-250-151.nip.io/api/v1/health

**Expected Response**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "service": "Physical AI Todo API"
}
```

**If you see this**: ✅ Backend is working correctly!
**If you see "details not found"**: ❌ Backend isn't accessible (check deployment)

---

### 2. Landing Page
**URL**: http://161-35-250-151.nip.io/landing

**What to check**:
- [ ] Page loads with gradient background
- [ ] Animations work (floating orbs)
- [ ] "Get Started" button is visible
- [ ] "Sign In" link works

---

### 3. Sign Up Flow (IMPORTANT TEST)
**URL**: http://161-35-250-151.nip.io/auth/signup

**Steps**:
1. Enter a **NEW email** (one you haven't used before)
2. Enter password (minimum 8 characters)
3. Enter full name
4. Click "Create Account"

**Expected Behavior**:
- ✅ **Should automatically log you in**
- ✅ **Should redirect to dashboard immediately**
- ✅ **NO email verification page should appear**

**If you see "Check Your Email" page**: ❌ Frontend not updated (run deploy-fixes.cmd)

---

### 4. Dashboard Access
**URL**: http://161-35-250-151.nip.io/dashboard

**What to check**:
- [ ] Dashboard loads after login
- [ ] Your email is shown at the top
- [ ] Task list is visible
- [ ] Can create new task
- [ ] Can mark task as complete
- [ ] Can edit task
- [ ] Can delete task

**Special Features**:
- [ ] Dark mode toggle works
- [ ] Language switch (English/Urdu) works
- [ ] Logout button works

---

### 5. AI Chatbot
**URL**: http://161-35-250-151.nip.io/chat

**What to check**:
- [ ] Chat interface loads
- [ ] Can type message
- [ ] AI responds to your message
- [ ] Follow-up questions work
- [ ] Conversation history is maintained

**Sample Messages to Try**:
- "What tasks do I have?"
- "Create a task to buy groceries"
- "What's the weather like?" (tests general knowledge)

---

### 6. GitHub OAuth (Optional)
**URL**: http://161-35-250-151.nip.io/auth/signup → "Continue with GitHub"

**What to check**:
- [ ] Redirects to GitHub authorization
- [ ] After authorization, redirects back to dashboard
- [ ] User is logged in

**If you see "redirect_uri not associated"**: ❌ Update GitHub OAuth app settings:
- Go to: https://github.com/settings/applications/2673078
- Set Authorization callback URL: `http://161-35-250-151.nip.io/api/v1/auth/github/callback`

---

### 7. Logout and Sign In
**After testing above**:

1. Click Logout button
   - **Expected**: Redirects to `/landing` (NOT `/auth/signin`)

2. Click "Sign In" from landing page
   - **URL**: http://161-35-250-151.nip.io/auth/signin

3. Enter email and password you created earlier
   - **Expected**: Logs you in and redirects to dashboard

---

## Common Issues and Fixes

### Issue: "details not found" on health endpoint
**Cause**: Backend CORS blocking requests
**Fix**:
```cmd
deploy-fixes.cmd
```

### Issue: Still seeing email verification page after signup
**Cause**: Frontend not updated
**Fix**:
```cmd
deploy-fixes.cmd
```

### Issue: Dashboard doesn't load after login
**Cause**: CORS or frontend routing issue
**Fix**:
1. Open browser console (F12)
2. Check for errors
3. Look for CORS errors
4. If you see CORS errors, run `deploy-fixes.cmd`

### Issue: Chatbot doesn't respond
**Possible Causes**:
- OpenAI API key not set correctly
- Backend not running
- CORS blocking requests

**Check**:
```cmd
set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml
kubectl logs -n production deployment/todo-backend --tail=100
```

---

## For Judges Demo

### Quick Demo Script
1. **Open**: http://161-35-250-151.nip.io/landing
2. **Click**: "Get Started"
3. **Sign Up**: Use any email (instant access)
4. **Dashboard**: Create a task → "Buy milk"
5. **AI Chat**: Ask "What tasks do I have?"
6. **Features**: Show dark mode, language switch
7. **Done**: Logout and show landing page

### Key Selling Points
- ✅ **Instant signup** (no email verification)
- ✅ **AI-powered** task management
- ✅ **Multi-language** support (English/Urdu)
- ✅ **Dark mode** for better UX
- ✅ **Cloud-deployed** on DigitalOcean Kubernetes
- ✅ **Production-ready** with proper CORS, health checks, ingress

---

## Debugging Commands

### Check Pod Status
```cmd
set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml
kubectl get pods -n production
```

### View Backend Logs
```cmd
kubectl logs -n production deployment/todo-backend --tail=100
```

### View Frontend Logs
```cmd
kubectl logs -n production deployment/todo-frontend --tail=100
```

### Check Ingress
```cmd
kubectl get ingress -n production
kubectl describe ingress todo-app-ingress -n production
```

### Force Restart Pods
```cmd
kubectl delete pod -n production -l app=todo-frontend
kubectl delete pod -n production -l app=todo-backend
```

---

## Success Criteria

All of these should work:
- [x] Health endpoint returns JSON
- [x] Landing page loads
- [x] Sign up auto-logs in user
- [x] Dashboard accessible after login
- [x] Can create/edit/delete tasks
- [x] AI chatbot responds
- [x] Dark mode works
- [x] Language switch works
- [x] Logout redirects to landing

If all checks pass: **READY FOR JUDGES! 🎉**
