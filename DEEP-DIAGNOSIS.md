# Deep Diagnosis: Dashboard Not Loading After Signup

## Problem Statement
**Symptom:** After signing up, user is not redirected to dashboard. Clicking "Go to Dashboard" does nothing.

**Expected Behavior:**
1. User fills signup form
2. Clicks "Create Account"
3. **Automatically logged in** (no email verification)
4. **Redirected to dashboard**
5. Dashboard shows with tasks

**Actual Behavior:**
1. User fills signup form
2. Clicks "Create Account"
3. ??? (User reports "nothing happens")

---

## Root Cause Analysis (Based on Phase 4 Experience)

### Issue 1: Frontend Pods Have OLD CODE (95% likely)

**Evidence:**
- We modified `frontend/contexts/AuthContext.tsx` line 118
- Changed from: `router.push('/auth/verify-email?registered=true')`
- Changed to: `await login(email, password)`
- Built Docker image with this fix
- Pushed to registry
- **BUT**: Kubernetes pods may still be running OLD image

**Why This Happens:**
- Kubernetes caches images with `:latest` tag
- When we run `kubectl rollout restart`, it might use cached image
- New image never actually pulled to nodes

**How to Verify:**
```cmd
kubectl get pod -n production -l app=todo-frontend -o jsonpath="{.items[0].status.containerStatuses[0].imageID}"
```
Compare the image ID with what we pushed.

**Symptoms if This is the Issue:**
- After signup, user sees "Check Your Email" page (old behavior)
- OR user sees signup form again (registration completes but no redirect)

---

### Issue 2: Frontend Uses WRONG API URL (Phase 4 Issue #1)

**From Phase 4 PHR:**
> **Problem**: All auth API calls hardcoded to `http://localhost:8000` instead of using `NEXT_PUBLIC_API_URL`
> **Impact**: Frontend couldn't reach backend (wrong URL)

**Current Status:**
- `AuthContext.tsx` line 4: `const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'`
- Dockerfile line 33: `NEXT_PUBLIC_API_URL=http://161-35-250-151.nip.io/api/v1`

**Looks correct**, BUT:
- If frontend image was built BEFORE we set the Dockerfile env var, it has wrong URL
- If `process.env.NEXT_PUBLIC_API_URL` is undefined at build time, defaults to localhost

**How to Verify:**
Check what URL the frontend is actually using:
```cmd
curl -s http://161-35-250-151.nip.io/auth/signup | grep -o "http://[^\"]*8000[^\"]*"
```
If you see `localhost:8000`, frontend has wrong URL baked in.

