// src/components/modals/Modal.jsx
import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';

export default function Modal({
  open,
  onClose,
  children,
  ariaLabel = 'Dialog',
  backdropClosable = true,
}) {
  // ✅ Hook is always called; it only *does work* when open = true
  useEffect(() => {
    if (!open) return; // <-- returns undefined (fine; React will not call cleanup)

    const onKey = (e) => e.key === 'Escape' && onClose?.();

    document.addEventListener('keydown', onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    // ✅ Cleanup returns a function (not the result of a call)
    return () => {
      document.body.style.overflow = prev;
      document.removeEventListener('keydown', onKey);
    };
  }, [open, onClose]);

  if (!open) return null;

  return createPortal(
    <div
      className="modal-backdrop"
      role="dialog"
      aria-modal="true"
      aria-label={ariaLabel}
      onClick={(e) => backdropClosable && e.target === e.currentTarget && onClose?.()}
    >
      <div className="modal">{children}</div>
    </div>,
    document.body
  );
}
