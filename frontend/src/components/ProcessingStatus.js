import React, { useState, useEffect } from 'react';
import './ProcessingStatus.css';

const STEPS = [
  'Uploading video file',
  'Extracting frames',
  'Extracting audio',
  'Transcribing audio',
  'Generating results',
];

function ProcessingStatus({ progress, currentStep, error }) {
  const [checkpoints, setCheckpoints] = useState([]);

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

  if (error) {
    return (
      <div className="processing-status">
        <div className="status-card">
          <div className="status-header">
            <span className="error-icon">❌</span>
            Error Processing Video
          </div>
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
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
          {currentStep || 'Processing...'}
        </div>

        <div className="status-checkpoints">
          {checkpoints.map((checkpoint, index) => (
            <div key={index} className="status-checkpoint">
              <div className={`checkpoint-icon ${checkpoint.status}`}>
                {checkpoint.status === 'completed' && '✓'}
                {checkpoint.status === 'current' && '●'}
              </div>
              <span>{checkpoint.step}</span>
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
            <span>{Math.round(progress)}%</span>
          </div>
        </div>
      </div>

      <p style={{ textAlign: 'center', marginTop: '20px', color: '#999', fontSize: '14px' }}>
        This may take a few minutes depending on video length and selected model size...
      </p>
    </div>
  );
}

export default ProcessingStatus;
