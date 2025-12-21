import React, { useState } from 'react';
import axios from 'axios';
import './JobCreation.css';

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
      'company_portal', 'linkedin', 'indeed', 'naukri', 'internal_referral'
    ] // All platforms selected by default
  });

  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [suggestedSkills, setSuggestedSkills] = useState([]);

  const platformOptions = [
    { id: 'company_portal', name: 'Company Career Portal', icon: '🏢' },
    { id: 'linkedin', name: 'LinkedIn Jobs', icon: '💼' },
    { id: 'indeed', name: 'Indeed', icon: '📋' },
    { id: 'naukri', name: 'Naukri.com', icon: '🇮🇳' },
    { id: 'internal_referral', name: 'Internal Referral Portal', icon: '👥' }
  ];

  // AI Skill suggestions based on job title
  const skillSuggestions = {
    'python': ['Django', 'FastAPI', 'Flask', 'Pandas', 'NumPy', 'Scikit-learn'],
    'java': ['Spring', 'Hibernate', 'Maven', 'Gradle', 'JUnit', 'Mockito'],
    'javascript': ['React', 'Node.js', 'Express', 'Vue.js', 'TypeScript'],
    'senior': ['System Design', 'Team Leadership', 'Code Review', 'Architecture'],
    'developer': ['Git', 'Docker', 'CI/CD', 'Agile', 'Testing'],
    'devops': ['Kubernetes', 'Docker', 'AWS', 'Jenkins', 'Terraform', 'Ansible'],
    'backend': ['REST API', 'Database Design', 'Microservices', 'Message Queues'],
    'frontend': ['HTML5', 'CSS3', 'Responsive Design', 'UI/UX', 'Accessibility'],
    'ml': ['TensorFlow', 'PyTorch', 'Machine Learning', 'Deep Learning', 'NLP'],
    'data': ['SQL', 'Data Analysis', 'Data Visualization', 'ETL', 'Big Data'],
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });

    // Generate skill suggestions based on title
    if (name === 'title') {
      const titleLower = value.toLowerCase();
      let suggested = [];
      for (const [keyword, skills] of Object.entries(skillSuggestions)) {
        if (titleLower.includes(keyword)) {
          suggested = [...suggested, ...skills];
        }
      }
      // Add common tech skills for all roles
      suggested = [...new Set([...suggested, 'Git', 'Agile', 'Communication', 'Problem Solving'])];
      setSuggestedSkills(suggested);
    }
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
      await axios.post('http://localhost:5000/api/jobs', jobData);
      setSuccess(true);
      setTimeout(() => onBack(), 2000);
    } catch (error) {
      console.error('Error creating job:', error);
      alert('Failed to create job');
    } finally {
      setSubmitting(false);
    }
  };

  if (success) {
    return (
      <div className="success-message">
        <h2 className="success-title">
          ✅ Job Created Successfully!
        </h2>
        <p>Published to all platforms. Redirecting...</p>
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
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="e.g., Senior Python Developer"
              className="form-input"
              required
            />
          </div>

          {suggestedSkills.length > 0 && (
            <div style={{
              backgroundColor: '#fef3c7',
              border: '2px solid #fbbf24',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '16px'
            }}>
              <p style={{ margin: '0 0 12px 0', fontWeight: '600', color: '#92400e' }}>
                🤖 AI Suggested Skills for this role:
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
