import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './CandidateList.css';

const FeedbackScorecard = ({ candidateId, onBack, onSubmit }) => {
  const [candidate, setCandidate] = useState(null);
  const [formData, setFormData] = useState({
    technical_skills: 0,
    communication: 0,
    problem_solving: 0,
    cultural_fit: 0,
    experience: 0,
    feedback: '',
    recommendation: 'Pending'
  });
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    if (candidateId) {
      fetchCandidate();
    }
  }, [candidateId]);

  const fetchCandidate = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/api/candidates/${candidateId}`);
      setCandidate(response.data);
    } catch (error) {
      console.error('Error fetching candidate:', error);
    }
  };

  const handleScoreChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: Math.min(5, Math.max(0, value))
    }));
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const getAverageScore = () => {
    const scores = [
      formData.technical_skills,
      formData.communication,
      formData.problem_solving,
      formData.cultural_fit,
      formData.experience
    ];
    const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
    return avg.toFixed(1);
  };

  const getRecommendation = () => {
    const avg = parseFloat(getAverageScore());
    if (avg >= 4.5) return 'Hire';
    if (avg >= 3.5) return 'Review';
    return 'No Hire';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const response = await axios.post('http://localhost:5000/api/feedback', {
        candidate_id: candidateId,
        feedback: formData.feedback,
        scores: {
          technical_skills: formData.technical_skills,
          communication: formData.communication,
          problem_solving: formData.problem_solving,
          cultural_fit: formData.cultural_fit,
          experience: formData.experience
        },
        recommendation: getRecommendation()
      });

      setSubmitted(true);
      if (onSubmit) {
        onSubmit(response.data.candidate);
      }

      setTimeout(() => {
        setSubmitted(false);
        if (onBack) onBack();
      }, 2000);
    } catch (error) {
      console.error('Error submitting feedback:', error);
      alert('Failed to submit feedback');
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="success-message">
        <h2 className="success-title">✅ Feedback Submitted!</h2>
        <p>Interview assessment recorded. Redirecting...</p>
      </div>
    );
  }

  if (!candidate) {
    return (
      <div className="candidate-list-container">
        <p>Loading candidate...</p>
      </div>
    );
  }

  const avgScore = parseFloat(getAverageScore());
  const recommendation = getRecommendation();

  return (
    <div className="candidate-list-container">
      <button onClick={onBack} className="back-button">
        ← Back
      </button>

      <div className="applications-card">
        <h2 className="candidate-list-title">📋 Digital Interview Scorecard</h2>

        <div style={{
          backgroundColor: '#f0fdf4',
          border: '2px solid #86efac',
          borderRadius: '8px',
          padding: '20px',
          marginBottom: '24px'
        }}>
          <h3 style={{ margin: '0 0 12px 0', color: '#166534' }}>👤 Candidate: {candidate.name}</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '12px' }}>
            <div>
              <p style={{ margin: '0', color: '#666', fontSize: '12px' }}>Position</p>
              <p style={{ margin: '4px 0 0 0', fontWeight: '600' }}>As Applied</p>
            </div>
            <div>
              <p style={{ margin: '0', color: '#666', fontSize: '12px' }}>Match Score</p>
              <p style={{ margin: '4px 0 0 0', fontWeight: '600' }}>{candidate.match_score}%</p>
            </div>
            <div>
              <p style={{ margin: '0', color: '#666', fontSize: '12px' }}>Experience</p>
              <p style={{ margin: '4px 0 0 0', fontWeight: '600' }}>{candidate.experience_years} years</p>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '20px',
            marginBottom: '24px'
          }}>
            {[
              { label: 'Technical Skills', field: 'technical_skills' },
              { label: 'Communication', field: 'communication' },
              { label: 'Problem Solving', field: 'problem_solving' },
              { label: 'Cultural Fit', field: 'cultural_fit' },
              { label: 'Relevant Experience', field: 'experience' }
            ].map(({ label, field }) => (
              <div key={field} style={{
                backgroundColor: '#f9fafb',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                padding: '16px'
              }}>
                <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151', display: 'block', marginBottom: '12px' }}>
                  {label}
                </label>
                <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                  {[1, 2, 3, 4, 5].map(score => (
                    <button
                      key={score}
                      type="button"
                      onClick={() => handleScoreChange(field, score)}
                      style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '50%',
                        border: '2px solid #e5e7eb',
                        backgroundColor: formData[field] >= score ? '#3b82f6' : 'white',
                        color: formData[field] >= score ? 'white' : '#666',
                        cursor: 'pointer',
                        fontWeight: '600',
                        transition: 'all 0.2s ease'
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.borderColor = '#3b82f6';
                        if (formData[field] < score) e.target.style.backgroundColor = '#dbeafe';
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.borderColor = '#e5e7eb';
                        if (formData[field] < score) e.target.style.backgroundColor = 'white';
                      }}
                    >
                      {score}
                    </button>
                  ))}
                </div>
                <p style={{
                  margin: '0',
                  fontSize: '12px',
                  color: '#666',
                  textAlign: 'center'
                }}>
                  {formData[field] === 0 ? 'Not rated' : `Score: ${formData[field]}/5`}
                </p>
              </div>
            ))}
          </div>

          <div className="form-group">
            <label className="form-label">Interview Feedback</label>
            <textarea
              name="feedback"
              value={formData.feedback}
              onChange={handleInputChange}
              placeholder="Share your detailed feedback about the candidate's performance during the interview..."
              className="form-textarea"
              rows="6"
            />
          </div>

          <div style={{
            backgroundColor: avgScore >= 4 ? '#d1fae5' : avgScore >= 3 ? '#fef3c7' : '#fee2e2',
            border: `2px solid ${avgScore >= 4 ? '#86efac' : avgScore >= 3 ? '#fcd34d' : '#fca5a5'}`,
            borderRadius: '8px',
            padding: '20px',
            marginBottom: '24px'
          }}>
            <h3 style={{
              margin: '0 0 12px 0',
              color: avgScore >= 4 ? '#166534' : avgScore >= 3 ? '#92400e' : '#991b1b'
            }}>
              📊 Assessment Summary
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '12px' }}>
              <div>
                <p style={{ margin: '0', color: '#666', fontSize: '12px' }}>Average Score</p>
                <p style={{
                  margin: '4px 0 0 0',
                  fontSize: '24px',
                  fontWeight: 'bold',
                  color: avgScore >= 4 ? '#047857' : avgScore >= 3 ? '#b45309' : '#dc2626'
                }}>
                  {getAverageScore()}/5
                </p>
              </div>
              <div>
                <p style={{ margin: '0', color: '#666', fontSize: '12px' }}>Recommendation</p>
                <p style={{
                  margin: '4px 0 0 0',
                  fontSize: '20px',
                  fontWeight: 'bold',
                  color: recommendation === 'Hire' ? '#047857' : recommendation === 'Review' ? '#b45309' : '#dc2626'
                }}>
                  {recommendation}
                </p>
              </div>
            </div>
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
            {submitting ? '⏳ Submitting...' : '✓ Submit Feedback & Assessment'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default FeedbackScorecard;
