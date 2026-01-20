import React, { useState, useEffect } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import '../styles/CandidateList.css';

const CandidateList = ({ jobId, onSchedule }) => {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [showApplicationForm, setShowApplicationForm] = useState(false);
  const [applicationForm, setApplicationForm] = useState({
    name: '',
    email: '',
    phone: '',
    resume: null,
  });

  useEffect(() => {
    fetchJobs();
  }, []);

  useEffect(() => {
    if (selectedJob) {
      fetchCandidates(selectedJob);
    }
  }, [selectedJob]);

  const fetchJobs = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/jobs`);
      setJobs(response.data);

      if (response.data.length > 0) {
        setSelectedJob(response.data[0].id);
      }
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

  const fetchCandidates = async (jobId) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/candidates?job_id=${jobId}`
      );
      setCandidates(response.data);
    } catch (error) {
      console.error('Error fetching candidates:', error);
    }
  };

  const handleFileChange = (e) => {
    setApplicationForm({
      ...applicationForm,
      resume: e.target.files[0],
    });
  };

  const handleInputChange = (e) => {
    setApplicationForm({
      ...applicationForm,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmitApplication = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('resume', applicationForm.resume);
    formData.append('job_id', selectedJob);
    formData.append('name', applicationForm.name);
    formData.append('email', applicationForm.email);
    formData.append('phone', applicationForm.phone);

    try {
      await axios.post(`${API_BASE_URL}/api/apply`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      alert('Application submitted successfully!');
      setShowApplicationForm(false);
      setApplicationForm({
        name: '',
        email: '',
        phone: '',
        resume: null,
      });

      fetchCandidates(selectedJob);
    } catch (error) {
      console.error('Error submitting application:', error);
      alert('Failed to submit application');
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'High':
        return 'priority-high';
      case 'Medium':
        return 'priority-medium';
      case 'Low':
        return 'priority-low';
      default:
        return 'priority-low';
    }
  };

  return (
    <div className="candidate-list-container">
      <div className="application-form-container">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '24px', marginBottom: '24px', flexWrap: 'wrap' }}>
          <div style={{ flex: 1 }}>
            <h2 className="candidate-list-title">Candidate Pipeline</h2>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'center' }}>
              <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Select Job:</label>
              <select
                value={selectedJob || ''}
                onChange={(e) => setSelectedJob(e.target.value)}
                className="form-input"
                style={{ maxWidth: '300px' }}
              >
                {jobs.map((job) => (
                  <option key={job.id} value={job.id}>
                    {job.title} ({job.applications || 0} applications)
                  </option>
                ))}
              </select>
            </div>
          </div>

          <button
            onClick={() => setShowApplicationForm(!showApplicationForm)}
            className="btn-primary"
            style={{ whiteSpace: 'nowrap' }}
          >
            {showApplicationForm ? 'Close Form' : '+ Test Application'}
          </button>
        </div>

        {showApplicationForm && (
          <div style={{ backgroundColor: '#f3f4f6', border: '2px solid #dbeafe', borderRadius: '8px', padding: '24px', marginBottom: '24px' }}>
            <h3 className="form-title">Submit Test Application</h3>

            <form onSubmit={handleSubmitApplication} className="job-form">
              <input
                type="text"
                name="name"
                placeholder="Full Name"
                value={applicationForm.name}
                onChange={handleInputChange}
                className="form-input"
                required
              />

              <input
                type="email"
                name="email"
                placeholder="Email"
                value={applicationForm.email}
                onChange={handleInputChange}
                className="form-input"
                required
              />

              <input
                type="tel"
                name="phone"
                placeholder="Phone"
                value={applicationForm.phone}
                onChange={handleInputChange}
                className="form-input"
                required
              />

              <input
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={handleFileChange}
                className="form-input"
                required
              />

              <button 
                type="submit" 
                className="btn-submit"
                style={{ width: '100%' }}
              >
                Submit Application
              </button>
            </form>
          </div>
        )}
      </div>

      {candidates.length === 0 ? (
        <div className="candidates-card" style={{ padding: '48px 20px', textAlign: 'center' }}>
          <p className="no-candidates">
            No candidates yet. Submit a test application above!
          </p>
        </div>
      ) : (
        <div className="candidates-card">
          <h3 className="candidates-title">Candidates List</h3>
          <div style={{ overflowX: 'auto' }}>
            <table className="candidates-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Skills</th>
                  <th>Experience</th>
                  <th>Match Score</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {candidates.map((candidate) => (
                  <tr key={candidate.id}>
                    <td style={{ fontWeight: '600' }}>{candidate.name}</td>
                    <td>{candidate.email}</td>

                    <td>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                        {candidate.skills.slice(0, 3).map((skill, idx) => (
                          <span key={idx} className="skill-badge" style={{ display: 'inline-block' }}>
                            {skill}
                          </span>
                        ))}

                        {candidate.skills.length > 3 && (
                          <span style={{ backgroundColor: '#e5e7eb', color: '#374151', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: '600' }}>
                            +{candidate.skills.length - 3}
                          </span>
                        )}
                      </div>
                    </td>

                    <td>{candidate.experience_years} yrs</td>

                    <td>
                      <div>
                        <div style={{ width: '96px', backgroundColor: '#e5e7eb', borderRadius: '9999px', height: '8px', marginBottom: '4px' }}>
                          <div
                            style={{
                              backgroundColor: '#10b981',
                              height: '8px',
                              borderRadius: '9999px',
                              width: `${candidate.match_score}%`
                            }}
                          />
                        </div>
                        <span style={{ fontSize: '12px', fontWeight: '600', color: '#374151' }}>{candidate.match_score}%</span>
                      </div>
                    </td>

                    <td>
                      <span className={`priority-badge ${getPriorityColor(candidate.priority)}`}>
                        {candidate.priority}
                      </span>
                    </td>

                    <td>{candidate.status}</td>

                    <td>
                      <button
                        className="btn-small"
                        onClick={() =>
                          alert(`View details for ${candidate.name}`)
                        }
                      >
                        View
                      </button>
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

export default CandidateList;
