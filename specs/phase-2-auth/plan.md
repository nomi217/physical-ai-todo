# Implementation Plan: Phase 2 Authentication Fixes

**Feature:** `phase-2-auth`
**Date:** 2025-12-13
**Status:** Ready for Implementation
**Est. Effort:** 2-3 hours

---

## 1. Architecture Overview

### Current State
```
┌─────────────────────────────────────────────┐
│  Frontend (Next.js 14 - Port 3001)         │
│  ┌──────────────────────────────────────┐  │
│  │  /auth/signup  ❌ No auth check     │  │
│  │  /auth/signin  ❌ No auth check     │  │
│  │  /auth/callback/github ❌ MISSING    │  │
│  ├──────────────────────────────────────┤  │
│  │  contexts/ThemeContext.tsx ❌ DEAD   │  │
│  │  contexts/AuthContext.tsx ✅ Works   │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
                     │
                     │ HTTP + Cookies
                     ↓
┌─────────────────────────────────────────────┐
│  Backend (FastAPI - Port 8000)             │
│  ┌──────────────────────────────────────┐  │
│  │  /api/v1/auth/github/authorize       │  │
│  │  ✅ Works - redirects to GitHub      │  │
│  ├──────────────────────────────────────┤  │
│  │  /api/v1/auth/github/callback        │  │
│  │  ✅ Works - exchanges code for token │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

### Target State
```
┌─────────────────────────────────────────────┐
│  Frontend (Next.js 14 - Port 3001)         │
│  ┌──────────────────────────────────────┐  │
│  │  /auth/signup  ✅ Auth check added   │  │
│  │  /auth/signin  ✅ Auth check added   │  │
│  │  /auth/callback/github ✅ CREATED    │  │
│  ├──────────────────────────────────────┤  │
│  │  contexts/AuthContext.tsx ✅ Works   │  │
│  │  (ThemeContext.tsx removed)          │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

---

## 2. Implementation Strategy

### Principle: Minimum Viable Fixes
- Fix only what's broken
- Don't refactor working code
- Don't add new features
- Prioritize judge testing experience

### Risk Mitigation
- Test each change independently
- Commit after each working fix
- Can roll back if issues arise

---

## 3. Detailed Design

### 3.1 GitHub OAuth Callback Page

**File:** `frontend/app/auth/callback/github/page.tsx`

**Design Decision:**
- Use `'use client'` directive (interactive page)
- Use `useSearchParams()` to read query parameters
- Use `useAuth()` context for session management
- Use `useRouter()` for navigation

**Flow:**
```typescript
1. Page loads with URL: /auth/callback/github?code=abc123
2. useEffect runs on mount
3. Extract code from URL
4. Call backend: POST /api/v1/auth/github/callback {code}
5. If success:
   - Backend returns TokenResponse
   - Backend sets JWT cookie
   - Frontend calls refreshUser() to update AuthContext
   - Redirect to /dashboard
6. If error:
   - Show error message
   - Provide link back to /auth/signin
```

**Error Scenarios:**
- `?error=access_denied` - User denied GitHub permission
- `?error` without code - OAuth flow failed
- Backend returns 400/500 - API error
- Network error - Show generic message

**UI States:**
1. **Loading:** "Completing sign-in with GitHub..."
2. **Success:** "Signed in! Redirecting..."
3. **Error:** "Authentication failed: [message]"

**Code Pattern:**
```typescript
'use client'
import { useEffect, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'

export default function GitHubCallbackPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const { refreshUser } = useAuth()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')

  useEffect(() => {
    const code = searchParams.get('code')
    const error = searchParams.get('error')

    if (error) {
      setStatus('error')
      setMessage(getErrorMessage(error))
      return
    }

    if (!code) {
      setStatus('error')
      setMessage('No authorization code received')
      return
    }

    handleCallback(code)
  }, [searchParams])

  const handleCallback = async (code: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/github/callback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ code })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Authentication failed')
      }

      setStatus('success')
      await refreshUser()  // Update AuthContext
      setTimeout(() => router.push('/dashboard'), 1000)
    } catch (err: any) {
      setStatus('error')
      setMessage(err.message)
    }
  }

  return (
    <div>
      {status === 'loading' && <LoadingUI />}
      {status === 'success' && <SuccessUI />}
      {status === 'error' && <ErrorUI message={message} />}
    </div>
  )
}
```

---

### 3.2 Auth State Check in Signup/Signin

**Files:**
- `frontend/app/auth/signup/page.tsx`
- `frontend/app/auth/signin/page.tsx`

**Design Decision:**
- Use existing `useAuth()` hook
- Check `user` and `isLoading` state
- Show different UI if already logged in
- Don't block form submission (let user decide)

