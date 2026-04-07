import React, { useState, useEffect } from 'react';
import './ProcessingStatus.css';

const STEPS = [
  'Extracting frames and audio',
  'Transcribing audio',
  'Performing OCR on frames',
  'Detecting logos',
  'Checking compliance rules',
  'Preparing frames',
  'Generating report',
];

function ProcessingStatus({ progress, currentStep, error, errorCode }) {
  const [checkpoints, setCheckpoints] = useState([]);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, [startTime]);

  useEffect(() => {
    const newCheckpoints = STEPS.map((step, index) => {
      const stepProgress = (index / STEPS.length) * 100;
      let status = 'pending';

      if (progress >= stepProgress) {
        status = 'completed';
      }
      if (currentStep.includes(step) || (progress < stepProgress + 15 && progress > stepProgress)) {
        status = 'current';
      }

      return { step, status };
    });

    setCheckpoints(newCheckpoints);
  }, [progress, currentStep]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const getErrorAdvice = (code) => {
    const advice = {
      'NO_FILE': 'Please select a video file first',
      'INVALID_FORMAT': 'Please use one of the supported formats: MP4, MOV, MKV, AVI, or WebM',
      'FILE_TOO_LARGE': 'Your file exceeds the 5GB limit. Try compressing or splitting the video',
      'PROCESSING_ERROR': 'An error occurred during processing. Check the backend logs for details',
      'INVALID_FORMAT_ERROR': 'The file format is not supported or the file is corrupted',
    };
    return advice[code] || 'Please try again or contact support if the problem persists';
  };

  if (error) {
    return (
      <div className="processing-status">
        <div className="status-card error-card">
          <div className="status-header error-header">
            <span className="error-icon">!</span>
            <span>Processing Failed</span>
          </div>
          <div className="error-message">
            <div className="error-title">{error}</div>
            {errorCode && (
              <div className="error-code">
                Error Code: <code>{errorCode}</code>
              </div>
            )}
            <div className="error-advice">
              {getErrorAdvice(errorCode)}
            </div>
          </div>
          <div className="error-suggestions">
            <h4>What you can try:</h4>
            <ul>
              <li>Check that your internet connection is stable</li>
              <li>Verify the video file is not corrupted</li>
              <li>Try with a smaller video file</li>
              <li>Use the "Tiny" model for faster processing</li>
              <li>Check the browser console for more details (F12)</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="processing-status">
      <div className="status-card">
        <div className="status-header">
          <div className="spinner"></div>
          <div className="status-text">
            <div className="current-step">{currentStep || 'Processing...'}</div>
            <div className="elapsed-time">{formatTime(elapsedTime)}</div>
          </div>
        </div>

        <div className="status-checkpoints">
          {checkpoints.map((checkpoint, index) => (
            <div key={index} className="status-checkpoint">
              <div className={`checkpoint-icon ${checkpoint.status}`}>
                {checkpoint.status === 'completed' && '✓'}
                {checkpoint.status === 'current' && <div className="pulse"></div>}
                {checkpoint.status === 'pending' && '○'}
              </div>
              <span className={checkpoint.status}>{checkpoint.step}</span>
            </div>
          ))}
        </div>

        <div className="progress-container">
          <div className="progress-bar-background">
            <div
              className="progress-bar-fill"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div className="progress-text">
            <span>Processing</span>
            <span className="progress-percentage">{Math.round(progress)}%</span>
          </div>
        </div>
      </div>

      <div className="processing-info">
        <p>This may take a few minutes depending on video length and selected model size...</p>
        <p>Tip: Keep this window open. Do not refresh the page.</p>
      </div>
    </div>
  );
}

export default ProcessingStatus;
