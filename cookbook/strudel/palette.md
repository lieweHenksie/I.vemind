# Recipe — the Agar palette (copy-me Strudel instruments)

The synth voices we built for cyBorge's songs. All **synthesised** — no tacky sample kits.
Paste the ones you want into a song's score (the `<textarea>`), then tweak. Everything is in
**A minor**; transpose by shifting the note names.

Rule of thumb per voice: `.gain()` = how loud, `.lpf()` = how bright, `.room()` = how far away,
`.delay()` = echo. Lower `lpf` = darker/more buried.

---

## Bass & drums

```js
// BASS — driving detuned saw, moody minor, a slow filter that breathes
let bass = note("a1 a1 e2 g1 a1 a1 c2 e2").s("sawtooth")
  .lpf(sine.range(250, 900).slow(8)).lpq(8)
  .gain(0.8)

// KICK — a deep SINE sub-thud on 1 & 3 (a slowed bass note, not a sample). This is "deep drums".
let kick = note("a1 ~ ~ ~ a1 ~ ~ ~").s("sine")
  .attack(0.001).decay(0.28).sustain(0)
  .gain(1)

// HATS — ticking synth hi-hats: white noise, tiny envelope, high-passed
let hats = s("white*8").decay(0.02).sustain(0).hpf(8000).gain(0.22)

// CLAP — a snappy backbeat on 2 & 4 (noise burst)
let clap = s("~ white ~ white").decay(0.09).sustain(0).hpf(1400).gain(0.4).room(0.35)

// SUB-HARD — deep, distorted, driving bass (hardcore/gabber energy). Sits ALONGSIDE `bass`.
let subHard = note("a0 a0 e1 a0 g0 a0 e1 g0").s("sawtooth").shape(0.6).lpf(600).lpq(5).gain(0.8)
```

## Melodic — arps, pad, lead, solo

```js
// ARP — the hypnotic Agar signature, ping-ponging into delay
let arp = note("[a3 e4 c4 e4 g4 e4 c4 b3]*2").s("triangle")
  .lpf(1600).delay(0.5).delaytime(0.375).delayfeedback(0.35).room(0.6).gain(0.45)

// ARP 2 — a higher variation, for a bridge or a lift
let arp2 = note("[e4 a4 c5 b4 a4 e4 c4 a3]*2").s("triangle")
  .lpf(1800).delay(0.5).delaytime(0.375).delayfeedback(0.35).room(0.6).gain(0.4)

// ARP FAST — busier 16ths, brighter square — for a solo/climax
let arpFast = note("[a3 c4 e4 g4 a4 g4 e4 c4]*4").s("square")
  .lpf(2200).delay(0.4).delaytime(0.1875).delayfeedback(0.3).room(0.5).gain(0.28)

// PAD — one woozy chord per bar (Am F C E)
let pad = note("<[a3,c4,e4] [f3,a3,c4] [c3,e3,g3] [e3,g3,b3]>").s("sawtooth")
  .attack(0.8).release(1.5).lpf(700).gain(0.3).room(0.85)

// BRIDGE PAD — a different progression (Dm C F G) that lifts the harmony
let bridgePad = note("<[d4,f4,a4] [c4,e4,g4] [f3,a3,c4] [g3,b3,d4]>").s("sawtooth")
  .attack(0.8).release(1.5).lpf(850).gain(0.32).room(0.85)

// LEAD — one long, simple held note per bar
let lead = note("<a4 c5 b4 e4>").s("triangle")
  .lpf(1300).release(0.3).room(0.7).gain(0.5)

// SOLO — a two-bar melodic run (alternates two phrases)
let solo = note("<[a4 c5 e5 d5 c5 b4 a4 e4] [g4 a4 b4 c5 e5 d5 b4 a4]>").s("triangle")
  .lpf(2400).delay(0.4).delaytime(0.375).delayfeedback(0.4).room(0.5).gain(0.5)
```

## Textures & FX — for breakdowns / drops

```js
// WASH — a dark atmosphere bed (filtered noise, drenched in reverb)
let wash = s("white").lpf(500).gain(0.12).room(0.9)

// RISER — tension that sweeps upward over its section (saw-swept noise)
let riser = s("white").lpf(saw.range(300, 8000).slow(8)).gain(0.18).room(0.7)

// IMPACT — a single deep sub-boom for a drop (put it in a 1-bar section: [1, impact])
let impact = note("a0").s("sine").attack(0.001).decay(1.6).sustain(0).gain(1).room(0.85)
```

---

Wire them together with [arrangement.md](arrangement.md). The whole song skeleton is in
[template.html](template.html).
