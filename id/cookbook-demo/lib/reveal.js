/* ─────────────────────────────────────────────────────────────
   RECIPE: reveal.js — scroll reactions
   CUT type: SCROLL (and PAUSE, via scrollResist)

   The reader's body is the instrument. These read the scroll and let the
   story answer: fade things in, boot them line by line, swell a sound as a
   section arrives, or make the page feel heavy.

   All four functions attach to `cyb`. Pair with base.css, which hides
   [data-reveal] elements until .is-revealed is added.

   NEEDS: nothing — native Intersection Observer + scroll math.
   ───────────────────────────────────────────────────────────── */
window.cyb = window.cyb || {};

/* onReveal(selector, cb, opts) — run cb(el) ONCE, the first time each matching
   element scrolls into view. Good for: play a sound on arrival, reveal a figure.

     cyb.onReveal('.bird-call', el => cuckoo());               */
cyb.onReveal = function (selector, cb, opts = {}) {
  const io = new IntersectionObserver((entries, obs) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        cb(e.target);
        obs.unobserve(e.target);          // fire once, then forget
      }
    });
  }, { threshold: opts.threshold ?? 0.15, rootMargin: opts.rootMargin ?? '0px' });
  document.querySelectorAll(selector).forEach(el => io.observe(el));
  return io;
};

/* stagger(selector, stepMs) — reveal a set of [data-reveal] elements one after
   another, like a machine rebooting line by line. Trigger it whenever the moment
   is right (on a thunder crack, on scroll, on a timer).

     cyb.stagger('[data-section="after"] [data-reveal]', 90);  */
cyb.stagger = function (selector, stepMs = 90) {
  [...document.querySelectorAll(selector)].forEach((el, i) => {
    setTimeout(() => el.classList.add('is-revealed'), i * stepMs);
  });
};

/* sectionProgress(el) — 0 while `el` is below the fold, 1 once fully passed,
   smoothly in between. Feed it into audio gains, opacities, anything reactive.

     const p = cyb.sectionProgress(storm);   // 0..1                */
cyb.sectionProgress = function (el) {
  const r  = el.getBoundingClientRect();
  const wh = window.innerHeight;
  if (r.top    >  wh) return 0;
  if (r.bottom <  0)  return 1;
  return (wh - r.top) / (wh + r.height);
};

/* scrollResist(getFactor) — make the page feel heavy / underwater. While the
   factor is truthy, each wheel tick moves the page by that fraction of normal
   (0.5 = half speed). Pass a function so you can turn it on and off; return 0
   or false to release. Returns stop() to remove the handler entirely.

     const release = cyb.scrollResist(() => inStorm ? 0.5 : 0);
     // ...later: release();

   Note: only affects the mouse wheel (trackpad/desktop), by design — it slows
   without trapping. */
cyb.scrollResist = function (getFactor) {
  const onWheel = (e) => {
    const f = typeof getFactor === 'function' ? getFactor() : getFactor;
    if (!f) return;
    e.preventDefault();
    window.scrollBy({ top: e.deltaY * f, behavior: 'instant' });
  };
  window.addEventListener('wheel', onWheel, { passive: false });
  return () => window.removeEventListener('wheel', onWheel);
};
