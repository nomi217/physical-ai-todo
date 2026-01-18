# Tasks: Phase 2 Authentication Fixes

**Feature:** `phase-2-auth`
**Date:** 2025-12-13
**Status:** Ready to Execute
**Total Tasks:** 12

---

## Task Execution Order

```
1. Remove Dead Code (Safe, Quick)
   ├─ Task 1: Delete ThemeContext.tsx
   └─ Task 2: Verify theme toggle works

2. Add Loading States (UX Improvement)
   ├─ Task 3: Signup loading state
   ├─ Task 4: Signin loading state
   └─ Task 5: Verify-email loading state

3. Add Auth State Checks (Bug Fix)
   ├─ Task 6: Signup auth check
   └─ Task 7: Signin auth check

4. GitHub OAuth Callback (New Feature)
   ├─ Task 8: Create callback page
   ├─ Task 9: Implement error handling
   └─ Task 10: Test OAuth flow

5. Documentation & Testing
   ├─ Task 11: Update documentation
   └─ Task 12: Create judge test checklist
```

---

## Task 1: Delete Dead Theme Code

**Priority:** P2 (Low Risk)
**Effort:** 5 minutes
**Depends On:** None

### Description
Remove unused custom ThemeContext.tsx file that duplicates next-themes functionality.

### Acceptance Criteria
- [ ] File `frontend/contexts/ThemeContext.tsx` is deleted
- [ ] Run `grep -r "ThemeContext" frontend/` shows no imports (except in deleted file history)
- [ ] Frontend builds without errors: `npm run build`
- [ ] No TypeScript errors related to theme

### Implementation Steps
```bash
cd frontend

# 1. Verify no imports exist
grep -r "from.*ThemeContext" .
grep -r "import.*ThemeContext" .

# Expected: No results (file is dead code)

# 2. Delete file
rm contexts/ThemeContext.tsx

# 3. Verify build works
npm run build

# 4. Start dev server
npm run dev
```

### Test Cases
| Test | Expected Result |
|------|-----------------|
| App loads | No console errors |
| Theme toggle clicks | Theme changes |
| Navigate between pages | Theme persists |

### Rollback
```bash
git checkout HEAD frontend/contexts/ThemeContext.tsx
```

---

## Task 2: Verify Theme Toggle Works

**Priority:** P2
**Effort:** 2 minutes
**Depends On:** Task 1

### Description
Manual verification that theme system still works after removing dead code.

### Acceptance Criteria
- [ ] Theme toggle button visible in header
- [ ] Clicking toggles between light/dark
- [ ] Theme persists across page navigations
- [ ] Theme persists across browser refresh
- [ ] No console errors related to theme

### Implementation Steps
1. Open http://localhost:3001
2. Locate theme toggle button (top right)
3. Click toggle - verify theme changes
4. Navigate to /dashboard - verify theme persists
5. Refresh browser - verify theme persists
6. Open DevTools Console - verify no errors

### Test Cases
```gherkin
Scenario: Toggle theme
  Given I am on the landing page
  When I click the theme toggle button
  Then the page theme changes from dark to light
  And the toggle button shows sun icon

Scenario: Theme persistence
  Given I have selected light theme
  When I navigate to another page
  Then the light theme is still applied

Scenario: Theme after refresh
  Given I have selected light theme
  When I refresh the page
  Then the light theme is still applied
```

---

## Task 3: Add Loading State to Signup Page

**Priority:** P1 (UX Critical)
**Effort:** 10 minutes
**Depends On:** None

### Description
Add loading state to signup form to prevent double submissions and show progress.

### Acceptance Criteria
- [ ] Add `isSubmitting` state variable
- [ ] Disable submit button when `isSubmitting === true`
- [ ] Show "Creating account..." text during submission
- [ ] Show loading spinner icon during submission
- [ ] Clear loading state on success or error
- [ ] Form cannot be resubmitted while loading

### Implementation
**File:** `frontend/app/auth/signup/page.tsx`

**Changes:**
```typescript
// Add state
const [isSubmitting, setIsSubmitting] = useState(false)

// Update handleSubmit
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault()
  setError('')
  setIsSubmitting(true)  // ← ADD

  try {
    await register(email, password, fullName)
  } catch (err: any) {
    setError(err.message || 'Failed to create account')
  } finally {
    setIsSubmitting(false)  // ← ADD
  }
}

// Update button
<button
  type="submit"
  disabled={isSubmitting || !email || !password}  // ← ADD isSubmitting
  className="..."
>
  {isSubmitting ? 'Creating account...' : 'Create Account'}  // ← ADD
</button>
```

