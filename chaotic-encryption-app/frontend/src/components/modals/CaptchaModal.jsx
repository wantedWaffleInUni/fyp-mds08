// src/components/modals/CaptchaModal.jsx
import React, { useState } from 'react';
import ReCAPTCHA from 'react-google-recaptcha';
import Modal from './Modal';

const SITE_KEY = "6LeEzNwrAAAAAIjy_YwGLqff60fzSGvFh9tQLpO-"; // replace with real site key


export default function CaptchaModal({ open, onClose, onVerify }) {
  const [verified, setVerified] = useState(false);
  const [token, setToken] = useState(null);

  const handleVerify = (token) => {
    if (token) {
      setVerified(true);
      setToken(token);
    }
  };

  const handleContinue = () => {
    if (verified && token) {
      onVerify(token);   // triggers navigation from Home.js
      onClose();         // close modal
    }
  };

  return (
    <Modal open={open} onClose={onClose} ariaLabel="Captcha Verification">
      <div className="captcha-modal">
        <h2>Please verify to continue</h2>
  
        <div className="captcha-box">
          <ReCAPTCHA sitekey={SITE_KEY} onChange={handleVerify} />
          {/* or <ReCAPTCHA sitekey={SITE_KEY} onChange={handleVerify} size="normal" /> */}
        </div>

        <div className="captcha-actions">
          <button
            className={`btn ${verified && token ? 'btn-primary' : 'btn-disabled'}`}
            disabled={!verified || !token}
            onClick={handleContinue}
          >
            Continue
          </button>
        </div>

      </div>
    </Modal>
  );
}
