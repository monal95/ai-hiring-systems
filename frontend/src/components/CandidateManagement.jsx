import React, { useState, useEffect } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import '../styles/CandidateManagement.css';

const CandidateManagement = ({ onNavigate }) => {
  const [candidates, setCandidates] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('details');
  const [panelRec, setPanelRec] = useState(null);
  const [assessmentRec, setAssessmentRec] = useState(null);
  const [interviewScores, setInterviewScores] = useState(null);

  const jobId = 'JOB1'; // Using first job

  useEffect(() => {
    fetchCandidates();
  }, []);

  const fetchCandidates = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/apply`);
      setCandidates(response.data);
      if (response.data.length > 0) {
        setSelectedCandidate(response.data[0]);
        loadCandidateDetails(response.data[0].id);
      }
    } catch (error) {
      console.error('Error fetching candidates:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCandidateDetails = async (candidateId) => {
    try {
      // Load interview panel recommendation (optional - may not exist)
      try {
        const panelRes = await axios.get(`${API_BASE_URL}/api/jobs/${jobId}/interview-panel`);
        setPanelRec(panelRes.data);
      } catch (err) {
        setPanelRec(null);
      }

      // Load assessment recommendation (optional - may not exist)
      try {
        const assessmentRes = await axios.get(`${API_BASE_URL}/api/jobs/${jobId}/assessment-recommendation`);
        setAssessmentRec(assessmentRes.data);
      } catch (err) {
        setAssessmentRec(null);
      }

      // Load interview scores for this candidate (optional - may not have completed interview)
      try {
        const scoresRes = await axios.get(`${API_BASE_URL}/api/candidates/${candidateId}/interview-scores`);
        setInterviewScores(scoresRes.data);
      } catch (err) {
        setInterviewScores(null);
      }
    } catch (error) {
      console.error('Error loading details:', error);
    }
  };

  const handleScoreCandidate = async (candidate) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/candidates/${candidate.id}/score?job_id=${jobId}`
      );
      
      // Update candidate with score
      const updatedCandidates = candidates.map(c =>
        c.id === candidate.id ? { ...c, score: response.data.overall_score, category: response.data.category } : c
      );
      setCandidates(updatedCandidates);
      setSelectedCandidate({ ...candidate, ...response.data });
      alert(`Candidate scored: ${response.data.overall_score}/100 - ${response.data.category}`);
    } catch (error) {
      console.error('Error scoring candidate:', error);
    }
  };

  const handleAssignAssessment = async (candidate) => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/candidates/${candidate.id}/assessment`,
        { job_id: jobId }
      );
      alert('Assessment assigned! Email sent to candidate.');
      setSelectedCandidate({ ...candidate, assessment: response.data });
    } catch (error) {
      console.error('Error assigning assessment:', error);
    }
  };

  const handleScheduleInterview = async (candidate) => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/candidates/${candidate.id}/interview/schedule`,
        { job_id: jobId, calendar_provider: 'google' }
      );
      alert(`Interview scheduled for ${response.data.scheduled_time}`);
      setSelectedCandidate({ ...candidate, interview: response.data });
    } catch (error) {
      console.error('Error scheduling interview:', error);
    }
  };

  const handleSubmitFeedback = async (candidate, feedback) => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/candidates/${candidate.id}/interview/feedback`,
        feedback
      );
      alert('Feedback submitted successfully!');
      setSelectedCandidate({ ...candidate, interview_feedback: response.data });
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  const handleRemoveCandidate = async (candidate, reason = 'After careful review of your application') => {
    const confirmRemove = window.confirm(
      `Are you sure you want to remove ${candidate.name}?\n\nA rejection email will be sent to: ${candidate.email}`
    );
    
    if (!confirmRemove) return;

    try {
      const response = await axios.delete(
        `${API_BASE_URL}/api/candidates/${candidate.id}`,
        {
          data: { 
            reason: reason,
            send_email: true 
          }
        }
      );
      
      if (response.data.success) {
        const emailStatus = response.data.email_sent 
          ? `📧 Rejection email sent to: ${response.data.candidate_email}`
          : '⚠️ Email could not be sent (check SendGrid configuration)';
        
        alert(
          `✅ Candidate Removed Successfully!\n\n${emailStatus}`
        );
        
        // Refresh candidates list
        fetchCandidates();
        setSelectedCandidate(null);
      }
    } catch (error) {
      console.error('Error removing candidate:', error);
      alert('Failed to remove candidate. Please try again.');
    }
  };

  const handleSendRejectionEmail = async (candidate) => {
    const reason = prompt(
      'Enter rejection reason (this will be included in the email):',
      'After careful review of your qualifications and experience'
    );
    
    if (!reason) return;

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/candidates/${candidate.id}/send-rejection`,
        { reason }
      );
      
      if (response.data.success) {
        alert(`✅ Rejection email sent to ${candidate.email}`);
        fetchCandidates(); // Refresh to show updated status
      }
    } catch (error) {
      console.error('Error sending rejection email:', error);
      alert('Failed to send rejection email.');
    }
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '40px' }}>Loading candidates...</div>;
  }

  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#f9fafb' }}>
      {/* Candidate List */}
      <div style={{ width: '25%', backgroundColor: 'white', borderRight: '1px solid #e5e7eb', overflowY: 'auto' }}>
        <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0, fontSize: '16px', color: '#1f2937' }}>Candidates ({candidates.length})</h3>
          <button
            onClick={fetchCandidates}
            style={{
              padding: '4px 8px',
              fontSize: '12px',
              backgroundColor: '#f3f4f6',
              border: '1px solid #d1d5db',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
            title="Refresh candidates"
          >
            ⟳
          </button>
        </div>
        <div>
          {candidates.map(candidate => (
            <div
              key={candidate.id}
              onClick={() => {
                setSelectedCandidate(candidate);
                loadCandidateDetails(candidate.id);
              }}
              style={{
                padding: '12px 16px',
                borderBottom: '1px solid #f3f4f6',
                cursor: 'pointer',
                backgroundColor: selectedCandidate?.id === candidate.id ? '#eff6ff' : 'white',
                borderLeft: selectedCandidate?.id === candidate.id ? '4px solid #3b82f6' : 'none'
              }}
            >
              <div style={{ fontWeight: '600', color: '#1f2937', marginBottom: '4px' }}>
                {candidate.name}
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>
                {candidate.email}
              </div>
              {candidate.score && (
                <div style={{ marginTop: '8px' }}>
                  <span style={{
                    display: 'inline-block',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    fontSize: '11px',
                    fontWeight: '600',
                    backgroundColor: candidate.score >= 75 ? '#d1fae5' : candidate.score >= 50 ? '#fef3c7' : '#fee2e2',
                    color: candidate.score >= 75 ? '#065f46' : candidate.score >= 50 ? '#92400e' : '#7f1d1d'
                  }}>
                    {candidate.category || 'Not Scored'}
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
        {selectedCandidate ? (
          <>
            <div style={{ marginBottom: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h1 style={{ margin: '0 0 8px 0', color: '#1f2937' }}>{selectedCandidate.name}</h1>
                  <p style={{ margin: 0, color: '#6b7280' }}>{selectedCandidate.email} • {selectedCandidate.phone}</p>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button
                    onClick={() => handleSendRejectionEmail(selectedCandidate)}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#f97316',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '14px',
                      fontWeight: '500',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                    title="Send rejection email without removing"
                  >
                    📧 Send Rejection Email
                  </button>
                  <button
                    onClick={() => handleRemoveCandidate(selectedCandidate)}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#ef4444',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '14px',
                      fontWeight: '500',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                    title="Remove candidate and send rejection email"
                  >
                    ❌ Remove Candidate
                  </button>
                </div>
              </div>
            </div>

            {/* Tabs */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', borderBottom: '2px solid #e5e7eb' }}>
              {['details', 'screening', 'assessment', 'interview'].map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  style={{
                    padding: '12px 16px',
                    border: 'none',
                    backgroundColor: activeTab === tab ? '#3b82f6' : 'transparent',
                    color: activeTab === tab ? 'white' : '#6b7280',
                    cursor: 'pointer',
                    fontWeight: activeTab === tab ? '600' : '400',
                    textTransform: 'capitalize'
                  }}
                >
                  {tab === 'details' && '👤'} {tab === 'assessment' && '📝'} {tab === 'interview' && '🎤'} {tab === 'screening' && '🔍'}
                  {' '}{tab}
                </button>
              ))}
            </div>

            {/* Candidate Details Tab */}
            {activeTab === 'details' && (
              <div>
                <div style={{ backgroundColor: 'white', borderRadius: '8px', padding: '20px', marginBottom: '20px' }}>
                  <h3 style={{ margin: '0 0 16px 0', color: '#1f2937' }}>👤 Candidate Information</h3>
                  
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
                    {/* Personal Information */}
                    <div style={{ backgroundColor: '#f3f4f6', padding: '16px', borderRadius: '8px' }}>
                      <h4 style={{ margin: '0 0 12px 0', color: '#374151' }}>📋 Personal Details</h4>
                      <div style={{ fontSize: '14px', color: '#1f2937' }}>
                        <p><strong>Name:</strong> {selectedCandidate.name}</p>
                        <p><strong>Email:</strong> {selectedCandidate.email}</p>
                        <p><strong>Phone:</strong> {selectedCandidate.phone || 'Not provided'}</p>
                        <p><strong>Applied:</strong> {selectedCandidate.applied_at ? new Date(selectedCandidate.applied_at).toLocaleDateString() : 'N/A'}</p>
                      </div>
                    </div>

                    {/* Skills */}
                    <div style={{ backgroundColor: '#f3f4f6', padding: '16px', borderRadius: '8px' }}>
                      <h4 style={{ margin: '0 0 12px 0', color: '#374151' }}>🔧 Skills</h4>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                        {selectedCandidate.skills && selectedCandidate.skills.length > 0 ? (
                          selectedCandidate.skills.map((skill, idx) => (
                            <span key={idx} style={{
                              padding: '4px 12px',
                              backgroundColor: '#dbeafe',
                              color: '#1e40af',
                              borderRadius: '20px',
                              fontSize: '12px',
                              fontWeight: '500'
                            }}>
                              {skill}
                            </span>
                          ))
                        ) : (
                          <span style={{ color: '#6b7280' }}>No skills listed</span>
                        )}
                      </div>
                    </div>

                    {/* Experience */}
                    <div style={{ backgroundColor: '#f3f4f6', padding: '16px', borderRadius: '8px' }}>
                      <h4 style={{ margin: '0 0 12px 0', color: '#374151' }}>💼 Experience</h4>
                      <div style={{ fontSize: '14px', color: '#1f2937' }}>
                        <p><strong>Years of Experience:</strong> {selectedCandidate.experience_years || 'Not specified'}</p>
                        <p><strong>Current Role:</strong> {selectedCandidate.current_role || 'Not specified'}</p>
                        <p><strong>Expected Salary:</strong> {selectedCandidate.expected_salary || 'Not specified'}</p>
                      </div>
                    </div>

                    {/* Education */}
                    <div style={{ backgroundColor: '#f3f4f6', padding: '16px', borderRadius: '8px' }}>
                      <h4 style={{ margin: '0 0 12px 0', color: '#374151' }}>🎓 Education</h4>
                      <div style={{ fontSize: '14px', color: '#1f2937' }}>
                        <p><strong>Degree:</strong> {selectedCandidate.education?.degree || selectedCandidate.degree || 'Not specified'}</p>
                        <p><strong>University:</strong> {selectedCandidate.education?.university || selectedCandidate.university || 'Not specified'}</p>
                      </div>
                    </div>
                  </div>

                  {/* Cover Letter / Notes */}
                  {selectedCandidate.cover_letter && (
                    <div style={{ marginTop: '20px', backgroundColor: '#fef3c7', padding: '16px', borderRadius: '8px' }}>
                      <h4 style={{ margin: '0 0 8px 0', color: '#92400e' }}>📝 Cover Letter / Notes</h4>
                      <p style={{ margin: 0, color: '#78350f', fontSize: '14px', lineHeight: '1.6' }}>
                        {selectedCandidate.cover_letter}
                      </p>
                    </div>
                  )}
                </div>

                {/* Interview Performance Section */}
                {interviewScores && (
                  <div style={{ backgroundColor: 'white', borderRadius: '8px', padding: '20px' }}>
                    <h3 style={{ margin: '0 0 16px 0', color: '#1f2937' }}>📊 Interview Performance</h3>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '20px' }}>
                      <div style={{ 
                        backgroundColor: interviewScores.overall_score >= 80 ? '#d1fae5' : interviewScores.overall_score >= 60 ? '#fef3c7' : '#fee2e2', 
                        padding: '16px', 
                        borderRadius: '8px', 
                        textAlign: 'center' 
                      }}>
                        <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Overall Score</div>
                        <div style={{ 
                          fontSize: '28px', 
                          fontWeight: 'bold', 
                          color: interviewScores.overall_score >= 80 ? '#065f46' : interviewScores.overall_score >= 60 ? '#92400e' : '#7f1d1d'
                        }}>
                          {interviewScores.overall_score}%
                        </div>
                      </div>
                      
                      <div style={{ backgroundColor: '#dbeafe', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
                        <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Technical</div>
                        <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1e40af' }}>
                          {interviewScores.technical_score || 0}%
                        </div>
                      </div>
                      
                      <div style={{ backgroundColor: '#e0e7ff', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
                        <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Behavioral</div>
                        <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#4338ca' }}>
                          {interviewScores.behavioral_score || 0}%
                        </div>
                      </div>
                      
                      <div style={{ backgroundColor: '#f3e8ff', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
                        <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Coding</div>
                        <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#7c3aed' }}>
                          {interviewScores.coding_score || 0}%
                        </div>
                      </div>
                    </div>

                    {/* Status Indicator */}
                    <div style={{
                      padding: '12px 16px',
                      borderRadius: '8px',
                      backgroundColor: interviewScores.overall_score >= 80 ? '#d1fae5' : '#fee2e2',
                      border: `1px solid ${interviewScores.overall_score >= 80 ? '#86efac' : '#fca5a5'}`,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}>
                      <span style={{ fontSize: '20px' }}>{interviewScores.overall_score >= 80 ? '✅' : '❌'}</span>
                      <span style={{ 
                        fontWeight: '600', 
                        color: interviewScores.overall_score >= 80 ? '#065f46' : '#7f1d1d'
                      }}>
                        {interviewScores.overall_score >= 80 
                          ? 'Qualified for HR Interview - Invitation Sent' 
                          : 'Did Not Meet Threshold - Rejection Email Sent'}
                      </span>
                    </div>

                    {/* AI Feedback */}
                    {interviewScores.ai_feedback && (
                      <div style={{ marginTop: '16px', backgroundColor: '#f3f4f6', padding: '16px', borderRadius: '8px' }}>
                        <h4 style={{ margin: '0 0 8px 0', color: '#374151' }}>🤖 AI Evaluation Feedback</h4>
                        <p style={{ margin: 0, color: '#1f2937', fontSize: '14px', lineHeight: '1.6' }}>
                          {interviewScores.ai_feedback}
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {!interviewScores && (
                  <div style={{ backgroundColor: 'white', borderRadius: '8px', padding: '20px' }}>
                    <h3 style={{ margin: '0 0 16px 0', color: '#1f2937' }}>📊 Interview Performance</h3>
                    <div style={{ textAlign: 'center', padding: '24px', color: '#6b7280' }}>
                      <p>No interview scores available yet.</p>
                      <p style={{ fontSize: '14px' }}>Interview scores will appear here after the candidate completes their interview session.</p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Screening Tab */}
            {activeTab === 'screening' && (
              <div>
                <div style={{ backgroundColor: 'white', borderRadius: '8px', padding: '20px', marginBottom: '20px' }}>
                  <h3 style={{ margin: '0 0 16px 0', color: '#1f2937' }}>📊 AI Screening & Scoring</h3>
                  
                  <div style={{ marginBottom: '20px' }}>
                    <h4 style={{ color: '#374151', marginBottom: '12px' }}>Match Analysis</h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                      <div style={{ backgroundColor: '#f3f4f6', padding: '12px', borderRadius: '6px' }}>
                        <div style={{ fontSize: '12px', color: '#6b7280' }}>Skills</div>
                        <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#1f2937' }}>
                          {selectedCandidate.skills ? selectedCandidate.skills.length : 0}
                        </div>
                      </div>
                      <div style={{ backgroundColor: '#f3f4f6', padding: '12px', borderRadius: '6px' }}>
                        <div style={{ fontSize: '12px', color: '#6b7280' }}>Experience</div>
                        <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#1f2937' }}>
                          {selectedCandidate.experience_years || 'N/A'} yrs
                        </div>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => handleScoreCandidate(selectedCandidate)}
                    style={{
                      padding: '12px 20px',
                      backgroundColor: '#3b82f6',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontWeight: '600'
                    }}
                  >
                    🎯 Score & Categorize Candidate
                  </button>
                </div>

                {selectedCandidate.score && (
                  <div style={{ backgroundColor: 'white', borderRadius: '8px', padding: '20px' }}>
                    <h4 style={{ margin: '0 0 12px 0', color: '#1f2937' }}>Scoring Result</h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                      <div style={{ backgroundColor: '#f3f4f6', padding: '12px', borderRadius: '6px', textAlign: 'center' }}>
                        <div style={{ fontSize: '12px', color: '#6b7280' }}>Overall Score</div>
                        <div style={{ fontSize: '28px', fontWeight: 'bold', color: selectedCandidate.score >= 75 ? '#10b981' : '#f59e0b' }}>
                          {selectedCandidate.score}%
                        </div>
                      </div>
                      <div style={{ backgroundColor: '#f3f4f6', padding: '12px', borderRadius: '6px', textAlign: 'center' }}>
                        <div style={{ fontSize: '12px', color: '#6b7280' }}>Category</div>
                        <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1f2937' }}>
                          {selectedCandidate.category}
                        </div>
                      </div>
                    </div>
                    {selectedCandidate.skill_gaps && selectedCandidate.skill_gaps.length > 0 && (
                      <div style={{ marginTop: '12px', padding: '12px', backgroundColor: '#fef3c7', borderRadius: '6px' }}>
                        <div style={{ fontSize: '12px', color: '#92400e', fontWeight: '600' }}>Skill Gaps</div>
                        <div style={{ fontSize: '13px', color: '#78350f', marginTop: '4px' }}>
                          {selectedCandidate.skill_gaps.join(', ')}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Assessment Tab */}
            {activeTab === 'assessment' && (
              <div style={{ backgroundColor: 'white', borderRadius: '8px', padding: '20px' }}>
                <h3 style={{ margin: '0 0 16px 0', color: '#1f2937' }}>📝 Assessment Assignment</h3>
                
                {assessmentRec ? (
                  <div style={{ marginBottom: '20px' }}>
                    <h4 style={{ color: '#374151', marginBottom: '12px' }}>Recommended Assessment</h4>
                    <div style={{ backgroundColor: '#f3f4f6', padding: '12px', borderRadius: '6px', marginBottom: '12px' }}>
                      <div style={{ fontWeight: '600', color: '#1f2937' }}>
                        {assessmentRec.details?.type || 'Coding Test'}
                      </div>
                      <div style={{ fontSize: '13px', color: '#6b7280', marginTop: '4px' }}>
                        Platform: {assessmentRec.details?.platform || 'HackerRank'}
                      </div>
                      <div style={{ fontSize: '13px', color: '#6b7280' }}>
                        Duration: {assessmentRec.details?.duration_minutes || 120} minutes
                      </div>
                    </div>
                  </div>
                ) : null}

                <button
                  onClick={() => handleAssignAssessment(selectedCandidate)}
                  style={{
                    padding: '12px 20px',
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontWeight: '600'
                  }}
                >
                  📤 Assign Assessment
                </button>

                {selectedCandidate.assessment && (
                  <div style={{ marginTop: '20px', backgroundColor: '#dbeafe', borderRadius: '6px', padding: '12px' }}>
                    <div style={{ fontWeight: '600', color: '#1e40af' }}>Assessment Status</div>
                    <div style={{ fontSize: '13px', color: '#1e3a8a', marginTop: '4px' }}>
                      Status: {selectedCandidate.assessment.status}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Interview Tab */}
            {activeTab === 'interview' && (
              <div style={{ backgroundColor: 'white', borderRadius: '8px', padding: '20px' }}>
                <h3 style={{ margin: '0 0 16px 0', color: '#1f2937' }}>🎤 Interview Management</h3>
                
                {panelRec && (
                  <div style={{ marginBottom: '20px' }}>
                    <h4 style={{ color: '#374151', marginBottom: '12px' }}>Recommended Interview Panel</h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '12px' }}>
                      {panelRec.recommended_panel?.slice(0, 3).map((interviewer, idx) => (
                        <div key={idx} style={{ backgroundColor: '#f3f4f6', padding: '12px', borderRadius: '6px' }}>
                          <div style={{ fontWeight: '600', color: '#1f2937' }}>{interviewer.name}</div>
                          <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                            {interviewer.expertise?.slice(0, 2).join(', ')}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <button
                  onClick={() => handleScheduleInterview(selectedCandidate)}
                  style={{
                    padding: '12px 20px',
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontWeight: '600',
                    marginBottom: '20px'
                  }}
                >
                  📅 Schedule Interview
                </button>

                {selectedCandidate.interview && (
                  <div style={{ backgroundColor: '#dbeafe', borderRadius: '6px', padding: '12px' }}>
                    <div style={{ fontWeight: '600', color: '#1e40af' }}>Interview Scheduled</div>
                    <div style={{ fontSize: '13px', color: '#1e3a8a', marginTop: '4px' }}>
                      Time: {selectedCandidate.interview.scheduled_time}
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
            Select a candidate to view details
          </div>
        )}
      </div>
    </div>
  );
};

export default CandidateManagement;