### Test Cases
```gherkin
Scenario: Loading state during signup
  Given I am on the signup page
  When I fill in valid credentials
  And I click "Create Account"
  Then the button text changes to "Creating account..."
  And the button becomes disabled
  When the request completes
  Then the button re-enables
  And the button text returns to "Create Account"
```

---

## Task 4: Add Loading State to Signin Page

**Priority:** P1
**Effort:** 10 minutes
**Depends On:** None

### Description
Same as Task 3, but for signin page.

### Acceptance Criteria
- [ ] Add `isSubmitting` state variable
- [ ] Disable submit button during submission
- [ ] Show "Signing in..." text during submission
- [ ] Show loading spinner icon during submission
- [ ] Clear loading state on success or error

### Implementation
**File:** `frontend/app/auth/signin/page.tsx`

**Changes:** (Same pattern as Task 3)

### Test Cases
```gherkin
Scenario: Loading state during signin
  Given I am on the signin page
  When I fill in valid credentials
  And I click "Sign In"
  Then the button text changes to "Signing in..."
  And the button becomes disabled
  And I cannot submit the form again
```

---

## Task 5: Add Loading State to Verify Email Page

**Priority:** P1
**Effort:** 10 minutes
**Depends On:** None

### Description
Add loading state while verification request is processing.

### Acceptance Criteria
- [ ] Show loading spinner immediately when page loads
- [ ] Show "Verifying your email..." message
- [ ] On success: show success message + redirect countdown
- [ ] On error: show error message + link back to signin

### Implementation
**File:** `frontend/app/auth/verify-email/page.tsx`

**Changes:**
```typescript
const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')

{status === 'loading' && (
  <div>
    <Spinner />
    <p>Verifying your email...</p>
  </div>
)}

{status === 'success' && (
  <div>
    <p>Email verified successfully!</p>
    <p>Redirecting to sign in...</p>
  </div>
)}

{status === 'error' && (
  <div>
    <p>{errorMessage}</p>
    <Link href="/auth/signin">Back to Sign In</Link>
  </div>
)}
```

### Test Cases
```gherkin
Scenario: Email verification loading
  Given I have a verification link
  When I open the link
  Then I see "Verifying your email..."
  And I see a loading spinner
  When verification completes successfully
  Then I see "Email verified successfully!"
  And I am redirected to signin after 2 seconds
```

---

## Task 6: Add Auth State Check to Signup Page

**Priority:** P0 (Bug Fix)
**Effort:** 15 minutes
**Depends On:** None

### Description
Show "already signed in" message when logged-in user visits signup page.

### Acceptance Criteria
- [ ] Check `user` and `isLoading` from `useAuth()`
- [ ] If loading, show loading spinner
- [ ] If user exists, show "already signed in" UI
- [ ] Provide "Go to Dashboard" button
- [ ] Provide "Sign out" button
- [ ] If no user, show normal signup form

### Implementation
**File:** `frontend/app/auth/signup/page.tsx`

**Changes:**
```typescript
import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'

export default function SignUpPage() {
  const { user, isLoading, logout } = useAuth()
  const router = useRouter()

  // Show loading while checking auth status
  if (isLoading) {
    return <LoadingSpinner />
  }

  // User is already logged in
  if (user) {
    return (
      <div className="...">
        <h2>You're Already Signed In</h2>
        <p>Signed in as: <strong>{user.email}</strong></p>

        <button onClick={() => router.push('/dashboard')}>
          Go to Dashboard
        </button>

        <button onClick={async () => {
          await logout()
          router.push('/auth/signup')
        }}>
          Sign out and create new account
        </button>
      </div>
    )
  }

  // Normal signup form
  return (
    <div className="...">
      {/* Existing form */}
    </div>
  )
}
```

### Test Cases
```gherkin
Scenario: Logged-in user visits signup
  Given I am logged in as "test@example.com"
  When I navigate to /auth/signup
  Then I see "You're Already Signed In"
  And I see "Signed in as: test@example.com"
  And I see "Go to Dashboard" button
  And I see "Sign out and create new account" button

Scenario: Click Go to Dashboard
  Given I see the "already signed in" message
  When I click "Go to Dashboard"
  Then I am redirected to /dashboard

Scenario: Click Sign out
  Given I see the "already signed in" message
  When I click "Sign out and create new account"
  Then I am logged out
  And I see the signup form
```

---

## Task 7: Add Auth State Check to Signin Page

**Priority:** P0
**Effort:** 10 minutes
**Depends On:** None

### Description
Redirect logged-in users directly to dashboard from signin page.

