import { useState, useEffect } from 'react';
import { useMsal } from '@azure/msal-react';

/**
 * Custom hook to fetch user profile photo from Microsoft Graph API
 * Returns photoUrl (blob URL) or null if unavailable, plus loading state
 */
function useUserProfilePhoto() {
  const { instance, accounts } = useMsal();
  const [photoUrl, setPhotoUrl] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPhoto() {
      try {
        const account = accounts[0];
        if (!account) {
          setLoading(false);
          return;
        }

        // Acquire token silently for Microsoft Graph API
        const response = await instance.acquireTokenSilent({
          scopes: ['User.Read'],
          account: account
        });

        // Fetch photo from Microsoft Graph API
        const photoResponse = await fetch(
          'https://graph.microsoft.com/v1.0/me/photo/$value',
          {
            headers: {
              'Authorization': `Bearer ${response.accessToken}`
            }
          }
        );

        if (photoResponse.ok) {
          const blob = await photoResponse.blob();
          const url = URL.createObjectURL(blob);
          setPhotoUrl(url);
        } else {
          // Photo not available (404) or other error
          console.log('Profile photo not available');
        }
      } catch (error) {
        // Handle errors gracefully - photo not available or token acquisition failed
        console.log('Error fetching profile photo:', error.message);
      } finally {
        setLoading(false);
      }
    }

    fetchPhoto();

    // Cleanup: Revoke blob URL on unmount to prevent memory leaks
    return () => {
      if (photoUrl) {
        URL.revokeObjectURL(photoUrl);
      }
    };
  }, [instance, accounts]);

  return { photoUrl, loading };
}

export default useUserProfilePhoto;
