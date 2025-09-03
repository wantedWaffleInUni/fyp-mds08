import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ImageUploader from '../components/ImageUploader';
import { decryptImage } from '../services/api';
import { saveAs } from 'file-saver';

const Decrypt = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [decryptionKey, setDecryptionKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [algorithm, setAlgorithm] = useState('chaos');
  const navigate = useNavigate();

  const handleImageUpload = (file) => {
    setSelectedFile(file);
    setError('');
    setResult(null);
  };

  const handleDecrypt = async () => {
    if (!selectedFile) {
      setError('Please select an encrypted image to decrypt');
      return;
    }

    if (!decryptionKey.trim()) {
      setError('Please enter the decryption key');
      return;
    }



    setIsLoading(true);
    setError('');

    try {
      const response = await decryptImage(selectedFile, decryptionKey, algorithm);
      setResult(response);

      // Navigate to results page with the data
      navigate('/results', {
        state: {
          type: 'decrypt',
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
      saveAs(blob, filename || 'decrypted_image.png');
    } catch (err) {
      setError('Download failed: ' + err.message);
    }
  };

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">🔓 Decrypt Image</h2>
          <p>Upload an encrypted image and decrypt it using the original key</p>
        </div>

        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        <div className="form-group">
          <label className="form-label">Select Encrypted Image</label>
          <ImageUploader onImageUpload={handleImageUpload} />
          {selectedFile && (
            <div className="mt-2">
              <p><strong>Selected:</strong> {selectedFile.name}</p>
              <p><strong>Size:</strong> {(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          )}
        </div>

        <div className="form-group">
          <label className="form-label">Decryption Key</label>
          <input
            type="text"
            className="form-control"
            value={decryptionKey}
            onChange={(e) => setDecryptionKey(e.target.value)}
            placeholder="Enter the decryption key (must match the encryption key)"
          />
          <small style={{ color: '#666', marginTop: '0.5rem', display: 'block' }}>
            The decryption key must be exactly the same as the key used for encryption.
          </small>
        </div>

        <div className="form-group">
          <label className="form-label">Algorithm</label>
          <div className="d-flex gap-2">
            <label className="radio">
              <input
                type="radio"
                name="algorithm"
                value="chaos"
                checked={algorithm === 'chaos'}
                onChange={() => setAlgorithm('chaos')}
              />
              <span>Chaotic Logistic (default)</span>
            </label>
            <label className="radio">
              <input
                type="radio"
                name="algorithm"
                value="fodhnn"
                checked={algorithm === 'fodhnn'}
                onChange={() => setAlgorithm('fodhnn')}
              />
              <span>FODHNN</span>
            </label>

            <label className="radio">
              <input
                type="radio"
                name="algorithm"
                value="2dlasm"
                checked={algorithm === '2dlasm'}
                onChange={() => setAlgorithm('2dlasm')}
              />
              <span>2DLASM</span>
            </label>

            <label className="radio">
              <input
                type="radio"
                name="algorithm"
                value="acm_2dscl"
                checked={algorithm === 'acm_2dscl'}
                onChange={() => setAlgorithm('acm_2dscl')}
              />
              <span>ACM_2DSCL</span>
            </label>

            <label className="radio">
              <input
                type="radio"
                name="algorithm"
                value="bulban"
                checked={algorithm === 'bulban'}
                onChange={() => setAlgorithm('bulban')}
              />
              <span>Bulban</span>
            </label>
          </div>
        </div>



        <div className="d-flex justify-center">
          <button
            className="btn btn-primary"
            onClick={handleDecrypt}
            disabled={isLoading || !selectedFile}
            style={{ minWidth: '200px' }}
          >
            {isLoading ? (
              <>
                <div className="spinner" style={{ width: '20px', height: '20px', marginRight: '10px' }}></div>
                Decrypting...
              </>
            ) : (
              '🔓 Decrypt Image'
            )}
          </button>
        </div>
      </div>

      {result && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Decryption Results</h3>
          </div>

          <div className="image-preview">
            <div className="image-container">
              <img
                src={`data:image/png;base64,${result.decrypted_image}`}
                alt="Decrypted"
              />
              <div className="image-title">Decrypted Image</div>
            </div>
          </div>

          <div className="d-flex justify-center gap-2 mt-3">
            <button
              className="btn btn-success"
              onClick={() => handleDownload(result.decrypted_image, result.decrypted_filename)}
            >
              📥 Download Decrypted Image
            </button>
          </div>
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Important Notes</h3>
        </div>

        <div className="alert alert-info">
          <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
            <li><strong>Key Requirement:</strong> You must use the exact same key that was used for encryption</li>
            <li><strong>Image Format:</strong> The encrypted image should be in PNG format</li>
            <li><strong>File Size:</strong> Maximum file size is 16MB</li>
            <li><strong>Security:</strong> Never share your decryption key with others</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Decrypt;