### Acceptance Criteria
- [ ] Check `user` from `useAuth()`
- [ ] If user exists, redirect to `/dashboard` automatically
- [ ] Use `useEffect` to avoid flickering

### Implementation
**File:** `frontend/app/auth/signin/page.tsx`

**Changes:**
```typescript
const { user, isLoading } = useAuth()
const router = useRouter()

useEffect(() => {
  if (!isLoading && user) {
    router.push('/dashboard')
  }
}, [user, isLoading, router])

if (isLoading) {
  return <LoadingSpinner />
}

// Normal signin form (only shown if !user)
```

### Test Cases
```gherkin
Scenario: Logged-in user visits signin
  Given I am logged in
  When I navigate to /auth/signin
  Then I am immediately redirected to /dashboard
  And I never see the signin form
```

---

## Task 8: Create GitHub OAuth Callback Page

**Priority:** P0 (Blocking OAuth)
**Effort:** 30 minutes
**Depends On:** None

### Description
Create frontend page to handle GitHub OAuth callback and exchange code for session.

### Acceptance Criteria
- [ ] Create file: `frontend/app/auth/callback/github/page.tsx`
- [ ] Extract `code` and `error` from URL query parameters
- [ ] Handle error scenario (user denied permission)
- [ ] Call backend endpoint: `POST /api/v1/auth/github/callback`
- [ ] On success: update auth state and redirect to dashboard
- [ ] On error: show error message with link to signin
- [ ] Show loading state during processing

### Implementation
**File:** `frontend/app/auth/callback/github/page.tsx` (CREATE NEW)

**Code:** (See plan.md Section 3.1 for full implementation)

**Key Points:**
```typescript
'use client'
import { useSearchParams } from 'next/navigation'

const searchParams = useSearchParams()
const code = searchParams.get('code')
const error = searchParams.get('error')

// Handle error from GitHub
if (error) {
  return <ErrorUI message={getErrorMessage(error)} />
}

// Call backend
const response = await fetch('http://localhost:8000/api/v1/auth/github/callback', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',  // IMPORTANT: Include cookies
  body: JSON.stringify({ code })
})
```

### Test Cases
```gherkin
Scenario: Successful GitHub OAuth callback
  Given GitHub redirects to /auth/callback/github?code=abc123
  When the page loads
  Then I see "Completing sign-in with GitHub..."
  When the backend responds successfully
  Then I see "Signed in! Redirecting..."
  And I am redirected to /dashboard within 1 second

Scenario: GitHub OAuth error (user denied)
  Given GitHub redirects to /auth/callback/github?error=access_denied
  When the page loads
  Then I see "GitHub authorization denied"
  And I see a link "Back to Sign In"

Scenario: Invalid code error
  Given backend returns 400 error
  When callback processing fails
  Then I see "Authentication failed: [error message]"
  And I see a link to return to signin
```

---

## Task 9: Implement Error Handling in OAuth Callback

**Priority:** P1
**Effort:** 10 minutes
**Depends On:** Task 8

### Description
Add comprehensive error handling for all GitHub OAuth failure scenarios.

### Acceptance Criteria
- [ ] Handle `?error=access_denied` from GitHub
- [ ] Handle `?error=<other>` from GitHub
- [ ] Handle missing `code` parameter
- [ ] Handle backend 400/500 errors
- [ ] Handle network errors (fetch failed)
- [ ] Show user-friendly error messages
- [ ] Provide "Try Again" link back to signin

### Implementation
```typescript
function getErrorMessage(error: string): string {
  const errorMessages: Record<string, string> = {
    'access_denied': 'You denied GitHub authorization. Please try again.',
    'invalid_request': 'Invalid OAuth request. Please try again.',
    'unauthorized_client': 'OAuth app not authorized. Contact support.',
    'unsupported_response_type': 'OAuth configuration error. Contact support.'
  }

  return errorMessages[error] || 'An unknown error occurred during GitHub sign-in.'
}

// In handleCallback
try {
  // ...API call
} catch (err: any) {
  if (err.message.includes('fetch')) {
    setMessage('Network error. Please check your connection and try again.')
  } else {
    setMessage(err.message || 'An error occurred. Please try again.')
  }
}
```

### Test Cases
| Scenario | URL | Expected Message |
|----------|-----|------------------|
| User denied | `?error=access_denied` | "You denied GitHub authorization..." |
| Invalid request | `?error=invalid_request` | "Invalid OAuth request..." |
| Missing code | `?` (no params) | "No authorization code received" |
| Backend error | Backend 400 | "Authentication failed: [backend message]" |
| Network error | Fetch fails | "Network error. Please check your connection..." |

