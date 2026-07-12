/* ─────────────────────────────────────────────────────────────
   RECIPE: particles.js — a field of little agents that fall and settle
   CUT type: PIXEL

   A swarm of tiny agents that spawn, walk downward, and pile up at the
   bottom of the viewport. Built for cyBorge's termites — letters detaching
   and crawling down the page — but it doesn't care what it's carrying:
   dust, snow, ash, sparks, rot.

   NEEDS one element (styled in base.css):
     <canvas class="particle-canvas"></canvas>
   Lift it above the prose (z-index: 2 in your <name>.css) when agents should
   crawl OVER the words; leave it behind (default) for weather.

   HOW TO USE:
     const field = cyb.particleField(canvas, {
       color: '#d4a843', size: 2, gravity: 0.35, drift: 0.6, max: 1200,
     });
     field.spawn(x, y, 20);   // release 20 agents at a point (a decaying letter)
     field.rain(3);           // release 3 from the top edge (weather), call per frame
     field.stop();            // freeze + clear
   ───────────────────────────────────────────────────────────── */
window.cyb = window.cyb || {};

cyb.particleField = function (canvas, opts = {}) {
  const cfg = {
    color: '#d4a843',   // agent colour
    size: 2,            // px per agent
    gravity: 0.35,      // downward pull per frame
    drift: 0.6,         // horizontal wander
    max: 1200,          // hard cap, so the page never chokes
    ...opts,
  };

  const ctx = canvas.getContext('2d');
  let agents  = [];
  let running = true;

  function resize() {
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize, { passive: true });

  function add(x, y) {
    if (agents.length >= cfg.max) return;
    agents.push({ x, y, vx: (Math.random() - 0.5) * cfg.drift, settled: false });
  }

  function frame() {
    if (!running) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = cfg.color;
    const floor = canvas.height - cfg.size;

    for (const a of agents) {
      if (!a.settled) {
        a.vx += (Math.random() - 0.5) * cfg.drift * 0.3;   // wander
        a.vx *= 0.92;                                       // damp
        a.x  += a.vx;
        a.y  += cfg.gravity + Math.random() * cfg.gravity;  // fall, unevenly
        if (a.y >= floor) { a.y = floor; a.settled = true; } // pile up
      }
      ctx.fillRect(a.x | 0, a.y | 0, cfg.size, cfg.size);
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  return {
    spawn: (x, y, count = 1) => { for (let i = 0; i < count; i++) add(x, y); },
    rain:  (count = 1)       => { for (let i = 0; i < count; i++) add(Math.random() * canvas.width, -5); },
    stop:  () => { running = false; ctx.clearRect(0, 0, canvas.width, canvas.height); },
    count: () => agents.length,
  };
};
