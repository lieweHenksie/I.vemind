# Recipe — the arrangement pattern (voice locked to music)

How a cyBorge song is put together: **one `arrange()` timeline** where the voice lines and the
music share a single clock, and the section lengths come from an auto-managed `bars` array so a
re-render re-fits everything. Voice + music never drift.

## The three pieces

```js
// 1) BARS — one entry per voice line = how many bars that line occupies.
//    tools/tts/eleven.py rewrites this between the markers on every render — DON'T hand-edit it.
// BARS-START
let bars = [4, 6, 3, 3, 5, 8, 3]
// BARS-END

// 2) VO — wrap a voice clip as a one-shot that holds across its slot (from `bars`).
let vo = (clip, i) => clip.slow(bars[i]).gain(1.15).room(0.2)

// 3) ARRANGE — [barCount, whatPlays] rows, played in turn, then looped.
//    Voice rows use bars[i] for BOTH the section length and vo()'s slow(), so they stay locked.
arrange(
  [8,       bass],                                                 // an instrumental section
  [bars[0], stack(kick, bass, arp, vo(s("voice:0"), 0))],         // a voice line over the groove
  ...
)
```

## Section templates (mix & match)

```js
// INTRO — build it up, a layer at a time
[4, bass],
[4, stack(bass, kick)],
[4, stack(bass, kick, hats)],
[4, stack(bass, kick, hats, arp)],

// A VOICE LINE — line i, over whatever layers you want. Strip layers for intimacy,
// stack them for intensity. The dialogue lands harder when you drop to bare bass:
[bars[i], stack(kick, hats, bass, arp, pad, vo(s("voice:" + 0), 0))],   // full  (NOTE: literal index!)
[bars[i], stack(bass,                        vo(s("voice:2"), 2))],     // bare — a breakdown line

// BREAKDOWN — fall away, build tension, drop
[4, stack(bass, wash)],          // everything falls to sub + dark wash
[4, stack(bass, riser, wash)],   // tension rises
[1, impact],                     // the drop — a sub-boom

// BRIDGE — the harmony lifts, a new arp
[8, stack(kick, hats, bass, arp2, bridgePad)],

// SOLO — the lead sings over a busy bed
[8, stack(kick, hats, clap, bass, arpFast, pad, solo)],

// CLIMAX / OUTRO
[8, stack(kick, hats, clap, bass, arpFast, pad, lead, solo)],   // everything
[8, stack(bass, lead)],                                         // a breath
```

## Arcs within a line (`split`)

A voice line can hold its own arc — the music **drops or changes mid-sentence** while the voice
carries on. Instead of `{ "voice": i, "layers": [...] }`, give the line a `split`:

```json
{ "voice": 7, "split": [ [5, ["kick","hats","bass","arp","pad"]],
                         [4, ["bass","wash"]],
                         [4, ["kick","hats","bass","solo"]] ] }
```

The voice **fires once** (in the first sub-section) and **rings out** across all of them — so the
middle `[4, ["bass","wash"]]` is a bare drop *under a line that's still speaking*, then it rebuilds.
Make the split bars **sum ≈ that line's rendered bars** (see the render log / `timing.md`) so the
next line still lands on time. Reserve it for long or turning lines; it's the "bars drop in the
middle of a sentence" move.

## The laws (learned in blood — see also cookbook/strudel/README.md)

- **`arrange` loops each section every bar.** A one-shot voice must be `.slow(n)` (via `vo`) so it
  fires once and holds. A bare `s("voice:0")` re-triggers every bar and stacks on itself.
- **Never build a mini-notation string with `"text" + variable`** — every `"…"` is parsed as
  mini-notation, so `s("voice:" + i)` breaks the parser. Pass the finished `s("voice:0")` clip in.
- **Voice + section length both read `bars[i]`** so a re-render (new word lengths) re-fits the song.
- Adding/removing a voice *line* is a shape change: it needs a new/removed `arrange` row (the
  `bars` array and the voice-file list auto-sync, but where the line sits musically is yours to place).
