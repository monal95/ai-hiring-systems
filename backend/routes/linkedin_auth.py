"""
LinkedIn OAuth 2.0 Authentication Routes
Handles login, callback, token exchange, and user profile fetching
"""

from flask import Blueprint, request, jsonify, redirect, session
import requests
import secrets
import json
from datetime import datetime, timedelta
from config.linkedin_config import LINKEDIN_CONFIG, get_authorization_url

linkedin_bp = Blueprint('linkedin', __name__)

# In-memory token storage (use database in production)
user_tokens = {}
user_profiles = {}

@linkedin_bp.route('/api/auth/linkedin/login', methods=['GET'])
def linkedin_login():
    """Initiate LinkedIn OAuth flow"""
    # Generate secure state token
    state = secrets.token_urlsafe(32)
    
    # Store state for verification (in production, use session or Redis)
    session['oauth_state'] = state
    
    auth_url = get_authorization_url(state)
    
    return jsonify({
        'authorization_url': auth_url,
        'state': state
    })

@linkedin_bp.route('/api/auth/linkedin/callback', methods=['POST'])
def linkedin_callback():
    """Handle LinkedIn OAuth callback - exchange code for access token"""
    data = request.json
    code = data.get('code')
    state = data.get('state')
    
    if not code:
        return jsonify({'error': 'Authorization code not provided'}), 400
    
    # Exchange code for access token
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': LINKEDIN_CONFIG['redirect_uri'],
        'client_id': LINKEDIN_CONFIG['client_id'],
        'client_secret': LINKEDIN_CONFIG['client_secret']
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(
            LINKEDIN_CONFIG['token_url'],
            data=token_data,
            headers=headers
        )
        
        if response.status_code != 200:
            return jsonify({
                'error': 'Failed to exchange code for token',
                'details': response.text
            }), 400
        
        token_response = response.json()
        access_token = token_response.get('access_token')
        expires_in = token_response.get('expires_in', 5184000)  # Default 60 days
        
        # Fetch user profile
        profile = fetch_linkedin_profile(access_token)
        
        if not profile:
            return jsonify({'error': 'Failed to fetch user profile'}), 400
        
        # Generate session token
        session_token = secrets.token_urlsafe(32)
        
        # Store token and profile
        user_tokens[session_token] = {
            'access_token': access_token,
            'expires_at': datetime.now() + timedelta(seconds=expires_in),
            'created_at': datetime.now().isoformat()
        }
        user_profiles[session_token] = profile
        
        return jsonify({
            'success': True,
            'session_token': session_token,
            'profile': profile,
            'expires_in': expires_in,
            'message': 'LinkedIn connected successfully!'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def fetch_linkedin_profile(access_token: str) -> dict:
    """Fetch user profile from LinkedIn API"""
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        # Fetch profile info using OpenID Connect userinfo endpoint
        profile_response = requests.get(
            LINKEDIN_CONFIG['profile_url'],
            headers=headers
        )
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            
            return {
                'id': profile_data.get('sub'),
                'name': profile_data.get('name'),
                'given_name': profile_data.get('given_name'),
                'family_name': profile_data.get('family_name'),
                'email': profile_data.get('email'),
                'picture': profile_data.get('picture'),
                'email_verified': profile_data.get('email_verified', False)
            }
        
        return None
        
    except Exception as e:
        print(f"Error fetching LinkedIn profile: {e}")
        return None

@linkedin_bp.route('/api/auth/linkedin/status', methods=['GET'])
def linkedin_status():
    """Check if user is connected to LinkedIn"""
    session_token = request.headers.get('X-LinkedIn-Session')
    
    if session_token and session_token in user_tokens:
        token_info = user_tokens[session_token]
        
        # Check if token is expired
        if datetime.now() < token_info['expires_at']:
            profile = user_profiles.get(session_token, {})
            return jsonify({
                'connected': True,
                'profile': profile
            })
    
    return jsonify({'connected': False})

@linkedin_bp.route('/api/auth/linkedin/logout', methods=['POST'])
def linkedin_logout():
    """Disconnect LinkedIn account"""
    session_token = request.headers.get('X-LinkedIn-Session')
    
    if session_token:
        user_tokens.pop(session_token, None)
        user_profiles.pop(session_token, None)
    
    return jsonify({'success': True, 'message': 'LinkedIn disconnected'})

@linkedin_bp.route('/api/auth/linkedin/profile', methods=['GET'])
def get_profile():
    """Get stored LinkedIn profile"""
    session_token = request.headers.get('X-LinkedIn-Session')
    
    if session_token and session_token in user_profiles:
        return jsonify({
            'success': True,
            'profile': user_profiles[session_token]
        })
    
    return jsonify({'error': 'Not connected to LinkedIn'}), 401


def get_user_access_token(session_token: str) -> str:
    """Get access token for a session (used by job sharing)"""
    if session_token and session_token in user_tokens:
        token_info = user_tokens[session_token]
        if datetime.now() < token_info['expires_at']:
            return token_info['access_token']
    return None
