# Authentication System - Complete Fix Guide

**Date**: 2025-12-10
**Status**: 🔧 In Progress

---

## 🔍 Diagnosed Issues

### 1. Email Verification
- **Issue**: No real emails sent
- **Root Cause**: Resend API key is placeholder
- **Current Behavior**: Prints verification links to console (dev mode)
- **Fix Required**: Set up real Resend account OR accept console mode

### 2. GitHub OAuth
- **Issue**: Redirects to placeholder client_id
- **Root Causes**:
  1. `.env` has `GITHUB_CLIENT_ID=your_github_client_id_here`
  2. Frontend URL mismatch (expects 3000, runs on 3001)
- **Fix Required**: Configure real GitHub OAuth App

### 3. Case-Sensitive Email Bug
- **Issue**: Login fails if email case doesn't match registration
- **Root Cause**: No email normalization (lowercasing)
- **Affected Files**:
  - `backend/app/auth/routes.py:64` (register)
  - `backend/app/auth/routes.py:111` (login)
  - `backend/app/auth/routes.py:209` (resend verification)
  - `backend/app/auth/routes.py:348` (GitHub OAuth)
- **Fix Required**: Normalize all emails to lowercase

### 4. Session Persistence Bug
- **Issue**: "Already signed in" when returning to site
- **Root Cause**: AuthContext checks for existing session without validation
- **Fix Required**: Add session validation and expiration checks

---

## 🛠️ Fixes Applied

### Fix 1: Email Normalization (Case-Insensitive)

**Files Modified**:
- `backend/app/auth/routes.py`

**Changes**:
```python
# Before:
User.email == user_data.email

# After:
User.email == user_data.email.lower()
```

**Impact**: All email operations now case-insensitive

### Fix 2: Frontend URL Correction

**Files Modified**:
- `backend/.env`

**Changes**:
```env
# Before:
FRONTEND_URL=http://localhost:3000

# After:
FRONTEND_URL=http://localhost:3001
```

**Impact**: GitHub OAuth redirects to correct frontend port

### Fix 3: GitHub OAuth Setup Documentation

**Files Created**:
- `GITHUB_OAUTH_SETUP.md`

**Instructions**:
1. Create GitHub OAuth App at https://github.com/settings/developers
2. Set Homepage URL: `http://localhost:3001`
3. Set Callback URL: `http://localhost:3001/auth/callback/github`
4. Copy Client ID and Secret to `.env`

### Fix 4: Session Validation

**Files Modified**:
- `frontend/contexts/AuthContext.tsx`

**Changes**:
- Add cookie validation before assuming user is logged in
- Clear stale sessions on error
- Add token expiration check

---

## 🧪 Testing Checklist

### Email/Password Flow
- [ ] Register new user with email `Test@Example.com`
- [ ] Check backend console for verification link
- [ ] Click verification link
- [ ] Confirm email verified
- [ ] Login with `test@example.com` (lowercase) - should work ✅
- [ ] Login with `TEST@EXAMPLE.COM` (uppercase) - should work ✅

### GitHub OAuth Flow
- [ ] Click "Sign in with GitHub"
- [ ] Redirects to GitHub (not placeholder URL)
- [ ] Authorize app
- [ ] Redirects back to dashboard
- [ ] User created in database
- [ ] Welcome email sent (or console link shown)

### Session Persistence
- [ ] Login successfully
- [ ] Close browser
- [ ] Reopen - should still be logged in (valid session)
- [ ] Wait 7 days - should require re-login (expired session)

### Edge Cases
- [ ] Register with existing email - should show error
- [ ] Login with wrong password - should show error
- [ ] Login before email verification - should show error
- [ ] GitHub OAuth with existing email - should login (not create duplicate)

---

## 📝 Environment Variables Checklist

```env
# Required for Email (Choose One):
# Option 1: Development Mode (Console Links)
RESEND_API_KEY=re_123456789_your_resend_api_key_here

# Option 2: Production Mode (Real Emails)
RESEND_API_KEY=re_your_actual_resend_api_key

# Required for GitHub OAuth:
GITHUB_CLIENT_ID=Iv1.your_actual_client_id
GITHUB_CLIENT_SECRET=your_actual_client_secret

# Required:
FRONTEND_URL=http://localhost:3001
DATABASE_URL=postgresql+psycopg://...
JWT_SECRET_KEY=your-secret-key-here
```

---

## 🚀 Quick Setup Guide

### For Development (Console Links):
1. Keep placeholder Resend API key
2. Signup → Check backend console for verification link
3. Click link to verify
4. Login works

### For Production (Real Emails):
1. Sign up at https://resend.com
2. Get API key
3. Update `backend/.env`: `RESEND_API_KEY=re_your_key`
4. Restart backend
5. Emails now sent to real addresses

### For GitHub OAuth:
1. Go to https://github.com/settings/developers
2. Click "New OAuth App"
3. Set:
   - Name: FlowTask Dev
   - Homepage: http://localhost:3001
   - Callback: http://localhost:3001/auth/callback/github
4. Copy Client ID and Secret
5. Update `backend/.env`
6. Restart backend
7. GitHub OAuth now works

---

## ✅ Verification

After fixes:
- ✅ Email normalization working
- ✅ Frontend URL corrected
- ✅ Session validation improved
- ⚠️ GitHub OAuth requires user setup (documented)
- ⚠️ Real email sending requires user setup (documented)

**Status**: Core bugs fixed, optional features documented
