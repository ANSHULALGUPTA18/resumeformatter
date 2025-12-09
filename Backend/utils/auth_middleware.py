"""
Azure AD (Entra ID) Authentication Middleware for Flask Backend
This middleware validates Azure AD tokens sent from the frontend
"""

import os
import jwt
import requests
from functools import wraps
from flask import request, jsonify
from jwt import PyJWKClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure AD Configuration
AZURE_TENANT_ID = os.getenv('AZURE_TENANT_ID', '')
AZURE_CLIENT_ID = os.getenv('AZURE_CLIENT_ID', '')

# Azure AD endpoints
AZURE_ISSUER = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/v2.0"
AZURE_JWKS_URI = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/discovery/v2.0/keys"


def get_token_from_header():
    """Extract Bearer token from Authorization header"""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None


def validate_azure_token(token):
    """
    Validate Azure AD access token
    Returns decoded token if valid, None otherwise
    """
    if not token:
        return None
    
    try:
        # Get signing keys from Azure AD
        jwks_client = PyJWKClient(AZURE_JWKS_URI)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # Decode and validate token
        decoded_token = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=AZURE_CLIENT_ID,
            issuer=AZURE_ISSUER,
            options={
                "verify_signature": True,
                "verify_aud": True,
                "verify_iss": True,
                "verify_exp": True
            }
        )
        
        return decoded_token
    
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None
    except Exception as e:
        print(f"Token validation error: {e}")
        return None


def require_auth(f):
    """
    Decorator to require Azure AD authentication for Flask routes
    Usage: @require_auth
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip auth if Azure credentials not configured (for development)
        if not AZURE_TENANT_ID or not AZURE_CLIENT_ID:
            print("⚠️  Azure AD not configured - skipping authentication")
            return f(*args, **kwargs)
        
        # Get token from request
        token = get_token_from_header()
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'No authentication token provided'
            }), 401
        
        # Validate token
        decoded_token = validate_azure_token(token)
        
        if not decoded_token:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired authentication token'
            }), 401
        
        # Add user info to request context
        request.user = {
            'oid': decoded_token.get('oid'),  # User object ID
            'name': decoded_token.get('name'),
            'email': decoded_token.get('preferred_username') or decoded_token.get('email'),
            'tenant_id': decoded_token.get('tid')
        }
        
        return f(*args, **kwargs)
    
    return decorated_function


def init_auth(app):
    """
    Initialize authentication for Flask app
    Call this in app.py after creating the Flask app
    """
    
    # Add CORS headers for auth
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Authorization')
        return response
    
    print("\n" + "="*70)
    print("🔐 Azure AD Authentication")
    print("="*70)
    
    if AZURE_TENANT_ID and AZURE_CLIENT_ID:
        print("✅ Azure AD configured")
        print(f"   Tenant ID: {AZURE_TENANT_ID[:8]}...")
        print(f"   Client ID: {AZURE_CLIENT_ID[:8]}...")
    else:
        print("⚠️  Azure AD NOT configured - authentication disabled")
        print("   Set AZURE_TENANT_ID and AZURE_CLIENT_ID in .env")
    
    print("="*70 + "\n")
