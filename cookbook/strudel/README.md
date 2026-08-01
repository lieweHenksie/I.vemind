# cookbook/strudel — cyBorge's song machinery

Everything for a **voice-over-music** cyBorge piece: an essay read by a synthetic voice, locked
onto a bed of Strudel code that builds, breaks down, and climaxes. This folder is the toolkit;
`id/agar-lab/` is the reference build.

Not a framework — copy-me recipes. Strudel *is* the engine (loaded from a `<script>` tag, no
build). The voice is pre-rendered to clips by `tools/tts/eleven.py`. The page glues them.

## The files

| File | What it is |
|------|------------|
| [`template.html`](template.html) | **Copy this to start a song.** The whole page: Strudel boot, voice-loading, play/stop, and a starter score. |
| [`palette.md`](palette.md) | The instruments — copy-me synth voices (bass, sub-kick, arps, pad, hats, clap, lead, solo, wash, riser, impact). |
| [`arrangement.md`](arrangement.md) | How to bind voice + music into one `arrange()` timeline, with section templates (intro / breakdown / bridge / solo / climax). |
| `../../tools/song/check.py` | **The bench ear** — evaluates every instrument in a palette on its own and *listens* to it. Names the one entry that kills the score, catches instruments that render silent with no error, and shows what a rebuild would change before you run it. |
| [`research/`](research/README.md) | **The listening bank** — studies of real Strudel artists (via `/cyborge-research`): techniques verified against the docs, caption-garble corrected, flagged against the pinned runtime. |
| `../../tools/tts/audio-tags.md` | ElevenLabs v3 audio tags (`[sigh]`, `[whispers]`, `[sad]`) — cyBorge's acting notes, dropped inline in the essay. |

## Make a song (the loop)

1. **Write** the essay in `mycelium/essays/<name>.md` — blank-line block = one spoken line;
   drop `[tags]` inline to direct the delivery.
2. **Scaffold**: copy `template.html` → `id/<name>/index.html` (or `ego/<name>/`).
3. **Render the voice** (cloud; ~zero local load):
   ```
   python3 tools/tts/eleven.py mycelium/essays/<name>.md id/<name>/audio/voice --index id/<name>/index.html
   ```
   This makes `line-NN.wav`, and **rewrites `bars` + `VOICE_FILES`** in the page to fit.
   It's **incremental** — after the first run it only re-renders lines you actually edited
   (tracked in `.render-manifest.json`). `--only 3` forces one line; `--all` forces everything.
4. **Shape** the `arrange(...)` in the score — copy sections from `arrangement.md`, place the
   voice lines, add breakdowns/bridges/solos. Serve (`python3 tools/serve.py`)
   and play.
5. **Check before you trust it** — `python3 tools/song/check.py id/<name>`. Ten seconds, muted,
   and it is the only thing that catches an instrument that evaluates fine and makes no sound.

## The laws (don't relearn them)

- **Tempo:** `setcpm`/`setcps` aren't global in `@strudel/web`. Default cps 0.5 = 120 BPM in 4/4;
  change tempo with `.fast(BPM/120)` after `arrange(...)`.
- **Samples load only in `prebake`**, and only when first triggered — so we **preload** the voice
  clips before enabling play, or the first pass drops half the lines.
- **Cache-bust the voice URLs** (`?t=…`), or a re-render is never heard (same filenames).
- **`arrange` loops each section every bar** — a one-shot voice needs `.slow(n)` (use `vo`).
- **Every `"…"` is mini-notation** — never `s("voice:" + i)`; pass a finished `s("voice:0")` clip.
- **Drums are synth** (a low sine sub-kick, noise hats/clap) — never the tacky sample kit.
- **The crate:** extra samples (cut by `tools/song/sample.py`, e.g. from a YouTube link) live in
  `id/<name>/audio/samples/` and are declared in `palette.json`'s `_samples` map **with source
  timestamps** (provenance); `build.py` registers them for prebake. A sample name is **not** a
  layer — an instrument plays it (`s("name")` + `chop`/`slice`/`loopAt`/`speed`). Commercial cuts
  stay in `id/`; rights-check before `ego/`.
- **The source film:** `sample.py --video` cuts a **small clip per sample** to `id/<name>/video/`
  (the full source is cached, gitignored — only the clips ship); `build.py` compiles the shape into
  `VIDEO-CUES` + a `VIDEO_CLIPS` map, and the page plays each sample's own clip **from frame 1** as
  the arrangement reaches it (dim + held between cues). Small files load fast; playing a fresh clip
  from its start is the one video path that never stalls — no big-file seeking.
- **One bad instrument kills the WHOLE score.** Every instrument is emitted into one evaluated
  block, so a syntax error in any single `let` makes `evaluate()` throw and the song plays
  *nothing* — with no error worth reading. `check.py` bisects it and names the entry.
- **An instrument can be silent with no error.** The known shape:
  `s("x").freq(…).decay(…).sustain(0)` with no explicit attack/release renders **silent** in
  1.0.3; `note(…).s("x")` with the same envelope is fine. Nothing throws. `check.py` listens.
- **Adding an instrument is free; wiring it costs.** `gen_instruments` only emits what a section
  actually names, so a new palette entry that nothing references changes not one byte of output.
  That is the safe way to stage a sound: add it, rebuild, confirm nothing moved, *then* wire it.
- **Enriching an instrument can move the film.** `gen_cues` reads instrument code with a regex —
  the **first** `s("…")`, plus `.slow(n)` and `.slice(`. Wrap an instrument in a `stack()` with a
  second sample, or add a `.slow()`, and the video cues shift under you. `check.py` shows the
  drift before you build.
- **Voice is always pre-rendered** — browser speech can't be beat-locked; and v3 audio tags are
  paid-tier ElevenLabs.

## Where this is headed

These recipes are what the song-pipeline skills will wield: `/cyborge-score` (essay → shape) →
`/cyborge-compose` (shape → built song) → `/cyborge-feedback` → `/cyborge-shape`. Build the
recipes first (here); the skills call them.
