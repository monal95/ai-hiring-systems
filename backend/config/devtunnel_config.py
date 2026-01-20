"""
Dev Tunnel Configuration Handler
Manages VS Code Dev Tunnel URLs for external candidate access
"""

import os
from dotenv import load_dotenv

load_dotenv()

class DevTunnelConfig:
    """Configuration for VS Code dev tunnel URLs"""
    
    # Dev Tunnel URLs - Update these when you create new tunnels
    BACKEND_TUNNEL_URL = os.getenv(
        'BACKEND_TUNNEL_URL', 
        'https://3h16jwxk-5000.inc1.devtunnels.ms'
    )
    
    FRONTEND_TUNNEL_URL = os.getenv(
        'FRONTEND_TUNNEL_URL',
        'https://3h16jwxk-3000.inc1.devtunnels.ms'
    )
    
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://3h16jwxk-3000.inc1.devtunnels.ms')
    
    # Local fallback URLs (for admin's local system)
    LOCAL_BACKEND_URL = os.getenv('LOCAL_BACKEND_URL', 'http://localhost:5000')
    LOCAL_FRONTEND_URL = os.getenv('LOCAL_FRONTEND_URL', 'http://localhost:3000')
    
    # Flask app configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'
    
    @staticmethod
    def get_backend_url(use_tunnel=True):
        """Get backend URL - uses tunnel if available"""
        if use_tunnel and DevTunnelConfig.BACKEND_TUNNEL_URL:
            return DevTunnelConfig.BACKEND_TUNNEL_URL
        return DevTunnelConfig.LOCAL_BACKEND_URL
    
    @staticmethod
    def get_frontend_url(use_tunnel=True):
        """Get frontend URL - uses tunnel if available"""
        if use_tunnel and DevTunnelConfig.FRONTEND_TUNNEL_URL:
            return DevTunnelConfig.FRONTEND_TUNNEL_URL
        return DevTunnelConfig.LOCAL_FRONTEND_URL


# Alias for compatibility
TunnelConfig = DevTunnelConfig


# CORS Configuration for dev tunnel access
def get_cors_config():
    """
    Get CORS configuration that allows dev tunnel URLs
    """
    allowed_origins = [
        'http://localhost:3000',
        'http://localhost:3001',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:3001',
    ]
    
    # Add tunnel URLs if configured
    if os.getenv('FRONTEND_TUNNEL_URL'):
        allowed_origins.append(os.getenv('FRONTEND_TUNNEL_URL'))
    if os.getenv('BACKEND_TUNNEL_URL'):
        allowed_origins.append(os.getenv('BACKEND_TUNNEL_URL'))
    if os.getenv('FRONTEND_URL'):
        allowed_origins.append(os.getenv('FRONTEND_URL'))
    
    return {
        'origins': allowed_origins,
        'supports_credentials': True,
        'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        'allow_headers': ['Content-Type', 'Authorization']
    }
