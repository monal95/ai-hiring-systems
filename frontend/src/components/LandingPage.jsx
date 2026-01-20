import React, { useState, useEffect } from 'react';
import '../styles/LandingPage.css';

const LandingPage = ({ onGetStarted }) => {
  const [animationPhase, setAnimationPhase] = useState('loading');
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    // Simplified animation sequence
    const timer1 = setTimeout(() => setAnimationPhase('logo'), 400);
    const timer2 = setTimeout(() => setAnimationPhase('title'), 1000);
    const timer3 = setTimeout(() => {
      setAnimationPhase('complete');
      setShowContent(true);
    }, 1800);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, []);

  return (
    <div className="landing-page">
      {/* Intro Animation */}
      <div className={`intro-animation ${animationPhase === 'complete' ? 'fade-out' : ''}`}>
        <div className="animation-container">
          {/* Subtle Background Glow */}
          <div className="bg-glow"></div>

          {/* Logo Animation */}
          <div className={`logo-animation ${animationPhase !== 'loading' ? 'visible' : ''}`}>
            <div className="logo-circle">
              <span className="logo-icon">🎯</span>
            </div>
          </div>

          {/* Title Animation */}
          <h1 className={`intro-title ${['title', 'complete'].includes(animationPhase) ? 'visible' : ''}`}>
            AI Hiring System
          </h1>

          {/* Loading Indicator */}
          <div className="loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>

      {/* Main Content - Single Page */}
      <div className={`landing-content ${showContent ? 'visible' : ''}`}>
        <div className="landing-main">
          {/* Background */}
          <div className="landing-bg">
            <div className="bg-gradient"></div>
          </div>

          {/* Center Content */}
          <div className="landing-center">
            <div className="brand-icon">🎯</div>
            
            <h1 className="main-title">
              AI-Powered <span>Hiring System</span>
            </h1>
            
            <p className="main-subtitle">
              Streamline your recruitment process with intelligent automation. 
              From resume screening to candidate interviews — all powered by AI.
            </p>

            {/* Key Features - Simple */}
            <div className="feature-pills">
              <div className="pill">
                <span className="pill-icon">📄</span>
                Smart Resume Parsing
              </div>
              <div className="pill">
                <span className="pill-icon">🎤</span>
                AI Interviews
              </div>
              <div className="pill">
                <span className="pill-icon">💻</span>
                Coding Assessments
              </div>
              <div className="pill">
                <span className="pill-icon">🔒</span>
                Secure Proctoring
              </div>
            </div>

            {/* CTA Button */}
            <button className="get-started-btn" onClick={onGetStarted}>
              Get Started
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </button>

            <p className="helper-text">
              No setup required • Start hiring smarter today
            </p>
          </div>

          {/* Footer */}
          <div className="landing-footer">
            <p>© 2025 AI Hiring System. AI-powered recruitment platform.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
