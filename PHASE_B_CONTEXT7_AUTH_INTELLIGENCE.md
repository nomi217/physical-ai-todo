# Phase B: Context7 MCP - Auth Intelligence Design

**Date:** 2025-12-13
**Purpose:** Create reusable auth intelligence for Phase 3 RAG chatbot
**Format:** Structured metadata consumable by Context7 MCP and LLMs

---

## Overview

This document defines **auth-context7** - a structured knowledge base about the authentication system that can be consumed by:
- Context7 MCP server for code understanding
- Phase 3 RAG chatbot for answering auth questions
- Future developers for onboarding
- AI assistants for debugging

---

## 1. Authentication Rules (Normative)

### Email Normalization Rule
```yaml
rule_id: AUTH-001
name: Email Case-Insensitive Normalization
applies_to: [register, login, verify, resend-verification]
implementation:
  backend: "email.lower() before any database operation"
  locations:
    - backend/app/auth/routes.py:64 (register)
    - backend/app/auth/routes.py:114 (login)
    - backend/app/auth/routes.py:224 (resend-verification)
    - backend/app/auth/routes.py:365 (github callback)
reasoning: |
  Users should be able to login with any case variant of their email.
  Database stores lowercase; all comparisons use lowercase.
test_cases:
  - input: "Test@Example.COM"
    stored_as: "test@example.com"
    login_with: ["test@example.com", "TEST@EXAMPLE.COM", "TeSt@ExAmPlE.cOm"]
    all_succeed: true
```

### Password Security Rule
```yaml
rule_id: AUTH-002
name: Password Hashing with bcrypt
applies_to: [register, password_reset]
implementation:
  library: passlib[bcrypt]
  version: "bcrypt<5.0.0"  # Important: v5+ incompatible with passlib
  location: backend/app/auth/password.py
  functions:
    - hash_password(plain: str) -> str
    - verify_password(plain: str, hashed: str) -> bool
security_requirements:
  - Never store plaintext passwords
  - Never log passwords (even hashed)
  - Use bcrypt with automatic salt
  - Minimum password length: 8 characters (enforced by Pydantic)
```

### JWT Session Rule
```yaml
rule_id: AUTH-003
name: JWT Token in httpOnly Cookie
applies_to: [login, github_callback]
implementation:
  storage: httpOnly cookie
  key: "access_token"
  security_flags:
    httponly: true
    samesite: "lax"
    secure: false  # development; true in production
    max_age: 604800  # 7 days
  location: backend/app/auth/routes.py:137-146, 406-413
reasoning: |
  httpOnly prevents XSS attacks from stealing tokens.
  samesite=lax allows cookies on same-site requests.
  secure=false needed for localhost HTTP (no HTTPS).
frontend_access:
  - Frontend cannot read cookie directly (httpOnly)
  - Must call /api/v1/auth/me to check auth status
  - Automatically included in fetch() with credentials:'include'
```

### Verification Flow Rule
```yaml
rule_id: AUTH-004
name: Email Verification Required Before Login
applies_to: [register, login]
flow:
  1_register:
    creates_user_with: {is_active: false, is_verified: false}
    generates: verification_token (32-byte urlsafe)
    sends_email: true (console in dev, real in prod)
  2_verify:
    endpoint: POST /api/v1/auth/verify-email {token}
    updates_user: {is_verified: true, is_active: true, verification_token: null}
    sends_welcome_email: true
  3_login:
    checks: is_verified == true
    if_false: raises 403 "Please verify your email address first"
exceptions:
  - GitHub OAuth users are auto-verified (is_verified=true immediately)
implementation:
  - backend/app/auth/routes.py:56-102 (register)
  - backend/app/auth/routes.py:158-196 (verify)
  - backend/app/auth/routes.py:126-130 (login check)
```

### OAuth Auto-Verification Rule
```yaml
rule_id: AUTH-005
name: OAuth Users Auto-Verified
applies_to: [github_callback]
reasoning: |
  GitHub verifies email ownership.
  We trust GitHub's verification process.
  No need for separate email verification.
implementation:
  - backend/app/auth/routes.py:373-380 (existing user)
  - backend/app/auth/routes.py:389 (new user)
  - Sets: is_verified=true, is_active=true
security_consideration:
  - Only trust verified primary emails from GitHub
  - Code: backend/app/auth/routes.py:353-356
```

---

## 2. Validation Formats (Error Handling)

### Pydantic Validation Error Format
```yaml
format_id: ERR-001
name: Pydantic 422 Validation Error
structure:
  status_code: 422
  body:
    detail:
      - type: string
        loc: [array, of, field, path]
        msg: string
        input: any
example:
  {
    "detail": [
      {
        "type": "string_too_short",
        "loc": ["body", "password"],
        "msg": "String should have at least 8 characters",
        "input": "pass"
      }
    ]
  }
frontend_handling:
  location: frontend/contexts/AuthContext.tsx:65-77
  logic: |
    if (Array.isArray(error.detail)) {
      const firstError = error.detail[0]
      const errorMsg = typeof firstError === 'object'
        ? (firstError.msg || JSON.stringify(firstError))
        : String(firstError)
      throw new Error(errorMsg)
    }
```

