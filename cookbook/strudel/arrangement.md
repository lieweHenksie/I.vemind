# Recipe — the arrangement pattern (voice locked to music)

How a cyBorge song is put together: **one `arrange()` timeline** for the MUSIC, with section
lengths for voice lines coming from an auto-managed `bars` array — and the voice clips themselves
played by the page's **voice bus**, scheduled sample-accurately on the WebAudio clock. Voice +
music share the same bar math, so they never drift; and because a voice line is not a strudel
event, main-thread jank can never make a line start late or skip (a one-shot only fires once —
it must be bulletproof).

## The three pieces

```js
// 1) BARS — one entry per voice line = how many bars that line occupies.
//    tools/tts/eleven.py rewrites this between the markers on every render — DON'T hand-edit it.
// BARS-START
let bars = [4, 6, 3, 3, 5, 8, 3]
// BARS-END

// 2) THE VOICE BUS (in the page, not the score) — at play, every line is armed directly on the
//    WebAudio clock at its row's start bar, from the preloaded buffer cache. The score never
//    contains voice events; eleven.py's VOICE_FILES/VOICE_TEXTS markers feed the bus + typewriter.

// 3) ARRANGE — [barCount, whatPlays] rows, played in turn. Voice rows use bars[i] as their
//    length, so a re-render (new word lengths) re-fits the whole song.
arrange(
  [8,       bass],                          // an instrumental section
  [bars[0], stack(kick, bass, arp)],        // a voice line's slot — MUSIC only, the bus speaks
  ...
)
```

## Section templates (mix & match)

```js
// INTRO — build it up, a layer at a time
[4, bass],
[4, stack(bass, kick)],
[4, stack(bass, kick, hats)],

// A VOICE LINE — line i's slot, over whatever layers you want. Strip layers for intimacy,
// stack them for intensity. The dialogue lands harder when you drop to bare bass:
[bars[0], stack(kick, hats, bass, arp, pad)],   // full groove under the line
[bars[2], bass],                                 // bare — a breakdown line
[bars[5], silence],                              // a line truly ALONE (build.py emits this for layers: [])

// BREAKDOWN — fall away, build tension, drop
[4, stack(bass, wash)],
[4, stack(bass, riser, wash)],
[1, impact],

// CLIMAX / OUTRO
[8, stack(kick, hats, clap, bass, arpFast, pad, lead, solo)],
[8, stack(bass, lead)],
```

## Arcs within a line (`split`)

A voice line can hold its own arc — the music **drops or changes mid-sentence** while the voice
carries on. Instead of `{ "voice": i, "layers": [...] }`, give the line a `split`:

```json
{ "voice": 7, "split": [ [5, ["kick","hats","bass","arp","pad"]],
                         [4, ["bass","wash"]],
                         [4, ["kick","hats","bass","solo"]] ] }
```

The voice **fires once** (at the first sub-section, via the bus) and **rings out** across all of
them — the middle `[4, ["bass","wash"]]` is a bare drop *under a line that's still speaking*.
Make the split bars **sum ≈ that line's rendered bars** (see the render log / `timing.md`) so the
next line still lands on time. Reserve it for long or turning lines.

## The words are load-bearing (labels)

Every section's `label` renders ON SCREEN as the piece's hero title: the text before the em-dash
is the **title**, after it the **subtitle** — so write labels as full invocations
(`"THE SNEEZE — the forest holds its breath"`), not comments. Two side effects to wield on purpose:

- a label containing **"drop"** (any case) marks the section as a **punch** — the film bounces
  there. Use it only on actual drops; a drop without the word can set `"punch": true`. (Careful
  with phrases like *"beat drops out"* — they punch too.)
- the **sea** (the visualizer back wall) follows each row's **energy** = its layer count vs the
  song's max. Sparse rows read as hush on screen; author density with the picture in mind — the
  water receding before a drop is free drama.

The essay's words themselves ship automatically (eleven.py → `VOICE_TEXTS` → the typewriter).

## The laws (learned in blood — see also cookbook/strudel/README.md)

- **Voice clips never live in the score.** A one-shot strudel event can start late or be skipped
  under render load, and a line only fires once — the page's voice bus owns them.
- **Never build a mini-notation string with `"text" + variable`** — every `"…"` is parsed as
  mini-notation, so `s("voice:" + i)` breaks the parser.
- **Voice slots read `bars[i]`** so a re-render (new word lengths) re-fits the song.
- Adding/removing a voice *line* is a shape change: it needs a new/removed `arrange` row (the
  `bars` array, voice files, and typewriter texts auto-sync, but where the line sits musically
  is yours to place).
