/* ─────────────────────────────────────────────────────────────
   RECIPE: textfx.js — the words themselves misbehave
   CUT type: TEXT_FX

   Small effects on the text layer: a signal breaking up, letters rotting
   away, a line typing itself out of nothing. Reach for these when the prose
   should feel handled by something that isn't quite alive.

   Each attaches to `cyb`. All operate on a single element's textContent.

   NEEDS: nothing.
   ───────────────────────────────────────────────────────────── */
window.cyb = window.cyb || {};

/* glitch(el, opts) — briefly scramble an element's text, then restore it.
   A transient — the signal recovers.

     cyb.glitch(document.querySelector('.key-line'));           */
cyb.glitch = function (el, { chars = '▓▒░#@%&*', duration = 600, fps = 20 } = {}) {
  const original = el.textContent;
  const start = performance.now();
  const tick = () => {
    if (performance.now() - start >= duration) { el.textContent = original; return; }
    el.textContent = original.split('').map(c =>
      c === ' ' ? ' ' : (Math.random() < 0.3 ? chars[(Math.random() * chars.length) | 0] : c)
    ).join('');
    setTimeout(tick, 1000 / fps);
  };
  tick();
};

/* degrade(el, pct) — permanently eat `pct` (0..1) of an element's characters,
   replacing them with gaps. Call repeatedly with a rising pct to rot a line as
   the reader scrolls. Remembers the original text on the element.

     cyb.degrade(line, 0.1);  // ...later:  cyb.degrade(line, 0.4);   */
cyb.degrade = function (el, pct = 0.1) {
  const full  = el.dataset.cybFull || (el.dataset.cybFull = el.textContent);
  const chars = full.split('');
  const holes = Math.floor(chars.length * Math.min(1, Math.max(0, pct)));
  const idx   = [...chars.keys()].filter(i => chars[i] !== ' ');
  for (let k = 0; k < holes && idx.length; k++) {
    chars[idx.splice((Math.random() * idx.length) | 0, 1)[0]] = ' ';
  }
  el.textContent = chars.join('');
};

/* typewriter(el, opts) — reveal an element's text one character at a time.
   Returns a promise that resolves when the line finishes.

     await cyb.typewriter(el, { cps: 40 });                     */
cyb.typewriter = function (el, { cps = 40 } = {}) {
  const text = el.textContent;
  el.textContent = '';
  return new Promise(resolve => {
    let i = 0;
    const tick = () => {
      el.textContent = text.slice(0, ++i);
      if (i < text.length) setTimeout(tick, 1000 / cps);
      else resolve();
    };
    tick();
  });
};
