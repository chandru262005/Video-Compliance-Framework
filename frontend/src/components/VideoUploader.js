import React, { useState, useRef } from 'react';
import axios from 'axios';
import './VideoUploader.css';

const SUPPORTED_FORMATS = ['.mp4', '.mov', '.mkv', '.avi', '.webm'];
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function VideoUploader({
  onUploadStart,
  onProcessingProgress,
  onProcessingComplete,
  onProcessingError,
  isProcessing,
}) {
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [settings, setSettings] = useState({
    sampleFps: 2.0,
    modelSize: 'tiny',
    wordLevel: false,
  });
  const [dragOver, setDragOver] = useState(false);
  const [validationError, setValidationError] = useState(null);

  const validateFile = (file) => {
    const extension = '.' + file.name.split('.').pop().toLowerCase();

    if (!SUPPORTED_FORMATS.includes(extension)) {
      const error = `Unsupported format: ${extension}. Supported: ${SUPPORTED_FORMATS.join(', ')}`;
      setValidationError(error);
      onProcessingError({ message: error, code: 'INVALID_FORMAT' });
      return false;
    }

    if (file.size > 5 * 1024 * 1024 * 1024) {
      const error = `File size (${formatFileSize(file.size)}) exceeds 5GB limit`;
      setValidationError(error);
      onProcessingError({ message: error, code: 'FILE_TOO_LARGE' });
      return false;
    }

    setValidationError(null);
    return true;
  };

  const handleFileSelect = (file) => {
    if (validateFile(file)) {
      setSelectedFile(file);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileInputChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleSettingChange = (key, value) => {
    setSettings((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleProcess = async () => {
    if (!selectedFile) {
      onProcessingError({ message: 'Please select a video file', code: 'NO_FILE' });
      return;
    }

    onUploadStart();

    const formData = new FormData();
    formData.append('video', selectedFile);
    formData.append('sampleFps', settings.sampleFps);
    formData.append('modelSize', settings.modelSize);
    formData.append('wordLevel', settings.wordLevel);

    try {
      onProcessingProgress('Uploading video file...', 10);

      const response = await axios.post(
        `${API_BASE_URL}/api/process-video`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            onProcessingProgress('Uploading video file...', Math.min(percentCompleted, 30));
          },
          timeout: 30000,
        }
      );

      onProcessingProgress('Processing video (this may take a while)...', 5);

      // Poll for processing completion
      let processingDone = false;
      let jobId = response.data.jobId || response.data.id;
      let attempts = 0;
      const maxAttempts = 600; // 10 minutes with 1-second intervals

      while (!processingDone && attempts < maxAttempts) {
        await new Promise((resolve) => setTimeout(resolve, 1000));

        try {
          const statusResponse = await axios.get(
            `${API_BASE_URL}/api/job-status/${jobId}`,
            { timeout: 10000 }
          );

          const status = statusResponse.data;
          
          if (status.status === 'completed') {
            processingDone = true;
            onProcessingProgress('Processing complete!', 100);
            onProcessingComplete(status.data);
          } else if (status.status === 'error') {
            throw new Error(status.error || status.message || 'Processing failed');
          } else {
            // Use server progress directly (already 0-100)
            const progressValue = status.progress || 50;
            onProcessingProgress(status.message || 'Processing...', progressValue);
          }
        } catch (error) {
          if (error.response?.status === 404) {
            // Job not found yet, continue polling
            onProcessingProgress('Processing started...', 10);
          } else if (error.code === 'ECONNABORTED') {
            // Timeout, just continue polling
            onProcessingProgress('Still processing...', 50);
          } else {
            throw error;
          }
        }

        attempts++;
      }

      if (!processingDone) {
        throw new Error('Processing timeout - the job took too long. Please try again with a shorter video or smaller model.');
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = error.response?.data?.error || error.message || 'An unexpected error occurred';
      const errorCode = error.response?.data?.code;
      onProcessingError({
        message: errorMessage,
        code: errorCode,
      });
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="video-uploader">
      {validationError && (
        <div className="validation-error">
          ⚠️ {validationError}
        </div>
      )}

      <div
        className={`upload-area ${dragOver ? 'dragover' : ''} ${isProcessing ? 'disabled' : ''}`}
        onDrop={handleDrop}
        onDragOver={(e) => {
          e.preventDefault();
          if (!isProcessing) setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onClick={!isProcessing ? handleClick : undefined}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden-input"
          onChange={handleFileInputChange}
          accept={SUPPORTED_FORMATS.join(',')}
          disabled={isProcessing}
        />

        <div className="upload-icon">▲</div>
        <div className="upload-text">
          <h3>Drag and drop your video here</h3>
          <p>or click to browse files</p>
        </div>

        {selectedFile ? (
          <div className="selected-file">
            <h4>Selected: {selectedFile.name}</h4>
            <div className="file-info">
              <span>Size: {formatFileSize(selectedFile.size)}</span>
              <span>Type: {selectedFile.type || selectedFile.name.split('.').pop()}</span>
            </div>
          </div>
        ) : (
          <div className="supported-formats">
            Supported formats: {SUPPORTED_FORMATS.join(', ')}
          </div>
        )}
      </div>

      <div className="settings">
        <h4>Processing Settings</h4>
        <div className="setting-group">
          <div className="setting-input">
            <label>Sample FPS (frames per second)</label>
            <input
              type="number"
              min="0.5"
              max="30"
              step="0.5"
              value={settings.sampleFps}
              onChange={(e) => handleSettingChange('sampleFps', parseFloat(e.target.value))}
              disabled={isProcessing}
              title="How many frames to extract per second"
            />
            <small>Range: 0.5 - 30</small>
          </div>
          <div className="setting-input">
            <label>Transcription Model Size</label>
            <select
              value={settings.modelSize}
              onChange={(e) => handleSettingChange('modelSize', e.target.value)}
              disabled={isProcessing}
              title="Larger models are more accurate but slower"
            >
              <option value="tiny">Tiny - Fastest (5-10s/min)</option>
              <option value="base">Base - Fast (10-20s/min)</option>
              <option value="small">Small - Medium (20-30s/min)</option>
              <option value="medium">Medium - Slower (40-60s/min)</option>
              <option value="large-v3">Large - Most accurate (60-120s/min)</option>
            </select>
            <small>Times are per minute of audio. With GPU, 2-3x faster.</small>
          </div>
        </div>

        <div className="setting-group">
          <div className="setting-input checkbox">
            <label>
              <input
                type="checkbox"
                checked={settings.wordLevel}
                onChange={(e) => handleSettingChange('wordLevel', e.target.checked)}
                disabled={isProcessing}
                title="Include word-level timestamps in transcription"
              />
              {' '}Word-level timestamps
            </label>
            <small>More detailed but slower transcription</small>
          </div>
        </div>
      </div>

      <div className="upload-controls">
        <button
          className="button button-primary"
          onClick={handleProcess}
          disabled={!selectedFile || isProcessing}
          title={!selectedFile ? 'Select a video file first' : 'Start processing'}
        >
          {isProcessing ? 'Processing...' : 'Process Video'}
        </button>
      </div>

      <div className="info-box">
        <h5>Tips</h5>
        <ul>
          <li>Use "Tiny" model for quick testing on smaller videos</li>
          <li>Use "Base" or "Small" for balanced speed/accuracy</li>
          <li>Processing time depends on video length and model size</li>
          <li>Larger videos may take 10-30+ minutes to process</li>
        </ul>
      </div>
    </div>
  );
}

export default VideoUploader;
