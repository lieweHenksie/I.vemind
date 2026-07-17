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
   voice lines, add breakdowns/bridges/solos. Serve (`python3 -m http.server --bind 127.0.0.1 8000`)
   and play.

## The laws (don't relearn them)

- **Tempo:** `setcpm`/`setcps` aren't global in `@strudel/web`. Default cps 0.5 = 120 BPM in 4/4;
  change tempo with `.fast(BPM/120)` after `arrange(...)`.
- **Samples load only in `prebake`**, and only when first triggered — so we **preload** the voice
  clips before enabling play, or the first pass drops half the lines.
- **Cache-bust the voice URLs** (`?t=…`), or a re-render is never heard (same filenames).
- **`arrange` loops each section every bar** — a one-shot voice needs `.slow(n)` (use `vo`).
- **Every `"…"` is mini-notation** — never `s("voice:" + i)`; pass a finished `s("voice:0")` clip.
- **Drums are synth** (a low sine sub-kick, noise hats/clap) — never the tacky sample kit.
- **Voice is always pre-rendered** — browser speech can't be beat-locked; and v3 audio tags are
  paid-tier ElevenLabs.

## Where this is headed

These recipes are what the song-pipeline skills will wield: `/cyborge-score` (essay → shape) →
`/cyborge-compose` (shape → built song) → `/cyborge-feedback` → `/cyborge-shape`. Build the
recipes first (here); the skills call them.
