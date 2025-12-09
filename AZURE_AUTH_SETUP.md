# Azure AD (Entra ID) Authentication Setup Guide

## 🔐 Overview

Your Resume Formatter application now includes **Microsoft Account authentication** using Azure Active Directory (Azure Entra ID). This provides secure, enterprise-grade authentication with single sign-on (SSO) capabilities.

## ✅ What's Been Implemented

1. **Frontend Authentication**
   - Login page with "Sign in with Microsoft" button
   - MSAL (Microsoft Authentication Library) integration
   - OAuth 2.0 + OpenID Connect
   - Single-tenant configuration (only your organization)
   - Auto token refresh
   - Secure session management

2. **UI Integration (No Changes to Existing Design)**
   - User info display in header (non-intrusive)
   - Logout button added to header
   - Login page matches your app's aesthetic
   - All existing features preserved

3. **Backend Protection**
   - JWT token validation middleware
   - Protected API endpoints
   - User context in requests

4. **Error Handling**
   - Login failures
   - Session expiry
   - Unauthorized access
   - Network errors

## 🚀 Setup Instructions

### Step 1: Configure Azure AD Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Find your app registration or create a new one
4. Note down:
   - **Client ID** (Application ID)
   - **Tenant ID** (Directory ID)
   - **Client Secret** (from Certificates & secrets)

5. Configure **Redirect URIs**:
   - Go to **Authentication** → **Platform configurations**
   - Add Web platform
   - Add redirect URI: `http://localhost:3000`
   - For production, add your production URL

6. Configure **API permissions**:
   - Add `User.Read` permission
   - Grant admin consent

### Step 2: Configure Frontend Environment Variables

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Open `.env` file and replace the placeholder values:
   ```env
   REACT_APP_AZURE_CLIENT_ID=your-actual-client-id-here
   REACT_APP_AZURE_TENANT_ID=your-actual-tenant-id-here
   REACT_APP_AZURE_REDIRECT_URI=http://localhost:3000
   ```

3. **IMPORTANT**: For production, update the redirect URI:
   ```env
   REACT_APP_AZURE_REDIRECT_URI=https://your-production-domain.com
   ```

### Step 3: Configure Backend Environment Variables

1. Navigate to the backend directory:
   ```bash
   cd Backend
   ```

2. Open `.env` file and replace the placeholder values:
   ```env
   AZURE_CLIENT_ID=your-actual-client-id-here
   AZURE_TENANT_ID=your-actual-tenant-id-here
   AZURE_CLIENT_SECRET=your-actual-client-secret-here
   ```

### Step 4: Restart Your Application

1. **Stop** both frontend and backend servers (Ctrl+C)

2. **Restart Backend**:
   ```bash
   cd Backend
   python app.py
   ```

3. **Restart Frontend**:
   ```bash
   cd frontend
   npm start
   ```

4. Open your browser to `http://localhost:3000`

## 🔧 How It Works

### Authentication Flow

1. **User visits app** → Redirected to Login page
2. **Click "Sign in with Microsoft"** → Opens Microsoft login popup
3. **Enter credentials** → Authenticates with Azure AD
4. **Successful login** → Token stored locally, user redirected to dashboard
5. **Using the app** → Token automatically attached to all API requests
6. **Token expires** → Automatically refreshed in background
7. **Logout** → Clears session and redirects to login

### Token Management

- **Access tokens** are automatically managed by MSAL
- **Silent refresh** happens when tokens expire
- **Fallback** to interactive login if silent refresh fails
- **Secure storage** in browser's localStorage

### Protected Routes

All existing routes are now protected:
- Template Selection
- Resume Upload
- Download Phase

Unauthenticated users cannot access any part of the application.

## 📝 Usage

### For End Users

1. Navigate to your app URL
2. Click "Sign in with Microsoft"
3. Enter your organization credentials
4. Use the app normally
5. Click "Logout" when done

### For Developers

**Making API calls with authentication:**

```javascript
import api from './services/apiService';

// GET request
const response = await api.get('http://localhost:5000/api/templates');

// POST request
const response = await api.post('http://localhost:5000/api/format', data);

// File upload
const formData = new FormData();
formData.append('file', file);
const response = await api.postFormData('http://localhost:5000/api/upload', formData);
```

The `api` service automatically:
- Attaches authentication tokens
- Refreshes expired tokens
- Handles authentication errors

## 🛡️ Security Features

1. **Single-Tenant**: Only users from your Azure AD tenant can sign in
2. **Token Validation**: Backend validates all tokens
3. **Auto Expiry**: Tokens expire and are refreshed automatically
4. **Secure Storage**: Tokens stored securely in browser
5. **HTTPS Ready**: Works with HTTPS in production
6. **CORS Protected**: Proper CORS configuration

## 🔍 Troubleshooting

### "Login failed" Error
- Verify your Azure AD credentials are correct in `.env`
- Check that redirect URI matches in Azure portal and `.env`
- Ensure your user account is part of the Azure AD tenant

### "Invalid token" Error
- Check that `AZURE_CLIENT_ID` and `AZURE_TENANT_ID` match in frontend and backend
- Verify backend `.env` has correct `AZURE_CLIENT_SECRET`
- Clear browser cache and try again

### "CORS Error"
- Check that backend is running on port 5000
- Verify `CORS` configuration in `app.py` includes `Authorization` header
- Make sure frontend is accessing correct backend URL

### Token Refresh Issues
- Clear browser localStorage
- Sign out and sign in again
- Check browser console for detailed error messages

## 📁 Files Added/Modified

### New Files Created:
- `frontend/src/authConfig.js` - MSAL configuration
- `frontend/src/components/Login.js` - Login page component
- `frontend/src/components/Login.css` - Login page styles
- `frontend/src/components/AuthGuard.js` - Route protection
- `frontend/src/services/apiService.js` - Authenticated API calls
- `frontend/.env` - Frontend environment variables
- `Backend/.env` - Backend environment variables
- `Backend/utils/auth_middleware.py` - Token validation middleware

### Modified Files:
- `frontend/src/index.js` - Added MSAL provider
- `frontend/src/App.js` - Added logout button and user info
- `frontend/src/App.css` - Added auth control styles

### Existing Features:
- ✅ All existing UI preserved
- ✅ All existing functionality working
- ✅ No breaking changes
- ✅ Backward compatible

## 🌐 Production Deployment

1. **Update Redirect URIs** in Azure portal with production URLs
2. **Update `.env` files** with production values
3. **Enable HTTPS** (required by Microsoft)
4. **Set up environment variables** in your hosting platform
5. **Test authentication flow** thoroughly

## 📞 Support

If you encounter issues:
1. Check the browser console for errors
2. Check backend logs for authentication errors
3. Verify all environment variables are set correctly
4. Ensure Azure AD app registration is configured properly

## 🎉 You're Done!

Your Resume Formatter now has enterprise-grade authentication powered by Microsoft Azure AD!

**Important**: Remember to replace the placeholder values in both `.env` files with your actual Azure AD credentials.
