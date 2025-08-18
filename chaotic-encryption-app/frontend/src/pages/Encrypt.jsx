import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ImageUploader from '../components/ImageUploader';
import { encryptImage } from '../services/api';
import { saveAs } from 'file-saver';

const Encrypt = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [encryptionKey, setEncryptionKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showAlgoModal, setShowAlgoModal] = useState(false);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('chaos');
  const [nonce, setNonce] = useState('');
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  const handleImageUpload = (file) => {
    setSelectedFile(file);
    setError('');
    setResult(null);
  };

  const handleEncrypt = async () => {
    if (!selectedFile) {
      setError('Please select an image to encrypt');
      return;
    }

    if (!encryptionKey.trim()) {
      setError('Please enter an encryption key');
      return;
    }
    // Open algorithm selection modal
    setShowAlgoModal(true);
  };

  const confirmEncrypt = async () => {
    setIsLoading(true);
    setError('');

    try {
      const response = await encryptImage(
        selectedFile,
        encryptionKey,
        selectedAlgorithm,
        selectedAlgorithm === 'fodhnn' ? (nonce || undefined) : undefined
      );
      setResult(response);
      setShowAlgoModal(false);
      // Navigate to results page with the data
      navigate('/results', {
        state: {
          type: 'encrypt',
          data: response
        }
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async (imageData, filename) => {
    try {
      // Convert base64 to blob
      const response = await fetch(`data:image/png;base64,${imageData}`);
      const blob = await response.blob();

      // Download the file
      saveAs(blob, filename || 'encrypted_image.png');
    } catch (err) {
      setError('Download failed: ' + err.message);
    }
  };

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">🔒 Encrypt Image</h2>
          <p>Upload an image and encrypt it using chaotic encryption</p>
        </div>

        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        <div className="form-group">
          <label className="form-label">Select Image</label>
          <ImageUploader onImageUpload={handleImageUpload} />
          {selectedFile && (
            <div className="mt-2">
              <p><strong>Selected:</strong> {selectedFile.name}</p>
              <p><strong>Size:</strong> {(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          )}
        </div>

        <div className="form-group">
          <label className="form-label">Encryption Key</label>
          <input
            type="text"
            className="form-control"
            value={encryptionKey}
            onChange={(e) => setEncryptionKey(e.target.value)}
            placeholder="Enter encryption key (optional, default will be used if empty)"
          />
          <small style={{ color: '#666', marginTop: '0.5rem', display: 'block' }}>
            The key is used to generate chaotic sequences. Keep it secure for decryption.
          </small>
        </div>

        <div className="d-flex justify-center">
          <button
            className="btn btn-primary"
            onClick={handleEncrypt}
            disabled={isLoading || !selectedFile}
            style={{ minWidth: '200px' }}
          >
            {isLoading ? (
              <>
                <div className="spinner" style={{ width: '20px', height: '20px', marginRight: '10px' }}></div>
                Encrypting...
              </>
            ) : (
              '🔒 Encrypt Image'
            )}
          </button>
        </div>
      </div>

      {result && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Encryption Results</h3>
          </div>

          <div className="image-preview">
            <div className="image-container">
              <img
                src={`data:image/png;base64,${result.original_image}`}
                alt="Original"
              />
              <div className="image-title">Original Image</div>
            </div>
            <div className="image-container">
              <img
                src={`data:image/png;base64,${result.encrypted_image}`}
                alt="Encrypted"
              />
              <div className="image-title">Encrypted Image</div>
            </div>
          </div>

          <div className="d-flex justify-center gap-2 mt-3">
            <button
              className="btn btn-success"
              onClick={() => handleDownload(result.encrypted_image, result.encrypted_filename)}
            >
              📥 Download Encrypted Image
            </button>
          </div>
        </div>
      )}

      {showAlgoModal && (
        <div className="modal-backdrop">
          <div className="modal">
            <div className="modal-header">
              <h3 className="modal-title">Choose Encryption Algorithm</h3>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">Algorithm</label>
                <div className="d-flex gap-2">
                  <label className="radio">
                    <input
                      type="radio"
                      name="algorithm"
                      value="chaos"
                      checked={selectedAlgorithm === 'chaos'}
                      onChange={() => setSelectedAlgorithm('chaos')}
                    />
                    <span>Chaotic Logistic (default)</span>
                  </label>
                  <label className="radio">
                    <input
                      type="radio"
                      name="algorithm"
                      value="fodhnn"
                      checked={selectedAlgorithm === 'fodhnn'}
                      onChange={() => setSelectedAlgorithm('fodhnn')}
                    />
                    <span>FODHNN (fractional-order Hopfield)</span>
                  </label>
                </div>
              </div>
              {selectedAlgorithm === 'fodhnn' && (
                <div className="form-group">
                  <label className="form-label">Nonce (optional)</label>
                  <input
                    type="text"
                    className="form-control"
                    value={nonce}
                    onChange={(e) => setNonce(e.target.value)}
                    placeholder="If empty, a nonce will be generated by the server"
                  />
                  <small style={{ color: '#666', marginTop: '0.5rem', display: 'block' }}>
                    Save the nonce with your key to decrypt later.
                  </small>
                </div>
              )}
            </div>
            <div className="modal-footer d-flex gap-2 justify-end">
              <button className="btn btn-secondary" onClick={() => setShowAlgoModal(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={confirmEncrypt} disabled={isLoading}>
                {isLoading ? 'Encrypting...' : 'Confirm'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Encrypt;
