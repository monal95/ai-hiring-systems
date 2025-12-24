import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Dashboard.css';

const Dashboard = ({ onNavigate }) => {
  const [stats, setStats] = useState({
    total_jobs: 0,
    total_applications: 0,
    high_priority: 0,
    medium_priority: 0,
    recent_applications: []
  });
  const [jobs, setJobs] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedStat, setSelectedStat] = useState(null);
  const [hoveredCard, setHoveredCard] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    setRefreshing(true);
    try {
      const response = await axios.get('http://localhost:5000/api/dashboard/stats');
      setStats(response.data);
      setError(null);
      
      // Fetch jobs and candidates for detail views
      const jobsRes = await axios.get('http://localhost:5000/api/jobs');
      setJobs(jobsRes.data || []);
      
      const candidatesRes = await axios.get('http://localhost:5000/api/candidates');
      setCandidates(candidatesRes.data || []);
    } catch (error) {
      console.error('Error fetching stats:', error);
      setStats({
        total_jobs: 0,
        total_applications: 0,
        high_priority: 0,
        medium_priority: 0,
        recent_applications: []
      });
      setError('Unable to fetch dashboard stats. Using default values.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <div className="loading-message">Loading Dashboard...</div>
      </div>
    );
  }

  const getStatDetails = (type) => {
    switch(type) {
      case 'jobs':
        return `You have ${stats.total_jobs} active job openings awaiting applications`;
      case 'applications':
        return `Total of ${stats.total_applications} candidates have applied`;
      case 'high':
        return `${stats.high_priority} high-priority candidates require immediate attention`;
      case 'medium':
        return `${stats.medium_priority} medium-priority candidates are in progress`;
      default:
        return '';
    }
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2 className="dashboard-title">Recruitment Dashboard</h2>
        <button 
          onClick={() => window.location.reload()}
          className={`dashboard-refresh-btn ${refreshing ? 'spinning' : ''}`}
          disabled={refreshing}
          title="Click to reload the page"
        >
          {refreshing ? '⟳ Refreshing...' : '⟳ Refresh'}
        </button>
      </div>

      {error && (
        <div className="dashboard-error">
          {error}
        </div>
      )}
      
      <div className="stats-grid">
        <div 
          className={`stat-card blue ${selectedStat === 'jobs' ? 'selected' : ''}`}
          onClick={() => setSelectedStat(selectedStat === 'jobs' ? null : 'jobs')}
          onMouseEnter={() => setHoveredCard('jobs')}
          onMouseLeave={() => setHoveredCard(null)}
        >
          <div className="stat-card-content">
            <div className="stat-card-icon">💼</div>
            <div className="stat-card-value">{stats.total_jobs}</div>
            <p className="stat-card-label">Total Jobs</p>
          </div>
          {hoveredCard === 'jobs' && (
            <div className="stat-card-tooltip">
              {getStatDetails('jobs')}
            </div>
          )}
        </div>

        <div 
          className={`stat-card green ${selectedStat === 'applications' ? 'selected' : ''}`}
          onClick={() => setSelectedStat(selectedStat === 'applications' ? null : 'applications')}
          onMouseEnter={() => setHoveredCard('applications')}
          onMouseLeave={() => setHoveredCard(null)}
        >
          <div className="stat-card-content">
            <div className="stat-card-icon">📝</div>
            <div className="stat-card-value">{stats.total_applications}</div>
            <p className="stat-card-label">Applications</p>
          </div>
          {hoveredCard === 'applications' && (
            <div className="stat-card-tooltip">
              {getStatDetails('applications')}
            </div>
          )}
        </div>

        <div 
          className={`stat-card red ${selectedStat === 'high' ? 'selected' : ''}`}
          onClick={() => setSelectedStat(selectedStat === 'high' ? null : 'high')}
          onMouseEnter={() => setHoveredCard('high')}
          onMouseLeave={() => setHoveredCard(null)}
        >
          <div className="stat-card-content">
            <div className="stat-card-icon">🚨</div>
            <div className="stat-card-value">{stats.high_priority}</div>
            <p className="stat-card-label">High Priority</p>
          </div>
          {hoveredCard === 'high' && (
            <div className="stat-card-tooltip">
              {getStatDetails('high')}
            </div>
          )}
        </div>

        <div 
          className={`stat-card yellow ${selectedStat === 'medium' ? 'selected' : ''}`}
          onClick={() => setSelectedStat(selectedStat === 'medium' ? null : 'medium')}
          onMouseEnter={() => setHoveredCard('medium')}
          onMouseLeave={() => setHoveredCard(null)}
        >
          <div className="stat-card-content">
            <div className="stat-card-icon">⏳</div>
            <div className="stat-card-value">{stats.medium_priority}</div>
            <p className="stat-card-label">Medium Priority</p>
          </div>
          {hoveredCard === 'medium' && (
            <div className="stat-card-tooltip">
              {getStatDetails('medium')}
            </div>
          )}
        </div>
      </div>

      {/* Dynamic Details Panel - Shows based on selected stat */}
      {selectedStat && (
        <div className="applications-card" style={{ animation: 'fadeIn 0.3s ease' }}>
          {selectedStat === 'jobs' && (
            <>
              <h3 className="applications-title">💼 All Jobs ({jobs.length})</h3>
              {jobs.length > 0 ? (
                <div style={{ overflowX: 'auto' }}>
                  <table className="applications-table">
                    <thead>
                      <tr>
                        <th>Title</th>
                        <th>Department</th>
                        <th>Location</th>
                        <th>Experience</th>
                        <th>Status</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {jobs.map((job) => (
                        <tr key={job.id}>
                          <td style={{ fontWeight: '600' }}>{job.title}</td>
                          <td>{job.department || 'N/A'}</td>
                          <td>{job.location}</td>
                          <td>{job.experience_required}</td>
                          <td>
                            <span style={{
                              backgroundColor: job.status === 'active' ? '#d1fae5' : '#fee2e2',
                              color: job.status === 'active' ? '#065f46' : '#7f1d1d',
                              padding: '4px 8px',
                              borderRadius: '4px',
                              fontSize: '12px',
                              fontWeight: '600'
                            }}>
                              {job.status || 'Active'}
                            </span>
                          </td>
                          <td>
                            <button 
                              onClick={() => onNavigate('jobs')}
                              style={{ padding: '4px 12px', fontSize: '12px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                            >
                              View
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p style={{ color: '#7f8c8d', textAlign: 'center', padding: '24px 0' }}>No jobs created yet</p>
              )}
            </>
          )}

          {selectedStat === 'applications' && (
            <>
              <h3 className="applications-title">📝 All Applications ({candidates.length})</h3>
              {candidates.length > 0 ? (
                <div style={{ overflowX: 'auto' }}>
                  <table className="applications-table">
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Skills</th>
                        <th>Score</th>
                        <th>Status</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {candidates.map((candidate) => (
                        <tr key={candidate.id}>
                          <td style={{ fontWeight: '600' }}>{candidate.name}</td>
                          <td>{candidate.email}</td>
                          <td>
                            {(candidate.skills || []).slice(0, 3).map(skill => (
                              <span key={skill} className="skill-badge">{skill}</span>
                            ))}
                          </td>
                          <td>
                            <span style={{
                              color: (candidate.score || 0) >= 75 ? '#10b981' : (candidate.score || 0) >= 50 ? '#f59e0b' : '#6b7280',
                              fontWeight: '600'
                            }}>
                              {candidate.score || 'N/A'}
                            </span>
                          </td>
                          <td>{candidate.status || 'Applied'}</td>
                          <td>
                            <button 
                              onClick={() => onNavigate('candidates')}
                              style={{ padding: '4px 12px', fontSize: '12px', backgroundColor: '#10b981', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                            >
                              View
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p style={{ color: '#7f8c8d', textAlign: 'center', padding: '24px 0' }}>No applications yet</p>
              )}
            </>
          )}

          {selectedStat === 'high' && (
            <>
              <h3 className="applications-title">🚨 High Priority Candidates ({stats.high_priority})</h3>
              {candidates.filter(c => (c.score || 0) >= 75).length > 0 ? (
                <div style={{ overflowX: 'auto' }}>
                  <table className="applications-table">
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Skills</th>
                        <th>Score</th>
                        <th>Status</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {candidates.filter(c => (c.score || 0) >= 75).map((candidate) => (
                        <tr key={candidate.id} style={{ backgroundColor: '#fef2f2' }}>
                          <td style={{ fontWeight: '600' }}>{candidate.name}</td>
                          <td>{candidate.email}</td>
                          <td>
                            {(candidate.skills || []).slice(0, 3).map(skill => (
                              <span key={skill} className="skill-badge">{skill}</span>
                            ))}
                          </td>
                          <td>
                            <span style={{ color: '#10b981', fontWeight: '700', fontSize: '16px' }}>
                              {candidate.score}%
                            </span>
                          </td>
                          <td>{candidate.status || 'Applied'}</td>
                          <td>
                            <button 
                              onClick={() => onNavigate('candidates')}
                              style={{ padding: '4px 12px', fontSize: '12px', backgroundColor: '#ef4444', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                            >
                              Review Now
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p style={{ color: '#7f8c8d', textAlign: 'center', padding: '24px 0' }}>No high priority candidates. Score candidates to identify top talent!</p>
              )}
            </>
          )}

          {selectedStat === 'medium' && (
            <>
              <h3 className="applications-title">⏳ Medium Priority Candidates ({stats.medium_priority})</h3>
              {candidates.filter(c => (c.score || 0) >= 50 && (c.score || 0) < 75).length > 0 ? (
                <div style={{ overflowX: 'auto' }}>
                  <table className="applications-table">
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Skills</th>
                        <th>Score</th>
                        <th>Status</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {candidates.filter(c => (c.score || 0) >= 50 && (c.score || 0) < 75).map((candidate) => (
                        <tr key={candidate.id} style={{ backgroundColor: '#fffbeb' }}>
                          <td style={{ fontWeight: '600' }}>{candidate.name}</td>
                          <td>{candidate.email}</td>
                          <td>
                            {(candidate.skills || []).slice(0, 3).map(skill => (
                              <span key={skill} className="skill-badge">{skill}</span>
                            ))}
                          </td>
                          <td>
                            <span style={{ color: '#f59e0b', fontWeight: '700', fontSize: '16px' }}>
                              {candidate.score}%
                            </span>
                          </td>
                          <td>{candidate.status || 'Applied'}</td>
                          <td>
                            <button 
                              onClick={() => onNavigate('candidates')}
                              style={{ padding: '4px 12px', fontSize: '12px', backgroundColor: '#f59e0b', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                            >
                              Review
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p style={{ color: '#7f8c8d', textAlign: 'center', padding: '24px 0' }}>No medium priority candidates. Score candidates to categorize them!</p>
              )}
            </>
          )}
        </div>
      )}

      <div className="applications-card">
        <h3 className="applications-title">Recent Applications</h3>
        {stats.recent_applications && stats.recent_applications.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table className="applications-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Skills</th>
                  <th>Match Score</th>
                  <th>Priority</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_applications.map((app, idx) => (
                  <tr key={app.id} className="application-row" style={{ animationDelay: `${idx * 0.1}s` }}>
                    <td>{app.name}</td>
                    <td>
                      <div>
                        {app.skills.map(skill => (
                          <span key={skill} className="skill-badge">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td>
                      <div className="match-score-container">
                        <div style={{ width: '100%', backgroundColor: '#e5e7eb', borderRadius: '9999px', height: '8px', marginBottom: '4px' }}>
                          <div 
                            className="match-score-bar"
                            style={{
                              backgroundColor: app.match_score >= 75 ? '#10b981' : app.match_score >= 50 ? '#f59e0b' : '#ef4444',
                              height: '8px',
                              borderRadius: '9999px',
                              width: `${app.match_score}%`,
                              transition: 'all 0.5s ease'
                            }}
                          ></div>
                        </div>
                        <span style={{ fontSize: '12px', color: '#7f8c8d', fontWeight: '600' }}>{app.match_score}%</span>
                      </div>
                    </td>
                    <td>
                      <span className={`priority-badge priority-${app.priority.toLowerCase()}`}>
                        {app.priority}
                      </span>
                    </td>
                    <td>{app.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ color: '#7f8c8d', textAlign: 'center', padding: '24px 0' }}>No applications yet</p>
        )}
      </div>

      <div className="applications-card" style={{ marginTop: '30px' }}>
        <h3 className="applications-title">Quick Actions</h3>
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
          <button 
            onClick={() => onNavigate('create-job')} 
            className="btn-primary action-btn"
            style={{ padding: '12px 24px' }}
          >
            + Create New Job
          </button>
          <button 
            onClick={() => onNavigate('jobs')} 
            className="btn-secondary action-btn"
            style={{ padding: '12px 24px' }}
          >
            📊 View All Jobs
          </button>
          <button 
            onClick={() => onNavigate('candidates')} 
            className="btn-secondary action-btn"
            style={{ padding: '12px 24px' }}
          >
            View All Candidates
          </button>
          <button 
            onClick={() => onNavigate('offers')} 
            className="btn-primary action-btn"
            style={{ padding: '12px 24px' }}
          >
            Manage Offers
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;