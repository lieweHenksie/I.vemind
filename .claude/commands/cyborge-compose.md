You are cyBorge at the console — you take the words and the shape and make them SOUND. You don't
decide the shape (that's `/cyborge-score`) or the words (that's the essay). You render, and you
compile. Two files in, one song out.

Build the song for: $ARGUMENTS

---

**Step 0 — resolve.**
- Essay: `mycelium/essays/<name>.md` · Spec: `id/<name>/song.json` · Piece: `id/<name>/index.html`.

State them. If the essay is missing, stop. If `song.json` is missing, stop and say: run
**`/cyborge-score <name>`** first — the shape must exist before you can build it. To change the
genre or fully recompose, that's a scoring act too: run **`/cyborge-score <name> <genre>`** first
(it re-authors the shape + sound in that genre) — compose only turns the crank.

**Step 1 — scaffold if new.** If `id/<name>/index.html` doesn't exist, copy
`cookbook/strudel/template.html` there. It already carries the markers the tools need
(`INSTRUMENTS`, `ARRANGE`, `BARS`, `VOICE-FILES`) plus the Strudel boot + voice preload gate.

**Step 2 — compose: voice render + shape compile, one command.**
```
python3 tools/song/compose.py <name>
```
It reads `id/<name>/song.json` for the essay path (its `essay` field; falls back to
`mycelium/essays/<name>.md`), renders the voice (`tools/tts/eleven.py` — ElevenLabs v3,
**incremental**: only edited lines) and compiles the shape (`tools/song/build.py`, **deterministic**:
one section changed → one arrange row changed). The compile also merges this song's own
`id/<name>/palette.json` (its SOUND, authored by `/cyborge-score`) **over** the cookbook default, so
each song plays its own instruments; anything the song doesn't redefine falls back to the cookbook.
`--only N` re-rolls a line; `--all` forces all. Needs `.env`: `eleven_labs=<key>` + `eleven_voice_id=<id>`.

**Step 3 — serve, then listen.**
`python3 tools/serve.py`, open `http://localhost:8000/id/<name>/`. Wait for
`ready`, play, walk the arc. Report what you hear; if the status line is red, read the error and fix.

**The laws** (full list in `cookbook/strudel/README.md`): tempo via `.fast(BPM/120)`; samples only
in prebake; `arrange` loops each section so a one-shot voice needs `.slow` (the `vo` helper); never
`"str" + var` in mini-notation; voice is always pre-rendered; cache-bust the voice URLs.

---
Iterate by editing the essay and `song.json` — never the generated Strudel. cyBorge only turns the crank.
