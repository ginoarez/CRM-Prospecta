"use client";
// Scramble effect driven by GSAP's ScrambleTextPlugin, triggered whenever the
// `text` prop changes (e.g. toggling login <-> register), not on mouse hover.
import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrambleTextPlugin } from 'gsap/ScrambleTextPlugin';

gsap.registerPlugin(ScrambleTextPlugin);

const ScrambleText = ({
  text,
  duration = 1.0,
  speed = 0.4,
  scrambleChars = 'upperCase',
  className = '',
  style = {},
}) => {
  const ref = useRef(null);
  const isFirst = useRef(true);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    // gsap fully owns the element's text so React can't overwrite mid-tween.
    if (isFirst.current) {
      isFirst.current = false;
      el.textContent = text;
      return;
    }
    const tween = gsap.to(el, {
      duration,
      ease: 'none',
      scrambleText: {
        text,
        chars: scrambleChars,
        speed,
        revealDelay: 0.2,
      },
    });
    return () => tween.kill();
  }, [text, duration, speed, scrambleChars]);

  // No children: gsap writes textContent. aria-label keeps it accessible.
  return <span ref={ref} className={className} style={style} aria-label={text} />;
};

export default ScrambleText;
