import React from 'react';
import Modal from './Modal';

export default function ProgressModal({ open, progress, phase, onCancel }) {
  return (
    <Modal open={open} onClose={onCancel} ariaLabel="Progress">
      <div className="modal-body" style={{ textAlign: 'center', paddingTop: 28 }}>
        <div className="spinner" style={{ width: 36, height: 36, margin: '0 auto 16px' }} />
        <div className="progressbar" role="progressbar"
             aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.round(progress)}>
          <div className="progressbar-fill" style={{ width: `${progress}%` }} />
        </div>
        <div style={{ marginTop: 10, fontSize: 13 }}>{phase}</div>
      </div>
      <div className="modal-footer d-flex gap-2 justify-end">
        <button className="btn btn-secondary" onClick={onCancel}>Cancel</button>
      </div>
    </Modal>
  );
}
