/* ─────────────────────────────────────────────────────────────
   RECIPE: loader.js — the boot screen + the [start story] gate
   CUT type: (framing — most pieces open with this)

   cyBorge preloads what the story needs, shows a status line while it works,
   then reveals a [ start story ] button. That click is the user gesture that
   unlocks audio — so wire audio.unlock() (and the story's opening beat) into
   onStart.

   NEEDS this markup (styled in base.css):
     <div id="loader"><div class="loader-inner">
       <p id="loader-status">cyBorge: [initialising]</p>
       <button id="start-btn">[ start story ]</button>
     </div></div>

   HOW TO USE:
     cyb.loader({
       assets: [
         { label: 'rain',    load: async () => { rain  = await audio.layerLoop('audio/rain.mp3', 0); } },
         { label: 'thunder', load: async () => { crack = await audio.oneShot('audio/crack.mp3'); } },
       ],
       onStart: () => { audio.unlock(); beginStory(); },   // fires on the click
     });

   Each asset's `load` returns a promise; the loader awaits them in order and
   shows "cyBorge: [loading <label>]" as it goes.
   ───────────────────────────────────────────────────────────── */
window.cyb = window.cyb || {};

cyb.loader = async function ({ assets = [], onReady, onStart, statusPrefix = 'cyBorge' } = {}) {
  const loader = document.getElementById('loader');
  const status = document.getElementById('loader-status');
  const btn    = document.getElementById('start-btn');
  if (!loader || !btn) return;

  try {
    for (const a of assets) {
      if (status) status.textContent = `${statusPrefix}: [loading ${a.label}]`;
      await a.load();
    }
  } catch (e) {
    if (status) status.textContent = `${statusPrefix}: [something failed]`;
    console.warn('[loader]', e);
  }

  if (status) status.textContent = `${statusPrefix}: [ready]`;
  if (onReady) onReady();

  btn.classList.add('visible');
  btn.addEventListener('click', () => {
    if (onStart) onStart();
    loader.style.opacity = '0';
    setTimeout(() => loader.remove(), 900);
  }, { once: true });
};
