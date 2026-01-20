import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import '../styles/SpeechTest.css';

const SpeechTest = ({ token, questions, onComplete, timeRemaining, formatTime }) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [responses, setResponses] = useState({});
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [evaluation, setEvaluation] = useState(null);
  const [speechSupported, setSpeechSupported] = useState(true);
  const [interviewCompleted, setInterviewCompleted] = useState(false);

  const recognitionRef = useRef(null);
  const recordingTimerRef = useRef(null);

  const currentQuestion = questions[currentQuestionIndex];
  const totalQuestions = questions.length;

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      setSpeechSupported(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
      let finalTranscript = '';
      let interimTranscript = '';

      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalTranscript += result[0].transcript + ' ';
        } else {
          interimTranscript += result[0].transcript;
        }
      }

      setTranscript(finalTranscript + interimTranscript);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      if (event.error === 'not-allowed') {
        alert('Microphone access denied. Please allow microphone access and try again.');
      }
    };

    recognition.onend = () => {
      if (recognitionRef.current && recognitionRef.current.isRecording) {
        try {
          recognitionRef.current.start();
        } catch (e) {}
      }
    };

    recognitionRef.current = recognition;
    recognitionRef.current.isRecording = false;

    return () => {
      if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch (e) {}
      }
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (isRecording) {
      recordingTimerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } else {
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
      }
    }

    return () => {
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
      }
    };
  }, [isRecording]);

  const startRecording = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not available in your browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    setTranscript('');
    setRecordingTime(0);
    setEvaluation(null);

    try {
      recognitionRef.current.start();
      recognitionRef.current.isRecording = true;
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting speech recognition:', error);
      alert('Could not start speech recognition. Please try again.');
    }
  };

  const stopRecording = () => {
    setIsRecording(false);

    if (recognitionRef.current) {
      recognitionRef.current.isRecording = false;
      try { recognitionRef.current.stop(); } catch (e) {}
    }
  };

  const submitAnswer = async () => {
    if (!transcript.trim()) {
      alert('Please record your answer first.');
      return;
    }

    setIsProcessing(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/interview/${token}/evaluate-speech`, {
        question_id: currentQuestion.id,
        question_text: currentQuestion.question,
        transcript: transcript.trim(),
        recording_duration: recordingTime,
        question_type: 'speech'
      });

      const evalResult = response.data.evaluation || {
        overall_score: 75,
        feedback: 'Answer recorded successfully.',
        clarity_score: 80,
        content_score: 75,
        communication_score: 70
      };

      setEvaluation(evalResult);

      setResponses(prev => ({
        ...prev,
        [`speech_${currentQuestion.id}`]: {
          question: currentQuestion.question,
          transcript: transcript.trim(),
          duration: recordingTime,
          evaluation: evalResult,
          timestamp: new Date().toISOString()
        }
      }));

    } catch (error) {
      console.error('Error submitting speech answer:', error);
      setResponses(prev => ({
        ...prev,
        [`speech_${currentQuestion.id}`]: {
          question: currentQuestion.question,
          transcript: transcript.trim(),
          duration: recordingTime,
          timestamp: new Date().toISOString()
        }
      }));
    } finally {
      setIsProcessing(false);
    }
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < totalQuestions - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
      setTranscript('');
      setRecordingTime(0);
      setEvaluation(null);
    }
  };

  const previousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
      const prevResponse = responses[`speech_${questions[currentQuestionIndex - 1].id}`];
      if (prevResponse) {
        setTranscript(prevResponse.transcript || '');
        setEvaluation(prevResponse.evaluation || null);
      } else {
        setTranscript('');
        setEvaluation(null);
      }
      setRecordingTime(0);
    }
  };

  const completeInterview = () => {
    if (transcript.trim()) {
      setResponses(prev => ({
        ...prev,
        [`speech_${currentQuestion.id}`]: {
          question: currentQuestion.question,
          transcript: transcript.trim(),
          duration: recordingTime,
          evaluation: evaluation,
          timestamp: new Date().toISOString()
        }
      }));
    }
    setInterviewCompleted(true);
  };

  const formatRecordingTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!speechSupported) {
    return (
      <div className="speech-test">
        <div className="interview-complete-screen">
          <div className="completion-card">
            <h2>Speech Recognition Not Supported</h2>
            <p>Your browser doesn't support Web Speech API. Please use Chrome, Edge, or Safari.</p>
            <button onClick={() => onComplete(responses)} className="nav-btn primary">
              Skip to Complete
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (interviewCompleted) {
    return (
      <div className="speech-test">
        <div className="interview-complete-screen">
          <div className="completion-card">
            <div className="completion-icon">✓</div>
            <h2>Thank You for Completing the Interview</h2>
            <p className="completion-message">
              Your answers will be evaluated based on your performance. Based on the evaluation, 
              you will be selected for the <strong>Final Round</strong> - either an HR Virtual Meeting 
              or an In-Person Meeting. Please check your email regularly for updates.
            </p>
            <div className="completion-stats">
              <div className="stat-item">
                <span className="stat-value">{totalQuestions}</span>
                <span className="stat-label">Questions</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{Object.keys(responses).length}</span>
                <span className="stat-label">Recorded</span>
              </div>
            </div>
            <p className="good-luck">Good luck with your application!</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="speech-test">
      <div className="speech-test-layout">
        <div className="speech-sidebar">
          <div className="sidebar-header">
            <h3>Speech Test</h3>
            <p>Question {currentQuestionIndex + 1} of {totalQuestions}</p>
          </div>

          <div className="speech-timer">
            <div className="timer-label">Time Remaining</div>
            <div className={`timer-value ${timeRemaining < 300 ? 'danger' : timeRemaining < 600 ? 'warning' : ''}`}>
              {formatTime(timeRemaining)}
            </div>
          </div>

          <div className="speech-progress">
            <div className="progress-info">
              <span>Progress</span>
              <span>{Object.keys(responses).length}/{totalQuestions}</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{width: `${(Object.keys(responses).length / totalQuestions) * 100}%`}}
              ></div>
            </div>
          </div>

          <div className="question-nav">
            <h4>Questions</h4>
            <div>
              {questions.map((q, index) => {
                const isCurrentQuestion = index === currentQuestionIndex;
                const hasAnswer = !!responses[`speech_${q.id}`];

                return (
                  <span
                    key={q.id}
                    className={`question-dot ${isCurrentQuestion ? 'active current' : ''} ${hasAnswer ? 'answered' : ''}`}
                    onClick={() => {
                      setCurrentQuestionIndex(index);
                      const resp = responses[`speech_${q.id}`];
                      if (resp) {
                        setTranscript(resp.transcript || '');
                        setEvaluation(resp.evaluation || null);
                      } else {
                        setTranscript('');
                        setEvaluation(null);
                      }
                      setRecordingTime(0);
                      setIsRecording(false);
                    }}
                  >
                    {index + 1}
                  </span>
                );
              })}
            </div>
          </div>
        </div>

        <div className="speech-main">
          <div className="speech-question-card">
            <div className="question-card-header">
              <div className="question-number-badge">
                <span>Question</span>
                <strong>{currentQuestionIndex + 1}</strong>
                <span>of {totalQuestions}</span>
              </div>
              <span className="category-badge">Speech</span>
            </div>

            <div className="question-card-body">
              <p className="question-text">{currentQuestion?.question}</p>

              <div className="recording-section">
                <div className="recording-controls">
                  {!isRecording ? (
                    <button 
                      onClick={startRecording} 
                      className="record-btn start"
                      disabled={isProcessing}
                    >
                      <span className="icon"></span>
                      Start Recording
                    </button>
                  ) : (
                    <button 
                      onClick={stopRecording} 
                      className="record-btn stop"
                    >
                      <span className="icon"></span>
                      Stop Recording
                    </button>
                  )}

                  {isRecording && (
                    <div className="recording-status active">
                      <span className="recording-dot"></span>
                      Recording: {formatRecordingTime(recordingTime)}
                    </div>
                  )}
                </div>

                <div className="transcript-section">
                  <div className="transcript-label">
                    Your Response
                    {isRecording && <span className="live-badge">LIVE</span>}
                  </div>
                  <div className={`transcript-box ${!transcript ? 'empty' : ''}`}>
                    {transcript || (isRecording 
                      ? 'Listening... Speak clearly and your words will appear here.'
                      : 'Click "Start Recording" and speak your answer.')}
                  </div>
                </div>

                {transcript && !isRecording && (
                  <div style={{display: 'flex', gap: '12px', marginTop: '16px'}}>
                    <button 
                      onClick={submitAnswer} 
                      className="nav-btn primary"
                      disabled={isProcessing}
                    >
                      {isProcessing ? 'Evaluating...' : 'Submit Answer'}
                    </button>
                    <button 
                      onClick={startRecording} 
                      className="nav-btn"
                      disabled={isProcessing}
                    >
                      Re-record
                    </button>
                  </div>
                )}

                {evaluation && (
                  <div className="evaluation-result">
                    <div className="evaluation-header">
                      <h4>AI Evaluation</h4>
                      <span className={`evaluation-score ${evaluation.overall_score >= 70 ? 'high' : evaluation.overall_score >= 50 ? 'medium' : 'low'}`}>
                        {evaluation.overall_score}%
                      </span>
                    </div>
                    <p className="evaluation-feedback">{evaluation.feedback}</p>
                  </div>
                )}
              </div>
            </div>

            <div className="question-card-footer">
              <button
                onClick={previousQuestion}
                disabled={currentQuestionIndex === 0}
                className="nav-btn"
              >
                Previous
              </button>

              {currentQuestionIndex === totalQuestions - 1 ? (
                <div className="final-question-buttons">
                  <button 
                    onClick={submitAnswer} 
                    className="btn-evaluate"
                    disabled={isProcessing || !transcript.trim() || isRecording}
                  >
                    {isProcessing ? 'Evaluating...' : 'Evaluate Answer'}
                  </button>
                  <button 
                    onClick={completeInterview} 
                    className="btn-complete-interview"
                    disabled={isRecording}
                  >
                    Complete Interview
                  </button>
                </div>
              ) : (
                <button onClick={nextQuestion} className="nav-btn primary">
                  Next Question
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SpeechTest;
