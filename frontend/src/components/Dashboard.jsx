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
  const [platformAnalytics, setPlatformAnalytics] = useState(null);
  const [selectedJob, setSelectedJob] = useState(null);
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
      
      // Fetch platform analytics for the first job if available
      if (response.data.total_jobs > 0) {
        const jobsList = await axios.get('http://localhost:5000/api/jobs');
        if (jobsList.data.length > 0) {
          fetchPlatformAnalytics(jobsList.data[0].id);
          setSelectedJob(jobsList.data[0]);
        }
      }
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

  const fetchPlatformAnalytics = async (jobId) => {
    try {
      const response = await axios.get(`http://localhost:5000/api/jobs/${jobId}/analytics`);
      setPlatformAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching platform analytics:', error);
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
          onClick={() => fetchStats()}
          className={`dashboard-refresh-btn ${refreshing ? 'spinning' : ''}`}
          disabled={refreshing}
          title="Click to refresh dashboard data"
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

      <div className="applications-card">
        <h3 className="applications-title">Platform Analytics</h3>
        {platformAnalytics ? (
          <div>
            <div style={{ marginBottom: '24px' }}>
              <h4 style={{ color: '#1f2937', marginBottom: '12px', fontSize: '14px', fontWeight: '600' }}>
                📊 {platformAnalytics.job_title || 'Job'} Performance Summary
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '12px' }}>
                <div style={{ backgroundColor: '#f3f4f6', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
                  <div style={{ color: '#6b7280', fontSize: '12px', marginBottom: '4px' }}>Total Views</div>
                  <div style={{ color: '#1f2937', fontSize: '24px', fontWeight: 'bold' }}>{platformAnalytics.summary.total_views}</div>
                </div>
                <div style={{ backgroundColor: '#f3f4f6', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
                  <div style={{ color: '#6b7280', fontSize: '12px', marginBottom: '4px' }}>Applications</div>
                  <div style={{ color: '#1f2937', fontSize: '24px', fontWeight: 'bold' }}>{platformAnalytics.summary.total_applications}</div>
                </div>
                <div style={{ backgroundColor: '#f3f4f6', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
                  <div style={{ color: '#6b7280', fontSize: '12px', marginBottom: '4px' }}>Ignored</div>
                  <div style={{ color: '#1f2937', fontSize: '24px', fontWeight: 'bold' }}>{platformAnalytics.summary.total_ignored}</div>
                </div>
                <div style={{ backgroundColor: '#f3f4f6', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
                  <div style={{ color: '#6b7280', fontSize: '12px', marginBottom: '4px' }}>Conversion</div>
                  <div style={{ color: '#10b981', fontSize: '24px', fontWeight: 'bold' }}>{platformAnalytics.summary.conversion_rate}%</div>
                </div>
              </div>
            </div>

            <div>
              <h4 style={{ color: '#1f2937', marginBottom: '12px', fontSize: '14px', fontWeight: '600' }}>
                🌐 Per-Platform Breakdown
              </h4>
              <div style={{ overflowX: 'auto' }}>
                <table className="applications-table" style={{ width: '100%' }}>
                  <thead>
                    <tr>
                      <th>Platform</th>
                      <th>Status</th>
                      <th>Views</th>
                      <th>Clicks</th>
                      <th>Applications</th>
                      <th>Ignored</th>
                      <th>Conversion</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(platformAnalytics.platforms || {}).map(([platform, data]) => (
                      <tr key={platform}>
                        <td style={{ fontWeight: '600', textTransform: 'capitalize' }}>
                          {platform.replace('_', ' ')}
                        </td>
                        <td>
                          <span style={{
                            backgroundColor: data.status === 'published' ? '#d1fae5' : '#fee2e2',
                            color: data.status === 'published' ? '#065f46' : '#7f1d1d',
                            padding: '4px 8px',
                            borderRadius: '4px',
                            fontSize: '12px',
                            fontWeight: '600'
                          }}>
                            {data.status}
                          </span>
                        </td>
                        <td>{data.views || 0}</td>
                        <td>{data.clicks || 0}</td>
                        <td style={{ fontWeight: '600', color: '#10b981' }}>{data.applications || 0}</td>
                        <td style={{ color: '#ef4444' }}>{data.ignored || 0}</td>
                        <td>
                          {data.views > 0 
                            ? `${((data.applications / data.views) * 100).toFixed(1)}%`
                            : '0%'
                          }
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : (
          <p style={{ color: '#7f8c8d', textAlign: 'center', padding: '24px 0' }}>
            No platform analytics available. Create and publish a job to see analytics.
          </p>
        )}
      </div>

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