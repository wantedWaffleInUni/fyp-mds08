import React from 'react';

const StatsDisplay = ({ metrics }) => {
  if (!metrics) {
    return null;
  }

  const formatValue = (value, decimals = 4) => {
    if (typeof value === 'number') {
      return value.toFixed(decimals);
    }
    return value;
  };

  const getQualityIndicator = (metric, value) => {
    switch (metric) {
      case 'entropy_encrypted':
        return value > 7.5 ? '🟢 Excellent' : value > 7.0 ? '🟡 Good' : '🔴 Poor';
      case 'npcr':
        return value > 99.5 ? '🟢 Excellent' : value > 99.0 ? '🟡 Good' : '🔴 Poor';
      case 'uaci':
        return value > 33.0 && value < 34.0 ? '🟢 Excellent' : 
               value > 32.0 && value < 35.0 ? '🟡 Good' : '🔴 Poor';
      default:
        return '';
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Encryption Quality Metrics</h3>
      </div>
      
      <div className="stats-grid">
        {metrics.entropy_original && (
          <div className="stat-card">
            <div className="stat-value">{formatValue(metrics.entropy_original)}</div>
            <div className="stat-label">Original Entropy (bits/pixel)</div>
          </div>
        )}
        
        {metrics.entropy_encrypted && (
          <div className="stat-card">
            <div className="stat-value">{formatValue(metrics.entropy_encrypted)}</div>
            <div className="stat-label">
              Encrypted Entropy (bits/pixel)
              <br />
              <small>{getQualityIndicator('entropy_encrypted', metrics.entropy_encrypted)}</small>
            </div>
          </div>
        )}
        
        {metrics.npcr && (
          <div className="stat-card">
            <div className="stat-value">{formatValue(metrics.npcr, 2)}%</div>
            <div className="stat-label">
              NPCR (Number of Pixel Change Rate)
              <br />
              <small>{getQualityIndicator('npcr', metrics.npcr)}</small>
            </div>
          </div>
        )}
        
        {metrics.uaci && (
          <div className="stat-card">
            <div className="stat-value">{formatValue(metrics.uaci, 2)}%</div>
            <div className="stat-label">
              UACI (Unified Average Changing Intensity)
              <br />
              <small>{getQualityIndicator('uaci', metrics.uaci)}</small>
            </div>
          </div>
        )}
      </div>
      
      <div className="mt-3">
        <h4>Metric Descriptions:</h4>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          <li><strong>Entropy:</strong> Measures randomness in pixel values. Higher values indicate better encryption.</li>
          <li><strong>NPCR:</strong> Percentage of pixels that changed between original and encrypted images. Should be close to 100%.</li>
          <li><strong>UACI:</strong> Average intensity difference between original and encrypted images. Ideal range: 33.0-34.0%.</li>
        </ul>
      </div>
    </div>
  );
};

export default StatsDisplay;
