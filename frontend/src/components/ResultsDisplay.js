import React, { useState } from 'react';
import './ResultsDisplay.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function ResultsDisplay({ results, onReset }) {
  const [activeTab, setActiveTab] = useState('metadata');
  const [copied, setCopied] = useState(false);

  const handleDownload = (filename, filepath) => {
    const url = `${API_BASE_URL}/api/download?file=${encodeURIComponent(filepath)}`;
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const handleCopyTranscription = () => {
    const transcriptionText = results.transcription || 'No transcription available';
    navigator.clipboard.writeText(transcriptionText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const downloadFramesAsZip = () => {
    handleDownload('frames.zip', results.framesZipPath || 'frames');
  };

  const downloadAudio = () => {
    handleDownload(
      'audio.wav',
      results.audioPath || 'audio.wav'
    );
  };

  const downloadTranscription = () => {
    const text = results.transcription || 'No transcription available';
    const element = document.createElement('a');
    element.setAttribute(
      'href',
      'data:text/plain;charset=utf-8,' + encodeURIComponent(text)
    );
    element.setAttribute('download', 'transcription.txt');
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const downloadMetadata = () => {
    const metadata = {
      videoDuration: results.duration,
      originalFps: results.originalFps,
      sampleFps: results.sampleFps,
      frameCount: results.frames?.length || 0,
      extractedAt: new Date().toISOString(),
    };
    const element = document.createElement('a');
    element.setAttribute(
      'href',
      'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(metadata, null, 2))
    );
    element.setAttribute('download', 'metadata.json');
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="results-display">
      <div className="results-header">
        <h2>✅ Processing Complete!</h2>
      </div>

      <div className="results-tabs">
        <button
          className={`tab-button ${activeTab === 'metadata' ? 'active' : ''}`}
          onClick={() => setActiveTab('metadata')}
        >
          📊 Metadata
        </button>
        <button
          className={`tab-button ${activeTab === 'transcription' ? 'active' : ''}`}
          onClick={() => setActiveTab('transcription')}
        >
          📝 Transcription
        </button>
        <button
          className={`tab-button ${activeTab === 'frames' ? 'active' : ''}`}
          onClick={() => setActiveTab('frames')}
        >
          🖼️ Frames
        </button>
        <button
          className={`tab-button ${activeTab === 'downloads' ? 'active' : ''}`}
          onClick={() => setActiveTab('downloads')}
        >
          ⬇️ Downloads
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'metadata' && (
          <div>
            <div className="metadata-grid">
              <div className="metadata-card">
                <h4>Video Duration</h4>
                <div className="value">{(results.duration || 0).toFixed(2)}s</div>
              </div>
              <div className="metadata-card">
                <h4>Original FPS</h4>
                <div className="value">{(results.originalFps || 0).toFixed(2)}</div>
              </div>
              <div className="metadata-card">
                <h4>Sample FPS</h4>
                <div className="value">{(results.sampleFps || 2).toFixed(2)}</div>
              </div>
              <div className="metadata-card">
                <h4>Total Frames</h4>
                <div className="value">{results.frames?.length || 0}</div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'transcription' && (
          <div>
            <div className="transcription-section">
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
                <h3>Audio Transcription</h3>
                <button className="copy-button" onClick={handleCopyTranscription}>
                  📋 Copy
                </button>
                {copied && <span className="copy-feedback">Copied!</span>}
              </div>
              <div className="transcription-content">
                {results.transcription || 'No transcription available'}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'frames' && (
          <div>
            {results.frames && results.frames.length > 0 ? (
              <div className="frames-grid">
                {results.frames.map((frame, index) => (
                  <div key={index} className="frame-card">
                    <img
                      src={frame.preview || frame.file_path}
                      alt={`Frame ${frame.frame_id}`}
                      className="frame-image"
                    />
                    <div className="frame-info">
                      <div className="frame-id">Frame #{frame.frame_id}</div>
                      <div className="frame-timestamp">
                        {frame.timestamp_sec.toFixed(2)}s
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-frames">
                <p>No frames extracted. Please check your video file.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'downloads' && (
          <div>
            <div className="download-section">
              <button
                className="download-button"
                onClick={downloadTranscription}
                title="Download transcription as text file"
              >
                📄 Transcription (.txt)
              </button>
              <button
                className="download-button"
                onClick={downloadAudio}
                title="Download extracted audio file"
              >
                🔊 Audio (.wav)
              </button>
              <button
                className="download-button"
                onClick={downloadFramesAsZip}
                title="Download all frames as ZIP"
              >
                📦 Frames (.zip)
              </button>
              <button
                className="download-button"
                onClick={downloadMetadata}
                title="Download video metadata"
              >
                📋 Metadata (.json)
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="button-group">
        <button className="button button-primary" onClick={onReset}>
          🔄 Process Another Video
        </button>
      </div>
    </div>
  );
}

export default ResultsDisplay;
