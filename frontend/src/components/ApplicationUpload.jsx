import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './CandidateList.css';

const ApplicationUpload = ({ jobId, onBack, onApplicationSubmitted }) => {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(jobId || null);
  const [applicationForm, setApplicationForm] = useState({
    name: '',
    email: '',
    phone: '',
    resume: null,
  });
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [uploadedApplications, setUploadedApplications] = useState([]);
  const [fileName, setFileName] = useState('');

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/jobs');
      setJobs(response.data);
      if (response.data.length > 0 && !selectedJob) {
        setSelectedJob(response.data[0].id);
      }
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setFileName(file.name);
      setApplicationForm({
        ...applicationForm,
        resume: file,
      });
    }
  };

  const handleInputChange = (e) => {
    setApplicationForm({
      ...applicationForm,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmitApplication = async (e) => {
    e.preventDefault();

    if (!applicationForm.resume) {
      alert('Please select a resume file');
      return;
    }

    if (!selectedJob) {
      alert('Please select a job');
      return;
    }

    const formData = new FormData();
    formData.append('resume', applicationForm.resume);
    formData.append('job_id', selectedJob);
    formData.append('name', applicationForm.name || 'Candidate ' + (uploadedApplications.length + 1));
    formData.append('email', applicationForm.email || 'candidate@example.com');
    formData.append('phone', applicationForm.phone || '');

    setSubmitting(true);

    try {
      const response = await axios.post('http://localhost:5000/api/apply', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const newApp = response.data.candidate;
      setUploadedApplications([...uploadedApplications, newApp]);

      // Reset form
      setApplicationForm({
        name: '',
        email: '',
        phone: '',
        resume: null,
      });
      setFileName('');

      // Show success for 1 second then allow next upload
      setSuccess(true);
      setTimeout(() => setSuccess(false), 1500);

      if (onApplicationSubmitted) {
        onApplicationSubmitted(newApp);
      }
    } catch (error) {
      console.error('Error submitting application:', error);
      alert('Failed to submit application: ' + (error.response?.data?.error || error.message));
    } finally {
      setSubmitting(false);
    }
  };

  const selectedJobData = jobs.find(j => j.id === selectedJob);

  return (
    <div className="candidate-list-container">
      <button onClick={onBack} className="back-button">
        ← Back to Dashboard
      </button>

      <div className="applications-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <h2 className="candidate-list-title">📤 Submit Applications</h2>
          <span style={{ 
            backgroundColor: '#d1fae5', 
            color: '#047857', 
            padding: '8px 16px', 
            borderRadius: '20px',
            fontWeight: '600'
          }}>
            {uploadedApplications.length} Uploaded
          </span>
        </div>

        <div style={{ marginBottom: '32px' }}>
          <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151', display: 'block', marginBottom: '8px' }}>
            Select Job Opening:
          </label>
          <select
            value={selectedJob || ''}
            onChange={(e) => setSelectedJob(e.target.value)}
            className="form-input"
            style={{ maxWidth: '400px' }}
          >
            <option value="">-- Choose a job --</option>
            {jobs.map((job) => (
              <option key={job.id} value={job.id}>
                {job.title} ({job.applications || 0} applications)
              </option>
            ))}
          </select>
        </div>

        {selectedJobData && (
          <div style={{ 
            backgroundColor: '#eff6ff', 
            border: '2px solid #3b82f6', 
            borderRadius: '8px', 
            padding: '16px',
            marginBottom: '24px'
          }}>
            <h3 style={{ margin: '0 0 8px 0', color: '#1e40af' }}>
              📋 {selectedJobData.title}
            </h3>
            <p style={{ margin: '0', color: '#3730a3', fontSize: '14px' }}>
              Required Skills: {selectedJobData.requirements?.must_have?.join(', ') || 'Not specified'}
            </p>
          </div>
        )}

        <form onSubmit={handleSubmitApplication} className="job-form">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '16px' }}>
            <div className="form-group">
              <label className="form-label">Candidate Name (Optional)</label>
              <input
                type="text"
                name="name"
                value={applicationForm.name}
                onChange={handleInputChange}
                placeholder="e.g., John Doe"
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Email (Optional)</label>
              <input
                type="email"
                name="email"
                value={applicationForm.email}
                onChange={handleInputChange}
                placeholder="candidate@example.com"
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Phone (Optional)</label>
              <input
                type="tel"
                name="phone"
                value={applicationForm.phone}
                onChange={handleInputChange}
                placeholder="+1-234-567-8900"
                className="form-input"
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">
              📄 Resume (PDF) <span className="required">*</span>
            </label>
            <div style={{
              border: '2px dashed #9ca3af',
              borderRadius: '8px',
              padding: '32px',
              textAlign: 'center',
              backgroundColor: '#f9fafb',
              cursor: 'pointer',
              transition: 'all 0.3s ease'
            }}>
              <input
                type="file"
                name="resume"
                onChange={handleFileChange}
                accept=".pdf,.doc,.docx"
                className="form-input"
                style={{ display: 'none' }}
                id="resume-input"
              />
              <label htmlFor="resume-input" style={{ cursor: 'pointer' }}>
                <div style={{ fontSize: '24px', marginBottom: '8px' }}>📤</div>
                <p style={{ margin: '8px 0', color: '#6b7280', fontSize: '14px' }}>
                  {fileName ? (
                    <><strong style={{ color: '#10b981' }}>✓ </strong>{fileName}</>
                  ) : (
                    <>Click to upload or drag & drop</>
                  )}
                </p>
                <p style={{ margin: '4px 0', color: '#9ca3af', fontSize: '12px' }}>
                  PDF, DOC, or DOCX (Max 10MB)
                </p>
              </label>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
            <button
              type="submit"
              disabled={submitting || !selectedJob}
              className="btn-primary"
              style={{
                opacity: submitting || !selectedJob ? 0.6 : 1,
                cursor: submitting || !selectedJob ? 'not-allowed' : 'pointer'
              }}
            >
              {submitting ? '⏳ Uploading...' : success ? '✓ Uploaded!' : '📤 Submit Application'}
            </button>
            {success && (
              <span style={{ color: '#10b981', fontWeight: '600', display: 'flex', alignItems: 'center' }}>
                ✓ Application processed!
              </span>
            )}
          </div>
        </form>
      </div>

      {uploadedApplications.length > 0 && (
        <div className="applications-card" style={{ marginTop: '32px' }}>
          <h3 className="applications-title">📊 Uploaded Applications Summary</h3>
          <div style={{ overflowX: 'auto' }}>
            <table className="applications-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Skills Detected</th>
                  <th>Match Score</th>
                  <th>Priority</th>
                  <th>AI Recommendation</th>
                </tr>
              </thead>
              <tbody>
                {uploadedApplications.map((app, idx) => (
                  <tr key={app.id} className="application-row">
                    <td><strong>{app.name}</strong></td>
                    <td>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {app.skills?.slice(0, 3).map(skill => (
                          <span key={skill} className="skill-badge">{skill}</span>
                        ))}
                        {app.skills?.length > 3 && (
                          <span className="skill-badge">+{app.skills.length - 3}</span>
                        )}
                      </div>
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{
                          width: '100%',
                          maxWidth: '80px',
                          backgroundColor: '#e5e7eb',
                          borderRadius: '9999px',
                          height: '6px',
                          overflow: 'hidden'
                        }}>
                          <div
                            style={{
                              backgroundColor: app.match_score >= 75 ? '#10b981' : app.match_score >= 50 ? '#f59e0b' : '#ef4444',
                              height: '100%',
                              width: `${app.match_score}%`
                            }}
                          />
                        </div>
                        <strong>{app.match_score}%</strong>
                      </div>
                    </td>
                    <td>
                      <span style={{
                        padding: '4px 12px',
                        borderRadius: '20px',
                        fontSize: '12px',
                        fontWeight: '600',
                        backgroundColor: app.priority === 'High' ? '#dbeafe' : app.priority === 'Medium' ? '#fef3c7' : '#fee2e2',
                        color: app.priority === 'High' ? '#1e40af' : app.priority === 'Medium' ? '#92400e' : '#991b1b'
                      }}>
                        {app.priority}
                      </span>
                    </td>
                    <td>
                      <span style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        backgroundColor: '#f0fdf4',
                        color: '#166534',
                        fontWeight: '500'
                      }}>
                        {app.recommended_action}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApplicationUpload;
