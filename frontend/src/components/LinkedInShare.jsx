import React, { useState } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config/api';

const LinkedInShare = ({ jobData, onShareComplete }) => {
  const [sharing, setSharing] = useState(false);
  const [shareResult, setShareResult] = useState(null);
  const [postPreview, setPostPreview] = useState(null);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState('REDIRECT'); // MOCK, REDIRECT, API

  const getSessionToken = () => localStorage.getItem('linkedin_session');

  const generatePreview = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/linkedin/generate-post`, jobData);
      setPostPreview(response.data.post_content);
    } catch (err) {
      console.error('Error generating preview:', err);
    }
  };

  const shareToLinkedIn = async () => {
    setSharing(true);
    setError(null);

    try {
      const sessionToken = getSessionToken();
      
      const response = await axios.post(
        `${API_BASE_URL}/api/linkedin/share/job`,
        { job_data: jobData },
        {
          headers: sessionToken ? { 'X-LinkedIn-Session': sessionToken } : {}
        }
      );

      const result = response.data;
      setShareResult(result);

      // Handle redirect mode
      if (result.mode === 'REDIRECT') {
        // Copy post content to clipboard
        if (result.post_content) {
          try {
            await navigator.clipboard.writeText(result.post_content);
          } catch (clipboardErr) {
            console.warn('Clipboard copy failed:', clipboardErr);
            // Fallback: content is available in UI for manual copy
          }
        }
      }

      if (onShareComplete) {
        onShareComplete(result);
      }
    } catch (err) {
      const errData = err.response?.data;
      setError(errData?.error || 'Failed to share to LinkedIn');
      
      // If API mode fails, show fallback option
      if (errData?.fallback === 'REDIRECT' && errData?.post_content) {
        setPostPreview(errData.post_content);
      }
    } finally {
      setSharing(false);
    }
  };

  const openLinkedInShare = () => {
    // Copy content to clipboard first
    const content = shareResult?.post_content || postPreview;
    if (content) {
      navigator.clipboard.writeText(content).catch(err => {
        console.warn('Clipboard copy failed:', err);
        // Content is still available in UI for manual copy
      });
    }
    // Open LinkedIn post composer
    window.open('https://www.linkedin.com/feed/?shareActive=true', '_blank', 'width=700,height=600');
  };

  const openLinkedInJobs = () => {
    // Copy content to clipboard first
    const content = shareResult?.post_content || postPreview;
    if (content) {
      navigator.clipboard.writeText(content).catch(err => {
        console.warn('Clipboard copy failed:', err);
        // Content is still available in UI for manual copy
      });
    }
    // Use free job posting URL (available to all users)
    window.open('https://www.linkedin.com/jobs/post/', '_blank');
  };

  const copyToClipboard = async () => {
    const content = postPreview || shareResult?.post_content;
    if (content) {
      try {
        await navigator.clipboard.writeText(content);
        alert('✅ Post content copied to clipboard!');
      } catch (err) {
        console.error('Failed to copy to clipboard:', err);
        alert('Unable to copy to clipboard. Please try again or manually copy the content.');
      }
    }
  };

  // Show result after sharing
  if (shareResult) {
    return (
      <div style={styles.container}>
        <div style={styles.resultBox}>
          {shareResult.mode === 'MOCK' && (
            <>
              <div style={styles.successHeader}>
                🎭 Mock Share Complete
              </div>
              <p style={styles.modeNote}>
                This is a mock service that simulates LinkedIn's real API behavior.
              </p>
              <div style={styles.infoRow}>
                <span style={styles.label}>Status:</span>
                <span style={styles.statusBadge}>{shareResult.status}</span>
              </div>
              <div style={styles.infoRow}>
                <span style={styles.label}>Post ID:</span>
                <span style={styles.value}>{shareResult.post_id}</span>
              </div>
            </>
          )}

          {shareResult.mode === 'REDIRECT' && (
            <>
              <div style={styles.successHeader}>
                📤 Ready to Post on LinkedIn
              </div>
              <p style={styles.modeNote}>
                The AI-generated post content has been copied to your clipboard.
              </p>
              <div style={styles.postPreview}>
                <pre style={styles.previewText}>{shareResult.post_content}</pre>
              </div>
              <div style={styles.buttonGroup}>
                <button onClick={openLinkedInShare} style={styles.linkedInBtn}>
                  🔗 Share on LinkedIn
                </button>
                <button onClick={openLinkedInJobs} style={styles.linkedInJobsBtn}>
                  💼 Post as Job
                </button>
                <button onClick={copyToClipboard} style={styles.copyBtn}>
                  📋 Copy Text
                </button>
              </div>
              <div style={styles.instructions}>
                <strong>Instructions:</strong>
                <ol style={styles.instructionsList}>
                  {shareResult.instructions?.map((step, idx) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ol>
              </div>
            </>
          )}

          {shareResult.mode === 'API' && (
            <>
              <div style={styles.successHeader}>
                ✅ Posted to LinkedIn!
              </div>
              <div style={styles.infoRow}>
                <span style={styles.label}>Status:</span>
                <span style={styles.statusBadge}>{shareResult.status}</span>
              </div>
              {shareResult.linkedin_url && (
                <a 
                  href={shareResult.linkedin_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  style={styles.viewPostLink}
                >
                  View Post on LinkedIn →
                </a>
              )}
            </>
          )}

          <button 
            onClick={() => setShareResult(null)} 
            style={styles.resetBtn}
          >
            Share Another Job
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.shareBox}>
        <h4 style={styles.title}>
          💼 Share on LinkedIn
        </h4>

        {error && (
          <div style={styles.errorBox}>
            ❌ {error}
          </div>
        )}

        {!postPreview ? (
          <button 
            onClick={generatePreview} 
            style={styles.previewBtn}
          >
            👁️ Preview AI Post
          </button>
        ) : (
          <div style={styles.postPreview}>
            <div style={styles.previewHeader}>
              <span>AI-Generated Post:</span>
              <button onClick={copyToClipboard} style={styles.smallCopyBtn}>
                📋 Copy
              </button>
            </div>
            <pre style={styles.previewText}>{postPreview}</pre>
          </div>
        )}

        <div style={styles.modeSelector}>
          <label style={styles.modeLabel}>Share Mode:</label>
          <select 
            value={mode} 
            onChange={(e) => setMode(e.target.value)}
            style={styles.modeSelect}
          >
            <option value="REDIRECT">Redirect (Manual Post)</option>
            <option value="MOCK">Mock (Demo)</option>
            <option value="API">API (Auto Post - Requires Login)</option>
          </select>
        </div>

        <button
          onClick={shareToLinkedIn}
          disabled={sharing}
          style={{
            ...styles.shareBtn,
            opacity: sharing ? 0.7 : 1,
            cursor: sharing ? 'not-allowed' : 'pointer',
          }}
        >
          {sharing ? '⏳ Sharing...' : '🚀 Share to LinkedIn'}
        </button>

        <p style={styles.helperText}>
          {mode === 'REDIRECT' && 'Opens LinkedIn with your post content ready to paste.'}
          {mode === 'MOCK' && 'Simulates LinkedIn API for demo purposes.'}
          {mode === 'API' && 'Posts directly to your LinkedIn feed (requires OAuth login).'}
        </p>
      </div>
    </div>
  );
};

const styles = {
  container: {
    marginTop: '16px',
  },
  shareBox: {
    padding: '16px',
    backgroundColor: '#f8fafc',
    border: '1px solid #e2e8f0',
    borderRadius: '12px',
  },
  title: {
    margin: '0 0 12px 0',
    fontSize: '16px',
    fontWeight: '600',
    color: '#1e293b',
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
  previewBtn: {
    width: '100%',
    padding: '10px',
    marginBottom: '12px',
    backgroundColor: '#f1f5f9',
    color: '#475569',
    border: '1px solid #cbd5e1',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
  },
  postPreview: {
    marginBottom: '12px',
    padding: '12px',
    backgroundColor: 'white',
    border: '1px solid #e2e8f0',
    borderRadius: '8px',
  },
  previewHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '8px',
    fontSize: '12px',
    fontWeight: '600',
    color: '#64748b',
  },
  previewText: {
    margin: 0,
    whiteSpace: 'pre-wrap',
    fontFamily: 'inherit',
    fontSize: '13px',
    lineHeight: '1.5',
    color: '#334155',
  },
  smallCopyBtn: {
    padding: '4px 8px',
    backgroundColor: 'transparent',
    color: '#2563eb',
    border: '1px solid #2563eb',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '11px',
  },
  modeSelector: {
    marginBottom: '12px',
  },
  modeLabel: {
    display: 'block',
    marginBottom: '4px',
    fontSize: '12px',
    fontWeight: '500',
    color: '#64748b',
  },
  modeSelect: {
    width: '100%',
    padding: '8px 12px',
    backgroundColor: 'white',
    border: '1px solid #cbd5e1',
    borderRadius: '6px',
    fontSize: '14px',
  },
  shareBtn: {
    width: '100%',
    padding: '12px',
    backgroundColor: '#0a66c2',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '15px',
    fontWeight: '600',
    transition: 'all 0.2s',
  },
  helperText: {
    marginTop: '8px',
    fontSize: '12px',
    color: '#64748b',
    textAlign: 'center',
  },
  resultBox: {
    padding: '20px',
    backgroundColor: '#f0fdf4',
    border: '1px solid #86efac',
    borderRadius: '12px',
  },
  successHeader: {
    marginBottom: '12px',
    fontSize: '18px',
    fontWeight: '600',
    color: '#166534',
  },
  modeNote: {
    marginBottom: '16px',
    padding: '10px',
    backgroundColor: '#fefce8',
    border: '1px solid #fde047',
    borderRadius: '6px',
    fontSize: '13px',
    color: '#854d0e',
  },
  infoRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '8px',
    fontSize: '14px',
  },
  label: {
    fontWeight: '500',
    color: '#166534',
  },
  value: {
    fontFamily: 'monospace',
    fontSize: '13px',
    color: '#15803d',
  },
  statusBadge: {
    padding: '4px 8px',
    backgroundColor: '#22c55e',
    color: 'white',
    borderRadius: '4px',
    fontSize: '12px',
    fontWeight: '600',
  },
  buttonGroup: {
    display: 'flex',
    gap: '8px',
    marginBottom: '16px',
    flexWrap: 'wrap',
  },
  linkedInBtn: {
    flex: 1,
    padding: '10px 16px',
    backgroundColor: '#0a66c2',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: '500',
  },
  linkedInJobsBtn: {
    flex: 1,
    padding: '10px 16px',
    backgroundColor: '#1e40af',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: '500',
  },
  copyBtn: {
    padding: '10px 16px',
    backgroundColor: '#f1f5f9',
    color: '#475569',
    border: '1px solid #cbd5e1',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: '500',
  },
  instructions: {
    padding: '12px',
    backgroundColor: 'white',
    borderRadius: '6px',
    fontSize: '13px',
  },
  instructionsList: {
    margin: '8px 0 0 0',
    paddingLeft: '20px',
  },
  viewPostLink: {
    display: 'inline-block',
    marginTop: '12px',
    padding: '10px 16px',
    backgroundColor: '#0a66c2',
    color: 'white',
    borderRadius: '6px',
    textDecoration: 'none',
    fontSize: '14px',
    fontWeight: '500',
  },
  resetBtn: {
    width: '100%',
    marginTop: '16px',
    padding: '10px',
    backgroundColor: 'transparent',
    color: '#475569',
    border: '1px solid #cbd5e1',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '13px',
  },
};

export default LinkedInShare;
