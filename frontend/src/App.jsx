import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import JobCreation from './components/JobCreation';
import ApplicationUpload from './components/ApplicationUpload';
import CandidateList from './components/CandidateList';
import InterviewScheduler from './components/InterviewScheduler';
import OfferManagement from './components/OfferManagement';
import JobsList from './components/JobsList';
import CandidateManagement from './components/CandidateManagement';
import JobManagement from './components/JobManagement';
import JobApplicationForm from './components/JobApplicationForm';
import PrivacyPolicy from './components/PrivacyPolicy';
import InterviewSession from './components/InterviewSession';
import LandingPage from './components/LandingPage';

function App() {
  // Check if user has already seen landing page in this session
  const [hasStarted, setHasStarted] = useState(() => {
    return sessionStorage.getItem('hasStartedApp') === 'true';
  });
  const [currentView, setCurrentView] = useState('dashboard');
  const [selectedJob, setSelectedJob] = useState(null);
  const [applicationJobId, setApplicationJobId] = useState(null);
  const [interviewToken, setInterviewToken] = useState(null);

  // Handle "Get Started" from landing page
  const handleGetStarted = () => {
    sessionStorage.setItem('hasStartedApp', 'true');
    setHasStarted(true);
  };

  // Check URL for application form route on load
  useEffect(() => {
    const path = window.location.pathname;
    const applyMatch = path.match(/^\/apply\/(.+)$/);
    const interviewMatch = path.match(/^\/interview\/(.+)$/);
    const linkedInCallback = path.includes('/auth/linkedin/callback');
    
    if (applyMatch) {
      setApplicationJobId(applyMatch[1]);
      setCurrentView('public-application');
    } else if (interviewMatch) {
      setInterviewToken(interviewMatch[1]);
      setCurrentView('interview-session');
    } else if (linkedInCallback) {
      // Handle LinkedIn OAuth callback - redirect to create-job view
      // The LinkedInLogin component will handle the token exchange
      setCurrentView('create-job');
    }
  }, []);

  // Handle browser back/forward
  useEffect(() => {
    const handlePopState = () => {
      const path = window.location.pathname;
      const applyMatch = path.match(/^\/apply\/(.+)$/);
      const interviewMatch = path.match(/^\/interview\/(.+)$/);
      if (applyMatch) {
        setApplicationJobId(applyMatch[1]);
        setCurrentView('public-application');
      } else if (interviewMatch) {
        setInterviewToken(interviewMatch[1]);
        setCurrentView('interview-session');
      } else {
        setCurrentView('dashboard');
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  // If on public application form, render only the form (no navbar)
  if (currentView === 'public-application' && applicationJobId) {
    return <JobApplicationForm jobId={applicationJobId} />;
  }

  // If on interview session, render only the interview (no navbar)
  if (currentView === 'interview-session' && interviewToken) {
    return <InterviewSession token={interviewToken} />;
  }

  // Show landing page if user hasn't clicked "Get Started"
  // Skip landing page for direct links (apply, interview, LinkedIn callback)
  if (!hasStarted && currentView === 'dashboard') {
    return <LandingPage onGetStarted={handleGetStarted} />;
  }

  const renderView = () => {
    switch(currentView) {
      case 'dashboard':
        return <Dashboard onNavigate={setCurrentView} />;
      case 'jobs':
        return <JobsList onNavigate={setCurrentView} onSelectJob={setSelectedJob} />;
      case 'job-management':
        return <JobManagement onNavigate={setCurrentView} />;
      case 'create-job':
        return <JobCreation onBack={() => setCurrentView('dashboard')} />;
      case 'apply':
        return <ApplicationUpload 
                 jobId={selectedJob}
                 onBack={() => setCurrentView('dashboard')}
                 onApplicationSubmitted={(app) => {
                   // App submitted, can add to state if needed
                 }}
               />;
      case 'candidates-management':
        return <CandidateManagement 
                 onNavigate={setCurrentView} 
               />;
      case 'candidates':
        return <CandidateList 
                 jobId={selectedJob} 
                 onSchedule={() => setCurrentView('schedule')} 
               />;
      case 'schedule':
        return <InterviewScheduler onBack={() => setCurrentView('candidates')} />;
      case 'offers':
        return <OfferManagement onBack={() => setCurrentView('dashboard')} />;
      case 'privacy-policy':
        return <PrivacyPolicy onBack={() => setCurrentView('dashboard')} />;
      default:
        return <Dashboard onNavigate={setCurrentView} />;
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#f5f5f5' }}>
      <nav style={{ background: '#2563eb' }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '0 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '64px', flexWrap: 'wrap' }}>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold', color: 'white', margin: 0 }}>🎯 AI Hiring System</h1>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <button 
              onClick={() => setCurrentView('dashboard')}
              style={{
                padding: '8px 16px',
                backgroundColor: currentView === 'dashboard' ? '#2563eb' : '#2563eb',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                transition: 'all 0.3s ease',
              }}
              onMouseEnter={(e) => e.target.style.backgroundColor = '#2563eb'}
              onMouseLeave={(e) => e.target.style.backgroundColor = currentView === 'dashboard' ? '#2563eb' : '#2563eb'}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setCurrentView('create-job')}
              style={{
                padding: '8px 16px',
                backgroundColor: currentView === 'create-job' ? '#2563eb' : '#2563eb',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                transition: 'all 0.3s ease',
              }}
              onMouseEnter={(e) => e.target.style.backgroundColor = '#2563eb'}
              onMouseLeave={(e) => e.target.style.backgroundColor = currentView === 'create-job' ? '#2563eb' : '#2563eb'}
            >
              Create Job
            </button>
            <button 
              onClick={() => setCurrentView('job-management')}
              style={{
                padding: '8px 16px',
                backgroundColor: currentView === 'job-management' ? '#2563eb' : '#2563eb',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                transition: 'all 0.3s ease',
              }}
              onMouseEnter={(e) => e.target.style.backgroundColor = '#2563eb'}
              onMouseLeave={(e) => e.target.style.backgroundColor = currentView === 'job-management' ? '#2563eb' : '#2563eb'}
            >
              Job Management
            </button>
            <button 
              onClick={() => setCurrentView('candidates-management')}
              style={{
                padding: '8px 16px',
                backgroundColor: currentView === 'candidates-management' ? '#2563eb' : '#2563eb',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                transition: 'all 0.3s ease',
              }}
              onMouseEnter={(e) => e.target.style.backgroundColor = '#2563eb'}
              onMouseLeave={(e) => e.target.style.backgroundColor = currentView === 'candidates-management' ? '#2563eb' : '#2563eb'}
            >
              Candidate Management
            </button>
            <button 
              onClick={() => setCurrentView('offers')}
              style={{
                padding: '8px 16px',
                backgroundColor: currentView === 'offers' ? '#2563eb' : '#2563eb',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                transition: 'all 0.3s ease',
              }}
              onMouseEnter={(e) => e.target.style.backgroundColor = '#2563eb'}
              onMouseLeave={(e) => e.target.style.backgroundColor = currentView === 'offers' ? '#2563eb' : '#2563eb'}
            >
              Offers
            </button>
          </div>
        </div>
      </nav>
      <main style={{ flex: 1, maxWidth: '1280px', margin: '0 auto', width: '100%', padding: '32px 16px' }}>
        {renderView()}
      </main>
    </div>
  );
}

export default App;