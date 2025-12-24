import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './JobApplicationForm.css';

const JobApplicationForm = ({ jobId }) => {
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    // Must-have fields
    fullName: '',
    email: '',
    phone: '',
    currentLocation: '',
    totalExperience: '',
    expectedSalary: '',
    noticePeriod: '',
    resume: null,
    // Highly recommended fields
    currentEmployer: '',
    currentDesignation: '',
    workExperience: '',
    education: '',
    linkedinProfile: '',
    keySkills: ''
  });

  useEffect(() => {
    fetchJobDetails();
  }, [jobId]);

  const fetchJobDetails = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/api/jobs/${jobId}`);
      setJob(response.data);
      setLoading(false);
    } catch (err) {
      setError('Job not found or has been closed.');
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        alert('File size should be less than 5MB');
        return;
      }
      setFormData(prev => ({
        ...prev,
        resume: file
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const submitData = new FormData();
      
      // Append all form fields
      Object.keys(formData).forEach(key => {
        if (key === 'resume' && formData[key]) {
          submitData.append('resume', formData[key]);
        } else if (formData[key]) {
          submitData.append(key, formData[key]);
        }
      });
      
      submitData.append('jobId', jobId);
      submitData.append('appliedAt', new Date().toISOString());

      await axios.post('http://localhost:5000/api/applications/public', submitData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setSubmitted(true);
    } catch (err) {
      alert('Failed to submit application. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="application-form-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading job details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="application-form-page">
        <div className="error-container">
          <h2>⚠️ {error}</h2>
          <p>Please check the link or contact the recruiter.</p>
        </div>
      </div>
    );
  }

  if (submitted) {
    return (
      <div className="application-form-page">
        <div className="success-container">
          <div className="success-icon">✅</div>
          <h2>Application Submitted Successfully!</h2>
          <p>Thank you for applying to <strong>{job?.title}</strong>.</p>
          <p>Our team will review your application and get back to you soon.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="application-form-page">
      <div className="application-form-container">
        {/* Job Header */}
        <div className="job-header">
          <h1>{job?.title}</h1>
          <div className="job-meta">
            <span>📍 {job?.location}</span>
            <span>🏢 {job?.department}</span>
            <span>💼 {job?.experience_required}</span>
          </div>
        </div>

        {/* Application Form */}
        <form onSubmit={handleSubmit} className="application-form">
          {/* Must-Have Section */}
          <div className="form-section">
            <h3 className="section-title">
              <span className="required-badge">Required</span>
              Personal Information
            </h3>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">
                  Full Name <span className="required">*</span>
                </label>
                <input
                  type="text"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleChange}
                  placeholder="Enter your full name"
                  className="form-input"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">
                  Email <span className="required">*</span>
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="your.email@example.com"
                  className="form-input"
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">
                  Phone <span className="required">*</span>
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="+91 9876543210"
                  className="form-input"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">
                  Current Location <span className="required">*</span>
                </label>
                <input
                  type="text"
                  name="currentLocation"
                  value={formData.currentLocation}
                  onChange={handleChange}
                  placeholder="City, Country"
                  className="form-input"
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">
                  Total Experience <span className="required">*</span>
                </label>
                <select
                  name="totalExperience"
                  value={formData.totalExperience}
                  onChange={handleChange}
                  className="form-select"
                  required
                >
                  <option value="">Select experience</option>
                  <option value="0-1 years">0-1 years</option>
                  <option value="1-2 years">1-2 years</option>
                  <option value="2-3 years">2-3 years</option>
                  <option value="3-5 years">3-5 years</option>
                  <option value="5-7 years">5-7 years</option>
                  <option value="7-10 years">7-10 years</option>
                  <option value="10+ years">10+ years</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">
                  Expected Salary (LPA) <span className="required">*</span>
                </label>
                <input
                  type="text"
                  name="expectedSalary"
                  value={formData.expectedSalary}
                  onChange={handleChange}
                  placeholder="e.g., 15-18 LPA"
                  className="form-input"
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">
                  Notice Period <span className="required">*</span>
                </label>
                <select
                  name="noticePeriod"
                  value={formData.noticePeriod}
                  onChange={handleChange}
                  className="form-select"
                  required
                >
                  <option value="">Select notice period</option>
                  <option value="Immediate">Immediate</option>
                  <option value="15 days">15 days</option>
                  <option value="30 days">30 days</option>
                  <option value="45 days">45 days</option>
                  <option value="60 days">60 days</option>
                  <option value="90 days">90 days</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">
                  Resume <span className="required">*</span>
                </label>
                <input
                  type="file"
                  name="resume"
                  onChange={handleFileChange}
                  accept=".pdf,.doc,.docx"
                  className="form-input file-input"
                  required
                />
                <span className="form-hint">PDF, DOC, DOCX (Max 5MB)</span>
              </div>
            </div>
          </div>

          {/* Highly Recommended Section */}
          <div className="form-section">
            <h3 className="section-title">
              <span className="recommended-badge">Recommended</span>
              Professional Details
            </h3>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Current Employer</label>
                <input
                  type="text"
                  name="currentEmployer"
                  value={formData.currentEmployer}
                  onChange={handleChange}
                  placeholder="Company name"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Current Designation</label>
                <input
                  type="text"
                  name="currentDesignation"
                  value={formData.currentDesignation}
                  onChange={handleChange}
                  placeholder="Your job title"
                  className="form-input"
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Work Experience Details</label>
              <textarea
                name="workExperience"
                value={formData.workExperience}
                onChange={handleChange}
                placeholder="Brief description of your work experience, projects, and achievements..."
                className="form-textarea"
                rows="4"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Education Details</label>
              <textarea
                name="education"
                value={formData.education}
                onChange={handleChange}
                placeholder="Degree, University, Year of passing..."
                className="form-textarea"
                rows="3"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">LinkedIn Profile</label>
                <input
                  type="url"
                  name="linkedinProfile"
                  value={formData.linkedinProfile}
                  onChange={handleChange}
                  placeholder="https://linkedin.com/in/yourprofile"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Key Skills</label>
                <input
                  type="text"
                  name="keySkills"
                  value={formData.keySkills}
                  onChange={handleChange}
                  placeholder="Python, React, AWS, etc."
                  className="form-input"
                />
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={submitting}
            className="submit-btn"
          >
            {submitting ? '⏳ Submitting...' : '🚀 Submit Application'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default JobApplicationForm;
