import React, { useState, useRef } from 'react';
import axios from 'axios';
import './VideoUploader.css';

const SUPPORTED_FORMATS = ['.mp4', '.mov', '.mkv', '.avi', '.webm'];
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

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

  const handleFileSelect = (file) => {
    const extension = '.' + file.name.split('.').pop().toLowerCase();

    if (!SUPPORTED_FORMATS.includes(extension)) {
      onProcessingError({
        message: `Unsupported format. Please use: ${SUPPORTED_FORMATS.join(', ')}`,
      });
      return;
    }

    if (file.size > 5 * 1024 * 1024 * 1024) {
      // 5GB limit
      onProcessingError({
        message: 'File size exceeds 5GB limit',
      });
      return;
    }

    setSelectedFile(file);
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

  const getModelSpeedInfo = (size) => {
    const info = {
      tiny: '⚡ Ultra-fast (~5-10s per minute)',
      base: '🚀 Fast (~10-20s per minute)',
      small: '⏱️ Medium (~20-30s per minute)',
      medium: '⏳ Slower (~40-60s per minute)',
      'large-v3': '🐢 Very Slow (~60-120s per minute)',
    };
    return info[size] || '';
  };

  const handleProcess = async () => {
    if (!selectedFile) {
      onProcessingError({ message: 'Please select a video file' });
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
        }
      );

      onProcessingProgress('Processing video...', 40);

      // Poll for processing completion
      let processingDone = false;
      let jobId = response.data.jobId || response.data.id;
      let attempts = 0;
      const maxAttempts = 300; // 5 minutes with 1-second intervals

      while (!processingDone && attempts < maxAttempts) {
        await new Promise((resolve) => setTimeout(resolve, 1000));

        try {
          const statusResponse = await axios.get(
            `${API_BASE_URL}/api/job-status/${jobId}`
          );

          const status = statusResponse.data;
          if (status.status === 'completed') {
            processingDone = true;
            onProcessingProgress('Processing complete!', 100);
            onProcessingComplete(status.data);
          } else if (status.status === 'error') {
            throw new Error(status.message || 'Processing failed');
          } else if (status.progress) {
            onProcessingProgress(status.message || 'Processing...', 40 + status.progress * 0.5);
          }
        } catch (error) {
          if (error.response?.status === 404) {
            // Job not found yet, continue polling
          } else {
            throw error;
          }
        }

        attempts++;
      }

      if (!processingDone) {
        throw new Error('Processing timeout - please try again');
      }
    } catch (error) {
      console.error('Error:', error);
      onProcessingError({
        message: error.response?.data?.message || error.message || 'An error occurred',
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
      <div
        className={`upload-area ${dragOver ? 'dragover' : ''}`}
        onDrop={handleDrop}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden-input"
          onChange={handleFileInputChange}
          accept={SUPPORTED_FORMATS.join(',')}
          disabled={isProcessing}
        />

        <div className="upload-icon">📹</div>
        <div className="upload-text">
          <h3>Drag & drop your video</h3>
          <p>or click to browse</p>
        </div>

        {selectedFile ? (
          <div className="selected-file">
            <h4>✓ Selected: {selectedFile.name}</h4>
            <div className="file-info">
              <span>Size: {formatFileSize(selectedFile.size)}</span>
              <span>Type: {selectedFile.type}</span>
            </div>
          </div>
        ) : (
          <div className="supported-formats">
            Supported formats: {SUPPORTED_FORMATS.join(', ')}
          </div>
        )}
      </div>

      <div className="settings">
        <h4>⚙️ Processing Settings</h4>
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
            />
          </div>
          <div className="setting-input">
            <label>Transcription Model Size</label>
            <select
              value={settings.modelSize}
              onChange={(e) => handleSettingChange('modelSize', e.target.value)}
              disabled={isProcessing}
            >
              <option value="tiny">Tiny - Ultra-fast (~5-10s/min)</option>
              <option value="base">Base - Fast (~10-20s/min, Better accuracy)</option>
              <option value="small">Small - Medium (~20-30s/min)</option>
              <option value="medium">Medium - Slower (~40-60s/min)</option>
              <option value="large-v3">Large - Very Slow (~60-120s/min, Best accuracy)</option>
            </select>
            <div style={{ fontSize: '12px', color: '#999', marginTop: '6px' }}>
              💡 Times shown are per minute of audio. With 16GB+ RAM and GPU, speeds are 2-3x faster.
            </div>
          </div>
        </div>

        <div className="setting-group">
          <div className="setting-input">
            <label>
              <input
                type="checkbox"
                checked={settings.wordLevel}
                onChange={(e) => handleSettingChange('wordLevel', e.target.checked)}
                disabled={isProcessing}
              />
              {' '}Word-level timestamps
            </label>
          </div>
        </div>
      </div>

      <div className="upload-controls">
        <button
          className="button button-primary"
          onClick={handleProcess}
          disabled={!selectedFile || isProcessing}
        >
          🚀 Process Video
        </button>
      </div>
    </div>
  );
}

export default VideoUploader;
