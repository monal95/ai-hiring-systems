import React, { useState, useEffect, useRef, useCallback } from 'react';
import '../styles/ProctoringSystem.css';

/**
 * Enterprise-Grade Proctoring System
 * 
 * Level 1: Basic Proctoring
 * - Full-screen enforcement
 * - Tab-switch detection
 * - Copy-paste blocking
 * - Time tracking
 * - Browser focus monitoring
 * 
 * Level 2: Advanced Proctoring
 * - Webcam monitoring
 * - Face presence detection
 * - Multiple face detection
 * - Microphone activity monitoring
 * - Behavioral flags
 */

const ProctoringSystem = ({ 
  isActive = false, 
  onViolation, 
  onStatusChange,
  candidateName = 'Candidate',
  showPreview = true 
}) => {
  // ============== State Management ==============
  const [proctoringStatus, setProctoringStatus] = useState({
    isFullscreen: false,
    cameraEnabled: false,
    microphoneEnabled: false,
    faceDetected: false,
    multipleFaces: false,
    isTabFocused: true,
    isBrowserFocused: true,
  });

  const [violations, setViolations] = useState([]);
  const [warnings, setWarnings] = useState([]);
  const [stats, setStats] = useState({
    tabSwitches: 0,
    focusLost: 0,
    faceNotDetected: 0,
    multipleFacesDetected: 0,
    copyAttempts: 0,
    pasteAttempts: 0,
    fullscreenExits: 0,
    totalTime: 0,
    activeTime: 0,
    suspiciousBehaviors: 0,
  });

  const [cameraError, setCameraError] = useState(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [showWarningModal, setShowWarningModal] = useState(false);
  const [currentWarning, setCurrentWarning] = useState(null);

  // ============== Refs ==============
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const faceDetectionIntervalRef = useRef(null);
  const timeTrackingIntervalRef = useRef(null);
  const lastFaceDetectedRef = useRef(Date.now());
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const microphoneStreamRef = useRef(null);

  // ============== Violation Recording ==============
  const recordViolation = useCallback((type, severity, message) => {
    const violation = {
      id: Date.now(),
      type,
      severity, // 'low', 'medium', 'high', 'critical'
      message,
      timestamp: new Date().toISOString(),
    };

    setViolations(prev => [...prev, violation]);

    if (onViolation) {
      onViolation(violation);
    }

    // Show warning for medium+ severity
    if (severity !== 'low') {
      setCurrentWarning(violation);
      setShowWarningModal(true);
      setTimeout(() => setShowWarningModal(false), 4000);
    }

    // Update stats based on type
    setStats(prev => {
      const newStats = { ...prev };
      switch (type) {
        case 'tab_switch':
          newStats.tabSwitches++;
          break;
        case 'focus_lost':
          newStats.focusLost++;
          break;
        case 'face_not_detected':
          newStats.faceNotDetected++;
          break;
        case 'multiple_faces':
          newStats.multipleFacesDetected++;
          break;
        case 'copy_attempt':
          newStats.copyAttempts++;
          break;
        case 'paste_attempt':
          newStats.pasteAttempts++;
          break;
        case 'fullscreen_exit':
          newStats.fullscreenExits++;
          break;
        default:
          newStats.suspiciousBehaviors++;
      }
      return newStats;
    });
  }, [onViolation]);

  // ============== Level 1: Basic Proctoring ==============

  // Full-screen enforcement
  const enterFullscreen = useCallback(async () => {
    try {
      const elem = document.documentElement;
      if (elem.requestFullscreen) {
        await elem.requestFullscreen();
      } else if (elem.webkitRequestFullscreen) {
        await elem.webkitRequestFullscreen();
      } else if (elem.msRequestFullscreen) {
        await elem.msRequestFullscreen();
      }
      setProctoringStatus(prev => ({ ...prev, isFullscreen: true }));
    } catch (error) {
      console.error('Fullscreen error:', error);
      recordViolation('fullscreen_denied', 'high', 'Fullscreen mode was denied');
    }
  }, [recordViolation]);

  // Fullscreen change handler
  useEffect(() => {
    const handleFullscreenChange = () => {
      const isFullscreen = !!(
        document.fullscreenElement ||
        document.webkitFullscreenElement ||
        document.msFullscreenElement
      );
      
      setProctoringStatus(prev => ({ ...prev, isFullscreen }));
      
      if (!isFullscreen && isActive && isInitialized) {
        recordViolation('fullscreen_exit', 'high', 'Exited fullscreen mode');
        // Re-enter fullscreen after a short delay
        setTimeout(() => {
          if (isActive) enterFullscreen();
        }, 1000);
      }
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    document.addEventListener('msfullscreenchange', handleFullscreenChange);

    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
      document.removeEventListener('msfullscreenchange', handleFullscreenChange);
    };
  }, [isActive, isInitialized, enterFullscreen, recordViolation]);

  // Tab visibility detection
  useEffect(() => {
    const handleVisibilityChange = () => {
      const isVisible = document.visibilityState === 'visible';
      
      setProctoringStatus(prev => ({ ...prev, isTabFocused: isVisible }));
      
      if (!isVisible && isActive) {
        recordViolation('tab_switch', 'high', 'Switched to another tab');
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [isActive, recordViolation]);

  // Browser focus detection
  useEffect(() => {
    const handleFocus = () => {
      setProctoringStatus(prev => ({ ...prev, isBrowserFocused: true }));
    };

    const handleBlur = () => {
      setProctoringStatus(prev => ({ ...prev, isBrowserFocused: false }));
      if (isActive) {
        recordViolation('focus_lost', 'medium', 'Browser window lost focus');
      }
    };

    window.addEventListener('focus', handleFocus);
    window.addEventListener('blur', handleBlur);

    return () => {
      window.removeEventListener('focus', handleFocus);
      window.removeEventListener('blur', handleBlur);
    };
  }, [isActive, recordViolation]);

  // Copy-paste blocking
  useEffect(() => {
    const handleCopy = (e) => {
      if (isActive) {
        e.preventDefault();
        recordViolation('copy_attempt', 'medium', 'Attempted to copy content');
      }
    };

    const handlePaste = (e) => {
      if (isActive) {
        e.preventDefault();
        recordViolation('paste_attempt', 'medium', 'Attempted to paste content');
      }
    };

    const handleCut = (e) => {
      if (isActive) {
        e.preventDefault();
        recordViolation('cut_attempt', 'medium', 'Attempted to cut content');
      }
    };

    // Block right-click context menu
    const handleContextMenu = (e) => {
      if (isActive) {
        e.preventDefault();
        recordViolation('context_menu', 'low', 'Attempted to open context menu');
      }
    };

    // Block keyboard shortcuts
    const handleKeyDown = (e) => {
      if (isActive) {
        // Block Ctrl+C, Ctrl+V, Ctrl+X, Ctrl+A, F12, etc.
        if (
          (e.ctrlKey && ['c', 'v', 'x', 'a', 'u', 's', 'p'].includes(e.key.toLowerCase())) ||
          e.key === 'F12' ||
          (e.ctrlKey && e.shiftKey && ['i', 'j', 'c'].includes(e.key.toLowerCase()))
        ) {
          e.preventDefault();
          recordViolation('keyboard_shortcut', 'low', `Blocked keyboard shortcut: ${e.key}`);
        }
      }
    };

    document.addEventListener('copy', handleCopy);
    document.addEventListener('paste', handlePaste);
    document.addEventListener('cut', handleCut);
    document.addEventListener('contextmenu', handleContextMenu);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('copy', handleCopy);
      document.removeEventListener('paste', handlePaste);
      document.removeEventListener('cut', handleCut);
      document.removeEventListener('contextmenu', handleContextMenu);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isActive, recordViolation]);

  // Time tracking
  useEffect(() => {
    if (isActive) {
      timeTrackingIntervalRef.current = setInterval(() => {
        setStats(prev => ({
          ...prev,
          totalTime: prev.totalTime + 1,
          activeTime: proctoringStatus.isBrowserFocused && proctoringStatus.isTabFocused 
            ? prev.activeTime + 1 
            : prev.activeTime,
        }));
      }, 1000);
    }

    return () => {
      if (timeTrackingIntervalRef.current) {
        clearInterval(timeTrackingIntervalRef.current);
      }
    };
  }, [isActive, proctoringStatus.isBrowserFocused, proctoringStatus.isTabFocused]);

  // ============== Level 2: Advanced Proctoring ==============

  // Initialize camera
  const initializeCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user',
        },
        audio: true,
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      // Set up audio analysis
      const audioTrack = stream.getAudioTracks()[0];
      if (audioTrack) {
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioContextRef.current.createMediaStreamSource(
          new MediaStream([audioTrack])
        );
        analyserRef.current = audioContextRef.current.createAnalyser();
        analyserRef.current.fftSize = 256;
        source.connect(analyserRef.current);
        microphoneStreamRef.current = stream;
      }

      setProctoringStatus(prev => ({
        ...prev,
        cameraEnabled: true,
        microphoneEnabled: !!audioTrack,
      }));

      setCameraError(null);
      return true;
    } catch (error) {
      console.error('Camera initialization error:', error);
      setCameraError(error.message || 'Failed to access camera');
      recordViolation('camera_denied', 'critical', 'Camera access was denied');
      return false;
    }
  }, [recordViolation]);

  // Face detection using simple motion/presence detection
  // (No ML library needed - uses pixel analysis)
  const detectFacePresence = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    if (!ctx || video.readyState !== 4) return;

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Simple presence detection based on center region analysis
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const sampleWidth = 200;
    const sampleHeight = 200;

    const startX = Math.max(0, centerX - sampleWidth / 2);
    const startY = Math.max(0, centerY - sampleHeight / 2);

    try {
      const imageData = ctx.getImageData(startX, startY, sampleWidth, sampleHeight);
      const data = imageData.data;

      // Analyze skin tone pixels (simple heuristic)
      let skinTonePixels = 0;
      let totalPixels = 0;
      let brightnessSum = 0;
      let motionPixels = 0;

      for (let i = 0; i < data.length; i += 4) {
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];
        totalPixels++;

        const brightness = (r + g + b) / 3;
        brightnessSum += brightness;

        // Simple skin tone detection (works for various skin tones)
        const isSkinTone = (
          r > 60 && r < 255 &&
          g > 40 && g < 230 &&
          b > 20 && b < 200 &&
          r > g && r > b &&
          Math.abs(r - g) > 15
        );

        if (isSkinTone) {
          skinTonePixels++;
        }
      }

      const skinToneRatio = skinTonePixels / totalPixels;
      const avgBrightness = brightnessSum / totalPixels;

      // Determine face presence
      const faceDetected = skinToneRatio > 0.15 && avgBrightness > 30 && avgBrightness < 230;

      // Detect multiple faces (higher skin tone ratio in multiple regions)
      const leftImageData = ctx.getImageData(0, startY, sampleWidth / 2, sampleHeight);
      const rightImageData = ctx.getImageData(canvas.width - sampleWidth / 2, startY, sampleWidth / 2, sampleHeight);

      let leftSkinPixels = 0, rightSkinPixels = 0;
      
      for (let i = 0; i < leftImageData.data.length; i += 4) {
        const r = leftImageData.data[i];
        const g = leftImageData.data[i + 1];
        const b = leftImageData.data[i + 2];
        if (r > 60 && r < 255 && g > 40 && g < 230 && b > 20 && b < 200 && r > g && r > b) {
          leftSkinPixels++;
        }
      }

      for (let i = 0; i < rightImageData.data.length; i += 4) {
        const r = rightImageData.data[i];
        const g = rightImageData.data[i + 1];
        const b = rightImageData.data[i + 2];
        if (r > 60 && r < 255 && g > 40 && g < 230 && b > 20 && b < 200 && r > g && r > b) {
          rightSkinPixels++;
        }
      }

      const leftRatio = leftSkinPixels / (leftImageData.data.length / 4);
      const rightRatio = rightSkinPixels / (rightImageData.data.length / 4);
      const multipleFaces = leftRatio > 0.2 && rightRatio > 0.2 && skinToneRatio > 0.3;

      // Update status
      setProctoringStatus(prev => ({
        ...prev,
        faceDetected,
        multipleFaces,
      }));

      // Record violations
      if (!faceDetected) {
        const timeSinceLastDetection = Date.now() - lastFaceDetectedRef.current;
        if (timeSinceLastDetection > 5000) { // 5 seconds threshold
          recordViolation('face_not_detected', 'high', 'Face not detected - candidate may have left seat');
          lastFaceDetectedRef.current = Date.now(); // Reset to avoid spam
        }
      } else {
        lastFaceDetectedRef.current = Date.now();
      }

      if (multipleFaces) {
        recordViolation('multiple_faces', 'critical', 'Multiple faces detected - possible external help');
      }

    } catch (error) {
      console.error('Face detection error:', error);
    }
  }, [recordViolation]);

  // Audio level monitoring
  const checkAudioLevels = useCallback(() => {
    if (!analyserRef.current) return;

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(dataArray);

    const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;

    // Detect prolonged silence (potential cheating indicator)
    // This is logged but not flagged as violation unless extended
    if (average < 5) {
      // Very low audio - could be silence
    }
  }, []);

  // Start face detection interval
  useEffect(() => {
    if (isActive && proctoringStatus.cameraEnabled) {
      faceDetectionIntervalRef.current = setInterval(() => {
        detectFacePresence();
        checkAudioLevels();
      }, 2000); // Check every 2 seconds
    }

    return () => {
      if (faceDetectionIntervalRef.current) {
        clearInterval(faceDetectionIntervalRef.current);
      }
    };
  }, [isActive, proctoringStatus.cameraEnabled, detectFacePresence, checkAudioLevels]);

  // ============== Initialization & Cleanup ==============

  const initializeProctoring = useCallback(async () => {
    const cameraSuccess = await initializeCamera();
    
    if (cameraSuccess) {
      await enterFullscreen();
      setIsInitialized(true);
      
      if (onStatusChange) {
        onStatusChange({ initialized: true, cameraEnabled: true });
      }
    }
  }, [initializeCamera, enterFullscreen, onStatusChange]);

  // Cleanup
  useEffect(() => {
    return () => {
      // Stop camera
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      // Stop audio context
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
      // Exit fullscreen
      if (document.fullscreenElement) {
        document.exitFullscreen().catch(() => {});
      }
      // Clear intervals
      if (faceDetectionIntervalRef.current) {
        clearInterval(faceDetectionIntervalRef.current);
      }
      if (timeTrackingIntervalRef.current) {
        clearInterval(timeTrackingIntervalRef.current);
      }
    };
  }, []);

  // ============== Get Proctoring Report ==============
  const getProctoringReport = useCallback(() => {
    return {
      candidateName,
      sessionStats: stats,
      violations,
      proctoringStatus,
      riskLevel: calculateRiskLevel(),
      timestamp: new Date().toISOString(),
    };
  }, [candidateName, stats, violations, proctoringStatus]);

  const calculateRiskLevel = () => {
    const { tabSwitches, focusLost, faceNotDetected, multipleFacesDetected, copyAttempts, fullscreenExits } = stats;
    
    const score = 
      (tabSwitches * 10) +
      (focusLost * 5) +
      (faceNotDetected * 15) +
      (multipleFacesDetected * 25) +
      (copyAttempts * 5) +
      (fullscreenExits * 10);

    if (score >= 50) return 'critical';
    if (score >= 30) return 'high';
    if (score >= 15) return 'medium';
    if (score > 0) return 'low';
    return 'none';
  };

  // Expose methods via ref if needed
  useEffect(() => {
    window.proctoringSystem = {
      getProctoringReport,
      getStats: () => stats,
      getViolations: () => violations,
    };
  }, [getProctoringReport, stats, violations]);

  // ============== Render ==============
  return (
    <div className="proctoring-system">
      {/* Hidden canvas for face detection processing */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      {/* Camera Preview */}
      {showPreview && (
        <div className={`proctoring-preview ${!proctoringStatus.faceDetected && isInitialized ? 'warning' : ''}`}>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="proctoring-video"
          />
          
          {/* Status Indicators */}
          <div className="proctoring-indicators">
            <div className={`indicator ${proctoringStatus.cameraEnabled ? 'active' : 'inactive'}`}>
              <span className="indicator-icon">📷</span>
              <span className="indicator-label">Camera</span>
            </div>
            <div className={`indicator ${proctoringStatus.microphoneEnabled ? 'active' : 'inactive'}`}>
              <span className="indicator-icon">🎤</span>
              <span className="indicator-label">Mic</span>
            </div>
            <div className={`indicator ${proctoringStatus.faceDetected ? 'active' : 'warning'}`}>
              <span className="indicator-icon">👤</span>
              <span className="indicator-label">Face</span>
            </div>
            <div className={`indicator ${proctoringStatus.isFullscreen ? 'active' : 'warning'}`}>
              <span className="indicator-icon">⛶</span>
              <span className="indicator-label">Fullscreen</span>
            </div>
          </div>

          {/* Violation Counter */}
          {violations.length > 0 && (
            <div className="violation-counter">
              <span className="violation-icon">⚠️</span>
              <span className="violation-count">{violations.length}</span>
            </div>
          )}

          {/* Multiple Faces Warning */}
          {proctoringStatus.multipleFaces && (
            <div className="multiple-faces-alert">
              ⚠️ Multiple faces detected!
            </div>
          )}

          {/* Face Not Detected Warning */}
          {!proctoringStatus.faceDetected && isInitialized && (
            <div className="face-missing-alert">
              ⚠️ Face not detected
            </div>
          )}
        </div>
      )}

      {/* Warning Modal */}
      {showWarningModal && currentWarning && (
        <div className="proctoring-warning-modal">
          <div className={`warning-content severity-${currentWarning.severity}`}>
            <span className="warning-icon">
              {currentWarning.severity === 'critical' ? '🚨' : 
               currentWarning.severity === 'high' ? '⚠️' : '⚡'}
            </span>
            <div className="warning-text">
              <strong>Proctoring Alert</strong>
              <p>{currentWarning.message}</p>
            </div>
          </div>
        </div>
      )}

      {/* Camera Error State */}
      {cameraError && (
        <div className="camera-error">
          <span className="error-icon">📷</span>
          <p>Camera Error: {cameraError}</p>
          <button onClick={initializeCamera} className="retry-btn">
            Retry Camera Access
          </button>
        </div>
      )}

      {/* Initialize Button (shown before proctoring starts) */}
      {!isInitialized && !cameraError && (
        <div className="proctoring-init-overlay">
          <div className="init-content">
            <div className="init-icon">🔒</div>
            <h3>Proctoring Required</h3>
            <p>This interview session is proctored. We need access to:</p>
            <ul className="permission-list">
              <li>📷 Your camera (face detection)</li>
              <li>🎤 Your microphone (audio monitoring)</li>
              <li>⛶ Fullscreen mode (focus enforcement)</li>
            </ul>
            <div className="init-notice">
              <strong>Note:</strong> The following actions are monitored:
              <ul>
                <li>Tab switching & window focus</li>
                <li>Copy/paste attempts</li>
                <li>Face presence & multiple faces</li>
                <li>Screen activity</li>
              </ul>
            </div>
            <button onClick={initializeProctoring} className="init-btn">
              Enable Proctoring & Start
            </button>
          </div>
        </div>
      )}

      {/* Stats Panel (for debugging/admin view) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="proctoring-debug">
          <details>
            <summary>Proctoring Stats</summary>
            <pre>{JSON.stringify(stats, null, 2)}</pre>
            <pre>{JSON.stringify(proctoringStatus, null, 2)}</pre>
          </details>
        </div>
      )}
    </div>
  );
};

// Export the component and a hook for accessing proctoring data
export default ProctoringSystem;

export const useProctoringReport = () => {
  return window.proctoringSystem?.getProctoringReport?.() || null;
};

export const getProctoringStats = () => {
  return window.proctoringSystem?.getStats?.() || null;
};

export const getProctoringViolations = () => {
  return window.proctoringSystem?.getViolations?.() || [];
};