**Implementation Pattern:**
```typescript
'use client'
import { useAuth } from '@/contexts/AuthContext'

export default function SignUpPage() {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (user) {
    return (
      <div className="...">
        <h2>You're Already Signed In</h2>
        <p>Signed in as: {user.email}</p>
        <button onClick={() => router.push('/dashboard')}>
          Go to Dashboard
        </button>
        <button onClick={handleLogout}>
          Sign out and create new account
        </button>
      </div>
    )
  }

  return (
    <div className="...">
      {/* Existing signup form */}
    </div>
  )
}
```

**Edge Cases:**
- User has cookie but API returns 401 - isLoading will be false, user will be null, form shows normally
- User logs out in another tab - No real-time sync, acceptable for MVP

---

### 3.3 Remove Dead Theme Code

**File to Delete:**
- `frontend/contexts/ThemeContext.tsx`

**Verification Steps:**
1. Search for imports: `grep -r "ThemeContext" frontend/`
2. Ensure only internal references in the file itself
3. Delete file
4. Verify app still runs
5. Verify theme toggle still works (uses `next-themes`)

**Rollback Plan:**
- Git can restore if needed
- But file is confirmed unused, so safe to delete

---

### 3.4 Add Loading States

**Files to Update:**
- `frontend/app/auth/signup/page.tsx`
- `frontend/app/auth/signin/page.tsx`
- `frontend/app/auth/verify-email/page.tsx`

**Pattern:**
```typescript
const [isSubmitting, setIsSubmitting] = useState(false)

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault()
  setError('')
  setIsSubmitting(true)  // ← Set loading state

  try {
    await authOperation()
  } catch (err: any) {
    setError(err.message)
  } finally {
    setIsSubmitting(false)  // ← Clear loading state
  }
}

<button
  type="submit"
  disabled={isSubmitting}  // ← Disable during loading
  className="..."
>
  {isSubmitting ? (
    <>
      <LoadingSpinner />
      <span>Processing...</span>
    </>
  ) : (
    'Submit'
  )}
</button>
```

**Loading Messages:**
- Signup: "Creating account..."
- Signin: "Signing in..."
- Verify email: "Verifying..."
- GitHub callback: "Completing sign-in..."

---

## 4. Testing Approach

### Testing Order
1. **Test Theme Removal**
   - Delete file
   - Run `npm run dev`
   - Toggle theme in UI
   - Verify no console errors

2. **Test Auth State Check**
   - Sign in as user
   - Visit `/auth/signup`
   - Verify "already signed in" message shows
   - Click "Go to Dashboard" - should redirect
   - Click "Sign out" - should logout and show form

3. **Test Loading States**
   - Submit signup form
   - Verify button disables
   - Verify loading text shows
   - Verify spinner appears
   - Wait for response
   - Verify loading clears

4. **Test GitHub OAuth (if configured)**
   - Click "Continue with GitHub"
   - Approve on GitHub
   - Verify redirect to `/auth/callback/github?code=...`
   - Verify loading screen shows
   - Verify redirect to dashboard
   - Verify user is logged in

---

## 5. Dependencies

### External Dependencies
- No new npm packages needed
- Uses existing: `next/navigation`, `framer-motion`, context hooks

### Backend Dependencies
- Backend endpoints already exist
- No backend changes required

### Configuration Dependencies
- GitHub OAuth requires:
  - `GITHUB_CLIENT_ID` in backend/.env
  - `GITHUB_CLIENT_SECRET` in backend/.env
  - GitHub OAuth App created at https://github.com/settings/developers

---

## 6. File Changes Summary

### Files to Create (1)
- `frontend/app/auth/callback/github/page.tsx` (new OAuth callback)

### Files to Modify (3)
- `frontend/app/auth/signup/page.tsx` (add auth check + loading)
- `frontend/app/auth/signin/page.tsx` (add auth check + loading)
- `frontend/app/auth/verify-email/page.tsx` (add loading state)

### Files to Delete (1)
- `frontend/contexts/ThemeContext.tsx` (dead code)

### Total Changes
- **+1 file** (GitHub callback)
- **~3 files** (auth pages)
- **-1 file** (dead theme code)
- **Net: +50 LOC**

---

## 7. Implementation Sequence

### Step 1: Remove Dead Code (5 minutes)
```bash
# Verify no imports
grep -r "from.*ThemeContext" frontend/

# Delete file
rm frontend/contexts/ThemeContext.tsx

# Test app still runs
cd frontend && npm run dev
```

**Why first:** Safest change, cleans codebase, no dependencies

### Step 2: Add Loading States (15 minutes)
- Update signup page: `isSubmitting` state
- Update signin page: `isSubmitting` state
- Update verify-email page: `isProcessing` state
- Test each page independently

