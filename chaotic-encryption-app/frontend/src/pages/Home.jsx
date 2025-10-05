// import React from 'react';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Typewriter from "../components/Typewriter";


const Home = () => {
  const navigate = useNavigate();


  return (
    <div className="text-center">
      <div className="card hero">
        <div className="card-header">
          <h1 className="card-title" style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
            🔐 Chaotic Image Encryption
          </h1>
          <p style={{ fontSize: '1rem', color: '#666' }}>
            Advanced image encryption using chaotic maps for enhanced security
          </p>
          <p style={{ fontSize: '1rem', color: '#666' }}>
            Protect sensitive visuals and ensure privacy with our reliable, user-friendly image encryption solution. 
          </p>
        </div>

       

        {/* “Get Started” lines */}
        <div style={{ margin: '10px 0 18px' }}>
          <p style={{ fontSize: '1.15rem', fontWeight: 600, margin: 0 }}>
            Ready to experience the power of chaotic encryption?
          </p>
          <p style={{ fontSize: '1.05rem', color: '#555', margin: '8px 0 18px' }}>
            Start by{' '}
            <Typewriter
              words={[
                'selecting from one of the options below',
              ]}
              typingSpeed={70}
              deletingSpeed={45}
              pauseTime={1100}
              loop
            />
          </p>
        </div>
        
        <div className="d-flex justify-center gap-2 mb-3">
          {/* <Link to="/encrypt" className="btn btn-primary">
            🔒 Encrypt Image
          </Link>
          <Link to="/decrypt" className="btn btn-secondary">
            🔓 Decrypt Image
          </Link> */}

          <button onClick={() => navigate('/encrypt')} className="btn btn-primary btn--md">
            🔒 Encrypt Image
          </button>
          <button onClick={() => navigate('/decrypt')} className="btn btn-secondary btn--md">
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
          <h2 className="card-title">FAQ</h2>
        </div>

        <div className="faq">
          <details>
            <summary>What image formats are supported?</summary>
            <p>PNG, JPG/JPEG, BMP, and TIFF (up to 16 MB)</p>
          </details>

          <details>
            <summary>Is my encryption key stored anywhere?</summary>
            <p>No. Keys are used in-session only and never persisted by the app</p>
          </details>

          <details>
            <summary>Can I decrypt later on another device?</summary>
            <p>Yes. Keep the exact same key you used for encryption, and the encrypted image</p>
          </details>

          <details>
            <summary>Does this run locally or on a server?</summary>
            <p>Processing runs in the app runtime; the image and key are not uploaded to third-party services</p>
          </details>

          <details>
            <summary>How do I choose a strong key?</summary>
            <p>Use 16+ characters with a mix of letters, numbers, and symbols. Avoid dictionary words</p>
          </details>

          <details>
            <summary>What are NPCR and UACI?</summary>
            <p>
              Common quality metrics for image ciphers - higher NPCR/UACI generally indicate stronger
              diffusion and randomness
            </p>
          </details>
        </div>
      </div>




    </div>
  );
};

export default Home;
