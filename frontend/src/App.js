import React, { useState } from 'react';
import './App.css';
import './styles/Header.css';
import Header from './components/Header';
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

  return (
    <div className="app">
      <Header />

      <main className="main-content">
        {!results && (
          <div className="upload-section">
            <VideoUploader
              onUploadStart={handleUploadStart}
              onProcessingProgress={handleProcessingProgress}
              onProcessingComplete={handleProcessingComplete}
              onProcessingError={handleProcessingError}
              isProcessing={processingState.isProcessing}
            />
          </div>
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
      </main>
    </div>
  );
}

export default App;
