"""
LinkedIn OAuth 2.0 Configuration
Handles LinkedIn authentication and API integration
"""

import os
from dotenv import load_dotenv

load_dotenv()

# LinkedIn OAuth Configuration
LINKEDIN_CONFIG = {
    # OAuth 2.0 Credentials
    'client_id': os.getenv('LINKEDIN_CLIENT_ID', '86yvqgasdy2sr3'),
    'client_secret': os.getenv('LINKEDIN_CLIENT_SECRET', 'WPL_AP1.1jYf2tAlOTfaGwRX.v4foRg=='),
    
    # OAuth URLs
    'authorization_url': 'https://www.linkedin.com/oauth/v2/authorization',
    'token_url': 'https://www.linkedin.com/oauth/v2/accessToken',
    'redirect_uri': os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost:3001/auth/linkedin/callback'),
    
    # API Endpoints
    'api_base_url': 'https://api.linkedin.com/v2',
    'profile_url': 'https://api.linkedin.com/v2/userinfo',
    'share_url': 'https://api.linkedin.com/v2/ugcPosts',
    
    # OAuth Scopes
    'scopes': ['openid', 'profile', 'email', 'w_member_social'],
    
    # Mode: MOCK, REDIRECT, or API
    'mode': os.getenv('LINKEDIN_MODE', 'REDIRECT'),
    
    # Token storage (in production, use Redis or database)
    'token_storage': {}
}

def get_authorization_url(state: str) -> str:
    """Generate LinkedIn OAuth authorization URL"""
    scopes = '%20'.join(LINKEDIN_CONFIG['scopes'])
    return (
        f"{LINKEDIN_CONFIG['authorization_url']}"
        f"?response_type=code"
        f"&client_id={LINKEDIN_CONFIG['client_id']}"
        f"&redirect_uri={LINKEDIN_CONFIG['redirect_uri']}"
        f"&scope={scopes}"
        f"&state={state}"
    )

def get_linkedin_mode():
    """Get current LinkedIn integration mode"""
    return LINKEDIN_CONFIG['mode']

def set_linkedin_mode(mode: str):
    """Set LinkedIn integration mode (MOCK, REDIRECT, API)"""
    if mode in ['MOCK', 'REDIRECT', 'API']:
        LINKEDIN_CONFIG['mode'] = mode
        return True
    return False