---

## Task 10: Test Complete GitHub OAuth Flow

**Priority:** P0
**Effort:** 20 minutes
**Depends On:** Tasks 8, 9

### Description
End-to-end manual testing of GitHub OAuth flow.

### Prerequisites
- [ ] GitHub OAuth App created at https://github.com/settings/developers
- [ ] `GITHUB_CLIENT_ID` set in `backend/.env`
- [ ] `GITHUB_CLIENT_SECRET` set in `backend/.env`
- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 3001

### Acceptance Criteria
- [ ] Click "Continue with GitHub" button (must be enabled first - remove `disabled` prop)
- [ ] Redirected to GitHub authorization page
- [ ] Approve the app on GitHub
- [ ] Redirected back to `http://localhost:3001/auth/callback/github?code=...`
- [ ] See loading screen: "Completing sign-in with GitHub..."
- [ ] See success message: "Signed in! Redirecting..."
- [ ] Redirected to dashboard within 1-2 seconds
- [ ] User is logged in (check navbar shows user email)
- [ ] JWT cookie is set (check DevTools → Application → Cookies)

### Test Steps
```bash
# 1. Set up GitHub OAuth (if not done)
# Visit https://github.com/settings/developers
# Create new OAuth App with:
#   - Homepage: http://localhost:3001
#   - Callback: http://localhost:3001/auth/callback/github
# Copy Client ID and Client Secret to backend/.env

# 2. Enable GitHub button in frontend
# Edit frontend/app/auth/signin/page.tsx
# Remove disabled={true} from GitHub button

# 3. Start both servers
cd backend && python -m uvicorn app.main:app --reload
cd frontend && npm run dev

# 4. Test OAuth flow
# Open http://localhost:3001/auth/signin
# Click "Continue with GitHub"
# Approve on GitHub
# Verify redirect back to app
# Verify logged in to dashboard
```

### Test Cases
```gherkin
Feature: GitHub OAuth Authentication

Scenario: First-time GitHub user signs up
  Given I have never signed up before
  When I click "Continue with GitHub" on signin page
  And I approve the app on GitHub
  Then a new account is created with my GitHub email
  And my email is automatically verified
  And I am logged in to the dashboard
  And I can see my GitHub name displayed

Scenario: Existing GitHub user signs in
  Given I previously signed up with GitHub
  When I click "Continue with GitHub"
  And I approve the app on GitHub
  Then I am logged in to my existing account
  And I am redirected to the dashboard

Scenario: User with email account links GitHub
  Given I have an account with email test@example.com
  And my GitHub account uses test@example.com
  When I sign in with GitHub
  Then I am logged in to my existing email-based account
  And my account is now verified

Scenario: User denies GitHub permission
  Given I click "Continue with GitHub"
  When I deny permission on GitHub
  Then I am redirected back to the app
  And I see "You denied GitHub authorization"
  And I can click "Back to Sign In" to try again
```

---

## Task 11: Update Documentation

**Priority:** P1
**Effort:** 15 minutes
**Depends On:** Tasks 8, 9, 10

### Description
Update authentication documentation with GitHub OAuth setup instructions.

### Acceptance Criteria
- [ ] Update `AUTHENTICATION_QUICK_START.md` with OAuth section
- [ ] Add step-by-step GitHub OAuth App creation guide
- [ ] Add screenshots or clear instructions for GitHub settings
- [ ] Update `README.md` .env example with OAuth variables
- [ ] Document that OAuth is optional for testing

### Implementation

**File:** `AUTHENTICATION_QUICK_START.md`

**Add Section:**
```markdown
## Option 2: Sign Up with GitHub OAuth (Optional)

### For Judges: GitHub OAuth is OPTIONAL
- Email/password auth works without any setup
- GitHub OAuth requires creating a GitHub OAuth App (5 minutes)
- If you skip this, email auth is fully functional

### Setting Up GitHub OAuth (If Desired)

#### Step 1: Create GitHub OAuth App
1. Visit https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in:
   - Application name: `FlowTask Local Development`
   - Homepage URL: `http://localhost:3001`
   - Authorization callback URL: `http://localhost:3001/auth/callback/github`
4. Click "Register application"
5. Copy the **Client ID**
6. Click "Generate a new client secret"
7. Copy the **Client Secret**

#### Step 2: Add Credentials to Backend
1. Open `backend/.env`
2. Update these lines:
   ```env
   GITHUB_CLIENT_ID=your_actual_client_id_here
   GITHUB_CLIENT_SECRET=your_actual_client_secret_here
   ```
3. Restart backend server: `python -m uvicorn app.main:app --reload`

