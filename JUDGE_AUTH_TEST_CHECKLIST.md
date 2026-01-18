# Judge Authentication Test Checklist

**Last Updated:** 2025-12-13
**Status:** ✅ All Auth Issues Fixed
**Test Time:** 2-5 minutes

---

## ✅ Quick Test (2 minutes) - Email Authentication

**Prerequisites:**
- Both servers running (backend port 8000, frontend port 3001)

**Steps:**
1. [ ] Visit http://localhost:3001
2. [ ] Click "Get Started"
3. [ ] Fill signup form:
   - Email: test@example.com
   - Password: SecurePass123!
   - Full Name: Test User
4. [ ] Submit form
5. [ ] See loading state: "Creating account..."
6. [ ] Check **backend console** for verification link (looks like):
   ```
   ========================================================================
   [EMAIL] Verification email for: test@example.com
   [LINK]  http://localhost:3001/auth/verify-email?token=abc123...
   ========================================================================
   ```
7. [ ] Copy verification link and open in browser
8. [ ] See "Verifying your email..." loading state
9. [ ] See "Email verified successfully!"
10. [ ] Redirected to signin page after 2 seconds
11. [ ] Enter same credentials and sign in
12. [ ] See loading: "Signing in..."
13. [ ] Redirected to dashboard
14. [ ] See your tasks

**Expected Result:** ✅ All steps work without errors

**Why Email Doesn't Arrive:**
- App is in **development mode**
- No Resend API key configured (intentional)
- Verification links print to console instead
- This is NORMAL and works perfectly for testing!

---

## ✅ Auth State Checks (30 seconds)

**Test "Already Signed In" Logic:**

1. [ ] While logged in, visit http://localhost:3001/auth/signup
2. [ ] See message: "You're Already Signed In"
3. [ ] See your email displayed
4. [ ] See two buttons:
   - "Go to Dashboard"
   - "Sign out and create new account"
5. [ ] Click "Go to Dashboard" → Redirected successfully
6. [ ] Go back to signup → Click "Sign out" → See signup form

**Test Signin Auto-Redirect:**

1. [ ] While logged in, visit http://localhost:3001/auth/signin
2. [ ] Automatically redirected to dashboard (no signin form shown)

**Expected Result:** ✅ No confusion, clear messaging

---

## ✅ Edge Cases Test (1 minute)

**Test Error Handling:**

1. [ ] Sign up with email that already exists
   - **Expected:** Error: "Email already registered"

2. [ ] Sign in with wrong password
   - **Expected:** Error: "Invalid email or password"

3. [ ] Sign in before verifying email
   - **Expected:** Error: "Please verify your email address first"

4. [ ] Try to submit signup form twice quickly
   - **Expected:** Button disables, only one request sent

5. [ ] Toggle theme (light/dark) throughout testing
   - **Expected:** Works smoothly, persists across pages

---

## ✅ GitHub OAuth Test (5 minutes) - OPTIONAL

**Only test this if you want to see OAuth in action**

### Setup (One-Time, 5 minutes):

1. [ ] Visit https://github.com/settings/developers
2. [ ] Click "New OAuth App"
3. [ ] Fill in:
   - **Application name:** FlowTask Local Dev
   - **Homepage URL:** http://localhost:3001
   - **Authorization callback URL:** http://localhost:3001/auth/callback/github
4. [ ] Click "Register application"
5. [ ] Copy **Client ID**
6. [ ] Click "Generate a new client secret"
7. [ ] Copy **Client Secret**
8. [ ] Open `backend/.env`
9. [ ] Update:
   ```env
   GITHUB_CLIENT_ID=your_actual_client_id_here
   GITHUB_CLIENT_SECRET=your_actual_client_secret_here
   ```
10. [ ] **Restart backend server:**
    ```bash
    # Stop backend (Ctrl+C)
    cd backend
    python -m uvicorn app.main:app --reload
    ```

### Test OAuth Flow:

