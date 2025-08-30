// src/components/modals/usePhasedProgress.js
import { useCallback, useEffect, useRef, useState } from 'react';

export default function usePhasedProgress(phases) {
  const [show, setShow] = useState(false);
  const [progress, setProgress] = useState(0);
  const [phase, setPhase] = useState('');
  const timerRef = useRef(null);

  const clearTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const start = useCallback((signal) => {
    setShow(true);
    const first = phases?.[0] ?? { from: 0, label: '' };
    setPhase(first.label);
    setProgress(first.from);

    clearTimer();
    let i = 0;
    let p = first.from;

    timerRef.current = setInterval(() => {
      if (signal?.aborted) {
        clearTimer();
        return;
      }
      const step = phases[i];
      const bump = i < 2 ? 1.2 : 0.6;
      p = Math.min(step.to, p + bump + Math.random() * 0.8);
      setProgress(p);

      if (p >= step.to && i < phases.length - 1) {
        i += 1;
        setPhase(phases[i].label);
        p = Math.max(p, phases[i].from);
      }
    }, 180);
  }, [phases]);

  const stop = useCallback(() => {
    clearTimer();
    setProgress(100);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearTimer(); // ✅ returns nothing (undefined), which is fine
    };
  }, []);

  // ✅ The hook itself returns ONLY data/functions, not a cleanup
  return { show, setShow, progress, phase, start, stop };
}