**Why second:** Independent changes, improves UX immediately

### Step 3: Add Auth State Check (20 minutes)
- Update signup page: check `user`, show "already signed in" UI
- Update signin page: same logic
- Test: sign in, visit pages, verify redirects work

**Why third:** Builds on existing AuthContext, no backend changes

### Step 4: Create GitHub Callback Page (30 minutes)
- Create `app/auth/callback/github/page.tsx`
- Implement loading/success/error states
- Test with console.log first (before actual OAuth)
- Configure GitHub OAuth App if needed
- Test full OAuth flow

**Why last:** Most complex, requires external service, optional for judges

---

## 8. Rollback Plan

### If GitHub OAuth Breaks
- Revert `app/auth/callback/github/page.tsx`
- Disable GitHub buttons (already have fallback)
- Judges can still test email auth

### If Auth State Check Breaks
- Revert changes to signup/signin pages
- Users can still sign up (just no warning)

### If Loading States Break
- Revert button changes
- Users can still submit forms (just no visual feedback)

### If Theme Removal Breaks
- `git checkout HEAD frontend/contexts/ThemeContext.tsx`
- App continues working (file was unused anyway)

---

## 9. Performance Considerations

### GitHub OAuth Callback
- Redirect latency: ~500ms (network to GitHub)
- Backend processing: ~200ms (token exchange)
- Total user wait: ~1 second (acceptable)
- Loading spinner prevents perceived slowness

### Auth State Check
- `useAuth()` hook already runs on mount
- No additional API calls
- Negligible performance impact

---

## 10. Security Considerations

### GitHub OAuth
- **Code reuse attack:** GitHub codes are one-time use only ✅
- **CSRF:** Not implemented (acceptable for MVP; add `state` parameter in Phase 3)
- **Man-in-the-middle:** Uses HTTPS for GitHub communication ✅
- **Session hijacking:** JWT in httpOnly cookie ✅

### Auth State Leakage
- User email shown in "already signed in" message
- Acceptable: user is already authenticated
- Does not expose other user data

---

## 11. Documentation Updates

### AUTHENTICATION_QUICK_START.md
- Add section: "Testing GitHub OAuth"
- Steps to create GitHub OAuth App
- Screenshots of GitHub settings page
- Note that it's optional for testing

### README.md
- Update .env example with GitHub OAuth variables
- Link to OAuth setup guide

---

## 12. Success Metrics

### Functional
- ✅ GitHub OAuth flow completes without errors
- ✅ Signed-in users see "already signed in" message
- ✅ Theme toggle still works after code removal
- ✅ Loading states show during all auth operations

### Non-Functional
- ✅ No new console errors
- ✅ No new TypeScript errors
- ✅ App bundle size unchanged or smaller
- ✅ Lighthouse score unchanged or better

---

## 13. Future Improvements (Out of Scope)

- Add OAuth `state` parameter for CSRF protection
- Add rate limiting to prevent brute force
- Add "Remember me" checkbox
- Add multi-factor authentication
- Add password reset flow
- Add email change flow
- Add account deletion

---

## 14. Architectural Decisions

### ADR-001: Use GitHub OAuth over other providers
**Decision:** Implement GitHub OAuth only (not Google, Microsoft, etc.)
**Rationale:**
- Judges likely have GitHub accounts (developer audience)
- Simpler setup (one OAuth provider vs many)
- GitHub provides verified email automatically
**Alternatives Considered:**
- Google OAuth - More universal but harder to set up
- Magic link - Simpler but requires email service
**Consequences:**
- Users without GitHub must use email/password
- Acceptable for developer-focused app

### ADR-002: Client-side auth state check vs. redirect
**Decision:** Show message on signup/signin page instead of automatic redirect
**Rationale:**
- User might want to logout and create new account
- More explicit, less "magic" behavior
- Gives user control
**Alternatives Considered:**
- Auto-redirect to dashboard - Less flexible
- Block form submission - Confusing UX
**Consequences:**
- Slightly more UI code
- Better user experience

### ADR-003: Remove custom ThemeContext vs. keep both
**Decision:** Remove custom implementation, keep only next-themes
**Rationale:**
- Custom code is unused (grep confirms)
- Reduces maintenance burden
- next-themes is battle-tested
**Alternatives Considered:**
- Keep both - Confusing, wasteful
- Remove next-themes, keep custom - More work, less features
**Consequences:**
- Cleaner codebase
- One less file to maintain

---

**Next Step:** Create `tasks.md` with testable, granular tasks

---

**Reviewed By:** Senior Cloud-Native Architect
**Status:** ✅ Ready for Implementation
