import React, { useState, useEffect } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import '../styles/Dashboard.css';

const JobsList = ({ onNavigate, onSelectJob }) => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [jobAnalytics, setJobAnalytics] = useState({});

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/jobs`);
      setJobs(response.data);
      setError(null);
      
      // Fetch analytics for each job
      response.data.forEach(job => {
        fetchJobAnalytics(job.id);
      });
    } catch (error) {
      console.error('Error fetching jobs:', error);
      setError('Unable to fetch jobs');
    } finally {
      setLoading(false);
    }
  };

  const fetchJobAnalytics = async (jobId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/jobs/${jobId}/analytics`);
      setJobAnalytics(prev => ({
        ...prev,
        [jobId]: response.data
      }));
    } catch (error) {
      console.error(`Error fetching analytics for ${jobId}:`, error);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <div className="loading-message">Loading Jobs...</div>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <button
        onClick={() => onNavigate('dashboard')}
        className="back-button"
      >
        ← Back to Dashboard
      </button>

      <h2 style={{ marginTop: '20px', marginBottom: '20px', color: '#1f2937' }}>
        📋 All Job Openings
      </h2>

      {error && (
        <div className="dashboard-error">{error}</div>
      )}

      <div style={{ display: 'grid', gap: '16px' }}>
        {jobs.length > 0 ? (
          jobs.map(job => {
            const analytics = jobAnalytics[job.id];
            return (
              <div
                key={job.id}
                onClick={() => setSelectedJobId(selectedJobId === job.id ? null : job.id)}
                style={{
                  backgroundColor: 'white',
                  border: selectedJobId === job.id ? '2px solid #3b82f6' : '1px solid #e5e7eb',
                  borderRadius: '8px',
                  padding: '20px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <div>
                    <h3 style={{ margin: '0 0 8px 0', color: '#1f2937' }}>{job.title}</h3>
                    <p style={{ margin: '0 0 4px 0', color: '#6b7280', fontSize: '14px' }}>
                      📍 {job.location} • {job.experience_required} years
                    </p>
                    <p style={{ margin: '0', color: '#6b7280', fontSize: '14px' }}>
                      🏢 {job.department}
                    </p>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#3b82f6' }}>
                      {analytics?.summary?.total_views || 0}
                    </div>
                    <div style={{ fontSize: '12px', color: '#6b7280' }}>Total Views</div>
                  </div>
                </div>

              </div>
            );
          })
        ) : (
          <div style={{ textAlign: 'center', padding: '40px 20px', color: '#6b7280' }}>
            <p>No jobs created yet. Create one to get started!</p>
            <button
              onClick={() => onNavigate('create-job')}
              className="btn-primary"
              style={{ marginTop: '12px', padding: '10px 20px' }}
            >
              + Create Job
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default JobsList;
