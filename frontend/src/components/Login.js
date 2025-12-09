import React from 'react';
import { useMsal } from '@azure/msal-react';
import { loginRequest } from '../authConfig';
import './Login.css';

/**
 * Login Component
 * Displays a Microsoft Sign-In button for Azure AD authentication
 * This component maintains your existing app styling and adds minimal intrusive UI
 */
function Login() {
  const { instance } = useMsal();

  const handleLogin = async () => {
    try {
      await instance.loginPopup(loginRequest);
    } catch (error) {
      console.error('Login failed:', error);
      // Handle error - show user-friendly message
      if (error.errorCode === 'user_cancelled') {
        // User closed the popup, no action needed
        return;
      }
      alert('Login failed. Please try again or contact your administrator.');
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <span className="login-logo">✨</span>
          <h1>Resume Formatter Pro</h1>
          <p className="login-subtitle">Transform Your Resumes with Professional Templates</p>
        </div>
        
        <div className="login-content">
          <div className="login-message">
            <h2>Welcome!</h2>
            <p>Please sign in with your Microsoft account to continue</p>
          </div>
          
          <button 
            className="microsoft-signin-btn" 
            onClick={handleLogin}
            aria-label="Sign in with Microsoft"
          >
            <svg className="microsoft-logo" viewBox="0 0 23 23" xmlns="http://www.w3.org/2000/svg">
              <rect x="1" y="1" width="10" height="10" fill="#f25022"/>
              <rect x="12" y="1" width="10" height="10" fill="#7fba00"/>
              <rect x="1" y="12" width="10" height="10" fill="#00a4ef"/>
              <rect x="12" y="12" width="10" height="10" fill="#ffb900"/>
            </svg>
            <span>Sign in with Microsoft</span>
          </button>
          
          <div className="login-info">
            <p className="info-text">
              🔒 Secure authentication via Azure Active Directory
            </p>
            <p className="info-text">
              ✅ Single sign-on with your organization account
            </p>
          </div>
        </div>
        
        <div className="login-footer">
          <p>© 2025 Resume Formatter Pro • Powered by AI</p>
        </div>
      </div>
    </div>
  );
}

export default Login;
