import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import CodingChallenge from './CodingChallenge';
import SpeechTest from './SpeechTest';
import '../styles/InterviewSession.css';

const InterviewSession = ({ token }) => {
  const [interviewData, setInterviewData] = useState(null);
  const [currentPhase, setCurrentPhase] = useState('welcome');
  const [status, setStatus] = useState('loading');
  const [loading, setLoading] = useState(false);

  const [allQuestions, setAllQuestions] = useState({ technical: [], behavioral: [], coding: [] });
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [responses, setResponses] = useState({});

  const [codingCode, setCodingCode] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('python');
  const [compileOutput, setCompileOutput] = useState('');
  const [codeEvaluation, setCodeEvaluation] = useState(null);
  const [codeSubmitted, setCodeSubmitted] = useState(false);

  const [timeRemaining, setTimeRemaining] = useState(0);
  const [phaseTimeRemaining, setPhaseTimeRemaining] = useState(0);
  const timerRef = useRef(null);
  const phaseTimerRef = useRef(null);

  const [score, setScore] = useState(null);

  const phases = [
    { id: 'welcome', label: 'Welcome', duration: 0 },
    { id: 'instruction', label: 'Instructions', duration: 0 },
    { id: 'technical', label: 'Technical Questions (15)', duration: 30 * 60 },
    { id: 'coding', label: 'Coding Challenge', duration: 0 },
    { id: 'speech', label: 'Speech Test (20)', duration: 40 * 60 },
    { id: 'completion', label: 'Completion', duration: 0 }
  ];

  useEffect(() => {
    fetchInterviewStatus();
  }, [token]);

  useEffect(() => {
    if (Object.keys(responses).length > 0) {
      localStorage.setItem(`interview_responses_${token}`, JSON.stringify(responses));
    }
  }, [responses, token]);

  useEffect(() => {
    if (phaseTimeRemaining > 0 && currentPhase !== 'welcome' && currentPhase !== 'instruction' && currentPhase !== 'completion') {
      const interval = setInterval(() => {
        setPhaseTimeRemaining(prev => {
          if (prev <= 1) {
            moveToNextPhase();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [phaseTimeRemaining, currentPhase]);

  useEffect(() => {
    if (timeRemaining > 0) {
      const interval = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            completeInterview();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [timeRemaining]);

  const fetchInterviewStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/interview/${token}/status`);
      setInterviewData(response.data);
      setStatus(response.data.status);
      if (response.data.status === 'completed') {
        setScore(response.data.interview_score);
      }
      const savedResponses = localStorage.getItem(`interview_responses_${token}`);
      if (savedResponses) {
        setResponses(JSON.parse(savedResponses));
      }
    } catch (error) {
      console.error('Error fetching interview:', error);
      setStatus('error');
    }
  };

  const startInterview = async () => {
    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE_URL}/api/interview/${token}/start`);

      const data = response.data;
      setInterviewData(data);
      setStatus('in_progress');

      if (data.questions && Array.isArray(data.questions)) {
        const technical = data.questions.filter(q => q.type === 'technical');
        const behavioral = data.questions.filter(q => q.type === 'behavioral');
        const coding = data.questions.filter(q => q.type === 'coding');

        setAllQuestions({
          technical: technical || [],
          behavioral: behavioral || [],
          coding: coding || []
        });
      }

      setTimeRemaining(130 * 60);
      setCurrentPhase('instruction');
    } catch (error) {
      console.error('Error starting interview:', error);
      setStatus('error');
    } finally {
      setLoading(false);
    }
  };

  const getCurrentPhaseQuestions = () => {
    if (currentPhase === 'technical') return allQuestions.technical;
    if (currentPhase === 'behavioral') return allQuestions.behavioral;
    if (currentPhase === 'coding') return allQuestions.coding;
    return [];
  };

  const getCurrentQuestion = () => {
    const questions = getCurrentPhaseQuestions();
    return questions[currentQuestionIndex] || null;
  };

  const saveCurrentAnswer = async (answer) => {
    const question = getCurrentQuestion();
    if (!question) return;

    const key = `${currentPhase}_${question.id}`;

    setResponses(prev => ({
      ...prev,
      [key]: {
        question: question.question,
        answer: answer,
        difficulty: question.difficulty,
        timestamp: new Date().toISOString()
      }
    }));

    if (currentPhase !== 'coding') {
      try {
        const response = await axios.post(`${API_BASE_URL}/api/interview/${token}/submit-response`, {
          question_id: question.id,
          response: answer,
          phase: currentPhase,
          question_text: question.question,
          question_type: currentPhase
        });

        if (response.data.evaluation) {
          setResponses(prev => ({
            ...prev,
            [key]: {
              ...prev[key],
              evaluation: response.data.evaluation
            }
          }));
        }
      } catch (error) {
        console.error('Error submitting response:', error);
      }
    }
  };

  const handleQuestionNavigation = (index) => {
    const question = getCurrentQuestion();
    if (question && currentPhase !== 'coding') {
      const textareaElement = document.querySelector('textarea[name="answer"]');
      if (textareaElement && textareaElement.value) {
        saveCurrentAnswer(textareaElement.value);
      }
    }
    setCurrentQuestionIndex(index);
    setCodeEvaluation(null);
    setCompileOutput('');
  };

  const moveToNextQuestion = () => {
    const questions = getCurrentPhaseQuestions();
    const question = getCurrentQuestion();

    if (currentPhase !== 'coding' && question) {
      const textareaElement = document.querySelector('textarea[name="answer"]');
      if (textareaElement && textareaElement.value) {
        saveCurrentAnswer(textareaElement.value);
      }
    }

    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setCodeEvaluation(null);
      setCompileOutput('');
    }
  };

  const moveToNextPhase = () => {
    const currentIndex = phases.findIndex(p => p.id === currentPhase);
    if (currentIndex < phases.length - 1) {
      const nextPhase = phases[currentIndex + 1];
      setCurrentPhase(nextPhase.id);
      setCurrentQuestionIndex(0);
      setCodingCode('');
      setSelectedLanguage('python');
      setCodeEvaluation(null);
      setCompileOutput('');
      setCodeSubmitted(false);

      if (nextPhase.duration > 0) {
        setPhaseTimeRemaining(nextPhase.duration);
      }
    }
  };

  const completeInterview = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/interview/${token}/complete`);
      setStatus('completed');
      setScore(response.data.interview_score);
      setCurrentPhase('completion');
    } catch (error) {
      console.error('Error completing interview:', error);
    }
  };

  const handleEndInterview = () => {
    if (window.confirm('Are you sure you want to end the interview process?')) {
      completeInterview();
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Loading state
  if (status === 'loading' || !interviewData) {
    return (
      <div className="interview-session">
        <div className="interview-loading">
          <div className="loading-spinner"></div>
          <p>Loading interview...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (status === 'error') {
    return (
      <div className="interview-session">
        <div className="interview-loading">
          <p style={{color: '#dc2626'}}>Error loading interview. Please try again.</p>
        </div>
      </div>
    );
  }

  // Welcome screen
  if (currentPhase === 'welcome') {
    return (
      <div className="interview-session">
        <div className="welcome-screen">
          <div className="welcome-content">
            <h1>Welcome to Your Interview</h1>
            <h2>{interviewData.job_title}</h2>
            <div className="welcome-details">
              <p><span>Candidate</span><strong>{interviewData.candidate_name}</strong></p>
              <p><span>Position</span><strong>{interviewData.job_title}</strong></p>
              <p><span>Duration</span><strong>Approx. 130 minutes</strong></p>
            </div>
            <div style={{textAlign: 'left', marginBottom: '32px', padding: '20px', background: '#f9fafb', borderRadius: '6px', border: '1px solid #e5e7eb'}}>
              <p style={{marginBottom: '16px', fontWeight: '600', color: '#111827', fontSize: '15px'}}>Interview Structure:</p>
              <div style={{color: '#4b5563', fontSize: '14px', lineHeight: '1.8'}}>
                <div style={{marginBottom: '8px'}}>1. Technical Questions - 15 questions, 30 minutes</div>
                <div style={{marginBottom: '8px'}}>2. Coding Challenge - Problem solving task</div>
                <div>3. Speech Test - 20 questions, 40 minutes (verbal answers)</div>
              </div>
            </div>
            <button onClick={startInterview} disabled={loading} className="start-btn">
              {loading ? 'Starting...' : 'Begin Interview'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Instructions screen
  if (currentPhase === 'instruction') {
    return (
      <div className="interview-session">
        <div className="instruction-screen">
          <div className="instruction-content">
            <h2>Interview Instructions</h2>
            <ul className="instruction-list">
              <li>
                <span className="icon">1</span>
                <div>
                  <strong>Technical Questions (30 minutes)</strong>
                  <p style={{margin: '4px 0 0 0', color: '#6b7280'}}>Answer 15 technical questions. You can navigate between questions freely.</p>
                </div>
              </li>
              <li>
                <span className="icon">2</span>
                <div>
                  <strong>Coding Challenge</strong>
                  <p style={{margin: '4px 0 0 0', color: '#6b7280'}}>Solve a programming problem. Test your code before submitting.</p>
                </div>
              </li>
              <li>
                <span className="icon">3</span>
                <div>
                  <strong>Speech Test (40 minutes)</strong>
                  <p style={{margin: '4px 0 0 0', color: '#6b7280'}}>Answer 20 questions verbally. Your speech will be transcribed and evaluated.</p>
                </div>
              </li>
              <li>
                <span className="icon">i</span>
                <div>
                  <strong>Auto-save Enabled</strong>
                  <p style={{margin: '4px 0 0 0', color: '#6b7280'}}>Your answers are saved automatically as you progress.</p>
                </div>
              </li>
            </ul>
            <div className="instruction-actions">
              <button onClick={moveToNextPhase} className="btn btn-primary btn-large">
                Begin Technical Questions
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Completion screen
  if (currentPhase === 'completion') {
    return (
      <div className="interview-session">
        <div className="completion-screen">
          <div className="completion-content">
            <div className="completion-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                <polyline points="22 4 12 14.01 9 11.01" />
              </svg>
            </div>
            <h2>Interview Complete</h2>
            <p>Thank you for completing the interview. Your responses have been submitted for review.</p>
            {score !== null && (
              <div className="completion-stats">
                <div className="stat-item">
                  <div className="stat-value">{score.toFixed(0)}%</div>
                  <div className="stat-label">Overall Score</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{allQuestions.technical.length}</div>
                  <div className="stat-label">Technical</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{allQuestions.behavioral.length}</div>
                  <div className="stat-label">Speech</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Technical phase
  if (currentPhase === 'technical') {
    const questions = getCurrentPhaseQuestions();
    const question = getCurrentQuestion();
    const totalQuestions = questions.length;
    const savedAnswer = responses[`${currentPhase}_${question?.id}`]?.answer || '';

    return (
      <div className="interview-session">
        {/* Top Timer Bar */}
        <div className="top-timer-bar">
          <div className="timer-left">
            <span className="phase-label">Technical Round</span>
            <span className="question-count">Question {currentQuestionIndex + 1} of {totalQuestions}</span>
          </div>
          <div className="timer-right">
            <div className="timer-item">
              <span className="timer-label">Phase</span>
              <span className={`timer-value ${phaseTimeRemaining < 300 ? 'danger' : phaseTimeRemaining < 600 ? 'warning' : ''}`}>
                {formatTime(phaseTimeRemaining)}
              </span>
            </div>
            <div className="timer-item">
              <span className="timer-label">Total</span>
              <span className="timer-value">{formatTime(timeRemaining)}</span>
            </div>
          </div>
        </div>

        <div className="interview-layout-new">
          <div className="interview-sidebar-compact">
            <div className="sidebar-section">
              <h4>Progress</h4>
              <div className="progress-info-compact">
                <span>{Object.keys(responses).filter(k => k.startsWith('technical_')).length}/{totalQuestions} answered</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{width: `${(Object.keys(responses).filter(k => k.startsWith('technical_')).length / totalQuestions) * 100}%`}}
                ></div>
              </div>
            </div>

            <div className="sidebar-section">
              <h4>Questions</h4>
              <div className="question-dots">
                {questions.map((q, index) => {
                  const answerKey = `${currentPhase}_${q.id}`;
                  const isCurrentQuestion = index === currentQuestionIndex;
                  const hasAnswer = !!responses[answerKey];

                  return (
                    <span
                      key={q.id}
                      className={`question-dot ${isCurrentQuestion ? 'active' : ''} ${hasAnswer ? 'answered' : ''}`}
                      onClick={() => handleQuestionNavigation(index)}
                      title={`Question ${index + 1}${hasAnswer ? ' (Answered)' : ''}`}
                    >
                      {index + 1}
                    </span>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="interview-main">
            {question ? (
              <div className="question-card">
                <div className="question-header">
                  <div className="question-meta">
                    <span className="question-badge badge-technical">Technical</span>
                    <span className={`difficulty-badge difficulty-${question.difficulty?.toLowerCase()}`}>
                      {question.difficulty}
                    </span>
                  </div>
                </div>

                <div className="question-body">
                  <p className="question-text">{question.question}</p>

                  <div className="answer-section">
                    <label>Your Answer</label>
                    <textarea
                      name="answer"
                      className="answer-textarea"
                      placeholder="Type your answer here..."
                      defaultValue={savedAnswer}
                      onBlur={(e) => saveCurrentAnswer(e.target.value)}
                      onChange={(e) => {
                        setResponses(prev => ({
                          ...prev,
                          [`${currentPhase}_${question.id}`]: {
                            ...prev[`${currentPhase}_${question.id}`],
                            answer: e.target.value,
                            timestamp: new Date().toISOString()
                          }
                        }));
                      }}
                    />
                  </div>

                  {responses[`${currentPhase}_${question.id}`]?.evaluation && (
                    <div style={{marginTop: '16px', padding: '16px', background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '6px'}}>
                      <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '8px'}}>
                        <strong style={{color: '#166534'}}>AI Feedback</strong>
                        <span style={{color: '#166534'}}>Score: {responses[`${currentPhase}_${question.id}`].evaluation.overall_score}%</span>
                      </div>
                      <p style={{margin: 0, color: '#166534', fontSize: '14px'}}>{responses[`${currentPhase}_${question.id}`].evaluation.feedback}</p>
                    </div>
                  )}
                </div>

                <div className="question-navigation">
                  <button
                    onClick={() => currentQuestionIndex > 0 && handleQuestionNavigation(currentQuestionIndex - 1)}
                    disabled={currentQuestionIndex === 0}
                    className="nav-btn"
                  >
                    Previous
                  </button>

                  {currentQuestionIndex === totalQuestions - 1 ? (
                    <button onClick={moveToNextPhase} className="nav-btn success">
                      Complete Technical Phase
                    </button>
                  ) : (
                    <button onClick={moveToNextQuestion} className="nav-btn primary">
                      Next Question
                    </button>
                  )}
                </div>
              </div>
            ) : (
              <div className="question-card">
                <div className="question-body">
                  <p>No questions available</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* End Interview Button - Fixed Bottom Right */}
        <button 
          className="end-interview-btn"
          onClick={handleEndInterview}
          title="End the interview and submit all responses"
        >
          End Interview
        </button>
      </div>
    );
  }

  // Coding phase
  if (currentPhase === 'coding') {
    const question = getCurrentQuestion();
    
    const handleCodingSubmit = async (submissionData) => {
      setResponses(prev => ({
        ...prev,
        [`coding_${question?.id || 1}`]: {
          question: question?.question || question?.title,
          answer: submissionData.code,
          language: submissionData.language,
          evaluation: submissionData.evaluation,
          timestamp: new Date().toISOString()
        }
      }));

      setTimeout(() => {
        moveToNextPhase();
      }, 2000);
    };

    return (
      <div className="interview-session">
        {/* Top Timer Bar */}
        <div className="top-timer-bar">
          <div className="timer-left">
            <span className="phase-label">Coding Challenge</span>
          </div>
          <div className="timer-right">
            <div className="timer-item">
              <span className="timer-label">Phase</span>
              <span className={`timer-value ${phaseTimeRemaining < 300 ? 'danger' : phaseTimeRemaining < 600 ? 'warning' : ''}`}>
                {formatTime(phaseTimeRemaining)}
              </span>
            </div>
            <div className="timer-item">
              <span className="timer-label">Total</span>
              <span className="timer-value">{formatTime(timeRemaining)}</span>
            </div>
          </div>
        </div>
        
        <div style={{paddingTop: '56px'}}>
          <CodingChallenge
            token={token}
            question={question}
            onSubmit={handleCodingSubmit}
            onSkip={moveToNextPhase}
            initialCode={codingCode}
          />
        </div>

        {/* End Interview Button - Fixed Bottom Right */}
        <button 
          className="end-interview-btn"
          onClick={handleEndInterview}
          title="End the interview and submit all responses"
        >
          End Interview
        </button>
      </div>
    );
  }

  // Speech Test Phase
  if (currentPhase === 'speech') {
    const speechQuestions = allQuestions.behavioral;

    const handleSpeechComplete = (speechResponses) => {
      setResponses(prev => ({
        ...prev,
        ...speechResponses
      }));
      
      completeInterview();
    };

    return (
      <SpeechTest
        token={token}
        questions={speechQuestions}
        onComplete={handleSpeechComplete}
        timeRemaining={phaseTimeRemaining}
        formatTime={formatTime}
      />
    );
  }

  return <div className="interview-session"><div className="interview-loading"><p>Unknown phase: {currentPhase}</p></div></div>;
};

export default InterviewSession;
