// import React from 'react';
import { Link } from 'react-router-dom';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import CaptchaModal from '../components/modals/CaptchaModal';
import Typewriter from "../components/Typewriter";


const Home = () => {
  const [modalOpen, setModalOpen] = useState(false);
  const [redirectPath, setRedirectPath] = useState('');
  const navigate = useNavigate();

  const handleClick = (path) => {
    setRedirectPath(path);
    setModalOpen(true);
  };

  const handleVerified = (token) => {
    // ✅ optional: send token to backend for validation
    console.log("Captcha verified:", token);
    navigate(redirectPath); // redirect after verification
  };

  return (
    <div className="text-center">
      <div className="card">
        <div className="card-header">
          <h1 className="card-title" style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
            🔐 Chaotic Image Encryption
          </h1>
          <p style={{ fontSize: '1rem', color: '#666' }}>
            Advanced image encryption using chaotic maps for enhanced security
          </p>
        </div>
        
        <div className="mb-3">
          <p style={{ fontSize: '1.1rem', lineHeight: '1.8' }}>
            Secure your images with advanced encryption. <br></br>
            Protect sensitive visuals and ensure privacy with our reliable, user-friendly image encryption solution.
            
          </p>
        </div>
        
        <div className="d-flex justify-center gap-2 mb-3">
          {/* <Link to="/encrypt" className="btn btn-primary">
            🔒 Encrypt Image
          </Link>
          <Link to="/decrypt" className="btn btn-secondary">
            🔓 Decrypt Image
          </Link> */}

          <button onClick={() => handleClick('/encrypt')} className="btn btn-primary btn--md">
            🔒 Encrypt Image
          </button>
          <button onClick={() => handleClick('/decrypt')} className="btn btn-secondary btn--md">
            🔓 Decrypt Image
          </button>
        </div>
      </div>
      
      
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Key Features & How It Works</h2>
        </div>

          <div className="features-steps-grid">
            {/* LEFT: one tall FEATURES card */}
            <section className="features features--cards">
              <article className="pill-card pill-card--stack">
                <div className="pill-card__label">FEATURES</div>

                <div className="feature-item">
                  <div className="feature-item__icon">🔐</div>
                  <h3>Chaotic Encryption</h3>
                  <p>Logistic maps & chaotic sequences for pixel-level encryption</p>
                </div>

                <hr className="pill-sep" />

                <div className="feature-item">
                  <div className="feature-item__icon">📊</div>
                  <h3>Quality Metrics</h3>
                  <p>Real-time entropy, NPCR, and UACI calculations</p>
                </div>
              </article>
            </section>

          {/* RIGHT column: step cards */}
          <section className="steps steps--cards">
            <article className="pill-card">
              <div className="pill-card__year">STEP 1</div>
              <div className="pill-card__icon">📤</div>
              <h3>Upload</h3>
              <p>Select an image file using drag-and-drop or file picker</p>
            </article>

            <article className="pill-card">
              <div className="pill-card__year">STEP 2</div>
              <div className="pill-card__icon">🔑</div>
              <h3>Encrypt</h3>
              <p>Enter or generate a strong key and apply chaotic encryption</p>
            </article>

            <article className="pill-card">
              <div className="pill-card__year">STEP 3</div>
              <div className="pill-card__icon">🧪</div>
              <h3>Analyze</h3>
              <p>Review encryption quality metrics & visual results</p>
            </article>

            <article className="pill-card">
              <div className="pill-card__year">STEP 4</div>
              <div className="pill-card__icon">🔗</div>
              <h3>Download</h3>
              <p>Save the encrypted or decrypted image or Share the results</p>
            </article>
          </section>
        </div>
      </div>


      
      {/* <div className="card">
        <div className="card-header">
          <h2 className="card-title">Security Advantages</h2>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
          <div>
            <h3>🔄 Non-Linear Transformation</h3>
            <p>Chaotic maps provide unpredictable, non-linear transformations that are highly sensitive to initial conditions</p>
          </div>
          
          <div>
            <h3>🎯 Pixel-Level Security</h3>
            <p>Each pixel is transformed using chaotic sequences, providing granular security</p>
          </div>
          
          <div>
            <h3>🔑 Key Sensitivity</h3>
            <p>Small changes in the encryption key produce completely different results</p>
          </div>
          
          <div>
            <h3>📈 High Entropy</h3>
            <p>Encrypted images achieve high entropy values, indicating strong randomness</p>
          </div>
        </div>
      </div> */}
      
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Get Started</h2>
        </div>
        
        <p style={{ fontSize: '1.2rem', fontWeight: 600, margin: 0 }}>
          Ready to experience the power of chaotic encryption?
        </p>

        <p style={{ fontSize: '1.1rem', color: '#555', marginTop: '8px', marginBottom: '25px' }}>
          Start by{" "}
          <Typewriter
            words={[
              "clicking the button below"
            ]}
            typingSpeed={70}
            deletingSpeed={45}
            pauseTime={1100}
            loop
          />
          
        </p>
        
        {/* <Link to="/encrypt" className="btn btn-primary" style={{ fontSize: '1.2rem', padding: '1rem 2rem' }}>
          🚀 Start Encrypting
        </Link> */}

        <button
          onClick={() => handleClick('/encrypt')}
          className="btn btn-primary btn--lg"
          style={{ fontSize: '1.2rem', padding: '1rem 2rem' }}
        >
          🚀 Start Encrypting
        </button>
      </div>

      {/* Captcha Modal */}
      <CaptchaModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onVerify={handleVerified}
      />

    </div>
  );
};

export default Home;
