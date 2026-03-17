import React, { useState } from 'react';
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
  });

  const [results, setResults] = useState(null);

  const handleUploadStart = () => {
    setProcessingState({
      isProcessing: true,
      progress: 0,
      currentStep: 'Uploading video...',
      error: null,
    });
  };

  const handleProcessingProgress = (step, progress) => {
    setProcessingState({
      isProcessing: true,
      progress,
      currentStep: step,
      error: null,
    });
  };

  const handleProcessingComplete = (data) => {
    setProcessingState({
      isProcessing: false,
      progress: 100,
      currentStep: 'Complete',
      error: null,
    });
    setResults(data);
  };

  const handleProcessingError = (error) => {
    setProcessingState({
      isProcessing: false,
      progress: 0,
      currentStep: '',
      error: error.message || 'An error occurred during processing',
    });
    setResults(null);
  };

  const handleReset = () => {
    setProcessingState({
      isProcessing: false,
      progress: 0,
      currentStep: '',
      error: null,
    });
    setResults(null);
  };

  return (
    <div className="app">
      <div className="app-container">
        <div className="header">
          <h1>🎬 Video Compliance Framework</h1>
          <p>Extract frames, audio, and transcriptions from your videos</p>
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
