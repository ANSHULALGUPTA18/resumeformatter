import React from 'react';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import Login from './Login';

/**
 * AuthGuard Component
 * Protects routes by requiring authentication
 * Shows login page if user is not authenticated
 * Renders children components only when authenticated
 */
function AuthGuard({ children }) {
  const isAuthenticated = useIsAuthenticated();
  const { inProgress } = useMsal();

  // Show loading state while authentication is in progress
  if (inProgress === 'login' || inProgress === 'handleRedirect') {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        fontSize: '18px',
        fontFamily: 'system-ui, -apple-system, sans-serif'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>⏳</div>
          <div>Authenticating...</div>
        </div>
      </div>
    );
  }

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return <Login />;
  }

  // Render protected content
  return <>{children}</>;
}

export default AuthGuard;
