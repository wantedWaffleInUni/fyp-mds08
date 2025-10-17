import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Typewriter from "../components/Typewriter";
import introJs from 'intro.js';
import 'intro.js/introjs.css';
import '../App.css';


const Home = () => {
  const navigate = useNavigate();


  useEffect(() => {
    // Prevent Intro.js from running multiple times in React Strict Mode
    if (!window.__introAlreadyStarted) {
      window.__introAlreadyStarted = true;


      const intro = introJs();
      intro.setOptions({
        steps: [
          {
            intro: "👋 Welcome to PEEKP🔑C! This is a system for image encryption and decryption using chaotic maps.",
            tooltipClass: 'custom-tooltip-large'
          },
          {
            element: '.btn-primary',
            intro: "Click here to upload and encrypt an image 🔒",
            position: 'right',
            tooltipClass: 'custom-tooltip-large'
          },
          {
            element: '.btn-secondary',
            intro: "Click here to upload and decrypt an image 🔓",
            position: 'left',
            tooltipClass: 'custom-tooltip-large'
          },
          {
            element: '#results-showcase',
            intro: "Quick preview of how images look before and after encryption/decryption 🧪",
            tooltipClass: 'custom-tooltip-large'
          },
          {
            element: '.features-steps-grid',
            intro: "Here you can explore the system's main features and workflow 🧭",
            tooltipClass: 'custom-tooltip-large'
          },
          {
            element: '.faq',
            intro: "Check frequently asked questions here 📖",
            tooltipClass: 'custom-tooltip-large'
          }
        ],
        showProgress: true,
        showButtons: true,
        exitOnOverlayClick: true,
        nextLabel: 'Next →',
        prevLabel: '← Back',
        doneLabel: 'Finish',
        tooltipPosition: 'auto',
        scrollTo: 'tooltip',
        overlayOpacity: 0.8,
        tooltipClass: 'custom-tooltip-large'
      });


      intro.start();

      
    }
  }, []);


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


        {/* “Get Started” section */}
        <div style={{ margin: '10px 0 18px' }}>
          <p style={{ fontSize: '1.15rem', fontWeight: 600, margin: 0 }}>
            Ready to experience the power of chaotic encryption?
          </p>
          <p style={{ fontSize: '1.05rem', color: '#555', margin: '8px 0 18px' }}>
            Start by{' '}
            <Typewriter
              words={['selecting one of the options below']}
              typingSpeed={70}
              deletingSpeed={45}
              pauseTime={1100}
              loop
            />
          </p>
        </div>


        <div className="d-flex justify-center gap-2 mb-3">
          <button onClick={() => navigate('/encrypt')} className="btn btn-primary btn--lg">
             Encrypt Image
          </button>
          <button onClick={() => navigate('/decrypt')} className="btn btn-secondary btn--lg">
             Decrypt Image
          </button>
        </div>
      </div>

      {/* Results Showcase */}
      <div className="card results-showcase" id="results-showcase">
        <div className="card-header">
          <h2 className="card-title">See It In Action</h2>
          <p className="results-subtitle">Original → Encrypted → Decrypted</p>
        </div>

        <ResultsCarousel />
      </div>


      {/* Features & Steps */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Key Features & How It Works</h2>
        </div>


        <div className="features-steps-grid">
          <section className="features features--cards">
            <article className="pill-card pill-card--stack">
              <div className="pill-card__label">FEATURES</div>


              <div className="feature-item">
                <div className="feature-item__icon">🔐</div>
                <h3>Chaotic Encryption</h3>
                <p>Utilizes logistic maps and chaotic sequences for pixel-level encryption</p>
              </div>


              <hr className="pill-sep" />


              <div className="feature-item">
                <div className="feature-item__icon">📊</div>
                <h3>Quality Metrics</h3>
                <p>Real-time entropy, NPCR, and UACI calculations</p>
              </div>
            </article>
          </section>


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
              <p>Review encryption quality metrics and visual results</p>
            </article>


            <article className="pill-card">
              <div className="pill-card__year">STEP 4</div>
              <div className="pill-card__icon">🔗</div>
              <h3>Download</h3>
              <p>Save the encrypted or decrypted image or share the results</p>
            </article>
          </section>
        </div>
      </div>


      {/* FAQ Section */}
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
            <p>No. Keys are used only in-session and never saved by the app.</p>
          </details>


          <details>
            <summary>Can I decrypt on another device?</summary>
            <p>Yes. Just use the same key and the encrypted image.</p>
          </details>


          <details>
            <summary>Does this run locally or on a server?</summary>
            <p>Processing happens in the app itself. No third-party uploads.</p>
          </details>


          <details>
            <summary>How do I choose a strong key?</summary>
            <p>Use 16+ characters with letters, numbers, and symbols. Avoid dictionary words.</p>
          </details>


          <details>
            <summary>What are NPCR and UACI?</summary>
            <p>They are metrics to evaluate image cipher strength. The higher the values, the better the diffusion and randomness.</p>
          </details>
        </div>
      </div>
    </div>
  );


  
};

const ResultsCarousel = () => {
  // Each page shows: Original → Encrypted → Decrypted
  const pages = [
    {
      caption: "Sample 1",
      items: [
        { label: "Original",  src: "/showcase/kodim13.png" },
        { label: "Encrypted", src: "/showcase/FODHNN_kodim13_enc.png" },
        { label: "Decrypted", src: "/showcase/FODHNN_kodim13_dec.png" }
      ]
    },

    {
      caption: "Sample 2",
      items: [
        { label: "Original",  src: "/showcase/kodim02.png" },
        { label: "Encrypted", src: "/showcase/grey_kodim02_enc.png" },
        { label: "Decrypted", src: "/showcase/grey_kodim02_dec.png" }
      ]
    },
  ];

  const total = pages.length;
  const [page, setPage] = React.useState(0);
  const prev = () => setPage((p) => (p - 1 + total) % total);
  const next = () => setPage((p) => (p + 1) % total);

  const { caption, items } = pages[page];

  return (
    <div className="results-stage">
      <div className="results-caption">{caption}</div>

      <div className="results-frame">
        <button className="results-arrow left" onClick={prev} aria-label="Previous samples">‹</button>

        <div className="results-grid">
          {items.map((img, i) => (
            <figure key={i} className="result-card">
              <img src={img.src} alt={`${img.label} preview`} loading="lazy" />
              <figcaption>{img.label}</figcaption>
            </figure>
          ))}
        </div>

        <button className="results-arrow right" onClick={next} aria-label="Next samples">›</button>
      </div>

      
    </div>
  );

};



export default Home;
