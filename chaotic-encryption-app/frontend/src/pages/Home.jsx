import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <div className="text-center">
      <div className="card">
        <div className="card-header">
          <h1 className="card-title" style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
            🔐 Chaotic Image Encryption
          </h1>
          <p style={{ fontSize: '1.2rem', color: '#666' }}>
            Advanced image encryption using chaotic maps for enhanced security
          </p>
        </div>
        
        <div className="mb-3">
          <p style={{ fontSize: '1.1rem', lineHeight: '1.8' }}>
            This application demonstrates the power of chaotic encryption algorithms for securing digital images. 
            Unlike traditional encryption methods, chaotic encryption provides enhanced security through 
            unpredictable, non-linear transformations based on chaotic mathematical systems.
          </p>
        </div>
        
        <div className="d-flex justify-center gap-2 mb-3">
          <Link to="/encrypt" className="btn btn-primary">
            🔒 Encrypt Image
          </Link>
          <Link to="/decrypt" className="btn btn-secondary">
            🔓 Decrypt Image
          </Link>
        </div>
      </div>
      
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Key Features</h2>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem' }}>
          <div>
            <h3>🔐 Chaotic Encryption</h3>
            <p>Uses logistic maps and chaotic sequences for pixel-level encryption</p>
          </div>
          
          <div>
            <h3>📊 Quality Metrics</h3>
            <p>Real-time calculation of entropy, NPCR, and UACI for encryption quality assessment</p>
          </div>
          
          <div>
            <h3>🖼️ Image Support</h3>
            <p>Supports multiple image formats: PNG, JPG, JPEG, GIF, BMP</p>
          </div>
          
          <div>
            <h3>⚡ Fast Processing</h3>
            <p>Optimized algorithms for quick encryption and decryption</p>
          </div>
        </div>
      </div>
      
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">How It Works</h2>
        </div>
        
        <div style={{ textAlign: 'left', maxWidth: '800px', margin: '0 auto' }}>
          <ol style={{ lineHeight: '2', fontSize: '1.1rem' }}>
            <li><strong>Upload:</strong> Select an image file using drag-and-drop or file picker</li>
            <li><strong>Encrypt:</strong> Choose an encryption key and apply chaotic encryption</li>
            <li><strong>Analyze:</strong> View encryption quality metrics and visual results</li>
            <li><strong>Download:</strong> Save the encrypted/decrypted image to your device</li>
          </ol>
        </div>
      </div>
      
      <div className="card">
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
      </div>
      
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Get Started</h2>
        </div>
        
        <p style={{ fontSize: '1.1rem', marginBottom: '2rem' }}>
          Ready to experience the power of chaotic encryption? Start by uploading an image!
        </p>
        
        <Link to="/encrypt" className="btn btn-primary" style={{ fontSize: '1.2rem', padding: '1rem 2rem' }}>
          🚀 Start Encrypting
        </Link>
      </div>
    </div>
  );
};

export default Home;
