# 🔐 Authentication Quick Start Guide

**For Judges & Reviewers** - Get authentication working in 2 minutes!

---

## ✅ What's Working RIGHT NOW (No Setup)

### Email/Password Authentication ✅
- **Status**: Fully functional
- **Setup needed**: None!
- **How it works**: Dev mode (verification links in console)

### GitHub OAuth ⚙️
- **Status**: Requires setup
- **Setup time**: 5 minutes
- **Alternative**: Use email/password (works great!)

---

## 🚀 Quick Test (2 minutes)

### 1. Start Servers

**Terminal 1 - Backend**:
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev -- -p 3001
```

### 2. Sign Up

1. Go to: http://localhost:3001/auth/signup
2. Fill in:
   ```
   Email: judge@example.com
   Password: JudgeTest123!
   Full Name: Judge
   ```
3. Click "Create Account"

### 3. Get Verification Link

**IMPORTANT**: Check the **backend terminal** (Terminal 1) for output like:

```
================================================================================
[EMAIL] Verification email for: judge@example.com
[LINK]  http://localhost:3001/auth/verify-email?token=ABC123...
================================================================================
```

**Copy the entire link** and open it in your browser.

### 4. Verify & Login

1. Click the verification link
2. You'll see "Email Verified!"
3. Go to: http://localhost:3001/auth/signin
4. Login with same email & password
5. Done! You're in the dashboard!

---

## 📧 Why Emails Don't Arrive

**Current Mode**: Development (Console Links)

**Why**: The `.env` file has a placeholder Resend API key:
```env
RESEND_API_KEY=re_123456789_placeholder
```

**This is intentional!** It means:
- ✅ No email setup required
- ✅ Works immediately
- ✅ Perfect for testing/demo
- ✅ Verification links print to console

### To Get Real Emails (Optional):

1. Sign up at: https://resend.com (free tier)
2. Get API key
3. Update `backend/.env`:
   ```env
   RESEND_API_KEY=re_your_actual_key
   ```
4. Restart backend
5. Now emails go to real inbox!

---

## 🔐 GitHub OAuth Setup (Optional)

GitHub button shows "Setup Required" because it needs real credentials.

### Quick Setup (5 minutes):

1. **Create OAuth App**:
   - Go to: https://github.com/settings/developers
   - Click "New OAuth App"

2. **Configure**:
   ```
   Application name: FlowTask Dev
   Homepage URL: http://localhost:3001
   Callback URL: http://localhost:3001/auth/callback/github
   ```

3. **Get Credentials**:
   - Copy Client ID (like: `Iv1.abc123...`)
   - Generate Client Secret
   - **Save it immediately** (can't see again!)

4. **Update `.env`**:
   ```env
   GITHUB_CLIENT_ID=Iv1.your_actual_id
   GITHUB_CLIENT_SECRET=your_actual_secret
   ```

5. **Restart Backend**:
   ```bash
   # Ctrl+C to stop
   uvicorn app.main:app --reload
   ```

6. **Test**:
   - Go to signin page
   - GitHub button now works!
   - Click and authorize

---

## 🐛 Common Issues & Fixes

### Issue: "Failed to fetch"

**Causes**:
- Wrong URL (use port 3001, not 3000)
- Backend not running
- Browser cache

**Fix**:
1. Check backend running: http://localhost:8000/health
2. Use correct URL: http://localhost:3001
3. Clear cache: Ctrl+Shift+Delete
4. Try incognito mode

### Issue: React Error "Objects are not valid as React child"

**Status**: ✅ **FIXED** in latest commit

**If still seeing it**:
1. Hard refresh: Ctrl+Shift+F5
2. Clear cache completely
3. Restart frontend server

### Issue: "Invalid email" on login

**Causes**:
- Email not verified
- Typo in email
- User doesn't exist

**Fix**:
1. Make sure you verified email first
2. Check spelling (emails are case-insensitive)
3. Try the test account from Quick Test above

### Issue: "Already signed in"

**Fix**:
1. Open http://localhost:3001/auth/signin
2. If you see a logout button, click it
3. OR clear browser cookies
4. OR use incognito mode

---

## ✨ Features That Work

### Email/Password ✅
- Registration with email
- Email verification (console mode)
- Secure login
- Case-insensitive email
- Password hashing (bcrypt)
- JWT tokens (HTTP-only cookies)
- Session persistence
- Logout

### Case-Insensitive Login ✅
Register with: `Test@Example.COM`
Login with any of these:
- `test@example.com` ✅
- `TEST@EXAMPLE.COM` ✅
- `TeSt@ExAmPlE.cOm` ✅
All work!

### Security ✅
- Passwords hashed with bcrypt
- JWT tokens in HTTP-only cookies
- CORS protection
- SQL injection protection
- XSS protection

---

## 📝 Test Accounts

You can create unlimited test accounts!

**Suggested test accounts**:
```
Email: demo@flowtask.com
Password: DemoPassword123!

Email: judge@hackathon.com
Password: JudgeTest123!

Email: test@example.com
Password: TestPassword123!
```

**All passwords must**:
- Be at least 8 characters
- Can include letters, numbers, symbols

---

## 🎯 For Judges - What to Test

### 1. Email Registration Flow (2 min)
✅ Sign up with email
✅ Get verification link from console
✅ Verify email
✅ Login successfully

### 2. Case-Insensitive Login (30 sec)
✅ Register with mixed case email
✅ Login with lowercase version
✅ Works perfectly!

### 3. Session Persistence (30 sec)
✅ Login
✅ Close browser
✅ Reopen - still logged in!

### 4. Task Management (2 min)
✅ Create tasks
✅ Toggle completion
✅ Delete tasks
✅ Filter & search

### 5. UI Features (1 min)
✅ Dark mode toggle
✅ Language switcher (6 languages!)
✅ Responsive design

**Total test time**: ~6 minutes

---

## 🔗 Important URLs

- **Frontend**: http://localhost:3001
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Pages:
- **Landing**: http://localhost:3001/landing
- **Sign Up**: http://localhost:3001/auth/signup
- **Sign In**: http://localhost:3001/auth/signin
- **Dashboard**: http://localhost:3001/dashboard

---

## 💡 Pro Tips

1. **Always check backend console** for verification links
2. **Use port 3001**, not 3000 for frontend
3. **Clear cache** if you see weird errors
4. **Check health endpoint** if backend seems down: http://localhost:8000/health
5. **Use incognito mode** for clean testing

---

## ✅ What's Fixed (Latest Commits)

1. ✅ React rendering error ("Objects are not valid as React child")
2. ✅ Verify-email endpoint accepts JSON properly
3. ✅ Resend-verification endpoint works correctly
4. ✅ All error messages display as strings
5. ✅ Email normalization (case-insensitive)
6. ✅ Frontend URL corrected to port 3001
7. ✅ CORS configured properly

---

## 📚 More Documentation

- **Full README**: [README.md](./README.md)
- **Test Report**: [PHASE_2_TEST_REPORT.md](./PHASE_2_TEST_REPORT.md)
- **Compliance**: [PHASE_2_COMPLIANCE_REPORT.md](./PHASE_2_COMPLIANCE_REPORT.md)
- **Auth Setup**: [AUTHENTICATION_SETUP.md](./AUTHENTICATION_SETUP.md)

---

**Need help?** All authentication features work in dev mode with zero setup! Just follow the Quick Test above. 🚀
