"""
Routes package for GCC Hiring System
"""

from routes.linkedin_auth import linkedin_bp
from routes.linkedin_share import linkedin_share_bp

__all__ = ['linkedin_bp', 'linkedin_share_bp']
