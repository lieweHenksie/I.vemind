# I.vemind — cyBorge

A toolkit for making two kinds of self-contained pieces:

- **Songs** — a synthetic voice reading an essay over a live [Strudel](https://strudel.cc) bed
  (in the vein of Agar Agar × Headache).
- **Story pages** — atmospheric, scroll-driven HTML.

The value is the *machinery*: copy-me recipe **cookbooks** and **pipelines of slash commands** that
carry raw text to a finished piece. `CLAUDE.md` is the full project bible; this is the quick start.

## Prerequisites

- **python3**, **ffmpeg**, **sox** (used by the render/build tools; no npm, no build step).
- A **paid ElevenLabs account** for the song voice — the free tier can't use library voices via the
  API. (Story pages need none of this.)
- **Claude Code** to drive the `/cyborge-*` skills — optional; you can run the tools directly.

## Setup

```bash
cp .env.example .env      # then paste your ElevenLabs key + a voice_id
```

## Make a song

Two files are your only source of truth: the **essay** (`mycelium/essays/<name>.md`, one spoken
line per blank-line block) and the **shape** (`id/<name>/song.json`). Everything else is generated.

```bash
# 1. write/rewrite  mycelium/essays/<name>.md   (drop [tags] like [sigh] inline)
# 2. shape it:      /cyborge-score <name>        (drafts/updates id/<name>/song.json)
# 3. build it:      python3 tools/song/compose.py <name>     (== /cyborge-compose)
# 4. play it:       python3 -m http.server --bind 127.0.0.1 8000   →   localhost:8000/id/<name>/
# 5. refine:        /cyborge-feedback <name>  →  /cyborge-shape <name>
```

`compose.py` renders **only lines you changed** (incremental) and recompiles **only shape sections
you changed** (deterministic) — iterating never clobbers takes you're happy with. The instrument
palette and arrangement recipes live in [`cookbook/strudel/`](cookbook/strudel/README.md).
`id/agar-lab/` is the reference build.

## Make a story page

A different craft with its own pipeline (`/cyborge-test → -direct → -code → -sync`) and cookbook
([`cookbook/`](cookbook/README.md)). See `CLAUDE.md` → *Story Pipeline*.

## Repo map

```
cookbook/         recipes — story (CSS/JS) + music (cookbook/strudel/)
tools/            dev-only build tools: tts/ (voice render), song/ (shape compiler)
.claude/commands/ the /cyborge-* slash commands (story + song pipelines)
mycelium/         source: story drafts, and song essays in essays/
id/  ego/         experiments / finished pieces
```
