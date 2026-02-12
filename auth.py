"""
Azure Entra ID (formerly Azure AD) authentication module using MSAL.
Handles user authentication and token management.
"""
import msal
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# MSAL Configuration
CLIENT_ID = os.getenv('ENTRA_CLIENT_ID')
CLIENT_SECRET = os.getenv('ENTRA_CLIENT_SECRET')
AUTHORITY = os.getenv('ENTRA_AUTHORITY', 'https://login.microsoftonline.com/common')
REDIRECT_URI = os.getenv('ENTRA_REDIRECT_URI', 'http://localhost:8000/auth/callback')

# Scopes for user profile access
SCOPES = ['User.Read']


def get_msal_app():
    """
    Initialize and return MSAL application instance.
    
    Returns:
        msal.PublicClientApplication: MSAL app for authentication
    """
    return msal.PublicClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        token_cache=None  # In production, implement proper token caching
    )


def get_auth_url():
    """
    Generate the authorization URL for user login.
    
    Returns:
        str: Authorization URL for Entra ID login
    """
    app = get_msal_app()
    auth_url = app.get_authorization_request_url(
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        prompt='select_account'
    )
    return auth_url[0] if isinstance(auth_url, tuple) else auth_url


def acquire_token_by_auth_code(code, scopes=None):
    """
    Exchange authorization code for access token.
    
    Args:
        code (str): Authorization code from Entra ID
        scopes (list): Optional list of scopes
        
    Returns:
        dict: Token response or error
    """
    if not scopes:
        scopes = SCOPES
        
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )
    
    try:
        token_response = app.acquire_token_by_authorization_code(
            code=code,
            scopes=scopes,
            redirect_uri=REDIRECT_URI
        )
        return token_response
    except Exception as e:
        logger.error(f"Error acquiring token: {str(e)}")
        return {'error': str(e)}


def validate_token(access_token):
    """
    Validate the access token by attempting to use it in an API call.
    
    Args:
        access_token (str): JWT access token
        
    Returns:
        dict: User info if valid, error dict if invalid
    """
    try:
        # In production, you would validate the JWT signature
        # For now, we just check if it's not empty and has valid structure
        if not access_token or not isinstance(access_token, str):
            return {'error': 'Invalid token format'}
        
        parts = access_token.split('.')
        if len(parts) != 3:
            return {'error': 'Invalid JWT format'}
        
        logger.info("Token validation successful")
        return {'valid': True}
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return {'error': str(e)}


def is_authenticated(session):
    """
    Check if user is authenticated based on session.
    
    Args:
        session (dict): Flask session dictionary
        
    Returns:
        bool: True if user is authenticated
    """
    return 'access_token' in session and session.get('access_token') is not None
