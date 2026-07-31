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
//    contains voice events; eleven.py's VOICE_FILES marker feeds the bus. (It also ships
//    VOICE_TEXTS — the spoken words as data. Nothing on the stage reads them any more; the
//    writing is read in the album's reading room, id/album/essay.html.)
//
//    CASTING: a block that starts `name: …` is spoken by `<name>_voice_id` from .env instead of
//    the narrator (`robot:` ends oh_dear as an emergency broadcast). One token then a colon, at
//    the very start — a sentence that merely contains a colon is never mistaken for a cue. The
//    prefix is direction: it stays in the essay and the manifest (so re-casting a line re-renders
//    exactly that line) and is stripped from what is spoken, printed, and read.

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

## Richness — don't let a section sit flat (`vary`, `fill`)

A stack of static loops is the main reason an arrangement feels *too simple*: the same one-bar
phrases repeat, unchanged, for a whole section. Two `build.py` primitives add motion **without
authoring a new instrument** — both additive, so a song that uses neither compiles as before.

**`vary` — evolve ONE layer, just here.** A layer is normally a name (`"bass"`); give it a preset
instead and that instrument transforms *in this section only*:

```json
"layers": ["kick", "hats", ["bass", "double"], {"l": "arp", "vary": "ghost"}]
```

| preset | move | reach for it when |
|--------|------|-------------------|
| `double` | `.fast(2)` | lifting into a drop — twice as busy |
| `half` | `.slow(2)` | a breakdown — half-time |
| `ghost` | scattered quiet notes | a stiff loop needs humanising |
| `stutter` | a doubling **fill every 4th bar** | end-of-phrase lift |
| `build` | tightening every other bar | rising tension |
| `ply2` | each hit retriggered twice | rolls |
| `thin` | drops ~30% of events | sparser, less mechanical |
| `echo` | an eighth-note echo tap | space, dub |

Presets are all core Strudel, verified on the pinned runtime, and *compose onto any instrument*
(appended chains — they don't override its own filter/gain the way a fade's postgain does). Add
new moves to `VARY` in `build.py`, never raw Strudel in `song.json` — the shape stays declarative.

**`fill` — a lift on the LAST bar.** An instrumental section can name a fill instrument that plays
only its final bar (the classic snare-roll before the change):

```json
{ "bars": 8, "layers": ["kick","bass","hats"], "fill": "snareroll", "label": "…" }
```

`build.py` compiles that to `[7, …]  [1, …+snareroll]`. Fills need a fixed `bars ≥ 2` and no
`fade` (fills and album-edge fades don't mix; a fill on a voice/fade/short section is skipped).

**The principle:** if the same ≤2 layers loop unchanged for more than ~8 bars, it's too flat —
reach for a `vary`, a `fill`, a counter-melody, or another layer. Motion is what separates an
arrangement from a loop.

## The words are load-bearing (labels)

Every section's `label` renders ON SCREEN as the piece's hero title: the text before the em-dash
is the **title**, after it the **subtitle** — so write labels as full invocations
(`"THE SNEEZE — the forest holds its breath"`), not comments. Two side effects to wield on purpose:

- a label containing **"drop"** (any case) marks the section as a **punch** — the film bounces
  there. Use it only on actual drops; a drop without the word can set `"punch": true`. (Careful
  with phrases like *"beat drops out"* — they punch too.)
- the **sea** (the visualizer back wall) listens to the OUTPUT — an analyser on everything that
  reaches the speakers, the bed and the voice both. Density still stages the water, but through
  the air rather than through a number: thin the layers before a drop and the sea visibly
  recedes *because it got quieter*. A sparse section that is loud will flood the stage anyway,
  and a spoken line ripples through the water with no instrument playing at all.

## The laws (learned in blood — see also cookbook/strudel/README.md)

- **Voice clips never live in the score.** A one-shot strudel event can start late or be skipped
  under render load, and a line only fires once — the page's voice bus owns them.
- **The bus edge-fades every clip.** Each line plays through its own GainNode with a ~12ms fade-in
  (kills the onset click) and a ~140ms fade-out that tapers *through* the trailing breath ElevenLabs
  leaves on the tail — so a line never ends on a hard digital cut (the old "cut on the breath-in").
  The body holds at full gain; only the very edges move. Tune the fades in the bus (`armVoice`), never
  by re-rendering clips — it's non-destructive and covers every existing clip at once.
- **Never build a mini-notation string with `"text" + variable`** — every `"…"` is parsed as
  mini-notation, so `s("voice:" + i)` breaks the parser.
- **Voice slots read `bars[i]`** so a re-render (new word lengths) re-fits the song.
- Adding/removing a voice *line* is a shape change: it needs a new/removed `arrange` row (the
  `bars` array and voice files auto-sync, but where the line sits musically is yours to place).
