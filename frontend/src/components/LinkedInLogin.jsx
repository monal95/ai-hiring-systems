import React, { useState, useEffect } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config/api';

const LinkedInLogin = ({ onLoginSuccess, onLogout }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Check LinkedIn connection status on mount
  useEffect(() => {
    checkLinkedInStatus();
  }, []);

  // Listen for OAuth callback
  useEffect(() => {
    const handleCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      const state = urlParams.get('state');
      
      if (code && window.location.pathname.includes('/auth/linkedin/callback')) {
        await exchangeCodeForToken(code, state);
        // Clean up URL
        window.history.replaceState({}, document.title, '/');
      }
    };
    
    handleCallback();
  }, []);

  const checkLinkedInStatus = async () => {
    const sessionToken = localStorage.getItem('linkedin_session');
    if (!sessionToken) {
      setIsConnected(false);
      return;
    }

    try {
      const response = await axios.get(`${API_BASE_URL}/api/auth/linkedin/status`, {
        headers: { 'X-LinkedIn-Session': sessionToken }
      });
      
      if (response.data.connected) {
        setIsConnected(true);
        setProfile(response.data.profile);
      } else {
        localStorage.removeItem('linkedin_session');
        setIsConnected(false);
      }
    } catch (err) {
      console.error('Error checking LinkedIn status:', err);
      setIsConnected(false);
    }
  };

  const initiateLogin = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(`${API_BASE_URL}/api/auth/linkedin/login`);
      const { authorization_url, state } = response.data;
      
      // Store state for verification
      localStorage.setItem('linkedin_oauth_state', state);
      
      // Redirect to LinkedIn
      window.location.href = authorization_url;
    } catch (err) {
      setError('Failed to initiate LinkedIn login');
      setLoading(false);
    }
  };

  const exchangeCodeForToken = async (code, state) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/linkedin/callback`, {
        code,
        state
      });

      if (response.data.success) {
        const { session_token, profile } = response.data;
        
        localStorage.setItem('linkedin_session', session_token);
        setIsConnected(true);
        setProfile(profile);
        
        if (onLoginSuccess) {
          onLoginSuccess(profile);
        }
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to connect LinkedIn');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    const sessionToken = localStorage.getItem('linkedin_session');
    
    try {
      await axios.post(`${API_BASE_URL}/api/auth/linkedin/logout`, {}, {
        headers: { 'X-LinkedIn-Session': sessionToken }
      });
    } catch (err) {
      console.error('Logout error:', err);
    }

    localStorage.removeItem('linkedin_session');
    setIsConnected(false);
    setProfile(null);
    
    if (onLogout) {
      onLogout();
    }
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loadingBox}>
          <span style={styles.spinner}>⏳</span>
          <span>Connecting to LinkedIn...</span>
        </div>
      </div>
    );
  }

  if (isConnected && profile) {
    return (
      <div style={styles.container}>
        <div style={styles.connectedBox}>
          <div style={styles.profileSection}>
            {profile.picture && (
              <img 
                src={profile.picture} 
                alt={profile.name}
                style={styles.avatar}
              />
            )}
            <div style={styles.profileInfo}>
              <div style={styles.connectedBadge}>
                ✅ LinkedIn Connected
              </div>
              <div style={styles.profileName}>{profile.name}</div>
              <div style={styles.profileEmail}>{profile.email}</div>
            </div>
          </div>
          <button onClick={handleLogout} style={styles.disconnectBtn}>
            Disconnect
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {error && (
        <div style={styles.errorBox}>
          ❌ {error}
        </div>
      )}
      <button onClick={initiateLogin} style={styles.linkedInBtn}>
        <svg style={styles.linkedInIcon} viewBox="0 0 24 24" fill="white">
          <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
        </svg>
        Login with LinkedIn
      </button>
      <p style={styles.helperText}>
        Connect to share job posts on LinkedIn
      </p>
    </div>
  );
};

const styles = {
  container: {
    padding: '12px',
  },
  loadingBox: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '12px 16px',
    backgroundColor: '#f0f9ff',
    borderRadius: '8px',
    color: '#0369a1',
  },
  spinner: {
    animation: 'spin 1s linear infinite',
  },
  connectedBox: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 16px',
    backgroundColor: '#f0fdf4',
    border: '1px solid #86efac',
    borderRadius: '8px',
  },
  profileSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  avatar: {
    width: '48px',
    height: '48px',
    borderRadius: '50%',
    border: '2px solid #22c55e',
  },
  profileInfo: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
  },
  connectedBadge: {
    fontSize: '12px',
    fontWeight: '600',
    color: '#16a34a',
  },
  profileName: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#166534',
  },
  profileEmail: {
    fontSize: '12px',
    color: '#15803d',
  },
  disconnectBtn: {
    padding: '6px 12px',
    backgroundColor: 'transparent',
    color: '#dc2626',
    border: '1px solid #dc2626',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: '500',
    transition: 'all 0.2s',
  },
  linkedInBtn: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    width: '100%',
    padding: '12px 20px',
    backgroundColor: '#0a66c2',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '15px',
    fontWeight: '600',
    transition: 'all 0.2s',
  },
  linkedInIcon: {
    width: '20px',
    height: '20px',
  },
  helperText: {
    marginTop: '8px',
    fontSize: '12px',
    color: '#6b7280',
    textAlign: 'center',
  },
  errorBox: {
    padding: '10px 12px',
    marginBottom: '12px',
    backgroundColor: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: '6px',
    color: '#dc2626',
    fontSize: '13px',
  },
};

export default LinkedInLogin;