#### Step 3: Test OAuth
1. Visit http://localhost:3001/auth/signin
2. Click "Continue with GitHub" (should now be enabled)
3. Approve the app on GitHub
4. You'll be redirected back and logged in automatically
5. No email verification needed (GitHub verified your email)

### Troubleshooting GitHub OAuth
- **Button disabled?** Check that `GITHUB_CLIENT_ID` is set in .env
- **404 error?** Verify callback URL is `http://localhost:3001/auth/callback/github`
- **"Invalid credentials"?** Restart backend after updating .env
```

**File:** `README.md`

**Update .env Example:**
```env
# GitHub OAuth (OPTIONAL - for social login)
# Create OAuth App: https://github.com/settings/developers
# Homepage: http://localhost:3001
# Callback: http://localhost:3001/auth/callback/github
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here
```

---

## Task 12: Create Judge Test Checklist

**Priority:** P1
**Effort:** 10 minutes
**Depends On:** All previous tasks

### Description
Create a simple checklist judges can follow to test all authentication features.

### Acceptance Criteria
- [ ] Create `JUDGE_AUTH_TEST_CHECKLIST.md`
- [ ] Include 2-minute email auth test
- [ ] Include 5-minute GitHub OAuth test (optional)
- [ ] Include troubleshooting tips
- [ ] Include expected behaviors

### Implementation

**File:** `JUDGE_AUTH_TEST_CHECKLIST.md` (CREATE NEW)

**Content:**
```markdown
# Judge Auth Test Checklist

## Quick Test (2 minutes) - Email Auth

- [ ] Start backend: `cd backend && python -m uvicorn app.main:app --reload`
- [ ] Start frontend: `cd frontend && npm run dev`
- [ ] Visit: http://localhost:3001
- [ ] Click "Get Started"
- [ ] Fill signup form (any email, password 8+ chars)
- [ ] Submit form
- [ ] Check backend console for verification link
- [ ] Copy verification link and open in browser
- [ ] See "Email verified successfully!"
- [ ] Click "Sign In"
- [ ] Enter same credentials
- [ ] See dashboard with tasks

**Expected:** ✅ All steps work without errors

## Full Test (5 minutes) - With GitHub OAuth

- [ ] Create GitHub OAuth App (see AUTHENTICATION_QUICK_START.md)
- [ ] Add credentials to backend/.env
- [ ] Restart backend
- [ ] Visit http://localhost:3001/auth/signin
- [ ] Click "Continue with GitHub"
- [ ] Approve on GitHub
- [ ] See loading screen "Completing sign-in..."
- [ ] See dashboard (auto-verified, no email step)

**Expected:** ✅ OAuth works end-to-end

## Edge Cases to Test

- [ ] Sign up with email that already exists → Error: "Email already registered"
- [ ] Sign in with wrong password → Error: "Invalid email or password"
- [ ] Sign in before verifying email → Error: "Please verify your email"
- [ ] Visit /signup while logged in → See "Already signed in" message
- [ ] Visit /signin while logged in → Redirect to dashboard
- [ ] Toggle theme → Works in light and dark mode
- [ ] Click submit twice quickly → Button disabled, only one request sent

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Site can't be reached" | Check both servers running (ports 8000, 3001) |
| "CORS error" | Verify `FRONTEND_URL=http://localhost:3001` in backend/.env |
| No verification email | Dev mode: Check backend console for link |
| GitHub OAuth 404 | Callback page created: `app/auth/callback/github/page.tsx` |
| Button stays loading | Check browser console (F12) for errors |
```

---

## Summary

**Total Tasks:** 12
**Estimated Total Time:** 2-3 hours
**Critical Path:** Tasks 8 → 9 → 10 (GitHub OAuth)
**Quick Wins:** Tasks 1, 2 (Remove dead code - 7 minutes)

**Task Categories:**
- 🗑️ **Cleanup:** Tasks 1-2 (Remove dead code)
- 🎨 **UX:** Tasks 3-5 (Loading states)
- 🐛 **Bug Fixes:** Tasks 6-7 (Auth state checks)
- ✨ **New Feature:** Tasks 8-10 (GitHub OAuth)
- 📚 **Documentation:** Tasks 11-12 (Guides and checklists)

**Completion Checklist:**
- [ ] All 12 tasks completed
- [ ] All test cases passing
- [ ] No console errors
- [ ] No TypeScript errors
- [ ] Documentation updated
- [ ] Ready for judge testing
- [ ] Committed to Git
- [ ] Pushed to GitHub

---

**Next Step:** Execute tasks in order, commit after each working change.
