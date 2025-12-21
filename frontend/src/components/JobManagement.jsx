import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './JobManagement.css';

const JobManagement = ({ onNavigate }) => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/jobs');
      setJobs(response.data);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveJob = async (job) => {
    if (window.confirm(`Are you sure you want to remove "${job.title}"? This will delete the job from all platforms (LinkedIn, Indeed, Naukri, etc.)`)) {
      try {
        await axios.delete(`http://localhost:5000/api/jobs/${job.id}`);
        alert('✅ Job removed successfully from dashboard and all platforms');
        setJobs(jobs.filter(j => j.id !== job.id));
        setSelectedJob(null);
        setShowDetails(false);
      } catch (error) {
        console.error('Error removing job:', error);
        alert('❌ Failed to remove job. Please try again.');
      }
    }
  };

  const getProgressColor = (filled, total) => {
    const percentage = (filled / total) * 100;
    if (percentage === 100) return '#ef4444'; // Red - filled
    if (percentage >= 80) return '#f59e0b'; // Orange - almost full
    if (percentage >= 50) return '#f59e0b'; // Orange - halfway
    return '#10b981'; // Green - available
  };

  const getStatusBadge = (job) => {
    if (job.status === 'filled' || job.hired_count >= job.openings) {
      return <span style={{ backgroundColor: '#fee2e2', color: '#7f1d1d' }}>🔴 FILLED</span>;
    }
    if (job.status === 'active') {
      return <span style={{ backgroundColor: '#d1fae5', color: '#065f46' }}>🟢 ACTIVE</span>;
    }
    return <span style={{ backgroundColor: '#f3f4f6', color: '#374151' }}>⚪ {job.status}</span>;
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '40px' }}>Loading jobs...</div>;
  }

  return (
    <div style={{ display: 'flex', gap: '24px', minHeight: '100vh' }}>
      {/* Job List */}
      <div style={{ flex: 1 }}>
        <h2 style={{ color: '#1f2937', marginBottom: '20px' }}>📋 Active Job Openings</h2>
        
        {jobs.length === 0 ? (
          <div style={{ 
            backgroundColor: '#f3f4f6', 
            padding: '40px', 
            borderRadius: '8px', 
            textAlign: 'center',
            color: '#6b7280'
          }}>
            <p>No active jobs. <a href="#" onClick={() => onNavigate('create-job')} style={{ color: '#3b82f6', textDecoration: 'none' }}>Create a new job</a></p>
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '16px' }}>
            {jobs.map(job => {
              const filledPercentage = Math.round((job.hired_count / job.openings) * 100);
              const isFilled = job.hired_count >= job.openings;
              
              return (
                <div
                  key={job.id}
                  onClick={() => {
                    setSelectedJob(job);
                    setShowDetails(true);
                  }}
                  style={{
                    backgroundColor: 'white',
                    border: selectedJob?.id === job.id ? '2px solid #3b82f6' : '1px solid #e5e7eb',
                    borderRadius: '8px',
                    padding: '16px',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    opacity: isFilled ? 0.6 : 1
                  }}
                  onMouseEnter={(e) => !isFilled && (e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)')}
                  onMouseLeave={(e) => (e.currentTarget.style.boxShadow = 'none')}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '12px' }}>
                    <div>
                      <h3 style={{ margin: '0 0 4px 0', color: '#1f2937', fontSize: '16px' }}>
                        {job.title}
                      </h3>
                      <p style={{ margin: 0, color: '#6b7280', fontSize: '13px' }}>
                        📍 {job.location} • 🔷 {job.id}
                      </p>
                    </div>
                    {getStatusBadge(job)}
                  </div>

                  {/* Slot Progress */}
                  <div style={{ marginBottom: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <span style={{ fontSize: '12px', color: '#6b7280' }}>Positions Filled</span>
                      <span style={{ fontSize: '12px', fontWeight: '600', color: '#1f2937' }}>
                        {job.hired_count}/{job.openings}
                      </span>
                    </div>
                    <div style={{
                      height: '8px',
                      backgroundColor: '#e5e7eb',
                      borderRadius: '4px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        height: '100%',
                        width: `${Math.min(filledPercentage, 100)}%`,
                        backgroundColor: getProgressColor(job.hired_count, job.openings),
                        transition: 'width 0.3s ease'
                      }} />
                    </div>
                  </div>

                  {/* Stats */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                    <div style={{ backgroundColor: '#f9fafb', padding: '8px', borderRadius: '4px', textAlign: 'center' }}>
                      <div style={{ fontSize: '11px', color: '#6b7280' }}>Applications</div>
                      <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1f2937' }}>
                        {job.applications || 0}
                      </div>
                    </div>
                    <div style={{ backgroundColor: '#f9fafb', padding: '8px', borderRadius: '4px', textAlign: 'center' }}>
                      <div style={{ fontSize: '11px', color: '#6b7280' }}>Platforms</div>
                      <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1f2937' }}>
                        {job.platforms ? Object.keys(job.platforms).length : 0}
                      </div>
                    </div>
                    <div style={{ backgroundColor: '#f9fafb', padding: '8px', borderRadius: '4px', textAlign: 'center' }}>
                      <div style={{ fontSize: '11px', color: '#6b7280' }}>Created</div>
                      <div style={{ fontSize: '13px', color: '#1f2937', fontWeight: '600' }}>
                        {new Date(job.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })}
                      </div>
                    </div>
                  </div>

                  {/* Filled Badge */}
                  {isFilled && (
                    <div style={{
                      marginTop: '12px',
                      padding: '8px',
                      backgroundColor: '#fee2e2',
                      border: '1px solid #fecaca',
                      borderRadius: '4px',
                      textAlign: 'center',
                      fontSize: '12px',
                      fontWeight: '600',
                      color: '#7f1d1d'
                    }}>
                      ⚠️ All positions filled - Consider removing this job
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Job Details */}
      {showDetails && selectedJob && (
        <div style={{ width: '350px', backgroundColor: 'white', borderRadius: '8px', padding: '20px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', height: 'fit-content', position: 'sticky', top: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h3 style={{ margin: 0, color: '#1f2937' }}>Job Details</h3>
            <button
              onClick={() => setShowDetails(false)}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '24px',
                cursor: 'pointer',
                color: '#6b7280'
              }}
            >
              ✕
            </button>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <h2 style={{ margin: '0 0 8px 0', color: '#1f2937', fontSize: '18px' }}>
              {selectedJob.title}
            </h2>
            <p style={{ margin: 0, color: '#6b7280', fontSize: '14px' }}>
              📍 {selectedJob.location}
            </p>
          </div>

          <div style={{ backgroundColor: '#f9fafb', padding: '12px', borderRadius: '6px', marginBottom: '20px' }}>
            <div style={{ marginBottom: '12px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Status</div>
              {getStatusBadge(selectedJob)}
            </div>
            <div style={{ marginBottom: '12px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Positions</div>
              <div style={{ fontSize: '14px', fontWeight: '600', color: '#1f2937' }}>
                {selectedJob.hired_count}/{selectedJob.openings} filled
              </div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Applications</div>
              <div style={{ fontSize: '14px', fontWeight: '600', color: '#1f2937' }}>
                {selectedJob.applications || 0} total
              </div>
            </div>
          </div>

          {selectedJob.description && (
            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ margin: '0 0 8px 0', color: '#374151', fontSize: '13px', fontWeight: '600' }}>
                Description
              </h4>
              <p style={{ margin: 0, color: '#6b7280', fontSize: '13px', lineHeight: '1.5' }}>
                {selectedJob.description.substring(0, 200)}...
              </p>
            </div>
          )}

          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ margin: '0 0 8px 0', color: '#374151', fontSize: '13px', fontWeight: '600' }}>
              Posted Platforms
            </h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {selectedJob.platforms && Object.keys(selectedJob.platforms).map(platform => (
                <span
                  key={platform}
                  style={{
                    backgroundColor: '#dbeafe',
                    color: '#1e40af',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '11px',
                    fontWeight: '600',
                    textTransform: 'capitalize'
                  }}
                >
                  {platform.replace('_', ' ')}
                </span>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ margin: '0 0 8px 0', color: '#374151', fontSize: '13px', fontWeight: '600' }}>
              Required Skills
            </h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {selectedJob.requirements?.must_have?.slice(0, 5).map((skill, idx) => (
                <span
                  key={idx}
                  style={{
                    backgroundColor: '#fef3c7',
                    color: '#92400e',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '11px'
                  }}
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
            <button
              onClick={() => onNavigate('candidates-management')}
              style={{
                padding: '10px 16px',
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '13px'
              }}
            >
              👥 View Candidates
            </button>
            <button
              onClick={() => {/* Create new job */}}
              style={{
                padding: '10px 16px',
                backgroundColor: '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '13px'
              }}
            >
              📊 Analytics
            </button>
          </div>

          {/* Remove Job Button */}
          <button
            onClick={() => handleRemoveJob(selectedJob)}
            style={{
              width: '100%',
              padding: '10px 16px',
              backgroundColor: '#ef4444',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '14px',
              transition: 'background-color 0.2s'
            }}
            onMouseEnter={(e) => e.target.style.backgroundColor = '#dc2626'}
            onMouseLeave={(e) => e.target.style.backgroundColor = '#ef4444'}
          >
            🗑️ Remove Job & Delete from All Platforms
          </button>

          <p style={{
            margin: '12px 0 0 0',
            fontSize: '11px',
            color: '#6b7280',
            textAlign: 'center'
          }}>
            This will remove the job from LinkedIn, Indeed, Naukri, and all other platforms.
          </p>
        </div>
      )}
    </div>
  );
};

export default JobManagement;
