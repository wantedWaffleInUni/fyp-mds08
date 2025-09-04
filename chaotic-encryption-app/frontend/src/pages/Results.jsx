import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import StatsDisplay from '../components/StatsDisplay';
import { saveAs } from 'file-saver';

const Results = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [resultData, setResultData] = useState(null);
  const [operationType, setOperationType] = useState('');

  useEffect(() => {
    if (location.state?.data) {
      setResultData(location.state.data);
      setOperationType(location.state.type);
    } else {
      // Redirect to home if no data
      navigate('/');
    }
  }, [location.state, navigate]);

  const isTiffName = (name = '') => /\.tiff?$/i.test(name);
  const isTiffMime = (mime = '') => /tiff/i.test(mime || '');
  // Prefer what Encrypt sent; fall back to any fields your backend may provide
  const srcName =
    location.state?.srcFile?.name ||
    resultData?.original_filename ||
    resultData?.original_name ||
    '';
  const srcType =
    location.state?.srcFile?.type ||
    resultData?.original_mime ||
    '';
  const isOriginalTIFF = isTiffName(srcName) || isTiffMime(srcType);

    const dataUrlFor = (base64, filename = '', fallbackMime = 'image/png') => {
      const ext = (filename || '').toLowerCase();
      const mime =
        ext.endsWith('.tif') || ext.endsWith('.tiff') ? 'image/tiff' : fallbackMime;
      return `data:${mime};base64,${base64}`;
    };

  const handleDownload = async (imageData, filename) => {
    try {
      // Convert base64 to blob
      const response = await fetch(dataUrlFor(imageData, filename));
      const blob = await response.blob();

      // Download the file
      saveAs(blob, filename);
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  if (!resultData) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading results...</p>
      </div>
    );
  }

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            {operationType === 'encrypt' ? '🔒 Encryption Results' : '🔓 Decryption Results'}
          </h2>
          <p>
            {operationType === 'encrypt'
              ? 'Your image has been successfully encrypted using chaotic encryption'
              : 'Your encrypted image has been successfully decrypted'
            }
          </p>
          {operationType === 'encrypt' && resultData?.algorithm && (
            <p><strong>Algorithm:</strong> {resultData.algorithm.toUpperCase()}</p>
          )}
        </div>
      </div>

      {/* Image Comparison */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Image Comparison</h3>
        </div>

        {/* ✨ Global TIFF disclaimer (shown only when applicable) */}
        {operationType === 'encrypt' && isOriginalTIFF && (
          <div className="alert alert-warning" style={{ margin: '0 1rem 1rem' }}>
            <strong>Note:</strong> Browser preview for <code>.tif</code>/<code>.tiff</code> images
            isn’t supported. The file is encrypted correctly—use the download button to view it locally.
          </div>
        )}

        <div className="image-preview">
          {operationType === 'encrypt' ? (
            <>
              <div className="image-container">
                {/* If original is TIFF, don’t try to render an <img> */}
                {isOriginalTIFF ? (
                  <div className="no-preview-box"
                       style={{display:'grid',placeItems:'center',height:260,background:'#fafafa',borderRadius:12,border:'1px dashed #ccc',padding:16}}>
                    <div style={{textAlign:'center',color:'#6b7280'}}>
                      Preview not supported for <code>.tif/.tiff</code> in most browsers.
                      <br/>Use the button below to download and view locally.
                    </div>
                  </div>
                ) : (

                <img
                    src={dataUrlFor(
                      resultData.original_image,
                      resultData.original_filename || 'original_image.png',
                      'image/png'
                    )}
                    alt="Original"
                  />
                )}
                <div className="image-title">Original Image</div>
                <button
                  className="btn btn-secondary mt-2"
                  onClick={() => handleDownload(resultData.original_image, resultData.original_filename || 'original_image.png')}
                >
                  📥 Download Original
                </button>
              </div>
              <div className="image-container">
                <img
                   src={dataUrlFor(
                    resultData.encrypted_image,
                    resultData.encrypted_filename || 'encrypted_image.png',
                    'image/png'
                  )}
                  alt="Encrypted"
                />
                <div className="image-title">Encrypted Image</div>
                <button
                  className="btn btn-success mt-2"
                  onClick={() => handleDownload(resultData.encrypted_image, resultData.encrypted_filename || 'encrypted_image.png')}
                >
                  📥 Download Encrypted
                </button>
              </div>
            </>
          ) : (
            <div className="image-container">
              <img
                src={dataUrlFor(
                  resultData.decrypted_image,
                  resultData.decrypted_filename || 'decrypted_image.png',
                  'image/png'
                )}
                alt="Decrypted"
              />
              <div className="image-title">Decrypted Image</div>
              <button
                className="btn btn-success mt-2"
                onClick={() => handleDownload(resultData.decrypted_image, resultData.decrypted_filename || 'decrypted_image.png')}
              >
                📥 Download Decrypted
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Encryption Metrics */}
      {operationType === 'encrypt' && resultData.metrics && (
        <StatsDisplay metrics={resultData.metrics} />
      )}

      {/* Analysis Section */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Analysis</h3>
        </div>

        {operationType === 'encrypt' ? (
          <div>
            <h4>Encryption Quality Assessment:</h4>
            <ul style={{ lineHeight: '2', fontSize: '1.1rem' }}>
              <li><strong>Entropy:</strong> The encrypted image shows {resultData.metrics?.entropy_encrypted > 7.5 ? 'excellent' : resultData.metrics?.entropy_encrypted > 7.0 ? 'good' : 'poor'} randomness with an entropy value of {resultData.metrics?.entropy_encrypted?.toFixed(4)} bits per pixel.</li>
              <li><strong>NPCR:</strong> {resultData.metrics?.npcr?.toFixed(2)}% of pixels changed during encryption, indicating {resultData.metrics?.npcr > 99.5 ? 'excellent' : resultData.metrics?.npcr > 99.0 ? 'good' : 'poor'} diffusion.</li>
              <li><strong>UACI:</strong> The average intensity change is {resultData.metrics?.uaci?.toFixed(2)}%, which is {resultData.metrics?.uaci > 33.0 && resultData.metrics?.uaci < 34.0 ? 'within the ideal range' : 'outside the ideal range'} for secure encryption.</li>
            </ul>
          </div>
        ) : (
          <div>
            <h4>Decryption Success:</h4>
            <p style={{ fontSize: '1.1rem', lineHeight: '1.8' }}>
              The image has been successfully decrypted using the provided key.
              The decrypted image should be identical to the original image if the correct key was used.
            </p>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Next Steps</h3>
        </div>

        <div className="d-flex justify-center gap-2">
          <button
            className="btn btn-primary"
            onClick={() => navigate('/encrypt')}
          >
            🔒 Encrypt Another Image
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => navigate('/decrypt')}
          >
            🔓 Decrypt Image
          </button>
          <button
            className="btn btn-success"
            onClick={() => navigate('/')}
          >
            🏠 Back to Home
          </button>
        </div>
      </div>

      {/* Security Information */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Security Information</h3>
        </div>

        <div className="alert alert-info">
          <h4>Chaotic Encryption Advantages:</h4>
          <ul style={{ margin: '1rem 0', paddingLeft: '1.5rem' }}>
            <li><strong>Non-linear transformation:</strong> Chaotic maps provide unpredictable transformations</li>
            <li><strong>High sensitivity:</strong> Small changes in the key produce completely different results</li>
            <li><strong>Pixel-level security:</strong> Each pixel is individually transformed</li>
            <li><strong>Statistical security:</strong> Encrypted images have high entropy and low correlation</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Results;
