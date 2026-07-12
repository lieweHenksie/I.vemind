/* ─────────────────────────────────────────────────────────────
   RECIPE: audio.js — layered ambience + one-shot hits
   CUT type: SOUND

   cyBorge remembers every sound it ever made. These are the layers.

   One shared AudioContext + compressor keeps levels sane when beds stack.
   A "layer" is a looping bed (rain, rumble, wind). A "one-shot" is a hit
   (a thunder crack, a bell, a bird call).

   HOW TO USE — copy this file into your piece, load it before your wiring
   script, then:

     const audio = cyb.createAudio();
     let rain, crack;
     // preload (a loader.js asset step is a good place):
     rain  = await audio.layerLoop('audio/rain.mp3', 0);   // starts silent
     crack = await audio.oneShot('audio/crack.mp3');        // preloaded hit
     // later, after the user has clicked [start story]:
     audio.unlock();          // REQUIRED inside a click handler (autoplay policy)
     rain.set(0.6, 2.5);      // fade the bed up to 0.6 over 2.5s
     crack();                 // fire the hit

   NEEDS: one audio file per layer / one-shot (mp3/ogg/wav).
   ───────────────────────────────────────────────────────────── */
window.cyb = window.cyb || {};

cyb.createAudio = function () {
  const ctx = new (window.AudioContext || window.webkitAudioContext)();

  // A gentle compressor so stacked layers never clip or stab the ears.
  const bus = ctx.createDynamicsCompressor();
  bus.threshold.value = -10;
  bus.ratio.value     = 6;
  bus.connect(ctx.destination);

  // Decode a file into a reusable buffer.
  async function load(url) {
    const res = await fetch(url);
    const ab  = await res.arrayBuffer();
    return ctx.decodeAudioData(ab);
  }

  // Smoothly move a gain to `value` over `seconds`. No clicks, no pops.
  function ramp(gainNode, value, seconds = 0.3) {
    const now = ctx.currentTime;
    gainNode.gain.cancelScheduledValues(now);
    gainNode.gain.setValueAtTime(gainNode.gain.value, now);
    gainNode.gain.linearRampToValueAtTime(value, now + seconds);
  }

  // A looping ambience bed. Starts at `gain` (default silent), loops forever.
  // Returns a handle: .set(value, seconds) to fade, .stop() to end it.
  async function layerLoop(url, gain = 0) {
    const buf = await load(url);
    const g = ctx.createGain();
    g.gain.value = gain;
    g.connect(bus);

    const src = ctx.createBufferSource();
    src.buffer = buf;
    src.loop   = true;
    src.connect(g);
    src.start();                       // safe on a suspended ctx; plays on unlock()

    return {
      set:  (value, seconds = 0.3) => ramp(g, value, seconds),
      stop: () => { try { src.stop(); } catch (e) {} },
      node: g,
    };
  }

  // A one-shot hit. Preload once; call the returned function to fire it.
  // Overlapping fires are fine — each gets its own source.
  async function oneShot(url) {
    const buf = await load(url);
    return () => {
      const src = ctx.createBufferSource();
      src.buffer = buf;
      src.connect(bus);
      src.start();
    };
  }

  // Call inside a user-gesture handler (a click) to satisfy autoplay policy.
  const unlock = () => ctx.resume();

  return { ctx, bus, load, layerLoop, oneShot, unlock };
};