### FastAPI HTTPException Format
```yaml
format_id: ERR-002
name: FastAPI HTTP Exception
structure:
  status_code: 400 | 401 | 403 | 404 | 409 | 500
  body:
    detail: string
example:
  status: 401
  body: {"detail": "Invalid email or password"}
frontend_handling:
  location: frontend/contexts/AuthContext.tsx:70-76
  logic: |
    if (typeof error.detail === 'string') {
      throw new Error(error.detail)
    } else if (typeof error.detail === 'object') {
      throw new Error(JSON.stringify(error.detail))
    }
```

### Error Normalization Contract
```yaml
contract_id: ERR-NORM-001
name: All Errors Must Be String-Safe for React
requirement: |
  Frontend must NEVER pass objects directly to React children.
  All error.detail values must be converted to strings.
enforcement:
  - AuthContext.tsx handles all format types
  - verify-email page handles all format types
  - All error displays use {errorMsg} where errorMsg is string
test_case:
  input_error: {detail: [{type: "x", msg: "y"}]}
  rendered_output: "y" (string, not object)
```

---

## 3. OAuth Configuration Requirements

### GitHub OAuth App Setup
```yaml
config_id: OAUTH-GITHUB-001
name: GitHub OAuth Application Configuration
required_credentials:
  GITHUB_CLIENT_ID:
    type: string
    format: "Iv1.XXXXXXXXXXXX"
    obtain_from: https://github.com/settings/developers
    click: "New OAuth App"
  GITHUB_CLIENT_SECRET:
    type: string
    format: "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    obtain_from: "Same page as client ID"
    security: "Never commit to git; use .env"
required_urls:
  homepage_url: "http://localhost:3001"
  authorization_callback_url: "http://localhost:3001/auth/callback/github"
  note: "Frontend handles callback, not backend"
scopes:
  - "user:email"  # Read user's email addresses
backend_endpoints:
  authorize: GET /api/v1/auth/github/authorize
    description: Redirects to GitHub OAuth page
    implementation: backend/app/auth/routes.py:261-277
  callback: POST /api/v1/auth/github/callback
    description: Exchanges code for token, creates/logs in user
    implementation: backend/app/auth/routes.py:280-418
    parameters:
      code: string (from GitHub)
    returns: TokenResponse with JWT cookie
frontend_endpoints:
  callback_page: /auth/callback/github
    status: ❌ MISSING - must be created
    responsibility: Extract ?code from URL, send to backend
```

### Email Service Configuration
```yaml
config_id: EMAIL-RESEND-001
name: Resend Email Service Configuration
required_credential:
  RESEND_API_KEY:
    type: string
    format: "re_XXXXXXXXXXXXXXXXXXXX"
    obtain_from: https://resend.com/api-keys
    free_tier: "100 emails/day"
dev_mode:
  when: RESEND_API_KEY is placeholder or empty
  behavior: Print verification link to console
  implementation: backend/app/auth/email_service.py:12-19
  example_output: |
    ================================================================================
    [EMAIL] Verification email for: test@example.com
    [LINK]  http://localhost:3001/auth/verify-email?token=abc123...
    ================================================================================
prod_mode:
  when: RESEND_API_KEY is valid
  behavior: Send real email via Resend API
  implementation: backend/app/auth/email_service.py:24-68
  from_address: "FlowTask <onboarding@flowtask.dev>"
  subject: "✓ Verify your FlowTask account"
```

---

## 4. API Contract

