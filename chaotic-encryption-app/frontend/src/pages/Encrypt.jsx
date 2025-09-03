import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ImageUploader from '../components/ImageUploader';
import { encryptImage } from '../services/api';
import { saveAs } from 'file-saver';

// NEW imports
import SelectAlgorithmModal from '../components/modals/SelectAlgorithmModal';
import ProgressModal from '../components/modals/ProgressModal';
import usePhasedProgress from '../components/modals/usePhasedProgress';


const Encrypt = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');           // NEW
  const previewUrlRef = useRef('');
  const [encryptionKey, setEncryptionKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showAlgoModal, setShowAlgoModal] = useState(false);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('chaos');

  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  // progress modal state
  // const [showProgress, setShowProgress] = useState(false);
  // const [progress, setProgress] = useState(0);
  // const [phase, setPhase] = useState('analysing image …');
  // const abortRef = useRef(null);

  // labels & soft caps for each phase (won’t exceed 95% until done)
  const PHASES = [
    { label: 'Analysing image …', from: 2, to: 25 },
    { label: 'Confusion & diffusion stage …', from: 26, to: 55 },
    { label: 'Encrypting …', from: 56, to: 85 },
    { label: 'Evaluating results …', from: 86, to: 95 },
  ];

  const { show, setShow, progress, phase, start, stop } = usePhasedProgress(PHASES);
  const abortRef = useRef(null);

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

  // copy and paste key handlers
  const keyInputRef = useRef(null);
  const [copied, setCopied] = useState(false);

  const handleCopyKey = async () => {
    try {
      await navigator.clipboard.writeText(encryptionKey || '');
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch (e) {
      setError('Copy failed (clipboard blocked by browser).');
    }
  };

  const handlePasteKey = async () => {
    try {
      const txt = await navigator.clipboard.readText();
      setEncryptionKey(txt || '');
      if (error) setError('');
    } catch (e) {
      setError('Paste blocked by browser. Click the field and use Cmd/Ctrl+V.');
    }
  };


  //   const confirmEncrypt = async () => {
  //     setIsLoading(true);
  //     setError('');
  // 
  //     try {
  //       const needsNonce = ['fodhnn', '2dlasm'].includes(selectedAlgorithm);
  //       const response = await encryptImage(
  //         selectedFile,
  //         encryptionKey,
  //         selectedAlgorithm,
  //         // selectedAlgorithm === 'fodhnn' ? (nonce || undefined) : undefined
  //         needsNonce ? (nonce || undefined) : undefined
  //       );
  //       setResult(response);
  //       setShowAlgoModal(false);
  //       // Navigate to results page with the data
  //       navigate('/results', {
  //         state: {
  //           type: 'encrypt',
  //           data: response
  //         }
  //       });
  //     } catch (err) {
  //       setError(err.message);
  //     } finally {
  //       setIsLoading(false);
  //     }
  //   };

  // const confirmEncrypt = async () => {
  //   setShowAlgoModal(false);
  //   setShowProgress(true);
  //   setPhase('analysing image…');
  //   setProgress(5);
  // 
  //   const needsNonce = ['fodhnn', '2dlasm'].includes(selectedAlgorithm);
  // 
  //   // optional: smooth fake progress while waiting (caps at 95%)
  //   const tick = setInterval(() => {
  //     setProgress(p => (p < 95 ? p + (p < 80 ? 1 : 0.5) : p));
  //   }, 200);
  // 
  //   const ac = new AbortController();
  //   abortRef.current = ac;
  // 
  //   try {
  //     const res = await encryptImage(
  //       selectedFile,
  //       encryptionKey,
  //       selectedAlgorithm,
  //       needsNonce ? (nonce || undefined) : undefined,
  //       { signal: ac.signal } // ok to omit if your API helper doesn’t use it
  //     );
  // 
  //     clearInterval(tick);
  //     setPhase('finalising…');
  //     setProgress(100);
  // 
  //     // small pause for UX polish
  //     setTimeout(() => {
  //       setShowProgress(false);
  //       navigate('/results', { state: { type: 'encrypt', data: res } });
  //     }, 250);
  //   } catch (e) {
  //     clearInterval(tick);
  //     setShowProgress(false);
  //     if (e.name !== 'AbortError') setError(e.message || 'Encryption failed.');
  //   }
  // };

  //   const confirmEncrypt = async () => {
  //     setShowAlgoModal(false);
  //     setShowProgress(true);
  //     setError('');
  // 
  //     const needsNonce = ['fodhnn', '2dlasm'].includes(selectedAlgorithm);
  // 
  //     // kick off fake phased progress while backend works
  //     const ac = new AbortController();
  //     abortRef.current = ac;
  //     const stop = startPhasedProgress(ac.signal);
  // 
  //     try {
  //       const res = await encryptImage(
  //         selectedFile,
  //         encryptionKey,
  //         selectedAlgorithm,
  //         needsNonce ? (nonce || undefined) : undefined,
  //         { signal: ac.signal } // safe to omit if your helper doesn’t support it
  //       );
  // 
  //       // finish bar nicely, then navigate
  //       stop();
  //       setPhase('Finalising …');
  //       setProgress(100);
  // 
  //       setTimeout(() => {
  //         setShowProgress(false);
  //         navigate('/results', { state: { type: 'encrypt', data: res } });
  //       }, 250);
  //     } catch (e) {
  //       stop();
  //       setShowProgress(false);
  //       if (e.name !== 'AbortError') setError(e.message || 'Encryption failed.');
  //     }
  //   };
  const confirmEncrypt = async () => {
    setIsLoading(true);
    setShowAlgoModal(false);
    setError('');

    const ac = new AbortController();
    abortRef.current = ac;

    start(ac.signal); // start phased progress

    try {
      const res = await encryptImage(
        selectedFile, encryptionKey, selectedAlgorithm,
        { signal: ac.signal } // if supported
      );

      stop();
      setShow(false);
      navigate('/results', { state: { type: 'encrypt', data: res } });
    } catch (e) {
      stop();
      setShow(false);
      if (e.name !== 'AbortError') setError(e.message || 'Encryption failed.');
    } finally {
      setIsLoading(false);
    }
  };




  //   const confirmEncrypt = async () => {
  //   // close modal and go to /results immediately
  //   const needsNonce = ['fodhnn', '2dlasm'].includes(selectedAlgorithm);
  // 
  //   setShowAlgoModal(false);
  // 
  //   navigate('/results', {
  //     state: {
  //       type: 'encrypt',
  //       params: {
  //         file: selectedFile,
  //         key: encryptionKey,
  //         algorithm: selectedAlgorithm,
  //         nonce: needsNonce ? (nonce || undefined) : undefined,
  //       },
  //     },
  //   });
  // };


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



  //   const algoOptions = [
  //   { value: 'chaos',  label: 'Chaotic Logistic (default)' },
  //   { value: 'fodhnn', label: 'FODHNN (fractional-order Hopfield)' },
  //   { value: '2dlasm', label: '2DLASM (2D Logistic Adjusted Sine Map)' },
  // ];
  const algoOptions = [
    {
      value: 'chaos', label: 'Chaotic Logistic (default)',
      desc: 'Fast baseline using logistic-map confusion+diffusion. Good general choice.'
    },
    {
      value: 'fodhnn', label: 'FODHNN (fractional-order Hopfield)',
      desc: 'Stronger confusion/diffusion via fractional-order dynamics. Slower but more secure.'
    },
    {
      value: '2dlasm', label: '2DLASM (2D Logistic Adjusted Sine Map)',
      desc: '2D chaotic map with high key sensitivity. Fast and secure.'
    },
    { value: 'bulban', label: 'Bülban chaotic map', desc: 'Fast, highly secure, accepts any pixel size, but internally converts to grayscale before encryption, and outputs a grayscale cipher image.' }
  ];

  const [flipped, setFlipped] = useState({});
  const setFlip = (val, on) => setFlipped(f => ({ ...f, [val]: on ?? !f[val] }));


  //   function startPhasedProgress(signal) {
  //     let i = 0;
  //     let p = PHASES[0].from;
  //     setPhase(PHASES[0].label);
  //     setProgress(p);
  // 
  //     const id = setInterval(() => {
  //       if (signal?.aborted) return clearInterval(id);
  // 
  //       const step = PHASES[i];
  //       // speed tapers slightly as we advance
  //       const bump = i < 2 ? 1.2 : 0.6;
  //       p = Math.min(step.to, p + bump + Math.random() * 0.8);
  //       setProgress(p);
  // 
  //       if (p >= step.to && i < PHASES.length - 1) {
  //         i += 1;
  //         setPhase(PHASES[i].label);
  //         p = Math.max(p, PHASES[i].from);
  //       }
  //     }, 180);
  // 
  //     return () => clearInterval(id); // stop function
  //   }



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
          {/* <input
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
          <div className="input-with-actions">
            <input
              ref={keyInputRef}
              type="text"
              className="form-control"
              value={encryptionKey}
              onChange={(e) => setEncryptionKey(e.target.value)}
              placeholder="Enter encryption key or generate a random one"
              style={{ paddingRight: '116px' }}  // room for the two buttons
            />

            <div className="input-actions">
              <button
                type="button"
                className="icon-btn"
                onClick={handlePasteKey}
                title="Paste from clipboard"
                aria-label="Paste from clipboard"
              >
                Paste
              </button>
              <button
                type="button"
                className="icon-btn"
                onClick={handleCopyKey}
                disabled={!encryptionKey}
                title="Copy key"
                aria-label="Copy key"
              >
                {copied ? 'Copied!' : 'Copy'}
              </button>
            </div>
          </div>
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

      {/* <SelectAlgorithmModal
        open={showAlgoModal}
        onClose={() => setShowAlgoModal(false)}
        onConfirm={confirmEncrypt}
        options={algoOptions}
        selected={selectedAlgorithm}
        onSelect={(val) => { setSelectedAlgorithm(val); }}
        confirming={isLoading}
        flipped={flipped}
        setFlip={setFlip}
      /> */}

      <SelectAlgorithmModal
        open={showAlgoModal}
        onClose={() => setShowAlgoModal(false)}
        onConfirm={confirmEncrypt}
        options={algoOptions}                 // ✅ array
        selected={selectedAlgorithm}          // ✅ string
        onSelect={(val) => { setSelectedAlgorithm(val); }}
        confirming={isLoading}                // ✅ (optional, see below)
        flipped={flipped}
        setFlip={setFlip}
      />


      <ProgressModal
        open={show}
        progress={progress}
        phase={phase}
        onCancel={() => {
          abortRef.current?.abort();
          stop();
          setShow(false);
        }}
      />

    </div>
  );
};

export default Encrypt;
