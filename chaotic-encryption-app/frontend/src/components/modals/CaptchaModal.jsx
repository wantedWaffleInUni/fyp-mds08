// src/components/modals/CaptchaModal.jsx
import React, { useState } from 'react';
import ReCAPTCHA from 'react-google-recaptcha';
import Modal from './Modal';

const SITE_KEY = "6LeEzNwrAAAAAIjy_YwGLqff60fzSGvFh9tQLpO-"; // replace with real site key
// 
// export default function CaptchaModal({ open, onClose, onVerify }) {
//   const [verified, setVerified] = useState(false);
// 
//   const handleVerify = (token) => {
//     if (token) {
//       setVerified(true);
//       onVerify(token); // Pass token back to parent (optional: server validation)
//     }
//   };
// 
//   return (
//     <Modal open={open} onClose={onClose} ariaLabel="Captcha Verification">
//       <div style={{ padding: '2rem', textAlign: 'center' }}>
//         <h2>Please verify to continue</h2>
//         <ReCAPTCHA sitekey={SITE_KEY} onChange={handleVerify} />
//         <div style={{ marginTop: '1.5rem' }}>
//           <button
//             className="btn btn-primary"
//             disabled={!verified}
//             onClick={onClose}
//           >
//             Continue
//           </button>
//         </div>
//       </div>
//     </Modal>
//   );
// }

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
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <h2>Please verify to continue</h2>

        <ReCAPTCHA sitekey={SITE_KEY} onChange={handleVerify} />
        {/* <div>captcha placeholder</div> */}

        <div style={{ marginTop: '1.5rem' }}>
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
