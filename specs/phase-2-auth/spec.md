# Specification: Phase 2 Authentication Fixes

**Feature ID:** `phase-2-auth`
**Status:** In Progress
**Priority:** P0 (Blocking Phase 2 Completion)
**Created:** 2025-12-13
**Author:** Senior Cloud-Native Architect

---

## 1. Problem Statement

Phase 2 Todo App has **3 critical authentication bugs** preventing judges from testing:

1. **GitHub OAuth callback missing** - OAuth flow redirects to 404
2. **"Already signed in" state not handled** - Users can sign up while logged in
3. **Theme system duplication** - Dead code confuses codebase

Additionally, UX needs improvement for judge testing experience.

---

## 2. Goals

### Primary Goals (Must Have)
- ✅ Fix GitHub OAuth complete flow (frontend callback page)
- ✅ Add auth state check to signup/signin pages
- ✅ Remove dead ThemeContext.tsx code
- ✅ Add loading states to all auth forms
- ✅ Create judge test checklist

### Non-Goals (Out of Scope)
- ❌ Do NOT refactor unrelated UI components
- ❌ Do NOT add new features beyond auth
- ❌ Do NOT change database schema
- ❌ Do NOT implement password reset (Phase 3)
- ❌ Do NOT add rate limiting (production feature)

---

## 3. Success Criteria

### Acceptance Criteria

**AC1: GitHub OAuth Works End-to-End**
```gherkin
Given a GitHub OAuth App is configured
When user clicks "Continue with GitHub"
Then user is redirected to GitHub authorization
And user approves the app
And user is redirected back to /auth/callback/github
And frontend exchanges code for session
And user is logged in to dashboard
And JWT cookie is set
```

**AC2: Signup Redirects When Already Logged In**
```gherkin
Given user is already logged in
When user navigates to /auth/signup
Then user sees message "You're already signed in"
And sees button "Go to Dashboard"
And sees button "Sign out and create new account"
```

**AC3: Theme System is Clean**
```gherkin
Given codebase review
When searching for theme implementations
Then only next-themes library is found
And custom ThemeContext.tsx does not exist
And no components import custom theme context
```

**AC4: Loading States Prevent Confusion**
```gherkin
Given user submits signup form
When backend is processing
Then submit button shows "Creating account..."
And button is disabled
And spinner icon is shown
When backend responds
Then loading state clears
And success/error message is shown
```

**AC5: Judge Testing is Easy**
```gherkin
Given judge follows AUTHENTICATION_QUICK_START.md
When judge tests email signup flow
Then verification link appears in backend console
And judge can verify within 2 minutes
When judge tests GitHub OAuth (if configured)
Then OAuth flow completes successfully
```

---

## 4. User Stories

### US1: GitHub OAuth User
**As a** user who prefers social login
**I want to** sign up with GitHub
**So that** I don't have to create another password

**Acceptance:**
- GitHub OAuth button is clickable (not disabled)
- Clicking redirects to GitHub
- After approval, I'm logged into the app
- My GitHub email is used for my account
- My account is auto-verified (no email verification needed)

### US2: Logged-In User on Signup Page
**As a** user who is already logged in
**I want to** see a clear message when I visit signup page
**So that** I'm not confused why signup isn't working

**Acceptance:**
- Signup page detects I'm logged in
- Shows message: "You're already signed in as [email]"
- Offers button to go to dashboard
- Offers button to logout and signup with different account

### US3: Judge Testing Auth
**As a** judge evaluating the project
**I want to** test authentication quickly
**So that** I can verify auth works without setup hassle

**Acceptance:**
- README links to AUTHENTICATION_QUICK_START.md
- Guide explains dev mode (console links) vs prod mode (real emails)
- I can test email auth in under 2 minutes
- I can see verification link in console (no email setup needed)
- If I want to test GitHub OAuth, setup steps are documented

---

## 5. Technical Requirements

### TR1: Frontend GitHub Callback Page
**Location:** `frontend/app/auth/callback/github/page.tsx`

**Responsibilities:**
1. Extract `code` query parameter from URL
2. Extract `error` query parameter (if GitHub denied)
3. Call `POST /api/v1/auth/github/callback {code}`
4. Handle success: redirect to `/dashboard`
5. Handle error: redirect to `/auth/signin?error=...`
6. Show loading state while processing

**Dependencies:**
- Backend endpoint already exists: `routes.py:280-418`
- Must use `credentials: 'include'` for cookie

### TR2: Auth State Check in Signup/Signin
**Location:** `frontend/app/auth/signup/page.tsx`, `frontend/app/auth/signin/page.tsx`

