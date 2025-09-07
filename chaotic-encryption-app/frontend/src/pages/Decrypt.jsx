import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ImageUploader from '../components/ImageUploader';
import { decryptImage } from '../services/api';
import { saveAs } from 'file-saver';

import SelectAlgorithmModal from '../components/modals/SelectAlgorithmModal';

// 👁️ icons
const EyeIcon = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
       stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8Z" />
    <circle cx="12" cy="12" r="3" />
  </svg>
);

const EyeOffIcon = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
       stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17.94 17.94A10.94 10.94 0 0 1 12 20c-7 0-11-8-11-8a21.77 21.77 0 0 1 5.06-6.94" />
    <path d="M1 1l22 22" />
    <path d="M10.58 10.58a2 2 0 1 0 2.83 2.83" />
    <path d="M9.88 4.24A10.94 10.94 0 0 1 12 4c7 0 11 8 11 8a21.77 21.77 0 0 1-3.16 4.19" />
  </svg>
);

const Decrypt = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [decryptionKey, setDecryptionKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [algorithm, setAlgorithm] = useState('chaos');
  const navigate = useNavigate();

  // ---- key copy/paste/show/hide ----
  const [showKey, setShowKey] = useState(false);
  const [copied, setCopied] = useState(false);
  const keyInputRef = useRef(null);

  const handleCopyKey = async () => {
    try {
      await navigator.clipboard.writeText(decryptionKey || '');
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch {
      setError('Copy failed (clipboard blocked by browser).');
    }
  };

  const handlePasteKey = async () => {
    try {
      const txt = await navigator.clipboard.readText();
      setDecryptionKey(txt || '');
      if (error) setError('');
    } catch {
      setError('Paste blocked by browser. Use Ctrl+V instead.');
    }
  };

  // ---- algorithm modal ----
  const [showAlgoModal, setShowAlgoModal] = useState(false);
  const [flipped, setFlipped] = useState({});
  const setFlip = (val, on) => setFlipped(f => ({ ...f, [val]: on ?? !f[val] }));

  const algoOptions = [
   {
      value: 'fodhnn', label: 'FODHNN (fractional-order Hopfield)',
      desc: 'Stronger confusion/diffusion via fractional-order dynamics. Slower but more secure.'
    },
    {
      value: '2dlasm', label: '2DLASM (2D Logistic Adjusted Sine Map)',
      desc: '2D chaotic map with high key sensitivity. Fast and secure.'
    },
    { value: 'bulban', label: 'Bülban chaotic map', 
      desc: 'Fast, highly secure, accepts any pixel size, but internally converts to grayscale before encryption, and outputs a grayscale cipher image.' 
    },
    { value: 'acm-2dscl', label: 'ACM-2DSCL (Arnold Cat Map + 2DSCL + Chen)', 
      desc: 'Hybrid chaotic cipher with multi-stage confusion and diffusion. Strongest security out of all.'
    },
  ];

  const handleImageUpload = (file) => {
    setSelectedFile(file);
    setError('');
    setResult(null);
  };

  const handleDecrypt = () => {
    if (!selectedFile) {
      setError('Please select an encrypted image to decrypt');
      return;
    }
    if (!decryptionKey.trim()) {
      setError('Please enter the decryption key');
      return;
    }
    setShowAlgoModal(true); // 打开算法选择弹窗
  };

  const confirmDecrypt = async () => {
    setIsLoading(true);
    setShowAlgoModal(false);
    setError('');
    try {
      const response = await decryptImage(selectedFile, decryptionKey, algorithm);
      setResult(response);
      navigate('/results', {
        state: { type: 'decrypt', data: response }
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async (imageData, filename) => {
    try {
      const response = await fetch(`data:image/png;base64,${imageData}`);
      const blob = await response.blob();
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

        {error && <div className="alert alert-error">{error}</div>}

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
          <div className="input-with-actions">
            <input
              ref={keyInputRef}
              type={showKey ? 'text' : 'password'}
              className="form-control"
              value={decryptionKey}
              onChange={(e) => setDecryptionKey(e.target.value)}
              placeholder="Enter the decryption key"
              style={{ paddingRight: '116px' }}
              autoComplete="off"
            />
            <div className="input-actions">
              <button type="button" className="icon-btn" onClick={handlePasteKey}>Paste</button>
              <button type="button" className="icon-btn" onClick={handleCopyKey} disabled={!decryptionKey}>
                {copied ? 'Copied!' : 'Copy'}
              </button>
              <button type="button" className="icon-btn" onClick={() => setShowKey(v => !v)}>
                {showKey ? <EyeOffIcon size={16} /> : <EyeIcon size={16} />}
              </button>
            </div>
          </div>
          <small style={{ color: '#666', marginTop: '0.5rem', display: 'block' }}>
            The decryption key must be exactly the same as the key used for encryption.
          </small>
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
              <img src={`data:image/png;base64,${result.decrypted_image}`} alt="Decrypted" />
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

      <SelectAlgorithmModal
        open={showAlgoModal}
        onClose={() => setShowAlgoModal(false)}
        onConfirm={confirmDecrypt}
        options={algoOptions}
        selected={algorithm}
        onSelect={(val) => setAlgorithm(val)}
        confirming={isLoading}
        flipped={flipped}
        setFlip={setFlip}
      />
    </div>
  );
};

export default Decrypt;