**Symptoms if This is the Issue:**
- Browser console shows: `Failed to fetch` or `ERR_CONNECTION_REFUSED`
- API calls go to `http://localhost:8000` (which doesn't exist in browser)
- Dashboard loads but is blank (can't fetch tasks)

---

### Issue 3: CORS Blocks Frontend Requests

**From Phase 4:** We had CORS allowing only localhost/todo.local

**Current Status:**
- I updated `backend/app/main.py` lines 40-51
- Changed from: `allow_origin_regex` with hardcoded patterns
- Changed to: `allow_origins` using `CORS_ORIGINS` env var
- Default includes: `http://161-35-250-151.nip.io`

**Looks correct**, BUT:
- If backend image wasn't rebuilt after CORS fix, old CORS config is running
- Backend would reject requests from `161-35-250-151.nip.io` origin

**How to Verify:**
```cmd
curl -I -H "Origin: http://161-35-250-151.nip.io" http://161-35-250-151.nip.io/api/v1/auth/me
```
Check for `Access-Control-Allow-Origin` header. Should include the production domain.

**Symptoms if This is the Issue:**
- Browser console shows: `CORS policy: No 'Access-Control-Allow-Origin' header`
- API calls fail with CORS error
- Dashboard can't fetch data

---

### Issue 4: Middleware Redirects Authenticated Users (Phase 4 Issue #3)

**From Phase 4 PHR:**
> **Problem**: Middleware runs server-side inside K8s pod, tried to call backend via external tunnel URL
> **Impact**: Auth token verification failed, redirecting users back to signin

**Current Code:** Need to check `frontend/middleware.ts`

**Potential Issues:**
- Middleware tries to verify auth token by calling backend
- If middleware uses wrong backend URL (localhost), verification fails
- Failed verification → redirect to `/auth/signin`
- User sees: "Already Signed In" page but can't access dashboard

**How to Verify:**
Check middleware.ts for API calls and ensure it uses correct backend URL.

**Symptoms if This is the Issue:**
- User IS logged in (cookie set)
- Dashboard URL redirects back to signin
- "Already Signed In" message shows

---

### Issue 5: Dashboard Component Has Errors

**Potential Issues:**
- Dashboard tries to fetch tasks on mount
- API call fails (wrong URL, CORS, auth)
- Error thrown, component doesn't render
- Page appears blank

**How to Verify:**
Open browser console (F12) when on dashboard page:
- Look for JavaScript errors (red text)
- Look for failed network requests
- Check what API calls are being made

**Symptoms if This is the Issue:**
- Dashboard URL loads but shows blank page
- Browser console has errors
- Network tab shows failed requests

---

## The Most Likely Issue (Based on Evidence)

**Primary Issue: Frontend pods have OLD code**

Why I believe this:
1. User behavior matches old code (no auto-login)
2. We modified code but didn't verify pods pulled new image
3. Same issue happened in Phase 4
4. Kubernetes `:latest` tag caching is a known issue

**Secondary Issue: Wrong API URL baked into frontend build**

If frontend was built before we updated Dockerfile with correct API URL, it has `localhost:8000` baked in, which won't work in production.

---

## Verification Steps (Do These in Order)

### Step 1: Check Frontend Image ID
```cmd
set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml
kubectl get pod -n production -l app=todo-frontend -o yaml | findstr "image:"
```

**Question:** Does this match the image we built and pushed?

### Step 2: Check Frontend Build Timestamp
```cmd
docker images registry.digitalocean.com/physical-ai-todo-registry/todo-frontend:latest --format "{{.CreatedAt}}"
```

**Question:** Was this image built AFTER we updated AuthContext.tsx?

### Step 3: Check What API URL Frontend Uses
```cmd
curl -s http://161-35-250-151.nip.io/auth/signup > signup-page.html
findstr "localhost" signup-page.html
```

**Question:** Do you see "localhost:8000" anywhere? (Bad if yes)

### Step 4: Test Backend CORS
```cmd
curl -I -H "Origin: http://161-35-250-151.nip.io" http://161-35-250-151.nip.io/api/v1/
```

**Question:** Do you see `Access-Control-Allow-Origin: http://161-35-250-151.nip.io`? (Good if yes)

### Step 5: Check Middleware
```cmd
type frontend\middleware.ts | findstr "localhost"
```

**Question:** Does middleware have hardcoded localhost URLs?

---

## The Fix (Guaranteed to Work)

### Solution 1: Rebuild with Unique Tag (Recommended)
This FORCES Kubernetes to pull fresh image:

```cmd
REM Build with timestamp tag
set TAG=%date:~-4%%date:~-10,2%%date:~-7,2%-%time:~0,2%%time:~3,2%%time:~6,2%

REM Build frontend
docker build -t registry.digitalocean.com/physical-ai-todo-registry/todo-frontend:%TAG% ^
  -f specs/004-kubernetes-deployment/docker/frontend.Dockerfile .

REM Push to registry
docker push registry.digitalocean.com/physical-ai-todo-registry/todo-frontend:%TAG%

REM Update deployment
set KUBECONFIG=C:\Users\Ahsan\physical-ai-todo\k8s-1-32-10-do-2-nyc3-1766308114429-kubeconfig.yaml
kubectl set image deployment/todo-frontend -n production ^
  frontend=registry.digitalocean.com/physical-ai-todo-registry/todo-frontend:%TAG%

REM Wait for rollout
kubectl rollout status deployment/todo-frontend -n production --timeout=5m
```

### Solution 2: Fix All Hardcoded URLs First

Before rebuilding, ensure NO hardcoded localhost URLs:

**Files to check:**
- `frontend/contexts/AuthContext.tsx` - Should use `process.env.NEXT_PUBLIC_API_URL`
- `frontend/middleware.ts` - Should use env var for backend URL
- `frontend/app/dashboard/page.tsx` - Check for fetch calls
- `frontend/app/chat/page.tsx` - Check for fetch calls

**Pattern to find:**
```bash
grep -r "localhost:8000" frontend/
```

**Fix pattern:**
```typescript
// BAD
const API_URL = "http://localhost:8000/api/v1"

// GOOD
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"
```

---

## Complete Fix Procedure

1. **Search for hardcoded URLs:**
   ```cmd
   findstr /s /i "localhost:8000" frontend\*.tsx frontend\*.ts
   ```
   Fix any found.

2. **Verify Dockerfile has correct env var:**
   ```
   NEXT_PUBLIC_API_URL=http://161-35-250-151.nip.io/api/v1
   ```

3. **Rebuild with unique tag:**
   Use timestamp tag, not `:latest`

4. **Push to registry:**
   Ensure push completes successfully

5. **Update deployment:**
   Use `kubectl set image` with specific tag

6. **Verify pod pulled new image:**
   Check image ID matches what we pushed

7. **Clear browser cache:**
   CRITICAL! Old cached JavaScript will use old API URLs

8. **Test signup flow:**
   Fresh signup with new email

---

## Expected Behavior After Fix

1. **Signup page:** User fills form, clicks "Create Account"
2. **Loading state:** Brief spinner/loading indicator
3. **Auto-login:** Backend creates user, returns JWT token, frontend saves cookie
4. **Auto-redirect:** `router.push('/dashboard')` executes
5. **Dashboard loads:** Shows task list (empty for new user)
6. **User can create task:** Form works, task appears in list
7. **Chatbot works:** Can ask "What tasks do I have?"

---

## How to Test Each Step

### Test 1: Signup API Call
Open browser console (F12), go to Network tab, sign up:
- Should see POST to `/api/v1/auth/register`
- Should return 200 with user object
- Should see `is_verified: true`

### Test 2: Auto-Login API Call
Immediately after signup, should see:
- POST to `/api/v1/auth/login`
- Should return 200 with token
- Cookie `access_token` should be set

### Test 3: Dashboard Navigation
After login response:
- URL should change to `/dashboard`
- Page should load (not blank)

### Test 4: Dashboard API Calls
On dashboard page:
- GET to `/api/v1/tasks` (fetch task list)
- Should return 200 with empty array for new user

### Test 5: Task Creation
Create a task:
- POST to `/api/v1/tasks`
- Should return 200 with created task
- Task should appear in list

---

## Summary

**The Issue:** Frontend pods are running OLD code without auto-login fix.

**Why:** Kubernetes cached `:latest` image tag, didn't pull new image.

**The Fix:** Rebuild frontend with UNIQUE tag, force deployment update.

**Verification:** After fix, signup should auto-redirect to dashboard without manual navigation.

---

## Next Steps for You

1. Run verification steps above
2. Share results with me
3. I'll confirm the exact issue
4. Run the guaranteed fix
5. Test and confirm it works

Would you like me to create an automated script that does all verification and fix steps?
