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

A song compiles from three data files — the **essay** (`mycelium/essays/<name>.md`, words),
**`id/<name>/song.json`** (shape), and **`id/<name>/palette.json`** (its own sound). Everything
else is generated; you never hand-edit the built page.

### The music skills

| Skill | When | What it does |
|-------|------|--------------|
| `/cyborge-research <url>` | any time | Studies a real Strudel artist's video → banks their **moves** in `cookbook/strudel/research/` (feeds every future score, not one song) |
| `/cyborge-sample <name> <url> [what]` | before the score | The crate-digger: cuts audio (and `--video` clips) from a YouTube link into `id/<name>/`, registers them in `palette.json`'s `_samples` |
| `/cyborge-score <name> [genre]` | step 1 | Reads the essay's arc + mood, picks a genre, drafts `song.json` (shape) + `palette.json` (sound). Bare `<name>` appends; `<name> <genre>` = full recompose |
| `/cyborge-compose <name>` | step 2 | Renders the voice (ElevenLabs, incremental) + compiles the shape → the playable page |
| `/cyborge-song <name> [genre]` | steps 1+2 | The one-pull wrapper: **score → compose** in a single command |
| `/cyborge-feedback <name>` | step 3 | Plays it; turns your reactions into `feedback.md` — **Keep** / **Fix** lists |
| `/cyborge-shape <name>` | step 4 | Applies the **Fix** list only — *fix where broken, leave what works*. Loop back to feedback |
| `/cyborge-album <name> [tracks…]` | when songs become a record | Builds/tends an album: the hallway page (one click plays all tracks in order), and the **edge pass** — every track fades in/out and each outro harmonically bridges the next intro. Never touches voice notes. Recipe: `cookbook/strudel/album.md` |

### Flow — voice song (no samples)

```
essay (mycelium/essays/<name>.md)
   │  /cyborge-song <name>            ← or /cyborge-score → /cyborge-compose
   ▼
id/<name>/  song.json + palette.json + index.html   (voice clips rendered per line)
   │  /cyborge-feedback ⇄ /cyborge-shape            ← loop until it sings
   ▼
play: python3 -m http.server --bind 127.0.0.1 8000  →  localhost:8000/id/<name>/
```

### Flow — with samples (a crate jam, or voice + crate)

Same as above, with one step in front: **stock the crate first**, then score.

```
YouTube link ──/cyborge-sample──▶ id/<name>/audio/samples/*.wav (+ video clips)
                                      registered in palette.json _samples
                                           │
essay (optional — a crate jam needs none) ─┴─ /cyborge-song <name> [genre] ─▶ …same loop
```

The sampler only *cuts and shelves* material — the scorer decides what the song does with it.
With `--video`, the page plays each sample's source clip in sync with the arrangement, over the
visualizer back wall. `id/agar-lab/` is the reference voice song; `id/demi_demi/` the reference
crate jam.

Everything is **incremental & deterministic**: edit one essay line → only that voice clip
re-renders; edit one `song.json` section → only that arrange row changes. Iterating never clobbers
takes you're happy with. The instrument palette and arrangement recipes live in
[`cookbook/strudel/`](cookbook/strudel/README.md).

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