### Authentication Endpoints
```yaml
endpoints:
  register:
    method: POST
    path: /api/v1/auth/register
    request_body:
      email: EmailStr (Pydantic validated)
      password: str (min_length=8, max_length=100)
      full_name: str | null
    response_success:
      status: 201
      body: UserResponse {id, email, full_name, is_verified, created_at}
    response_error:
      400: "Email already registered"
      422: Pydantic validation errors
    side_effects:
      - Creates user in database
      - Sends verification email
    does_not:
      - Log user in
      - Set JWT cookie
      - Verify email automatically

  login:
    method: POST
    path: /api/v1/auth/login
    request_body:
      email: EmailStr
      password: str
    response_success:
      status: 200
      body: TokenResponse {access_token, token_type, user}
      cookie_set: access_token (httpOnly, 7 days)
    response_error:
      401: "Invalid email or password"
      403: "Please verify your email address first"
    side_effects:
      - Sets JWT cookie
      - Does NOT create session in database (stateless JWT)

  verify_email:
    method: POST
    path: /api/v1/auth/verify-email
    request_body:
      token: str
    response_success:
      status: 200
      body: {message: "Email verified successfully", user: UserResponse}
    response_error:
      400: "Invalid verification token" | "Email already verified"
    side_effects:
      - Updates user: is_verified=true, is_active=true
      - Clears verification_token
      - Sends welcome email
    does_not:
      - Log user in
      - Set JWT cookie

  get_current_user:
    method: GET
    path: /api/v1/auth/me
    requires: JWT cookie
    response_success:
      status: 200
      body: UserResponse
    response_error:
      401: "Not authenticated"
    use_case: Check if user is logged in

  github_authorize:
    method: GET
    path: /api/v1/auth/github/authorize
    requires: GITHUB_CLIENT_ID configured
    response_success:
      status: 302 (redirect)
      location: https://github.com/login/oauth/authorize?client_id=...
    response_error:
      501: "GitHub OAuth is not configured"

  github_callback:
    method: POST
    path: /api/v1/auth/github/callback
    request_body:
      code: str (from GitHub)
    response_success:
      status: 200
      body: TokenResponse
      cookie_set: access_token
    response_error:
      400: "Failed to exchange code" | "No access token received"
      501: "GitHub OAuth is not configured"
    side_effects:
      - Exchanges code for GitHub access token
      - Fetches user email from GitHub
      - Creates user if not exists (auto-verified)
      - Logs in user if exists
      - Sets JWT cookie
```

---

## 5. Security Considerations

### Attack Surface Analysis
```yaml
threats:
  xss:
    mitigation: httpOnly cookies prevent JS access to tokens
    status: ✅ Mitigated

  csrf:
    risk: POST endpoints without CSRF protection
    mitigation: samesite=lax cookie + CORS configuration
    status: ⚠️ Acceptable for localhost; add CSRF in production

  password_brute_force:
    risk: No rate limiting on /login endpoint
    mitigation_needed: Add rate limiting middleware
    status: 🔴 TODO for production

  email_enumeration:
    risk: "Email already registered" reveals user existence
    mitigation: Accept as reasonable for user experience
    alternative: Generic "Check your email" message
    status: ⚠️ Accepted risk

  token_expiry:
    current: JWT expires in 7 days
    risk: Long-lived tokens if stolen
    mitigation_needed: Add refresh token rotation
    status: ⚠️ Acceptable for MVP; improve for production
```

---

## 6. Frontend-Backend Coupling Points

### API Base URL
```yaml
coupling_point: API_BASE_URL
current_value: "http://localhost:8000"
hardcoded_in:
  - frontend/contexts/AuthContext.tsx (lines 36, 55, 86)
  - All auth pages make direct fetch() calls
recommended:
  - Extract to environment variable: NEXT_PUBLIC_API_URL
  - Create API client wrapper: lib/api.ts
  - Centralize all API calls
```

### Cookie Domain
```yaml
coupling_point: COOKIE_DOMAIN
current_backend: "localhost" (implicit, no domain set)
current_frontend: "localhost" (browser default)
works_because: Both on localhost
production_issue: Must set domain for cross-subdomain cookies
solution: Set cookie domain in backend based on FRONTEND_URL
```

### CORS Configuration
```yaml
coupling_point: CORS_ORIGINS
backend_env: CORS_ORIGINS=http://localhost:3001
backend_code: app.main.py
must_match: Frontend URL exactly
test_verification: Browser console should not show CORS errors
```

---

## 7. Data Flow Diagrams

### Successful Login Flow
```
┌─────────┐                ┌──────────┐                 ┌─────────┐
│ Browser │                │ Frontend │                 │ Backend │
└────┬────┘                └────┬─────┘                 └────┬────┘
     │                          │                            │
     │  1. Submit form          │                            │
     │─────────────────────────>│                            │
     │                          │                            │
     │                          │  2. POST /api/v1/auth/login│
     │                          │   {email, password}        │
     │                          │───────────────────────────>│
     │                          │                            │
     │                          │                   3. Normalize email
     │                          │                      Query database
     │                          │                      Verify password
     │                          │                      Create JWT
     │                          │                            │
     │                          │ 4. 200 OK + Set-Cookie     │
     │                          │<───────────────────────────│
     │                          │   {access_token, user}     │
     │                          │                            │
     │  5. Redirect /dashboard  │                            │
     │<─────────────────────────│                            │
     │                          │                            │
```

### Failed Login Flow (Unverified)
```
┌─────────┐                ┌──────────┐                 ┌─────────┐
│ Browser │                │ Frontend │                 │ Backend │
└────┬────┘                └────┬─────┘                 └────┬────┘
     │                          │                            │
     │  1. Submit form          │                            │
     │─────────────────────────>│                            │
     │                          │                            │
     │                          │  2. POST /api/v1/auth/login│
     │                          │───────────────────────────>│
     │                          │                            │
     │                          │              3. Find user  │
     │                          │                 Check: is_verified=false
     │                          │                            │
     │                          │ 4. 403 Forbidden           │
     │                          │<───────────────────────────│
     │                          │   "Please verify email"    │
     │                          │                            │
     │  5. Show error message   │                            │
     │<─────────────────────────│                            │
```

