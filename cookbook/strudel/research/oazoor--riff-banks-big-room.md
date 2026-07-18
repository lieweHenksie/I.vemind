# Oazoor — "I Coded a Martin Garrix & Matt Pridgyn Track in Strudel (No DAW, No Keyboard)"

- source: https://www.youtube.com/shorts/IGm68hB72FI (short, 1:06)
- artist: Oazoor · Jean-François
- studied: 2026-07-18 · **frames-only study** (no captions — read via `transcribe.py --frames 6`,
  the eye's first outing; every move below was read off the screen, not un-garbled from audio)
- genre: big-room EDM / festival house

## The moves

1. **The riff bank.** Every part is an ARRAY of ~8 mininotation variations
   (`const RIFF_PIANO = [...]`), and the part is `pick(BANK, "<0 1 2 3 4 5 6 7>")` — the index
   pattern walks the bank one variation per cycle. Writing a part = writing its variations;
   8-bar phrases fall out for free, and every layer stays in step by sharing the same walk.
2. **Rhythm and harmony live apart, married by `.inhabit()`.** Chord voicings sit in one bank
   (`RIFF_BASS_PIANO_CHORD = ["[gb2,db2,gb3,a3]", …]`); rhythm is written as *index skeletons*
   (`"{[0 ~ ~ 0] [~ 0] …}"`) that `.inhabit(CHORD_BANK)` fills. Re-voice the harmony without
   touching a rhythm; re-groove the rhythm without touching a chord.
3. **Factory instruments.** `const createPiano = p => note(p).sound("piano").transpose(12).postgain(0.9)`
   — an instrument is a function; the same timbre chain serves any riff. Orchestration becomes
   function application.
4. **Thickness IS the arrangement.** The sections are the SAME riff walks under more factories:
   seq1 = piano+bass piano → seq2 = +four bass layers +synth → seq3 = +kick → seq4 = breakdown
   (filtered bass + violins). `arrange([8,seq1],[8,seq2],[16,seq3],[16,seq4])` — the song is an
   orchestration ladder, not new material.
5. **The four-bass pyramid.** One bassline rendered by four factories at once (pianoBass+12,
   mainBass, bass, ultraBass) — registral stacking is where the big-room size comes from.
6. **The drop holds long notes: `"{0@4}".inhabit(CHORDS)`** — same chord bank, whole-bar `@`
   elongation. The drop's weight is the *rhythm skeleton* changing, nothing else.
7. **Two samples in one voice.** `.sound("synth-oazoor:3,synth-oazoor:74".loop(1))` — a comma
   layers two samples inside a single sound string; `.loop(1)` sustains them. Instant ensemble.
8. **Mix discipline: `postgain` per part, `all(x => x.gain(0.5))` as master.** Levels are set
   after the FX chain; one global trim at the end.
9. **Tempo thought in bars: `setcpm(133/4)`** — BPM divided by beats-per-bar, so one cycle = one
   bar (matches how our build.py already counts).
10. **See everything:** `$:play._pianoroll({height:320,width:800})`, `.color("red")` per part —
    the piano roll is part of composing (REPL-only, like switch-angel's scope).

## Verified vocabulary

| move | exact Strudel | status |
|------|---------------|--------|
| bank walk | `pick(BANK, "<0 1 2 3 4 5 6 7>")` | **runtime-verified** — survived feedback in nice_ron (drop walks), fenton (film kit + bass), theGodInUrhead (wardbass) |
| skeleton fill | `"{[0 ~ ~ 0] [~ 0]}".inhabit(LOOKUP)` | **runtime-verified** — nice_ron + fenton + theGodInUrhead bass banks, confirmed by ear |
| held index | `"{0@4}".inhabit(CHORDS)` | **runtime-verified** — nice_ron drop II exhales on the held bar |
| post-FX level | `.postgain(0.15)` | **runtime-verified** — the crushed voices in nice_ron sit right |
| bar tempo | `setcpm(133/4)` | doc-verified · in pinned bundle (we use `.fast(BPM/120)` instead — same effect, arrange-local) |
| octave clone | `.transpose(12)` | doc-verified · in pinned bundle |
| sustained sample | `.sound("name:3".loop(1))` | doc-verified (sampler `loop`) |
| layered voice | `.sound("a:3,b:74")` | frame-read — comma-layered sound string, clear on screen; not doc-confirmed |
| piano roll | `._pianoroll({...})`, `.color()` | repl-only |
| filter ride | `.lpf(slider(...))` | repl-only (slider) — the *move* (filter-as-energy) is bankable, the widget is not |

**Garble corrections (video-compression edition):** on-screen rests read as `-` but the 1.0.3
mini-notation grammar only accepts `~` (verified by grepping the pinned bundle's parser char
class) — the tilde flattens to a dash at Shorts bitrate. `TRIADS.maj` read as `"0,5"` on screen
(likely `"0,4,7"` clipped); unused in the verified moves, recorded as uncertain.

## A recipe of ours (not theirs)

Our key (D minor), our motif — the *architecture* demonstrated, no Oazoor pattern lifted:

```js
// harmony bank — three voicings, one place to re-color the whole song
const CHORDS = ["[d2,a2,f3]", "[bb1,f2,d3]", "[c2,g2,e3]"]
// rhythm skeletons — indices into CHORDS; regroove without touching harmony
const BASSBANK = [
  "{[0 ~ ~ 0] [~ 0] [0 ~ ~ 0] [~ 0]}".inhabit(CHORDS),   // pushed
  "{[1 ~ ~ 1] [~ 1] [1 1] [1 1]}".inhabit(CHORDS),        // answered
  "{2@4}".inhabit(CHORDS),                                 // the drop hold
]
// factory instruments — one timbre chain, any riff
const mkBass = p => note(p).s("sawtooth").lpf(700).postgain(0.6)
const mkLead = p => note(p).s("triangle").transpose(12).postgain(0.8).room(0.4)
// thickness is the arrangement: same walk, more factories
arrange(
  [8, mkBass(pick(BASSBANK, "<0 0 1 0>"))],
  [8, stack(mkBass(pick(BASSBANK, "<0 0 1 2>")),
            mkLead(pick(BASSBANK, "<0 1>")))],
)
```

## Runtime notes

- **Spendable NOW on 1.0.3:** `pick`, `inhabit`/`inhabitmod`, `postgain`, `setcpm`, `transpose`,
  `@` holds, sampler `.loop` — all present in the pinned bundle (grep-verified, this study).
- **Untested on our embed:** `.sound("piano")` — the default sample bank may not load through
  our custom `initStrudel({prebake})`; test before a song leans on it (our songs synthesize or
  crate their own samples, so this hasn't come up).
- **No embed equivalent:** `slider()`, `._pianoroll()`, `.color()` — REPL widgets. The
  filter-as-energy move they serve is already banked (switch-angel study); ride `lpf` with a
  signal (`saw.range(...)`) instead of a hand.
- Candidate first spend: **riff banks + inhabit** would let a `/cyborge-score` write drop
  variations as data (skeletons over one chord bank) — a natural fit for `palette.json`, where
  banks are just more instrument strings.