1. [ ] Visit http://localhost:3001/auth/signin
2. [ ] GitHub button should now be clickable (not disabled)
3. [ ] Click "Continue with GitHub"
4. [ ] Redirected to GitHub authorization page
5. [ ] Click "Authorize [your-app-name]"
6. [ ] Redirected back to http://localhost:3001/auth/callback/github?code=...
7. [ ] See loading: "Completing Sign-In"
8. [ ] See loading spinner
9. [ ] See success: "Signed in successfully!"
10. [ ] Redirected to dashboard after 1 second
11. [ ] You are logged in (check navbar)
12. [ ] Your GitHub email is used (no verification needed!)

**Expected Result:** ✅ OAuth works end-to-end

**If OAuth button is still disabled:**
- Check `GITHUB_CLIENT_ID` is set in `.env`
- Restart backend server
- Check backend logs for errors

---

## ❌ Troubleshooting

| Issue | Solution |
|-------|----------|
| "Site can't be reached" | Check both servers running (ports 8000, 3001) |
| "CORS error" in console | Verify `FRONTEND_URL=http://localhost:3001` in backend/.env |
| No verification link in console | Check backend terminal output (not frontend) |
| Verification link 404 | Link must be opened in browser, not clicked in terminal |
| GitHub OAuth 404 | Callback page created: `frontend/app/auth/callback/github/page.tsx` |
| GitHub OAuth "Setup Required" | Follow GitHub OAuth Test setup steps above |
| Button stays loading forever | Check browser console (F12) for errors, check backend logs |
| Theme doesn't change | Hard refresh: Ctrl+Shift+R |
| "Email already registered" | Delete user from database or use different email |

---

## ✅ What We Fixed

1. **GitHub OAuth Callback 404**
   - ❌ Before: Clicking GitHub button → 404 error
   - ✅ After: Complete OAuth flow works end-to-end

2. **"Already Signed In" Not Handled**
   - ❌ Before: Could sign up while logged in (confusing)
   - ✅ After: Clear message + buttons (dashboard or logout)

3. **Theme System Duplication**
   - ❌ Before: Dead `ThemeContext.tsx` file confusing codebase
   - ✅ After: Removed, clean single theme system

4. **Loading States**
   - ✅ Verified: All auth forms show loading during submission
   - ✅ Verified: Buttons disable to prevent double submission

---

## 📊 Test Results Summary

After running all tests above, you should see:

- ✅ **Email Auth:** Works perfectly (dev mode = console links)
- ✅ **Auth State:** Proper handling of logged-in users
- ✅ **Error Handling:** Clear, user-friendly error messages
- ✅ **Loading States:** Visual feedback during all operations
- ✅ **Theme Toggle:** Works smoothly
- ✅ **GitHub OAuth:** Works if configured (optional)

---

## 📝 Notes for Judges

1. **Email Service in Dev Mode:**
   - Verification links print to **backend console**
   - This is intentional for easy testing
   - No email service API key needed
   - Production mode sends real emails via Resend API

2. **GitHub OAuth is Optional:**
   - Email/password auth is fully functional without it
   - OAuth requires 5-minute GitHub App setup
   - Skip if you want to test quickly

3. **All Servers Must Be Running:**
   - Backend: `cd backend && python -m uvicorn app.main:app --reload`
   - Frontend: `cd frontend && npm run dev`
   - Check ports: 8000 (backend), 3001 (frontend)

4. **Phase 2 Completion:**
   - All critical auth bugs fixed
   - All 30 features documented in README working
   - Ready for final submission

---

**Test completed on:** __________
**All tests passed:** [ ] Yes [ ] No
**Notes:** ___________________________________________

---

**For detailed technical documentation, see:**
- `PHASE_A_AUTH_DIAGNOSIS.md` - Complete diagnosis of auth issues
- `PHASE_B_CONTEXT7_AUTH_INTELLIGENCE.md` - Reusable auth knowledge base
- `AUTHENTICATION_QUICK_START.md` - Original quick start guide
- `specs/phase-2-auth/` - Full spec-driven development artifacts