---

## 8. Testing Checklist for RAG

### Manual Test Cases
```yaml
test_cases:
  happy_path_email_auth:
    steps:
      1: "Visit http://localhost:3001/auth/signup"
      2: "Enter email: test@example.com, password: SecurePass123!, name: Test User"
      3: "Submit form"
      4: "Check backend console for verification link"
      5: "Copy verification link and open in browser"
      6: "Verify success message shown"
      7: "Visit http://localhost:3001/auth/signin"
      8: "Enter same credentials"
      9: "Verify redirect to /dashboard"
    expected_result: "User logged in, dashboard visible"

  case_insensitive_login:
    steps:
      1: "Sign up with: Test@Example.COM"
      2: "Verify email"
      3: "Sign in with: test@example.com (all lowercase)"
    expected_result: "Login successful"

  unverified_login_blocked:
    steps:
      1: "Sign up"
      2: "Do NOT click verification link"
      3: "Attempt to sign in"
    expected_result: "403 error: Please verify your email address first"

  already_registered:
    steps:
      1: "Sign up with email: duplicate@test.com"
      2: "Attempt to sign up again with same email"
    expected_result: "400 error: Email already registered"

  invalid_credentials:
    steps:
      1: "Sign in with wrong password"
    expected_result: "401 error: Invalid email or password"
```

---

## 9. Common Debugging Scenarios

### User Can't Log In
```yaml
scenario: "User reports 'invalid email or password'"
debug_steps:
  1:
    check: "Is email verified?"
    query: "SELECT email, is_verified FROM user WHERE email = '...'"
    if_false: "Error should be 403 'verify email', not 401"
  2:
    check: "Email case mismatch?"
    query: "SELECT email FROM user WHERE LOWER(email) = LOWER('...')"
    if_true: "Backend normalizes - should work"
  3:
    check: "Password correct?"
    test: "Try password reset flow"
  4:
    check: "Network/CORS error?"
    location: "Browser console F12"
    look_for: "CORS policy blocked" or "Failed to fetch"
```

### Verification Email Not Received
```yaml
scenario: "User didn't get verification email"
debug_steps:
  1:
    check: "Development mode?"
    verify: "Check backend console for printed link"
  2:
    check: "RESEND_API_KEY configured?"
    command: "grep RESEND_API_KEY backend/.env"
    if_placeholder: "Emails only print to console"
  3:
    check: "Email sent successfully?"
    location: "Backend logs: [EMAIL] Verification email sent"
  4:
    check: "Spam folder?"
    advice: "Check user's spam/junk folder"
```

---

## 10. Phase 3 RAG Integration Points

### Questions RAG Chatbot Should Answer
```yaml
category: authentication
questions:
  - "How do I set up GitHub OAuth?"
  - "Why isn't my verification email arriving?"
  - "What's the difference between signup and signin?"
  - "How do I reset a user's password?"
  - "Why does login return 403?"
  - "How are passwords stored?"
  - "What's the JWT expiration time?"
  - "How do I test auth without email?"

knowledge_sources:
  - PHASE_A_AUTH_DIAGNOSIS.md (failure points)
  - PHASE_B_CONTEXT7_AUTH_INTELLIGENCE.md (this file)
  - backend/app/auth/routes.py (implementation)
  - AUTHENTICATION_QUICK_START.md (user guide)

retrieval_strategy:
  - Embed all auth docs in vector database
  - Use semantic search for user questions
  - Return relevant sections from this file
  - Include code snippets with line numbers
```

### Metadata for Context7 MCP
```yaml
context7_metadata:
  project: physical-ai-todo
  component: authentication
  tech_stack:
    backend: FastAPI 0.100+
    frontend: Next.js 14
    database: PostgreSQL (Neon)
    email: Resend API
    oauth: GitHub OAuth 2.0
  key_files:
    - path: backend/app/auth/routes.py
      purpose: All auth endpoints
      critical_functions: [register, login, verify_email, github_callback]
    - path: frontend/contexts/AuthContext.tsx
      purpose: Frontend auth state management
      exports: [useAuth, AuthProvider]
    - path: backend/app/auth/email_service.py
      purpose: Email sending (dev + prod modes)
  last_updated: "2025-12-13"
  documentation_quality: "Production-ready"
```

---

**End of Phase B: Context7 MCP Auth Intelligence**

This document serves as the "single source of truth" for authentication logic,
consumable by LLMs, RAG systems, and human developers.
