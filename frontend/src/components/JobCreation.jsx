import React, { useState, useEffect } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import '../styles/JobCreation.css';
import LinkedInLogin from './LinkedInLogin';
import LinkedInShare from './LinkedInShare';

const JobCreation = ({ onBack }) => {
  const [formData, setFormData] = useState({
    title: '',
    department: '',
    location: '',
    experience_required: '',
    description: '',
    must_have_skills: '',
    good_to_have_skills: '',
    selected_platforms: [
      'company_portal', 'linkedin'
    ] // All platforms selected by default
  });

  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [createdJobId, setCreatedJobId] = useState(null);
  const [createdJobData, setCreatedJobData] = useState(null);
  const [suggestedSkills, setSuggestedSkills] = useState([]);
  const [linkedInConnected, setLinkedInConnected] = useState(false);
  const [linkedInPostResult, setLinkedInPostResult] = useState(null);
  const [autoPosting, setAutoPosting] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [skillsLoading, setSkillsLoading] = useState(false);

  // Check LinkedIn connection status on mount
  useEffect(() => {
    const checkLinkedInStatus = async () => {
      const sessionToken = localStorage.getItem('linkedin_session');
      if (sessionToken) {
        try {
          const response = await axios.get(`${API_BASE_URL}/api/auth/linkedin/status`, {
            headers: { 'X-LinkedIn-Session': sessionToken }
          });
          setLinkedInConnected(response.data.connected);
        } catch (err) {
          console.error('Error checking LinkedIn status:', err);
        }
      }
    };
    checkLinkedInStatus();
  }, []);

  const platformOptions = [
    { id: 'company_portal', name: 'Company Career Portal', icon: '🏢' },
    { id: 'linkedin', name: 'LinkedIn Jobs', icon: '💼' },
  ];

  // Fetch AI skill suggestions when job title changes (debounced)
  useEffect(() => {
    const timer = setTimeout(() => {
      if (formData.title.length >= 3) {
        fetchAISkillSuggestions(formData.title);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [formData.title]);

  const fetchAISkillSuggestions = async (jobTitle) => {
    setSkillsLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/ai/suggest-skills`, {
        job_title: jobTitle,
        current_skills: formData.must_have_skills.split(',').map(s => s.trim()).filter(Boolean)
      });
      setSuggestedSkills(response.data.skills || []);
    } catch (error) {
      console.error('Error fetching AI skills:', error);
      // Fallback to basic suggestions
      setSuggestedSkills(['Communication', 'Problem Solving', 'Team Work', 'Git', 'Agile']);
    } finally {
      setSkillsLoading(false);
    }
  };

  // Generate full job description using AI
  const generateAIJobDescription = async () => {
    if (!formData.title) {
      alert('Please enter a job title first');
      return;
    }
    
    setAiLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/ai/generate-job-description`, {
        job_title: formData.title,
        department: formData.department,
        location: formData.location
      });
      
      const aiData = response.data;
      
      // Auto-fill the form with AI-generated content
      setFormData(prev => ({
        ...prev,
        description: aiData.description || prev.description,
        experience_required: aiData.experience_required || prev.experience_required,
        must_have_skills: (aiData.must_have_skills || []).join(', ') || prev.must_have_skills,
        good_to_have_skills: (aiData.nice_to_have_skills || []).join(', ') || prev.good_to_have_skills
      }));
      
      // Update skill suggestions
      setSuggestedSkills([
        ...(aiData.must_have_skills || []),
        ...(aiData.nice_to_have_skills || [])
      ]);
      
    } catch (error) {
      console.error('Error generating AI job description:', error);
      alert('Failed to generate job description. Please try again.');
    } finally {
      setAiLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const togglePlatform = (platformId) => {
    const updated = formData.selected_platforms.includes(platformId)
      ? formData.selected_platforms.filter(p => p !== platformId)
      : [...formData.selected_platforms, platformId];
    
    setFormData({
      ...formData,
      selected_platforms: updated
    });
  };

  const addSkillSuggestion = (skill) => {
    const currentSkills = formData.must_have_skills
      .split(',')
      .map(s => s.trim())
      .filter(Boolean);
    
    if (!currentSkills.includes(skill)) {
      currentSkills.push(skill);
      setFormData({
        ...formData,
        must_have_skills: currentSkills.join(', ')
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    const mustHaveSkills = formData.must_have_skills
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);

    const goodToHaveSkills = formData.good_to_have_skills
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);

    const jobData = {
      ...formData,
      requirements: {
        must_have: mustHaveSkills,
        good_to_have: goodToHaveSkills,
      },
    };

    try {
      // Create the job first
      const response = await axios.post(`${API_BASE_URL}/api/jobs`, jobData);
      const jobId = response.data.id || response.data.job_id || Date.now();
      const applicationUrl = `${window.location.origin}/apply/${jobId}`;
      
      setCreatedJobId(jobId);
      const fullJobData = {
        ...response.data,
        id: jobId,
        application_url: applicationUrl
      };
      setCreatedJobData(fullJobData);
      setSuccess(true);

      // Auto-post to LinkedIn if LinkedIn is selected
      if (formData.selected_platforms.includes('linkedin')) {
        setAutoPosting(true);
        try {
          const sessionToken = localStorage.getItem('linkedin_session');
          const linkedInResponse = await axios.post(
            `${API_BASE_URL}/api/linkedin/auto-post`,
            { job_data: fullJobData },
            {
              headers: sessionToken ? { 'X-LinkedIn-Session': sessionToken } : {}
            }
          );
          setLinkedInPostResult(linkedInResponse.data);
          
          // If auto-posted successfully, show success
          if (linkedInResponse.data.auto_posted) {
            console.log('✅ Job automatically posted to LinkedIn!');
          } else {
            // Copy content to clipboard for manual posting
            if (linkedInResponse.data.post_content) {
              navigator.clipboard.writeText(linkedInResponse.data.post_content).catch(err => {
                console.warn('Clipboard copy failed:', err);
                // Content is still available in the UI
              });
            }
          }
        } catch (linkedInError) {
          console.error('LinkedIn auto-post error:', linkedInError);
          setLinkedInPostResult({
            success: false,
            auto_posted: false,
            error: 'Failed to post to LinkedIn'
          });
        } finally {
          setAutoPosting(false);
        }
      }
    } catch (error) {
      console.error('Error creating job:', error);
      alert('Failed to create job');
    } finally {
      setSubmitting(false);
    }
  };

  const getApplicationLink = () => {
    return `${window.location.origin}/apply/${createdJobId}`;
  };

  const copyLinkToClipboard = () => {
    navigator.clipboard.writeText(getApplicationLink()).catch(err => {
      console.error('Failed to copy to clipboard:', err);
      alert('Unable to copy to clipboard. Link: ' + getApplicationLink());
    });
    alert('Application link copied to clipboard!');
  };

  const openApplicationForm = () => {
    window.open(getApplicationLink(), '_blank');
  };

  if (success) {
    const applicationLink = getApplicationLink();
    
    return (
      <div className="job-creation-container">
        <div className="success-message" style={{ maxWidth: '700px', margin: '0 auto' }}>
          <h2 className="success-title">
            ✅ Job Created Successfully!
          </h2>
          <p style={{ marginBottom: '1.5rem' }}>Published to all selected platforms.</p>
          
          <div style={{ 
            backgroundColor: '#f0f9ff', 
            border: '1px solid #bae6fd', 
            borderRadius: '8px', 
            padding: '1.25rem',
            marginBottom: '1rem'
          }}>
            <p style={{ fontWeight: '600', color: '#0369a1', marginBottom: '0.75rem' }}>
              📋 Application Link (for development):
            </p>
            <div style={{ 
              backgroundColor: '#ffffff', 
              border: '1px solid #e0f2fe',
              borderRadius: '6px',
              padding: '0.75rem',
              wordBreak: 'break-all',
              fontSize: '0.875rem',
              color: '#0284c7',
              marginBottom: '1rem'
            }}>
              {applicationLink}
            </div>
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
              <button
                onClick={copyLinkToClipboard}
                style={{
                  padding: '0.5rem 1rem',
                  backgroundColor: '#2563eb',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  fontWeight: '500'
                }}
              >
                📋 Copy Link
              </button>
              <button
                onClick={openApplicationForm}
                style={{
                  padding: '0.5rem 1rem',
                  backgroundColor: '#059669',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  fontWeight: '500'
                }}
              >
                🔗 Open Form
              </button>
            </div>
          </div>
          
          {/* LinkedIn Auto-Post Result Section */}
          {formData.selected_platforms.includes('linkedin') && (
            <div style={{
              marginBottom: '1.5rem',
              padding: '1.25rem',
              backgroundColor: linkedInPostResult?.auto_posted ? '#f0fdf4' : '#eff6ff',
              border: `1px solid ${linkedInPostResult?.auto_posted ? '#86efac' : '#bfdbfe'}`,
              borderRadius: '12px'
            }}>
              <h3 style={{ 
                margin: '0 0 12px 0', 
                fontSize: '16px', 
                fontWeight: '600', 
                color: linkedInPostResult?.auto_posted ? '#166534' : '#0a66c2' 
              }}>
                💼 LinkedIn Post Status
              </h3>
              
              {autoPosting ? (
                <div style={{ textAlign: 'center', padding: '20px' }}>
                  <span style={{ fontSize: '24px' }}>⏳</span>
                  <p style={{ margin: '8px 0 0', color: '#0369a1' }}>Posting to LinkedIn...</p>
                </div>
              ) : linkedInPostResult?.auto_posted ? (
                <div>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    marginBottom: '12px',
                    color: '#166534'
                  }}>
                    <span style={{ fontSize: '20px' }}>✅</span>
                    <strong>Job automatically posted to LinkedIn!</strong>
                  </div>
                  {linkedInPostResult.linkedin_url && (
                    <a 
                      href={linkedInPostResult.linkedin_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        display: 'inline-block',
                        padding: '8px 16px',
                        backgroundColor: '#0a66c2',
                        color: 'white',
                        borderRadius: '6px',
                        textDecoration: 'none',
                        fontSize: '14px',
                        fontWeight: '500'
                      }}
                    >
                      View Post on LinkedIn →
                    </a>
                  )}
                </div>
              ) : linkedInPostResult ? (
                <div>
                  <p style={{ margin: '0 0 12px', color: '#0369a1' }}>
                    📋 Post content is ready! Click below to share on LinkedIn.
                  </p>
                  <p style={{ margin: '0 0 12px', fontSize: '13px', color: '#64748b' }}>
                    (Content has been copied to your clipboard)
                  </p>
                  
                  {/* Show post preview */}
                  {linkedInPostResult.post_content && (
                    <div style={{
                      maxHeight: '200px',
                      overflow: 'auto',
                      padding: '12px',
                      backgroundColor: 'white',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      marginBottom: '12px',
                      fontSize: '12px',
                      whiteSpace: 'pre-wrap',
                      fontFamily: 'inherit'
                    }}>
                      {linkedInPostResult.post_content}
                    </div>
                  )}
                  
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(linkedInPostResult.post_content);
                        window.open('https://www.linkedin.com/feed/?shareActive=true', '_blank');
                      }}
                      style={{
                        padding: '10px 20px',
                        backgroundColor: '#0a66c2',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: '500',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px'
                      }}
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
                        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                      </svg>
                      Post on LinkedIn Now
                    </button>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(linkedInPostResult.post_content);
                        alert('✅ Post content copied to clipboard!');
                      }}
                      style={{
                        padding: '10px 16px',
                        backgroundColor: 'white',
                        color: '#0a66c2',
                        border: '1px solid #0a66c2',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: '500'
                      }}
                    >
                      📋 Copy Post
                    </button>
                  </div>
                </div>
              ) : (
                <div>
                  {/* LinkedIn Login for auto-posting */}
                  <p style={{ margin: '0 0 12px', fontSize: '14px', color: '#475569' }}>
                    Connect your LinkedIn account for automatic posting:
                  </p>
                  <LinkedInLogin 
                    onLoginSuccess={(profile) => {
                      setLinkedInConnected(true);
                    }}
                    onLogout={() => setLinkedInConnected(false)}
                  />
                </div>
              )}
            </div>
          )}
          
          <button
            onClick={onBack}
            style={{
              padding: '0.625rem 1.25rem',
              backgroundColor: '#f3f4f6',
              color: '#374151',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: '500'
            }}
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="job-creation-container">
      <button
        onClick={onBack}
        className="back-button"
      >
        ← Back
      </button>

      <div className="job-creation-card">
        <h2 className="job-creation-title">
          📝 Create New Job Opening
        </h2>

        <form onSubmit={handleSubmit} className="job-form">
          <div className="form-group">
            <label className="form-label">
              Job Title <span className="required">*</span>
            </label>
            <div style={{ display: 'flex', gap: '12px' }}>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="e.g., Senior Python Developer"
                className="form-input"
                style={{ flex: 1 }}
                required
              />
              <button
                type="button"
                onClick={generateAIJobDescription}
                disabled={aiLoading || !formData.title}
                style={{
                  padding: '12px 20px',
                  backgroundColor: aiLoading ? '#9ca3af' : '#8b5cf6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: aiLoading ? 'wait' : 'pointer',
                  fontSize: '14px',
                  fontWeight: '600',
                  whiteSpace: 'nowrap',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                {aiLoading ? '⏳ Generating...' : '🤖 Generate with AI'}
              </button>
            </div>
            <p style={{ margin: '8px 0 0', fontSize: '12px', color: '#6b7280' }}>
              💡 Enter a job title and click "Generate with AI" to auto-fill the description and skills
            </p>
          </div>

          {(suggestedSkills.length > 0 || skillsLoading) && (
            <div style={{
              backgroundColor: '#fef3c7',
              border: '2px solid #fbbf24',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '16px'
            }}>
              <p style={{ margin: '0 0 12px 0', fontWeight: '600', color: '#92400e' }}>
                🤖 AI Suggested Skills for this role: {skillsLoading && <span style={{ fontWeight: 'normal' }}>Loading...</span>}
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {suggestedSkills.map(skill => (
                  <button
                    key={skill}
                    type="button"
                    onClick={() => addSkillSuggestion(skill)}
                    style={{
                      padding: '6px 12px',
                      backgroundColor: 'white',
                      border: '1px solid #fbbf24',
                      borderRadius: '20px',
                      cursor: 'pointer',
                      fontSize: '13px',
                      transition: 'all 0.2s ease',
                      color: '#92400e'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.backgroundColor = '#fbbf24';
                      e.target.style.color = 'white';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.backgroundColor = 'white';
                      e.target.style.color = '#92400e';
                    }}
                  >
                    + {skill}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">
                Department <span className="required">*</span>
              </label>
              <input
                type="text"
                name="department"
                value={formData.department}
                onChange={handleChange}
                placeholder="e.g., Engineering"
                className="form-input"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                Location <span className="required">*</span>
              </label>
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="e.g., Bangalore / Hybrid"
                className="form-input"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">
              Experience Required <span className="required">*</span>
            </label>
            <input
              type="text"
              name="experience_required"
              value={formData.experience_required}
              onChange={handleChange}
              placeholder="e.g., 5–7 years"
              className="form-input"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              Job Description <span className="required">*</span>
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows="6"
              placeholder="Describe the role, responsibilities, and expectations..."
              className="form-textarea"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              Must-Have Skills <span className="required">*</span> (comma-separated)
            </label>
            <input
              type="text"
              name="must_have_skills"
              value={formData.must_have_skills}
              onChange={handleChange}
              placeholder="python, sql, aws"
              className="form-input"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              Good-to-Have Skills (comma-separated)
            </label>
            <input
              type="text"
              name="good_to_have_skills"
              value={formData.good_to_have_skills}
              onChange={handleChange}
              placeholder="docker, kubernetes, fastapi"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              📢 Publish To Platforms <span className="required">*</span>
            </label>
            <p style={{ fontSize: '13px', color: '#6b7280', marginBottom: '12px' }}>
              Select which job boards to publish this opening to:
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '12px' }}>
              {platformOptions.map(platform => (
                <label
                  key={platform.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '12px',
                    border: formData.selected_platforms.includes(platform.id) 
                      ? '2px solid #3b82f6' 
                      : '2px solid #e5e7eb',
                    borderRadius: '8px',
                    backgroundColor: formData.selected_platforms.includes(platform.id)
                      ? '#eff6ff'
                      : '#f9fafb',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <input
                    type="checkbox"
                    checked={formData.selected_platforms.includes(platform.id)}
                    onChange={() => togglePlatform(platform.id)}
                    style={{ marginRight: '8px', cursor: 'pointer' }}
                  />
                  <span>
                    <span style={{ marginRight: '6px' }}>{platform.icon}</span>
                    {platform.name}
                  </span>
                </label>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting || formData.selected_platforms.length === 0}
            className="btn-submit"
            style={{ width: '100%' }}
          >
            {submitting ? '⏳ Publishing...' : '🚀 Create & Publish Job'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default JobCreation;
