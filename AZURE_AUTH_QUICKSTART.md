# 🚀 Azure AD Authentication - Quick Reference

## ⚡ Quick Setup (5 Minutes)

### Option 1: Automated Setup
```bash
# Run the configuration script
configure-azure-auth.bat

# Enter your credentials when prompted:
# - Azure Client ID
# - Azure Tenant ID  
# - Azure Client Secret

# Restart servers
```

### Option 2: Manual Setup

**Frontend (.env):**
```env
REACT_APP_AZURE_CLIENT_ID=your-client-id
REACT_APP_AZURE_TENANT_ID=your-tenant-id
REACT_APP_AZURE_REDIRECT_URI=http://localhost:3000
```

**Backend (.env):**
```env
AZURE_CLIENT_ID=your-client-id
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_SECRET=your-client-secret
```

## 🔑 Where to Find Azure Credentials

1. Go to [Azure Portal](https://portal.azure.com)
2. **Azure Active Directory** → **App registrations**
3. Select your app

**Client ID:** Overview page → Application (client) ID  
**Tenant ID:** Overview page → Directory (tenant) ID  
**Client Secret:** Certificates & secrets → New client secret

## 📋 Azure Portal Configuration Checklist

- [ ] Redirect URI set to `http://localhost:3000`
- [ ] API permission `User.Read` added
- [ ] Admin consent granted
- [ ] Single-tenant (current directory only)

## 🎯 How to Use

### For Users:
1. Open `http://localhost:3000`
2. Click "Sign in with Microsoft"
3. Enter organization credentials
4. Use app normally
5. Click "Logout" when done

### For Developers:
```javascript
// Import the API service
import api from './services/apiService';

// All requests auto-attach auth tokens
const data = await api.get('http://localhost:5000/api/templates');
```

## 🔧 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Login fails | Check `.env` credentials match Azure portal |
| "Invalid redirect URI" | Add `http://localhost:3000` to Azure app |
| CORS error | Verify backend is running on port 5000 |
| Token expired | App auto-refreshes, if persists: logout/login |
| Backend auth fails | Check `AZURE_CLIENT_SECRET` in Backend/.env |

## 📁 Key Files

```
frontend/
├── .env                          # Your Azure credentials
├── src/
│   ├── authConfig.js            # MSAL configuration
│   ├── components/
│   │   ├── Login.js             # Login page
│   │   └── AuthGuard.js         # Route protection
│   └── services/
│       └── apiService.js        # Authenticated API calls

Backend/
├── .env                          # Your Azure credentials  
└── utils/
    └── auth_middleware.py       # Token validation
```

## 🛡️ Security Notes

- ✅ Single-tenant (only your organization)
- ✅ Tokens validated on backend
- ✅ Auto token refresh
- ✅ Secure storage
- ⚠️ Never commit `.env` files
- ⚠️ Use HTTPS in production

## 🌐 Production Deployment

1. Update redirect URI in Azure portal with production URL
2. Update `.env` files:
   ```env
   REACT_APP_AZURE_REDIRECT_URI=https://your-domain.com
   ```
3. Set environment variables in hosting platform
4. Enable HTTPS (required)
5. Test authentication flow

## 🧪 Testing

**Test authentication is working:**
1. Visit app → Should see login page
2. Sign in → Should see your name in header
3. Use app → All features work
4. Logout → Redirects to login page
5. Refresh → Still authenticated (if session valid)

## 💡 Pro Tips

- Use Azure AD groups for role-based access
- Enable MFA for enhanced security
- Monitor sign-ins in Azure portal
- Set token lifetime in Azure AD
- Use managed identities for production

## 📞 Need Help?

1. Check browser console for errors
2. Check backend logs
3. Verify Azure app configuration
4. See full guide: `AZURE_AUTH_SETUP.md`

---

**Remember:** Replace all placeholder values in `.env` files with your actual Azure AD credentials!
