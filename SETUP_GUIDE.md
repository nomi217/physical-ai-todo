# FlowTask Setup Guide

**Date**: 2025-12-10
**Status**: ✅ Email Verification Working | ⚠️ GitHub OAuth Needs Setup

This guide explains how to set up email verification and GitHub OAuth for FlowTask.

---

## 📧 Email Verification Setup

### Current State: ✅ WORKING (Development Mode)

**When users sign up**, the verification link now appears in the backend console:

```
================================================================================
[EMAIL] Verification email for: user@example.com
[LINK]  http://localhost:3001/auth/verify-email?token={verification_token}
================================================================================
```

### How to Verify Email (Current Setup)

1. **User signs up** at http://localhost:3001/auth/signup
2. **Check backend console** - verification link appears with formatting above
3. **Copy the link** from `[LINK]` line
4. **Paste into browser** to verify email
5. **User is verified** and can now sign in

**This works perfectly for development and testing!**

---

### Optional: Send Real Emails with Resend

If you want to send actual emails to users (instead of using console links):

#### Step 1: Sign Up for Resend

1. Go to https://resend.com/signup
2. Create a free account
3. Verify your email address

#### Step 2: Get API Key

1. Go to https://resend.com/api-keys
2. Click "Create API Key"
3. Give it a name (e.g., "FlowTask Development")
4. Select permissions: "Sending access"
5. Copy the API key (starts with `re_`)

#### Step 3: Update Backend Configuration

1. Open `backend/.env`
2. Find the line: `RESEND_API_KEY=re_123456789_your_resend_api_key_here`
3. Replace with your actual API key:
   ```env
   RESEND_API_KEY=re_your_actual_api_key_from_resend
   ```
4. Save the file

#### Step 4: Verify Domain (Required for Production)

For production use, you need to verify your domain:

1. Go to https://resend.com/domains
2. Click "Add Domain"
3. Enter your domain (e.g., `flowtask.dev`)
4. Follow DNS configuration instructions
5. Wait for verification (usually takes a few minutes)

#### Step 5: Update Email Sender Address

After domain verification, update the sender in `backend/app/auth/email_service.py`:

```python
# Change from:
"from": "FlowTask <onboarding@flowtask.dev>"

# To your verified domain:
"from": "FlowTask <onboarding@yourdomain.com>"
```

#### Step 6: Restart Backend

```bash
# Backend will auto-reload, but to be sure:
cd backend
python -m uvicorn app.main:app --reload
```

Now real emails will be sent to users!

---

## 🔐 GitHub OAuth Setup

### Current Issue: ⚠️ Placeholder Values

When clicking "Continue with GitHub", you see:
```
https://github.com/login/oauth/authorize?client_id=your_github_client_id_here&redirect_uri=...
```

The `your_github_client_id_here` is a placeholder that needs to be replaced.

### How to Fix GitHub OAuth

#### Step 1: Create GitHub OAuth App

1. Go to https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in the form:
   - **Application name**: FlowTask (or your app name)
   - **Homepage URL**: `http://localhost:3001`
   - **Authorization callback URL**: `http://localhost:3001/auth/callback/github`
4. Click "Register application"

#### Step 2: Get Client ID and Secret

1. After creating the app, you'll see:
   - **Client ID**: Copy this (looks like `Iv1.abc123def456...`)
   - Click "Generate a new client secret"
   - **Client Secret**: Copy this immediately (you won't see it again!)

#### Step 3: Update Backend Configuration

1. Open `backend/.env`
2. Find these lines:
   ```env
   GITHUB_CLIENT_ID=your_github_client_id_here
   GITHUB_CLIENT_SECRET=your_github_client_secret_here
   ```
3. Replace with your actual values:
   ```env
   GITHUB_CLIENT_ID=Iv1.your_actual_client_id
   GITHUB_CLIENT_SECRET=your_actual_client_secret
   ```
4. Save the file

#### Step 4: Restart Backend

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Now GitHub OAuth will work! The button will redirect to the proper GitHub authorization page.

---

## 🧪 Testing the Setup

### Test Email Verification (Working Now!)

1. **Sign up** at http://localhost:3001/auth/signup
2. **Check backend console** for verification link like this:
   ```
   ================================================================================
   [EMAIL] Verification email for: yourname@example.com
   [LINK]  http://localhost:3001/auth/verify-email?token=abc123...
   ================================================================================
   ```
3. **Copy and paste link** into browser
4. **Email verified!** You can now sign in

### Test GitHub OAuth (After Configuration)

1. **Click "Continue with GitHub"** at http://localhost:3001/auth/signin
2. **Should redirect** to GitHub authorization page (not showing placeholder)
3. **Authorize the app**
4. **Should redirect back** to FlowTask and sign you in

---

## ✅ Current Status

| Feature | Status | Notes |
|---------|--------|-------|
| Email Verification | ✅ Working | Console links appear clearly formatted |
| Email Sending (Resend) | ⚠️ Optional | Currently using console links (placeholder API key) |
| GitHub OAuth | ⚠️ Needs Config | Requires real GitHub Client ID/Secret (see steps above) |
| Sign In / Sign Up | ✅ Working | Email/password authentication fully functional |
| Multi-Language | ✅ Working | 6 languages with RTL support |
| Dark Mode | ✅ Working | Theme toggle functional |
| Dashboard | ✅ Working | All features functional |
| Task Management | ✅ Working | Create, edit, delete, complete tasks |

---

## 📝 Summary

**For Development (Current Setup):**
- ✅ Email verification works via console links - **working now!**
- ⚠️ GitHub OAuth needs configuration (follow steps above)

**For Production:**
- Set up real Resend API key for email sending
- Configure GitHub OAuth for production domain
- Update callback URLs to production URLs

---

## 🚀 Quick Start (Development)

**You can use FlowTask right now!**

1. **Backend**: http://127.0.0.1:8000 ✅ Running
2. **Frontend**: http://localhost:3001 ✅ Running
3. **Sign Up**: Works with email/password
4. **Verify Email**: Use link from backend console (formatted clearly!)
5. **GitHub OAuth**: Configure using steps above if needed

### Example: Sign Up Flow

1. Go to http://localhost:3001/auth/signup
2. Enter name, email (e.g., `test@example.com`), password
3. Click "Sign Up"
4. **Check backend console** for:
   ```
   ================================================================================
   [EMAIL] Verification email for: test@example.com
   [LINK]  http://localhost:3001/auth/verify-email?token=2FNFt9TitvPez7KkoEnKG89sKl61YPP2eTotOijo-_U
   ================================================================================
   ```
5. **Copy the verification link** and paste in browser
6. **Email verified!** Sign in and start using FlowTask

---

## 📞 Need Help?

- **Email Verification**: ✅ Working - Check backend console for formatted links
- **GitHub OAuth**: ⚠️ Follow "GitHub OAuth Setup" section above to fix placeholder issue
- **Other Issues**: Check `AUTHENTICATION_DIAGNOSTICS.md` and `MULTI_LANGUAGE_IMPLEMENTATION.md`

**Email verification is working perfectly!** Just configure GitHub OAuth if you need it.

---

## 🎯 Next Steps

1. **Optional**: Configure GitHub OAuth (follow steps above)
2. **Optional**: Set up real email sending with Resend API key
3. **Start using FlowTask** - everything else is ready!
