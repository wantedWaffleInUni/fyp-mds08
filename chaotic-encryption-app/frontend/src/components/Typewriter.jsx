import React, { useEffect, useState } from "react";

export default function Typewriter({
  words = [],
  typingSpeed = 70,        // ms per char
  deletingSpeed = 45,
  pauseTime = 1200,        // pause at word end
  loop = true,
  className = ""
}) {
  const [i, setI] = useState(0);           // word index
  const [text, setText] = useState("");    // visible text
  const [del, setDel] = useState(false);   // deleting?

  useEffect(() => {
    const current = words[i % words.length] || "";
    const doneTyping = text === current;
    const doneDeleting = del && text === "";

    let t = typingSpeed;

    if (!del) {
      // typing
      if (!doneTyping) {
        t = typingSpeed;
        const next = current.slice(0, text.length + 1);
        const id = setTimeout(() => setText(next), t);
        return () => clearTimeout(id);
      }
      // pause then start deleting
      const id = setTimeout(() => setDel(true), pauseTime);
      return () => clearTimeout(id);
    } else {
      // deleting
      if (!doneDeleting) {
        t = deletingSpeed;
        const next = current.slice(0, text.length - 1);
        const id = setTimeout(() => setText(next), t);
        return () => clearTimeout(id);
      }
      // move to next word
      const nextI = (i + 1) % words.length;
      if (!loop && nextI === 0) return; // stop if not looping
      setDel(false);
      setI(nextI);
    }
  }, [text, del, i, words, typingSpeed, deletingSpeed, pauseTime, loop]);

  return (
    <span className={`typewriter ${className}`} aria-live="polite">
      <span className="typewriter-text">{text}</span>
      <span className="typewriter-caret" aria-hidden="true" />
    </span>
  );
}
