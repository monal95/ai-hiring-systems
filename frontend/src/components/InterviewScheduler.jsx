import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './InterviewScheduler.css';

function InterviewScheduler({ onBack }) {
  const [candidates, setCandidates] = useState([]);
  const [formData, setFormData] = useState({
    candidateId: '',
    interviewDate: '',
    interviewTime: '',
    interviewType: 'video',
    interviewers: [],
    notes: ''
  });
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  const interviewers = ['Sarah Johnson', 'Mike Chen', 'Emily Rodriguez', 'David Kumar'];

  useEffect(() => {
    fetchCandidates();
  }, []);

  const fetchCandidates = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/candidates');
      setCandidates(response.data.filter(c => c.status !== 'Rejected'));
    } catch (err) {
      console.error('Error fetching candidates:', err);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    if (name === 'candidateId') {
      const candidate = candidates.find(c => c.id === value);
      setSelectedCandidate(candidate);
    }
  };

  const handleInterviewerToggle = (interviewer) => {
    setFormData(prev => ({
      ...prev,
      interviewers: prev.interviewers.includes(interviewer)
        ? prev.interviewers.filter(i => i !== interviewer)
        : [...prev.interviewers, interviewer]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.candidateId || !formData.interviewDate || !formData.interviewTime) {
      setError('Please fill in all required fields');
      return;
    }

    if (formData.interviewers.length === 0) {
      setError('Please select at least one interviewer');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await axios.post('http://localhost:5000/api/schedule-interview', {
        candidate_id: formData.candidateId,
        slots: [`${formData.interviewDate}T${formData.interviewTime}`],
        interviewers: formData.interviewers
      });

      setSubmitted(true);
      setTimeout(() => {
        setSubmitted(false);
        if (onBack) onBack();
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to schedule interview');
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="success-message" style={{ maxWidth: '800px', margin: '0 auto' }}>
        <h2 className="success-title">✅ Interview Scheduled!</h2>
        <p>Calendar invites sent to interviewers and candidate. Redirecting...</p>
      </div>
    );
  }

  return (
    <div className="interview-scheduler-container">
      {onBack && (
        <button 
          onClick={onBack}
          className="back-button"
        >
          ← Back
        </button>
      )}
      
      <div className="interview-card">
        <h1 className="interview-title">📅 Schedule Interview</h1>

        {error && (
          <div style={{
            backgroundColor: '#fee2e2',
            border: '2px solid #fca5a5',
            borderRadius: '8px',
            padding: '12px 16px',
            marginBottom: '24px',
            color: '#991b1b'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="interview-form">
          <div className="form-group">
            <label className="form-label">
              Select Candidate <span className="required">*</span>
            </label>
            <select
              name="candidateId"
              value={formData.candidateId}
              onChange={handleChange}
              className="form-input"
              required
            >
              <option value="">-- Choose a candidate --</option>
              {candidates.map((candidate) => (
                <option key={candidate.id} value={candidate.id}>
                  {candidate.name} - {candidate.priority} Priority ({candidate.match_score}% match)
                </option>
              ))}
            </select>
          </div>

          {selectedCandidate && (
            <div style={{
              backgroundColor: '#f0fdf4',
              border: '2px solid #86efac',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '24px'
            }}>
              <h3 style={{ margin: '0 0 12px 0', color: '#166534' }}>📋 Candidate Details</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
                <div>
                  <p style={{ margin: '0', color: '#666', fontSize: '12px' }}>Email</p>
                  <p style={{ margin: '4px 0 0 0', fontWeight: '600' }}>{selectedCandidate.email}</p>
                </div>
                <div>
                  <p style={{ margin: '0', color: '#666', fontSize: '12px' }}>Phone</p>
                  <p style={{ margin: '4px 0 0 0', fontWeight: '600' }}>{selectedCandidate.phone || 'Not provided'}</p>
                </div>
                <div>
                  <p style={{ margin: '0', color: '#666', fontSize: '12px' }}>Years of Experience</p>
                  <p style={{ margin: '4px 0 0 0', fontWeight: '600' }}>{selectedCandidate.experience_years} years</p>
                </div>
              </div>
            </div>
          )}

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">
                Interview Date <span className="required">*</span>
              </label>
              <input
                type="date"
                name="interviewDate"
                value={formData.interviewDate}
                onChange={handleChange}
                className="form-input"
                required
                min={new Date().toISOString().split('T')[0]}
              />
            </div>
            <div className="form-group">
              <label className="form-label">
                Interview Time <span className="required">*</span>
              </label>
              <input
                type="time"
                name="interviewTime"
                value={formData.interviewTime}
                onChange={handleChange}
                className="form-input"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Interview Type</label>
            <select
              name="interviewType"
              value={formData.interviewType}
              onChange={handleChange}
              className="form-input"
            >
              <option value="phone">☎️ Phone Screen</option>
              <option value="video">📹 Video Call</option>
              <option value="in-person">🏢 In-Person</option>
              <option value="technical">💻 Technical Interview</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">
              Select Interviewers <span className="required">*</span>
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', marginTop: '12px' }}>
              {interviewers.map((interviewer) => (
                <label key={interviewer} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '12px',
                  border: '2px solid #e5e7eb',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  backgroundColor: formData.interviewers.includes(interviewer) ? '#dbeafe' : 'white',
                  borderColor: formData.interviewers.includes(interviewer) ? '#3b82f6' : '#e5e7eb'
                }}>
                  <input
                    type="checkbox"
                    checked={formData.interviewers.includes(interviewer)}
                    onChange={() => handleInterviewerToggle(interviewer)}
                    style={{ cursor: 'pointer' }}
                  />
                  <span style={{ fontWeight: '500' }}>{interviewer}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Additional Notes (Optional)</label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              placeholder="e.g., Focus on system design, ask about previous projects..."
              className="form-textarea"
              rows="4"
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="btn-primary"
            style={{
              width: '100%',
              padding: '12px 24px',
              cursor: submitting ? 'not-allowed' : 'pointer',
              opacity: submitting ? 0.6 : 1
            }}
          >
            {submitting ? '⏳ Scheduling...' : '📤 Schedule & Send Invitations'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default InterviewScheduler;
             