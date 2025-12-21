import React, { useState } from 'react';
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

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [selectedJob, setSelectedJob] = useState(null);

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
      default:
        return <Dashboard onNavigate={setCurrentView} />;
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#f5f5f5' }}>
      <nav style={{ background: 'linear-gradient(90deg, #3498db 0%, #8e44ad 100%)', boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)' }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '0 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '64px', flexWrap: 'wrap' }}>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold', color: 'white', margin: 0 }}>🎯 GCC Hiring System</h1>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <button 
              onClick={() => setCurrentView('dashboard')}
              style={{
                padding: '8px 16px',
                backgroundColor: currentView === 'dashboard' ? 'rgba(255, 255, 255, 0.4)' : 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                transition: 'all 0.3s ease',
              }}
              onMouseEnter={(e) => e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.3)'}
              onMouseLeave={(e) => e.target.style.backgroundColor = currentView === 'dashboard' ? 'rgba(255, 255, 255, 0.4)' : 'rgba(255, 255, 255, 0.2)'}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setCurrentView('create-job')}
              style={{
                padding: '8px 16px',
                backgroundColor: currentView === 'create-job' ? 'rgba(255, 255, 255, 0.4)' : 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                transition: 'all 0.3s ease',
              }}
              onMouseEnter={(e) => e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.3)'}
              onMouseLeave={(e) => e.target.style.backgroundColor = currentView === 'create-job' ? 'rgba(255, 255, 255, 0.4)' : 'rgba(255, 255, 255, 0.2)'}
            >
              Create Job
            </button>
            <button 
              onClick={() => setCurrentView('job-management')}
              style={{
                padding: '8px 16px',
                backgroundColor: currentView === 'job-management' ? 'rgba(255, 255, 255, 0.4)' : 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                transition: 'all 0.3s ease',
              }}
              onMouseEnter={(e) => e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.3)'}
              onMouseLeave={(e) => e.target.style.backgroundColor = currentView === 'job-management' ? 'rgba(255, 255, 255, 0.4)' : 'rgba(255, 255, 255, 0.2)'}
            >
              Job Management
            </button>
            <button 
              onClick={() => setCurrentView('candidates-management')}
              style={{
                padding: '8px 16px',
                backgroundColor: currentView === 'candidates-management' ? 'rgba(255, 255, 255, 0.4)' : 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                transition: 'all 0.3s ease',
              }}
              onMouseEnter={(e) => e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.3)'}
              onMouseLeave={(e) => e.target.style.backgroundColor = currentView === 'candidates-management' ? 'rgba(255, 255, 255, 0.4)' : 'rgba(255, 255, 255, 0.2)'}
            >
              Candidate Management
            </button>
            <button 
              onClick={() => setCurrentView('offers')}
              style={{
                padding: '8px 16px',
                backgroundColor: currentView === 'offers' ? 'rgba(255, 255, 255, 0.4)' : 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                transition: 'all 0.3s ease',
              }}
              onMouseEnter={(e) => e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.3)'}
              onMouseLeave={(e) => e.target.style.backgroundColor = currentView === 'offers' ? 'rgba(255, 255, 255, 0.4)' : 'rgba(255, 255, 255, 0.2)'}
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