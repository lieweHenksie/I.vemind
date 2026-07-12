/* demo.js — wiring five cookbook recipes together, standalone.
   Reuses one of Azibo's audio beds so the demo needs no new assets. */
(function () {
  'use strict';

  const audio  = cyb.createAudio();
  const canvas = document.querySelector('.particle-canvas');
  const field  = cyb.particleField(canvas, { color: '#4a7c59', size: 2, gravity: 0.25, max: 700 });
  let bush;

  cyb.loader({
    assets: [
      { label: 'a layer', load: async () => {
          bush = await audio.layerLoop('../../ego/azibo/audio/bush-ambience.mp3', 0);
      } },
    ],
    onStart: () => {
      audio.unlock();
      bush.set(0.7, 3);                                  // audio.js — a bed fades in

      setInterval(() => field.rain(2), 120);            // particles.js — a slow fall

      // reveal.js — lines rise as they arrive
      cyb.onReveal('[data-reveal]', el => el.classList.add('is-revealed'));

      // flash.js — the mark strikes when it scrolls into view
      cyb.onReveal('[data-mark]', () => cyb.flash({ color: '#e8e4d9', hold: 80, fade: 600 }));
    },
  });
}());
