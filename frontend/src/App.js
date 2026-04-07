import React, { useState, useEffect } from 'react';
import './App.css';
import './styles/Header.css';
import './styles/Sidebar.css';
import './styles/Dashboard.css';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
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
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState('dashboard'); // 'dashboard', 'upload', 'settings', 'account'

  // Check API health on mount
  useEffect(() => {
    checkApiHealth();
    const healthInterval = setInterval(checkApiHealth, 30000); // Check every 30s
    return () => clearInterval(healthInterval);
  }, []);

  const checkApiHealth = async () => {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
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
    setCurrentPage('dashboard');
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const navigateTo = (page) => {
    setCurrentPage(page);
    setSidebarOpen(false); // Close sidebar on mobile after navigation
  };

  return (
    <div className="app">
      <Header />
      <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} navigateTo={navigateTo} currentPage={currentPage} />

      <main className="main-content">
        {currentPage === 'dashboard' && (
          <Dashboard navigateTo={navigateTo} />
        )}

        {currentPage === 'upload' && (
          <>
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
          </>
        )}

        {currentPage === 'settings' && (
          <div style={{ padding: '40px 20px' }}>
            <h2>Settings</h2>
            <p>Settings page coming soon...</p>
          </div>
        )}

        {currentPage === 'account' && (
          <div style={{ padding: '40px 20px' }}>
            <h2>Account</h2>
            <p>Account page coming soon...</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