**Implementation:**
```typescript
const { user, isLoading } = useAuth()

useEffect(() => {
  if (!isLoading && user) {
    // User is already logged in
    setAlreadyLoggedIn(true)
  }
}, [user, isLoading])

if (alreadyLoggedIn) {
  return <AlreadyLoggedInMessage />
}
```

**Dependencies:**
- `AuthContext` already provides `user` and `isLoading`

### TR3: Remove Dead Theme Code
**Files to Delete:**
- `frontend/contexts/ThemeContext.tsx`

**Files to Update:**
- None (file is not imported anywhere)

**Verification:**
```bash
grep -r "ThemeContext" frontend/
# Should only show ThemeToggle using next-themes
```

### TR4: Loading States
**Pages to Update:**
- `frontend/app/auth/signup/page.tsx`
- `frontend/app/auth/signin/page.tsx`
- `frontend/app/auth/verify-email/page.tsx`

**Pattern:**
```typescript
const [isLoading, setIsLoading] = useState(false)

<button disabled={isLoading}>
  {isLoading ? 'Loading...' : 'Submit'}
</button>
```

---

## 6. API Contract (No Changes)

All backend endpoints remain unchanged. This is purely frontend fixes.

**Existing Endpoints Used:**
- `GET /api/v1/auth/github/authorize` - Already implemented
- `POST /api/v1/auth/github/callback` - Already implemented
- `GET /api/v1/auth/me` - Already implemented

---

## 7. Data Model (No Changes)

No database migrations required.

---

## 8. Security Considerations

### OAuth Security
- **CSRF Protection:** GitHub provides `state` parameter (not implemented yet - acceptable for MVP)
- **Code Exchange:** Backend validates code with GitHub directly
- **Email Verification:** Only use verified primary email from GitHub

### Auth State Leakage
- User state is client-side only (AuthContext)
- Does not expose sensitive data
- JWT is httpOnly (not accessible to JS)

---

## 9. Error Handling

### GitHub OAuth Errors

| Error Scenario | User sees | Redirect |
|----------------|-----------|----------|
| User denies permission | "GitHub authorization denied" | `/auth/signin?error=access_denied` |
| Invalid code | "Authentication failed" | `/auth/signin?error=invalid_code` |
| GitHub API down | "GitHub is temporarily unavailable" | `/auth/signin?error=service_unavailable` |
| Backend error | "An error occurred. Please try again." | `/auth/signin?error=unknown` |

### Already Logged In

| Scenario | UI |
|----------|-----|
| Logged in user visits /signup | Show message with dashboard link |
| Logged in user visits /signin | Redirect to /dashboard immediately |

---

## 10. Testing Strategy

### Unit Tests (Future - Not Required for MVP)
- `AuthContext` state transitions
- Error normalization logic

### Manual Tests (Required)
See `PHASE_E_TEST_CHECKLIST.md` (to be created)

### E2E Tests (Future)
- Playwright tests for full auth flows

---

## 11. Rollout Plan

### Phase 1: Implementation (This Spec)
1. Create GitHub callback page
2. Add auth state checks
3. Remove dead code
4. Add loading states
5. Test manually

### Phase 2: Documentation
1. Update README
2. Update AUTHENTICATION_QUICK_START.md with GitHub OAuth steps
3. Create test checklist for judges

### Phase 3: Deployment
1. Commit all changes
2. Push to GitHub
3. Update Phase 2 submission

---

## 12. Open Questions

**Q1:** Should we implement OAuth `state` parameter for CSRF protection?
**A1:** No - acceptable to skip for MVP; add in Phase 3

**Q2:** Should signup page block submission if already logged in, or just show message?
**A2:** Show message but don't block form (let user decide to logout)

**Q3:** Should we add "Remember me" checkbox to login?
**A3:** No - out of scope; JWT already lasts 7 days

---

## 13. References

- **Phase A Diagnosis:** `PHASE_A_AUTH_DIAGNOSIS.md`
- **Auth Intelligence:** `PHASE_B_CONTEXT7_AUTH_INTELLIGENCE.md`
- **Backend Implementation:** `backend/app/auth/routes.py`
- **Frontend Auth:** `frontend/contexts/AuthContext.tsx`
- **GitHub OAuth Docs:** https://docs.github.com/en/apps/oauth-apps/building-oauth-apps

---

## 14. Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-13 | 1.0 | Initial specification |

---

**Approved By:** Senior Cloud-Native Architect
**Next Step:** Create `plan.md` with implementation strategy
