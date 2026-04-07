import React from 'react';
import { ArrowRight } from 'lucide-react';
import '../styles/Dashboard.css';

function Dashboard({ navigateTo }) {
  const features = [
    {
      id: 1,
      title: 'Video Processing',
      description: 'Advanced video analysis and frame extraction for compliance checking',
      icon: '▶️',
      color: 'feature-blue',
      page: 'upload'
    },
    {
      id: 2,
      title: 'Compliance Analysis',
      description: 'Real-time compliance detection and reporting with detailed insights',
      icon: '✓',
      color: 'feature-green',
      page: 'upload'
    },
    {
      id: 3,
      title: 'OCR & Text Detection',
      description: 'Extract and analyze text content from video frames',
      icon: '📄',
      color: 'feature-purple',
      page: 'upload'
    },
    {
      id: 4,
      title: 'Smart Grid Analysis',
      description: 'Intelligent pattern recognition and anomaly detection',
      icon: '🔍',
      color: 'feature-teal',
      page: 'upload'
    },
    {
      id: 5,
      title: 'Security & Encryption',
      description: 'Enterprise-grade security for data protection and privacy',
      icon: '🔒',
      color: 'feature-orange',
      page: 'settings'
    },
    {
      id: 6,
      title: 'Audio Transcription',
      description: 'High-accuracy audio-to-text conversion with compliance validation',
      icon: '🎙️',
      color: 'feature-red',
      page: 'upload'
    },
  ];

  const handleCardClick = (page) => {
    navigateTo(page);
  };

  return (
    <div className="dashboard">
      <div className="dashboard-grid">
        {features.map((feature) => (
          <div 
            key={feature.id} 
            className={`feature-card ${feature.color}`}
            onClick={() => handleCardClick(feature.page)}
            style={{ cursor: 'pointer' }}
          >
            <div className="card-header">
              <span className="card-icon">{feature.icon}</span>
            </div>
            <div className="card-content">
              <h3 className="card-title">{feature.title}</h3>
              <p className="card-description">{feature.description}</p>
            </div>
            <div className="card-footer">
              <button className="btn btn-primary" onClick={(e) => {
                e.stopPropagation();
                handleCardClick(feature.page);
              }}>
                Get Started
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;
