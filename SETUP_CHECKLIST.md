# 🎯 Azure AD Authentication - Setup Checklist

Use this checklist to ensure everything is configured correctly.

---

## ✅ Pre-Implementation Checklist

- [x] MSAL React libraries installed
- [x] Backend JWT validation libraries installed
- [x] Login component created
- [x] AuthGuard component created
- [x] API service with auto token attachment created
- [x] Backend middleware created
- [x] Environment file templates created
- [x] Documentation created
- [x] Automated setup script created
- [x] Existing UI preserved (no breaking changes)

**Status: ✅ ALL IMPLEMENTATION COMPLETE**

---

## 📋 Your Setup Checklist

### Part 1: Azure Portal Configuration

- [ ] Logged into [Azure Portal](https://portal.azure.com)
- [ ] Navigated to **Azure Active Directory** → **App registrations**
- [ ] Found your app registration (or created new one)
- [ ] Copied **Client ID** (Application ID)
- [ ] Copied **Tenant ID** (Directory ID)
- [ ] Created **Client Secret** (Certificates & secrets)
- [ ] Added redirect URI: `http://localhost:3000`
- [ ] Added API permission: `User.Read`
- [ ] Granted admin consent for permissions
- [ ] Verified app type: **Single-tenant**

### Part 2: Frontend Configuration

- [ ] Opened `frontend/.env` file
- [ ] Replaced `REACT_APP_AZURE_CLIENT_ID` with your Client ID
- [ ] Replaced `REACT_APP_AZURE_TENANT_ID` with your Tenant ID
- [ ] Verified `REACT_APP_AZURE_REDIRECT_URI=http://localhost:3000`
- [ ] Saved the file

### Part 3: Backend Configuration

- [ ] Opened `Backend/.env` file
- [ ] Replaced `AZURE_CLIENT_ID` with your Client ID
- [ ] Replaced `AZURE_TENANT_ID` with your Tenant ID
- [ ] Replaced `AZURE_CLIENT_SECRET` with your Client Secret
- [ ] Saved the file

### Part 4: Server Restart

- [ ] Stopped frontend server (Ctrl+C)
- [ ] Stopped backend server (Ctrl+C)
- [ ] Restarted backend: `cd Backend && python app.py`
- [ ] Restarted frontend: `cd frontend && npm start`
- [ ] Verified backend started on port 5000
- [ ] Verified frontend started on port 3000

### Part 5: Testing

- [ ] Opened `http://localhost:3000` in browser
- [ ] Saw login page (not dashboard)
- [ ] Clicked "Sign in with Microsoft" button
- [ ] Microsoft login popup appeared
- [ ] Entered organization credentials
- [ ] Successfully authenticated
- [ ] Redirected to dashboard
- [ ] Saw user name in header
- [ ] Saw logout button in header
- [ ] Used app features (templates, upload, etc.)
- [ ] Features work correctly
- [ ] Clicked logout button
- [ ] Redirected back to login page
- [ ] **VERIFIED: Existing UI unchanged**

### Part 6: Security Verification

- [ ] Verified `.env` files are in `.gitignore`
- [ ] Verified no credentials in git commits
- [ ] Tested without authentication (should see login page)
- [ ] Tested token expiry (auto refresh works)
- [ ] Tested with wrong credentials (shows error)
- [ ] Tested logout (clears session)

---

## 🚨 Common Issues & Fixes

### Issue 1: "Login failed" or "Invalid credentials"
**Check:**
- [ ] Client ID matches in frontend/.env and Azure portal
- [ ] Tenant ID matches in frontend/.env and Azure portal
- [ ] User account is part of the Azure AD tenant
- [ ] Redirect URI is exactly `http://localhost:3000` (no trailing slash)

### Issue 2: "CORS Error"
**Check:**
- [ ] Backend is running on port 5000
- [ ] Frontend is accessing `http://localhost:5000/api/*`
- [ ] Backend has CORS enabled (already configured in app.py)

### Issue 3: "Invalid token" on API calls
**Check:**
- [ ] Backend AZURE_CLIENT_ID matches frontend
- [ ] Backend AZURE_TENANT_ID matches frontend
- [ ] AZURE_CLIENT_SECRET is correct
- [ ] User is logged in on frontend

### Issue 4: Stuck on loading screen
**Check:**
- [ ] Browser console for errors
- [ ] Network tab for failed requests
- [ ] Clear browser cache and cookies
- [ ] Try incognito/private mode

### Issue 5: Redirect URI mismatch
**Fix:**
- Go to Azure portal
- App registrations → Your app → Authentication
- Add redirect URI: `http://localhost:3000`
- Save

---

## 🎯 Quick Test Script

Run this test to verify everything:

```bash
# 1. Check environment files exist
ls frontend/.env
ls Backend/.env

# 2. Check frontend has values (should not show placeholder)
cat frontend/.env | grep "your-client-id"
# Should return nothing if configured correctly

# 3. Check backend has values
cat Backend/.env | grep "your-client-id"
# Should return nothing if configured correctly

# 4. Test servers are running
curl http://localhost:5000/api/templates
curl http://localhost:3000

# 5. Open browser
start http://localhost:3000
```

---

## 📊 Verification Matrix

| Component | Expected Behavior | Status |
|-----------|------------------|--------|
| Login page loads | Should see "Sign in with Microsoft" | ⬜ |
| Click sign-in | Microsoft popup opens | ⬜ |
| Enter credentials | Authenticates successfully | ⬜ |
| After login | Redirected to dashboard | ⬜ |
| User info | Name shown in header | ⬜ |
| Logout button | Visible in header | ⬜ |
| Click logout | Redirected to login | ⬜ |
| Template selection | Works normally | ⬜ |
| Resume upload | Works normally | ⬜ |
| Download | Works normally | ⬜ |
| **UI unchanged** | Same colors/layout | ⬜ |

**All checkboxes should be ✅ after setup**

---

## 🎓 Production Checklist

When deploying to production:

- [ ] Updated redirect URI in Azure portal with production URL
- [ ] Updated `REACT_APP_AZURE_REDIRECT_URI` in frontend/.env
- [ ] Set environment variables in hosting platform (not .env files)
- [ ] Enabled HTTPS (required by Microsoft)
- [ ] Tested authentication flow on production
- [ ] Verified CORS allows production domain
- [ ] Removed `.env` files from deployment (use platform env vars)
- [ ] Enabled logging for authentication events
- [ ] Set up monitoring in Azure portal
- [ ] Tested MFA if enabled
- [ ] Verified conditional access policies work

---

## 💡 Next Steps After Setup

Once authentication is working:

1. **Optional Enhancements:**
   - Add role-based access control (RBAC)
   - Integrate with Microsoft Graph API
   - Add user profile pictures
   - Implement refresh token rotation
   - Add session timeout warnings

2. **Monitoring:**
   - Check Azure AD sign-in logs
   - Monitor authentication failures
   - Track user access patterns

3. **Security:**
   - Enable MFA for all users
   - Set up conditional access policies
   - Review permissions regularly
   - Audit token usage

---

## ✅ Final Verification

**Your setup is complete when:**
- ✅ You can sign in with Microsoft account
- ✅ You see your name in the header
- ✅ All app features work
- ✅ Logout works
- ✅ Can't access app without logging in
- ✅ **Existing UI is unchanged**

---

## 📞 Need Help?

1. **Quick fixes:** See `AZURE_AUTH_QUICKSTART.md`
2. **Detailed guide:** See `AZURE_AUTH_SETUP.md`
3. **Browser console:** Check for error messages
4. **Backend logs:** Check terminal for errors

---

**Good luck! 🚀**
