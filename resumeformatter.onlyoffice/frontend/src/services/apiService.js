/**
 * API Service with Azure AD Authentication
 * This service handles all API calls and automatically attaches authentication tokens
 */

import { msalInstance } from '../index';
import { loginRequest } from '../authConfig';

/**
 * Get access token for API calls
 * Automatically refreshes if expired
 */
async function getAccessToken() {
  try {
    const account = msalInstance.getAllAccounts()[0];
    
    if (!account) {
      throw new Error('No active account');
    }

    // Try to acquire token silently
    const response = await msalInstance.acquireTokenSilent({
      ...loginRequest,
      account: account
    });

    return response.accessToken;
  } catch (error) {
    console.error('Error acquiring token:', error);
    
    // If silent acquisition fails, try interactive
    try {
      const response = await msalInstance.acquireTokenPopup(loginRequest);
      return response.accessToken;
    } catch (interactiveError) {
      console.error('Interactive token acquisition failed:', interactiveError);
      throw interactiveError;
    }
  }
}

/**
 * Make authenticated API request
 * @param {string} url - API endpoint URL
 * @param {object} options - Fetch options
 * @returns {Promise} - Fetch response
 */
export async function authenticatedFetch(url, options = {}) {
  try {
    const token = await getAccessToken();
    
    const headers = {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    };

    return fetch(url, {
      ...options,
      headers
    });
  } catch (error) {
    console.error('Authenticated fetch failed:', error);
    // Fallback to unauthenticated request for development
    console.warn('Falling back to unauthenticated request');
    return fetch(url, options);
  }
}

/**
 * Helper functions for common HTTP methods
 */
export const api = {
  get: (url, options = {}) => authenticatedFetch(url, {
    ...options,
    method: 'GET'
  }),
  
  post: (url, data, options = {}) => authenticatedFetch(url, {
    ...options,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    body: JSON.stringify(data)
  }),
  
  put: (url, data, options = {}) => authenticatedFetch(url, {
    ...options,
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    body: JSON.stringify(data)
  }),
  
  delete: (url, options = {}) => authenticatedFetch(url, {
    ...options,
    method: 'DELETE'
  }),
  
  // For file uploads
  postFormData: (url, formData, options = {}) => authenticatedFetch(url, {
    ...options,
    method: 'POST',
    body: formData
    // Don't set Content-Type for FormData - browser will set it with boundary
  })
};

export default api;
