/* ─────────────────────────────────────────────────────────────
   RECIPE: flash.js — a full-screen wash of colour, then fade
   CUT type: VISUAL

   The lightning strike. The cut to white. The blowout that hides a scene
   change underneath it. Fire it on a beat and let the page reset behind it.

   NEEDS one element (styled in base.css):
     <div id="flash-overlay"></div>

   HOW TO USE:
     await cyb.flash({ color: '#ffffff', hold: 100, fade: 700 });
     // resolves when the fade completes — good for sequencing what comes next.

   hold = ms held at full colour.  fade = ms to fade back to nothing.
   ───────────────────────────────────────────────────────────── */
window.cyb = window.cyb || {};

cyb.flash = function ({ color = '#ffffff', hold = 100, fade = 700, el } = {}) {
  const overlay = el || document.getElementById('flash-overlay');
  if (!overlay) return Promise.resolve();

  return new Promise(resolve => {
    overlay.style.background = color;
    overlay.style.transition = 'opacity 0.06s';
    overlay.style.opacity    = '1';                 // snap to full — the strike

    setTimeout(() => {
      overlay.style.transition = `opacity ${fade}ms ease`;
      overlay.style.opacity    = '0';               // ...and fade
      setTimeout(resolve, fade);
    }, hold);
  });
};
