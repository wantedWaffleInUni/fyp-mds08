import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ImageUploader from '../components/ImageUploader';
import { encryptImage } from '../services/api';
import { saveAs } from 'file-saver';

const Encrypt = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');           // NEW
  const previewUrlRef = useRef('');
  const [encryptionKey, setEncryptionKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showAlgoModal, setShowAlgoModal] = useState(false);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('chaos');
  const [nonce, setNonce] = useState('');
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  // Revoke object URLs to avoid memory leaks
  useEffect(() => {
    return () => {
      if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
    };
  }, []);

  const handleImageUpload = (file) => {
    setSelectedFile(file);
    setError('');
    setResult(null);

    // manage preview url
    if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
    const url = URL.createObjectURL(file);
    previewUrlRef.current = url;
    setPreviewUrl(url);
  };

  // ------- validation flags/messages -------
  const keyFilled = encryptionKey.trim().length > 0;
  const canEncrypt = !!selectedFile && keyFilled;

  const validationMsg =
    !selectedFile && !keyFilled
      ? 'Please select an image and enter an encryption key'
      : !selectedFile
      ? 'Please select an image to encrypt'
      : !keyFilled
      ? 'Please enter an encryption key'
      : '';

  const handleEncrypt = async () => {
    if (!canEncrypt) {
      setError(validationMsg);
      return;
    }

    //     if (!selectedFile && !encryptionKey.trim()) {
    //       setError('Please select an image and enter an encryption key');
    //       return;
    //     }
    //     if (!selectedFile) {
    //       setError('Please select an image to encrypt');
    //       return;
    //     }
    // 
    //     if (!encryptionKey.trim()) {
    //       setError('Please enter an encryption key');
    //       return;
    //     }
    // Open algorithm selection modal
    setShowAlgoModal(true);
  };

  const confirmEncrypt = async () => {
    setIsLoading(true);
    setError('');

    try {
      const needsNonce = ['fodhnn', '2dlasm'].includes(selectedAlgorithm);
      const response = await encryptImage(
        selectedFile,
        encryptionKey,
        selectedAlgorithm,
        // selectedAlgorithm === 'fodhnn' ? (nonce || undefined) : undefined
        needsNonce ? (nonce || undefined) : undefined
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

  const needsNonce = ['fodhnn', '2dlasm'].includes(selectedAlgorithm);

//   const algoOptions = [
//   { value: 'chaos',  label: 'Chaotic Logistic (default)' },
//   { value: 'fodhnn', label: 'FODHNN (fractional-order Hopfield)' },
//   { value: '2dlasm', label: '2DLASM (2D Logistic Adjusted Sine Map)' },
// ];
  const algoOptions = [
    { value: 'chaos',  label: 'Chaotic Logistic (default)',
      desc: 'Fast baseline using logistic-map confusion+diffusion. Good general choice.' },
    { value: 'fodhnn', label: 'FODHNN (fractional-order Hopfield)',
      desc: 'Stronger confusion/diffusion via fractional-order dynamics. Slower; may need nonce.' },
    { value: '2dlasm', label: '2DLASM (2D Logistic Adjusted Sine Map)',
      desc: '2D chaotic map with high key sensitivity. Requires nonce; usually fast.' },
  ];

  const [flipped, setFlipped] = useState({});
  const setFlip = (val, on) => setFlipped(f => ({ ...f, [val]: on ?? !f[val] }));




  return (
    <div>
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">🔒 Encrypt Image</h2>
          <p>Upload an image to encrypt it using chaotic encryption</p>
        </div>

        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        <div className="form-group">
          <label className="form-label"><strong>Upload An Image</strong></label>
          <ImageUploader onImageUpload={handleImageUpload} />
          {selectedFile && (
            <div className="mt-2">
              <p>Uploaded: {selectedFile.name}</p>
              <p>Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          )}
        </div>

        <div className="form-group">
          <label className="form-label"><strong>Enter Encryption Key</strong></label>
          <input
            type="text"
            className="form-control"
            value={encryptionKey}
            onChange={(e) => setEncryptionKey(e.target.value)}
            placeholder="Enter encryption key or generate a random one"
          />
  
          {/* radio for enabling auto generation of strong key */}
          {/* <div className="form-check mt-2">
            <input
              type="checkbox"
              className="form-check-input"
              id="autoGenerateKey"
              checked={autoGenerateKey}
              onChange={(e) => setAutoGenerateKey(e.target.checked)}
            />
            <label className="form-check-label" htmlFor="autoGenerateKey">
              Auto-generate a strong key
            </label>
          </div> */}
          <small style={{ color: '#666', marginTop: '0.5rem', display: 'block' }}>
            Tip: Use a strong, memorable key. The key is used to generate chaotic sequences, essential for decryption.
          </small>
        </div>

        <div className="d-flex justify-center">
          <button

            className={`btn ${canEncrypt ? 'btn-primary' : 'btn-disabled'}`}
            onClick={handleEncrypt}
            disabled={!canEncrypt || isLoading}
            style={{ minWidth: '200px' }}
            aria-disabled={!canEncrypt || isLoading}
            // className="btn btn-primary"
            // onClick={handleEncrypt}
            // disabled={isLoading || !selectedFile}
            // style={{ minWidth: '200px' }}
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
        {/* live validation hint when disabled */}
          {!canEncrypt && !isLoading && (
            <div className="mt-2" style={{ color: '#6b7280', fontSize: 13, alignContent: 'center', textAlign: 'center' }}>
              {validationMsg}
            </div>
          )}
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
              <h3 className="modal-title">🔒 Before Encrypting</h3>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label className="form-label" style={{alignContent: 'center'}}>Select a method you prefer. </label>
                <p style={{fontStyle:'italic', fontSize: '0.8rem'}}> Hover over each algorithm to see which one fits you best! </p>
                <br></br>
                
                {/* <div className="btn-choice-group">
                  {algoOptions.map(opt => {
                    const active = selectedAlgorithm === opt.value;
                    return (
                      <button
                        key={opt.value}
                        type="button"
                        className={`btn btn-choice ${active ? 'active' : ''}`}
                        style={{ flex: 1, height: '100px', fontSize: '0.9rem' }}
                        onClick={() => setSelectedAlgorithm(opt.value)}
                        aria-pressed={active}
                      >
                        {opt.label}
                      </button>
                    );
                  })}
                </div> */}

                <div className="algo-grid">
                  {algoOptions.map(opt => {
                    const active = selectedAlgorithm === opt.value;
                    const isFlipped = !!flipped[opt.value];
                    return (
                      <div
                        key={opt.value}
                        className={`algo-card ${active ? 'active' : ''} ${isFlipped ? 'flipped' : ''}`}
                        onClick={() => setSelectedAlgorithm(opt.value)}                 // click selects
                        onMouseEnter={() => setFlip(opt.value, true)}                   // hover flips
                        onMouseLeave={() => setFlip(opt.value, false)}
                        tabIndex={0}
                        onFocus={() => setFlip(opt.value, true)}                        // keyboard focus flips
                        onBlur={() => setFlip(opt.value, false)}
                        role="button"
                        aria-pressed={active}
                        aria-label={`Choose ${opt.label}`}
                      >
                        <div className="algo-card-inner">
                          <div className="algo-face front">
                            <div className="algo-title">{opt.label}</div>
                            {/* <div className="algo-hint">Click to select • Tap ⓘ for info</div> */}
                          </div>

                          <div className="algo-face back">
                            <div className="algo-back-title" style={{fontWeight:"bold"}}>{opt.label}</div>
                            <p className="algo-desc">{opt.desc}</p>
                            <div className="algo-actions">
                              {/* <button
                                type="button"
                                className="btn btn-primary btn-sm"
                                onClick={(e) => { e.stopPropagation(); setSelectedAlgorithm(opt.value); }}
                              >
                                Choose
                              </button> */}
                            </div>
                          </div>
                        </div>

                        {/* Works on touch: tap ⓘ to flip without selecting */}
                        <button
                          type="button"
                          className="info-badge"
                          aria-label={`About ${opt.label}`}
                          onClick={(e) => { e.stopPropagation(); setFlip(opt.value); }}
                        >
                          ⓘ
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
              {/* {selectedAlgorithm === 'fodhnn' && ( */}
              {needsNonce && (
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
