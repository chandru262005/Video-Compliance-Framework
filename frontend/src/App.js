import React, { useState, useEffect } from 'react';
import './App.css';
import VideoUploader from './components/VideoUploader';
import ProcessingStatus from './components/ProcessingStatus';
import ResultsDisplay from './components/ResultsDisplay';

function App() {
  const [processingState, setProcessingState] = useState({
    isProcessing: false,
    progress: 0,
    currentStep: '',
    error: null,
    errorCode: null,
  });

  const [results, setResults] = useState(null);
  const [apiHealth, setApiHealth] = useState('unknown');

  // Check API health on mount
  useEffect(() => {
    checkApiHealth();
    const healthInterval = setInterval(checkApiHealth, 30000); // Check every 30s
    return () => clearInterval(healthInterval);
  }, []);

  const checkApiHealth = async () => {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      await fetch(`${apiUrl}/api/health`, {
        method: 'GET',
        mode: 'no-cors'
      });
      setApiHealth('connected');
    } catch (error) {
      console.error('API health check failed:', error);
      setApiHealth('disconnected');
    }
  };

  const handleUploadStart = () => {
    setProcessingState({
      isProcessing: true,
      progress: 0,
      currentStep: 'Validating file...',
      error: null,
      errorCode: null,
    });
  };

  const handleProcessingProgress = (step, progress) => {
    setProcessingState({
      isProcessing: true,
      progress,
      currentStep: step,
      error: null,
      errorCode: null,
    });
  };

  const handleProcessingComplete = (data) => {
    setProcessingState({
      isProcessing: false,
      progress: 100,
      currentStep: 'Complete',
      error: null,
      errorCode: null,
    });
    setResults(data);
  };

  const handleProcessingError = (error) => {
    console.error('Processing error:', error);
    setProcessingState({
      isProcessing: false,
      progress: 0,
      currentStep: '',
      error: error.message || 'An error occurred during processing',
      errorCode: error.code || null,
    });
    setResults(null);
  };

  const handleReset = () => {
    setProcessingState({
      isProcessing: false,
      progress: 0,
      currentStep: '',
      error: null,
      errorCode: null,
    });
    setResults(null);
  };

  const getApiStatusIndicator = () => {
    if (apiHealth === 'connected') return '●';
    if (apiHealth === 'disconnected') return '●';
    return '●';
  };

  return (
    <div className="app">
      <div className="api-status" title={`API Status: ${apiHealth}`}>
        <span className="status-indicator">{getApiStatusIndicator()}</span>
        <span className="status-text">{apiHealth}</span>
      </div>

      <div className="app-container">
        <div className="header">
          <h1>Video Compliance Framework</h1>
          <p>Extract frames, audio, and transcriptions from video content</p>
        </div>

        <div className="content">
          {!results && (
            <VideoUploader
              onUploadStart={handleUploadStart}
              onProcessingProgress={handleProcessingProgress}
              onProcessingComplete={handleProcessingComplete}
              onProcessingError={handleProcessingError}
              isProcessing={processingState.isProcessing}
            />
          )}

          {processingState.isProcessing && (
            <ProcessingStatus
              progress={processingState.progress}
              currentStep={processingState.currentStep}
              error={processingState.error}
              errorCode={processingState.errorCode}
            />
          )}

          {results && (
            <ResultsDisplay
              results={results}
              onReset={handleReset}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
