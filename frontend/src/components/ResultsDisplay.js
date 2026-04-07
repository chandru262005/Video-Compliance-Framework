import React, { useState } from 'react';
import './ResultsDisplay.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function ResultsDisplay({ results, onReset }) {
  const [activeTab, setActiveTab] = useState('metadata');
  const [copied, setCopied] = useState(false);
  const [selectedFrame, setSelectedFrame] = useState(null);

  const handleDownload = (filename, filepath) => {
    const url = `${API_BASE_URL}/api/download?file=${encodeURIComponent(filepath)}`;
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'download';
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
    if (results.framesZipPath) {
      handleDownload('frames.zip', results.framesZipPath);
    }
  };

  const downloadAudio = () => {
    if (results.audioPath) {
      handleDownload('audio.wav', results.audioPath);
    }
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

  const downloadComplianceReport = (format = 'json') => {
    const jobId = results.jobId || 'unknown';
    const url = `${API_BASE_URL}/api/download-report/${jobId}?format=${format}`;
    const a = document.createElement('a');
    a.href = url;
    const filename = `compliance_report.${format === 'html' ? 'html' : format === 'csv' ? 'csv' : 'json'}`;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const getFrameUrl = (frame) => {
    // If preview is a base64 data URL, use it directly
    if (frame.preview && frame.preview.startsWith('data:')) {
      return frame.preview;
    }
    // Otherwise, construct API URL
    if (frame.preview || frame.file_path) {
      return `${API_BASE_URL}/${frame.preview || frame.file_path}`;
    }
    return null;
  };

  return (
    <div className="results-display">
      <div className="results-header">
        <h2>Processing Complete</h2>
        <p className="results-summary">
          {results.frames?.length || 0} frames extracted • {(results.duration || 0).toFixed(1)}s video • {results.sampleFps}fps sample rate
        </p>
      </div>

      <div className="results-tabs">
        <button
          className={`tab-button ${activeTab === 'metadata' ? 'active' : ''}`}
          onClick={() => setActiveTab('metadata')}
          title="Video metadata and statistics"
        >
          Metadata
        </button>
        <button
          className={`tab-button ${activeTab === 'transcription' ? 'active' : ''}`}
          onClick={() => setActiveTab('transcription')}
          title="Transcribed audio text"
        >
          Transcription
        </button>
        <button
          className={`tab-button ${activeTab === 'frames' ? 'active' : ''}`}
          onClick={() => setActiveTab('frames')}
          title="Preview extracted frames"
        >
          Frames ({results.frames?.length || 0})
        </button>
        <button
          className={`tab-button ${activeTab === 'compliance' ? 'active' : ''}`}
          onClick={() => setActiveTab('compliance')}
          title="Compliance and analysis report"
        >
          Compliance Report
        </button>
        <button
          className={`tab-button ${activeTab === 'downloads' ? 'active' : ''}`}
          onClick={() => setActiveTab('downloads')}
          title="Download processed files"
        >
          Downloads
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
              <div className="metadata-card">
                <h4>Estimated Size</h4>
                <div className="value">{((results.frames?.length || 0) * 2).toFixed(0)} MB</div>
              </div>
              <div className="metadata-card">
                <h4>Processing Time</h4>
                <div className="value">~Few min</div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'transcription' && (
          <div>
            <div className="transcription-section">
              <div className="transcription-header">
                <h3>Audio Transcription</h3>
                <button className="copy-button" onClick={handleCopyTranscription}>
                  {copied ? 'Copied!' : 'Copy'}
                </button>
              </div>
              <div className="transcription-content">
                {results.transcription ? (
                  <p>{results.transcription}</p>
                ) : (
                  <p className="no-data">No transcription available</p>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'frames' && (
          <div>
            {results.frames && results.frames.length > 0 ? (
              <>
                {selectedFrame && (
                  <div className="frame-viewer">
                    <div className="frame-viewer-header">
                      <h3>Frame Preview</h3>
                      <button className="close-button" onClick={() => setSelectedFrame(null)}>×</button>
                    </div>
                    <div className="frame-viewer-content">
                      <img
                        src={getFrameUrl(selectedFrame)}
                        alt={`Frame ${selectedFrame.frame_id}`}
                        className="frame-viewer-image"
                      />
                      <div className="frame-viewer-info">
                        <p><strong>Frame ID:</strong> {selectedFrame.frame_id}</p>
                        <p><strong>Timestamp:</strong> {selectedFrame.timestamp_sec.toFixed(3)}s</p>
                      </div>
                    </div>
                  </div>
                )}
                <div className="frames-grid">
                  {results.frames.map((frame, index) => {
                    const imageUrl = getFrameUrl(frame);
                    return (
                      <div key={index} className="frame-card" onClick={() => setSelectedFrame(frame)}>
                        {imageUrl ? (
                          <img
                            src={imageUrl}
                            alt={`Frame ${frame.frame_id}`}
                            className="frame-image"
                            onError={(e) => {
                              e.target.style.background = '#f0f0f0';
                              e.target.style.display = 'none';
                            }}
                          />
                        ) : (
                          <div className="frame-placeholder">No Preview</div>
                        )}
                        <div className="frame-info">
                          <div className="frame-id">Frame #{frame.frame_id}</div>
                          <div className="frame-timestamp">
                            {frame.timestamp_sec.toFixed(2)}s
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </>
            ) : (
              <div className="no-frames">
                <p>😞 No frames could be extracted.</p>
                <p>Please check if the video file is valid and try again.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'compliance' && (
          <div>
            <div className="compliance-report">
              {results.compliance_report ? (
                <div className="report-container">
                  <div className="report-header">
                    <h3>Compliance Analysis Report</h3>
                    <div className={`status-badge ${results.compliance_report.overall_status.toLowerCase()}`}>
                      {results.compliance_report.overall_status}
                    </div>
                  </div>

                  <div className="report-download-options">
                    <button 
                      className="download-report-btn json-btn"
                      onClick={() => downloadComplianceReport('json')}
                      title="Download report as JSON"
                    >
                      📄 JSON
                    </button>
                    <button 
                      className="download-report-btn csv-btn"
                      onClick={() => downloadComplianceReport('csv')}
                      title="Download report as CSV"
                    >
                      📊 CSV
                    </button>
                    <button 
                      className="download-report-btn html-btn"
                      onClick={() => downloadComplianceReport('html')}
                      title="Download report as HTML"
                    >
                      🌐 HTML
                    </button>
                  </div>

                  <div className="score-display">
                    <div className="score-circle">
                      <span className="score-value">{results.compliance_report.overall_score}</span>
                      <span className="score-label">/100</span>
                    </div>
                  </div>

                  <div className="report-sections">
                    <div className="report-section">
                      <h4>Video Analysis</h4>
                      <div className="report-content">
                        <p>Duration: {results.compliance_report.video_analysis?.duration?.toFixed(2)}s</p>
                        <p>Frames: {results.compliance_report.video_analysis?.frame_count}</p>
                        <p>Sample Rate: {results.compliance_report.video_analysis?.fps} fps</p>
                      </div>
                    </div>

                    <div className="report-section">
                      <h4>Text Analysis (OCR)</h4>
                      <div className="report-content">
                        <p>{results.compliance_report.text_analysis?.summary}</p>
                        <p>Frames Analyzed: {results.compliance_report.text_analysis?.detected_frames}</p>
                        {results.compliance_report.text_analysis?.samples?.length > 0 && (
                          <div className="samples">
                            <strong>Detected Text Samples:</strong>
                            {results.compliance_report.text_analysis.samples.map((sample, idx) => (
                              <p key={idx} className="sample-text">
                                Frame {sample.frame_id}: "{sample.text}"
                              </p>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="report-section">
                      <h4>Logo Detection</h4>
                      <div className="report-content">
                        <p>{results.compliance_report.logo_analysis?.summary}</p>
                        <p>Total Logos Detected: {results.compliance_report.logo_analysis?.logos_detected}</p>
                      </div>
                    </div>

                    <div className="report-section">
                      <h4>Transcript Compliance</h4>
                      <div className="report-content">
                        <p>Status: {results.compliance_report.compliance?.transcript_validation}</p>
                        <p>Compliance Score: {results.compliance_report.compliance?.score}/100</p>
                        {results.compliance_report.compliance?.issues?.length > 0 && (
                          <div className="issues">
                            <strong>Issues Found:</strong>
                            <ul>
                              {results.compliance_report.compliance.issues.map((issue, idx) => (
                                <li key={idx} className="issue">{issue}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {results.compliance_report.compliance?.warnings?.length > 0 && (
                          <div className="warnings">
                            <strong>Warnings:</strong>
                            <ul>
                              {results.compliance_report.compliance.warnings.map((warning, idx) => (
                                <li key={idx} className="warning">{warning}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="report-footer">
                    <p>Generated: {new Date(results.compliance_report.timestamp).toLocaleString()}</p>
                  </div>
                </div>
              ) : (
                <div className="no-data">
                  <p>No compliance report available</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'downloads' && (
          <div>
            <div className="download-section">
              <div className="download-group">
                <h4>📥 Download Results</h4>
                <button
                  className="download-button"
                  onClick={downloadTranscription}
                  title="Download transcription as TXT file"
                >
                  📄 Transcription (TXT)
                </button>
                <button
                  className="download-button"
                  onClick={downloadAudio}
                  title="Download extracted audio WAV file"
                  disabled={!results.audioPath}
                >
                  🔊 Audio (WAV)
                </button>
                <button
                  className="download-button"
                  onClick={downloadFramesAsZip}
                  title="Download all frames as ZIP"
                  disabled={!results.framesZipPath || (results.frames?.length || 0) === 0}
                >
                  🎞️ Frames (ZIP)
                </button>
                <button
                  className="download-button"
                  onClick={downloadMetadata}
                  title="Download metadata as JSON"
                >
                  ⚙️ Metadata (JSON)
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="button-group">
        <button className="button button-primary" onClick={onReset}>
          ▶ Process Another Video
        </button>
      </div>
    </div>
  );
}

export default ResultsDisplay;
