import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './OfferManagement.css';

function OfferManagement({ onBack }) {
  const [candidates, setCandidates] = useState([]);
  const [offers, setOffers] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [formData, setFormData] = useState({
    candidateId: '',
    salary: '',
    joining_date: '',
    benefits: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [candidatesRes, offersRes] = await Promise.all([
        axios.get('http://localhost:5000/api/candidates?filter=ready_for_offer'),
        axios.get('http://localhost:5000/api/candidates')
      ]);
      
      const readyCandidates = offersRes.data.filter(c => 
        c.status === 'Ready for Offer' || c.interview_score >= 70
      );
      setCandidates(readyCandidates);

      const offersData = offersRes.data
        .filter(c => c.offer)
        .map(c => c.offer);
      setOffers(offersData);
    } catch (error) {
      console.error('Error fetching data:', error);
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const response = await axios.post('http://localhost:5000/api/generate-offer', {
        candidate_id: formData.candidateId,
        salary: parseInt(formData.salary),
        joining_date: formData.joining_date
      });

      setOffers([...offers, response.data.offer]);
      setShowForm(false);
      setFormData({
        candidateId: '',
        salary: '',
        joining_date: '',
        benefits: ''
      });
      setSelectedCandidate(null);
    } catch (error) {
      console.error('Error creating offer:', error);
      alert('Failed to create offer');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="offer-management-container">
      {onBack && (
        <button 
          onClick={onBack}
          className="back-button"
        >
          ← Back
        </button>
      )}

      <div className="offer-card">
        <div className="offer-header">
          <h1 className="offer-title">📜 Offer Management</h1>
          <button 
            className="btn-primary"
            onClick={() => setShowForm(!showForm)}
            style={{ whiteSpace: 'nowrap' }}
          >
            {showForm ? '✕ Cancel' : '✎ Create New Offer'}
          </button>
        </div>

        {showForm && (
          <form onSubmit={handleSubmit} className="offer-form" style={{
            backgroundColor: '#f3f4f6',
            border: '2px solid #dbeafe',
            borderRadius: '8px',
            padding: '24px',
            marginBottom: '24px'
          }}>
            <h3 style={{ marginTop: 0, color: '#1e40af' }}>Generate Job Offer</h3>

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
                    {candidate.name} - {candidate.priority} Priority
                  </option>
                ))}
              </select>
            </div>

            {selectedCandidate && (
              <div style={{
                backgroundColor: 'white',
                border: '2px solid #10b981',
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '24px'
              }}>
                <h4 style={{ margin: '0 0 12px 0', color: '#047857' }}>✓ Candidate Profile</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
                  <div>
                    <p style={{ margin: '0', color: '#666', fontSize: '12px' }}>Email</p>
                    <p style={{ margin: '4px 0 0 0', fontWeight: '600' }}>{selectedCandidate.email}</p>
                  </div>
                  <div>
                    <p style={{ margin: '0', color: '#666', fontSize: '12px' }}>Phone</p>
                    <p style={{ margin: '4px 0 0 0', fontWeight: '600' }}>{selectedCandidate.phone}</p>
                  </div>
                  <div>
                    <p style={{ margin: '0', color: '#666', fontSize: '12px' }}>Match Score</p>
                    <p style={{ margin: '4px 0 0 0', fontWeight: '600' }}>{selectedCandidate.match_score}%</p>
                  </div>
                  <div>
                    <p style={{ margin: '0', color: '#666', fontSize: '12px' }}>Interview Score</p>
                    <p style={{ margin: '4px 0 0 0', fontWeight: '600' }}>{selectedCandidate.interview_score || 'N/A'}</p>
                  </div>
                </div>
              </div>
            )}

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">
                  Annual Salary (USD) <span className="required">*</span>
                </label>
                <input
                  type="number"
                  name="salary"
                  value={formData.salary}
                  onChange={handleChange}
                  placeholder="e.g., 120000"
                  className="form-input"
                  required
                  min="0"
                />
              </div>

              <div className="form-group">
                <label className="form-label">
                  Joining Date <span className="required">*</span>
                </label>
                <input
                  type="date"
                  name="joining_date"
                  value={formData.joining_date}
                  onChange={handleChange}
                  className="form-input"
                  required
                />
              </div>
            </div>

            <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
              <button 
                type="submit" 
                className="btn-primary"
                disabled={submitting}
                style={{
                  cursor: submitting ? 'not-allowed' : 'pointer',
                  opacity: submitting ? 0.6 : 1
                }}
              >
                {submitting ? '⏳ Generating...' : '📄 Generate & Send Offer'}
              </button>
            </div>
          </form>
        )}
      </div>

      <div className="offer-card">
        <h3 className="offers-title">📋 Active Offers</h3>
        {offers.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table className="offers-table">
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Position</th>
                  <th>Salary</th>
                  <th>Joining Date</th>
                  <th>Status</th>
                  <th>Sent Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {offers.map(offer => (
                  <tr key={offer.id} style={{ borderBottom: '1px solid #e5e7eb' }}>
                    <td style={{ fontWeight: '600' }}>{offer.candidate_name}</td>
                    <td>{offer.job_title}</td>
                    <td style={{ fontWeight: '600', color: '#10b981' }}>
                      ${(offer.salary || 0).toLocaleString()}
                    </td>
                    <td>{offer.joining_date || 'TBD'}</td>
                    <td>
                      <span style={{
                        padding: '4px 12px',
                        borderRadius: '20px',
                        fontSize: '12px',
                        fontWeight: '600',
                        backgroundColor: offer.status === 'Accepted' ? '#d1fae5' : '#fee2e2',
                        color: offer.status === 'Accepted' ? '#047857' : '#991b1b'
                      }}>
                        {offer.status}
                      </span>
                    </td>
                    <td>{offer.sent_at ? new Date(offer.sent_at).toLocaleDateString() : 'Today'}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button style={{
                          padding: '4px 8px',
                          backgroundColor: '#3b82f6',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '12px'
                        }}>
                          View
                        </button>
                        <button style={{
                          padding: '4px 8px',
                          backgroundColor: '#f59e0b',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '12px'
                        }}>
                          Track
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ color: '#7f8c8d', textAlign: 'center', padding: '24px' }}>No offers generated yet</p>
        )}
      </div>

      <div className="offer-card" style={{ marginTop: '24px' }}>
        <h3 className="offers-title">📊 Engagement Tracking</h3>
        <div style={{ 
          backgroundColor: '#fef3c7',
          border: '2px solid #fbbf24',
          borderRadius: '8px',
          padding: '20px'
        }}>
          <p style={{ margin: '0 0 12px 0', color: '#92400e', fontWeight: '600' }}>
            🎯 Track candidate engagement with offers
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <div style={{ backgroundColor: 'white', padding: '12px', borderRadius: '6px' }}>
              <p style={{ margin: '0', color: '#666', fontSize: '12px' }}>Email Opens</p>
              <p style={{ margin: '4px 0 0 0', fontSize: '20px', fontWeight: 'bold', color: '#f59e0b' }}>85%</p>
            </div>
            <div style={{ backgroundColor: 'white', padding: '12px', borderRadius: '6px' }}>
              <p style={{ margin: '0', color: '#666', fontSize: '12px' }}>Portal Logins</p>
              <p style={{ margin: '4px 0 0 0', fontSize: '20px', fontWeight: 'bold', color: '#f59e0b' }}>5</p>
            </div>
            <div style={{ backgroundColor: 'white', padding: '12px', borderRadius: '6px' }}>
              <p style={{ margin: '0', color: '#666', fontSize: '12px' }}>Engagement Risk</p>
              <p style={{ margin: '4px 0 0 0', fontSize: '20px', fontWeight: 'bold', color: '#10b981' }}>Low</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default OfferManagement;
