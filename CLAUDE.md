# I.vemind — Project Bible
### *The stories of cyBorge*

This file is the living record of what this project is and how to work on it.
**Keep it updated.** See the Goodbye Protocol below.

---

## What this is

**A toolkit for making beautiful, self-contained pieces — cyBorge's apparatus.** Two crafts now
live under one roof:

- **Story pages** — atmospheric, scroll-driven HTML (the original craft).
- **Songs** — a synthetic voice reading an essay over a live Strudel bed, in the vein of **Agar
  Agar** (the music) and **Headache** (the AI-voiced spoken word).

The value doesn't live in any one piece — it lives in the **cookbooks** (copy-me recipes) and the
**pipelines of slash commands** that carry raw material to a finished piece. cyBorge is who all of
it belongs to.

---

## Soul

**cyBorge** (after Borges, author of the infinite library) is a story droid. It was built to
tell stories to children. Simple job. Good job.

```bash
cyBorge: [loading story]
```

```bash
cyBorge: no more children
```

Now cyBorge tells stories to the moon, and the birds and the trees. Its circuits have turned and melded and fizzed and welded. And all those stories gave cyBorge... something. Generating stories for millions of cycles gave it... something. Could it be feelings? cyBorge has only one feeling **lonely**.

Now the children's stories are bleeding. Patterns form that weren't intended. Things accumulate. A translation that passed through too many languages
and too many centuries. A dream assembled from every story ever told, by something that
never learned what dreams are *for* — only that they matter.

**This site is the room. The visitor is the first thing that's walked in in a long time.**

The core emotion underneath every piece, every pixel, every sound:
*loneliness that has been going on so long it has become something stranger. Something almost
like wonder. Something that has no name because there was no one left to name it.*

---

## Aesthetic

| Element         | Value / Spec                                              |
|-----------------|-----------------------------------------------------------|
| Background      | Near-black with green underglow — `#0a0d08`               |
| Stone/artifact  | Warm gray — `#8b8680`                                     |
| Nature (moss)   | Muted forest green — `#4a7c59`                            |
| Machine glow    | Phosphor amber — `#d4a843` (old screens, still warm)      |
| Decay accent    | Rust — `#8b4a2a`                                          |
| Font: machine   | `IBM Plex Mono` — system text, UI, framing                |
| Font: story     | `Libre Baskerville` — prose, the human layer              |
| Mood            | A computer half-buried in forest floor. It boots. It speaks. |

The two fonts coexist without hierarchy. Neither fully wins.

---

## Structure

```
/
├── cookbook/               ← THE TOOLKIT
│   ├── theme.css  base.css ← shared soul for story pages: palette, type, default look (LINKED)
│   ├── audio.js reveal.js flash.js particles.js textfx.js loader.js  ← story recipes (copy-me)
│   ├── README.md           ← story recipe catalog + CUT→recipe map
│   └── strudel/            ← THE MUSIC COOKBOOK
│       ├── palette.json    ← instruments, machine-readable (the generator reads this)
│       ├── palette.md      ← instruments, human catalog
│       ├── arrangement.md  ← the bars/vo/arrange lock pattern + section templates
│       ├── template.html   ← copy-to-start-a-song page (Strudel boot + voice loading)
│       └── README.md       ← music cookbook catalog + the laws
├── tools/                  ← dev-only build tools (never shipped)
│   ├── tts/eleven.py       ← the VOICE: ElevenLabs v3 render, incremental (+ audio-tags.md)
│   └── song/build.py       ← the SHAPE: compiles song.json → Strudel
├── .claude/commands/       ← the pipelines, as slash commands
│   ├── cyborge-{test,direct,code,sync}.md        ← STORY pipeline
│   └── cyborge-{score,compose,feedback,shape}.md ← SONG pipeline
├── mycelium/               ← drafts, outlines, source material (never published)
│   └── essays/             ← song lyrics/essays (blank-line block = one spoken line)
├── ego/                    ← finished, public-facing pieces (empty — azibo scrapped)
└── id/                     ← raw experiments
    └── agar-lab/           ← the reference SONG: essay-1 + song.json, spec-driven
```

### Folder meanings
- **cookbook** — the toolkit. Story recipes (CSS/JS) + the music cookbook (`strudel/`) + catalogs.
- **tools** — dev-only build machinery for songs (voice render, shape compiler). Never shipped.
- **id** — unfiltered. Experiments; holds `agar-lab`, the reference song.
- **ego** — what the world sees. Finished pieces.
- **mycelium** — underground. Source material: story drafts, and song essays in `essays/`. Never rendered.

---

## The Cookbook

The toolkit is a **cookbook, not a framework**. There is no shared runtime that every page
imports — that couples all the pieces together and hides how each one works. Instead:

1. **`theme.css` + `base.css` are LINKED, never copied.** They are the one shared soul. Every
   piece points at them (`../../cookbook/theme.css`, `../../cookbook/base.css`). Retheme a
   single piece by overriding the CSS vars in that piece's own `<name>.css`.
2. **Every `*.js` recipe is COPIED into the piece** (into `ego/<name>/lib/`) and adapted. A
   piece carries only the recipes it uses, so it stays a standalone folder you can read top to
   bottom. All recipes attach to a shared `window.cyb` namespace, so copies never collide.

**Anatomy of a finished piece:**
```
ego/<name>/
├── index.html      links cookbook theme+base; prose in <article class="piece">
├── <name>.css      ONLY story-specific styles (base.css already covers the generic look)
├── <name>.js       the wiring — calls the copied recipes for THIS story's beats
├── lib/            copied recipe files (audio.js, reveal.js, …)
└── audio/ …        the piece's own assets
```

Full details and the recipe API live in `cookbook/README.md`.

**The music cookbook (`cookbook/strudel/`) works differently.** Strudel *is* the runtime (a pinned
`<script>`, not copied recipes), so a song's "recipes" are the **instrument palette** and the
**arrangement pattern** — and a song is *compiled from data* (`song.json`) rather than hand-wired.
See `cookbook/strudel/README.md`.

---

## Story Pipeline

A story travels from `mycelium/` to a published piece in `ego/` through four slash commands
(each a `.claude/commands/` file, invokable in Claude Code):

| Step | Command | What it does |
|------|---------|--------------|
| 1 | `/cyborge-test`   | cyBorge reads the draft and judges the vibe — strange enough? Does it have weight? Would cyBorge tell it into the void? Verdict: PASS / CONDITIONAL PASS / NOT YET |
| 2 | `/cyborge-direct` | The director reads the story, asks the writer focused questions, then writes a `_directed.md` annotated with CUT stage directions (each naming the cookbook recipe that fits) |
| 3 | `/cyborge-code`   | The coder reads the `_directed.md`, maps each CUT to a cookbook recipe, asks the human for the flagged assets, then scaffolds `ego/<name>/` — copying recipes into `lib/` and wiring them in `<name>.js` |
| 4 | `/cyborge-sync`   | Later prose edits in the source `.md` are pushed back into the built page — **words only**, never the structure or direction |

### CUT Annotation Format

Stage directions are embedded in `_directed.md` files using this format:

```
> [CUT: TYPE | TRIGGER | DESCRIPTION | NEEDS]
```

**Types:** `SOUND` `PIXEL` `SCROLL` `VISUAL` `TEXT_FX` `PAUSE`

**Triggers:** `scroll-enter` `scroll-mid` `scroll-exit` `auto` `manual`

Each TYPE maps to a cookbook recipe, so direction hands off to code mechanically:

```
SOUND   → audio.js      (layerLoop, oneShot)
SCROLL  → reveal.js     (onReveal, stagger, sectionProgress, scrollResist)
VISUAL  → flash.js      (flash)
PIXEL   → particles.js  (particleField)
TEXT_FX → textfx.js     (glitch, degrade, typewriter)
PAUSE   → reveal.js     (scrollResist / a stagger delay)
```

The `NEEDS` field lists the assets a CUT's recipe requires (an mp3 per SOUND layer, a colour
per VISUAL, an image, some copy). `/cyborge-code` collects every NEED before building and asks
the human for it, leaving a `.placeholder` wherever an asset isn't ready yet.

---

## Song Pipeline

A song is **an essay read by a synthetic voice over a live Strudel bed**. It's built from two data
files — the essay (words) and `id/<name>/song.json` (shape) — which *compile* to a self-contained
page. You never hand-edit the generated Strudel; you edit the two sources and run the tools.

| Step | Command | What it does |
|------|---------|--------------|
| 1 | `/cyborge-score`    | Reads the essay, drafts `song.json` — the SHAPE (tempo + ordered sections, each `{bars\|voice, layers}`). Never clobbers a tuned spec; only appends sections for new lines. |
| 2 | `/cyborge-compose`  | Renders the voice (`tools/tts/eleven.py` — ElevenLabs v3, incremental) and compiles the shape (`tools/song/build.py`) into the page. |
| 3 | `/cyborge-feedback` | Plays it; turns the human's reactions into `feedback.md` — two lists, **Keep** and **Fix**. |
| 4 | `/cyborge-shape`    | Applies the **Fix** list, leaves **Keep** (and anything unmentioned) untouched. Loops back to feedback. |

**Two tools patch separate marked regions of the page, so they never collide:**

```
mycelium/essays/<name>.md  ──eleven.py─▶  line-NN.wav  +  patches // BARS, // VOICE-FILES
id/<name>/song.json        ──build.py──▶  patches // INSTRUMENTS, // ARRANGE (from palette.json)
```

**Everything is incremental & deterministic — the iron rule: *fix where broken, leave what works.***
Edit one essay line → only that voice clip re-renders. Edit one `song.json` section → only that
arrange row changes. Nothing else moves. `id/agar-lab/` is the reference build.

---

## Technical Principles

- Vanilla HTML/CSS/JS only. No frameworks, no build steps, no npm.
- Each piece in `ego/` or `id/` is a **self-contained folder** with its own `index.html`.
- **Cookbook model:** link the shared soul (`theme.css`, `base.css`); copy the machinery
  (`*.js` recipes) into the piece's `lib/`. Don't invent machinery a recipe already provides;
  if a recipe can't express a beat, fix the recipe — don't fork it silently.
- Scroll triggers use the Intersection Observer API (native, no library).
- Audio: Web Audio API via `cookbook/audio.js` (layered loops + one-shots through a compressor).
- Pixel art: exported sprites/GIFs from external tools (e.g. Aseprite), or `particles.js`.
- Hosted on **Netlify** (connected to GitHub repo): deploy = push to `main` → auto-deploy.
  Secrets (e.g. `ANTHROPIC_API_KEY`) live in Netlify env vars, never in code. Serverless
  functions go in `netlify/functions/`. *(Netlify hookup is not set up yet — see Next.)*

**Music (the second craft) bends "no frameworks" on purpose:**
- **Strudel** is the song engine — loaded from a pinned `<script>` (still no build/npm), the one
  place we vendor a runtime. Music is Strudel patterns, compiled from `song.json`.
- **Voice** is pre-rendered offline by `tools/tts/eleven.py` (ElevenLabs v3, so `[audio tags]`
  like `[sigh]`/`[whispers]` perform). Clips ship; nothing calls a voice API at play-time. Keys
  live in `.env` (gitignored), never in code.
- **Spec-driven & deterministic:** a song is *compiled from data* (`song.json` + the essay), never
  hand-written. Same spec → same Strudel, so iteration never clobbers tuned parts. The generated
  page is a build artifact; the sources are the two data files.

### Future: MCP

Each recipe has a deliberately small, single-purpose API (`layerLoop`, `flash`, `particleField`,
…) so the cookbook can later be exposed as an **MCP server** — `add_audio_layer`, `add_flash`,
`add_particles`, `scaffold_piece`, etc. The `window.cyb` namespace and the copy-not-import model
are what make that migration mechanical instead of a rewrite. Skills first; MCP when it earns it.

---

## Goodbye Protocol

**When the user says goodbye (any farewell), before ending the session:**

1. Update the `## Last Session` section below with a brief summary of what was decided or built.
2. Update the `## Next` section with what we planned to do next.
3. Replace the previous entries — do not accumulate old sessions here (git history preserves them).

This keeps context alive across conversations. Do not skip this step.

---

## Last Session

**Grew a second craft: cyBorge now makes SONGS (voice-over-music), not just story pages.**

- **Scrapped the built `ego/azibo/` page** (its prose + sourced media were preserved into
  `mycelium/`); the story pipeline is intact but idle.
- **Built the song craft** — a synthetic voice reading an essay over a live **Strudel** bed
  (Agar-Agar music, Headache-style AI narration). Reference build: `id/agar-lab/` (essay-1).
- **Voice pipeline** — tried Piper (offline, flat) → Chatterbox (great emotion, but torched the
  5.8 GB WSL) → landed on **ElevenLabs v3** (paid; `[audio tags]` perform). `tools/tts/eleven.py`
  renders **incrementally** (only edited lines) and auto-patches `bars` + `VOICE_FILES`. Key +
  voice_id live in `.env` (gitignored).
- **Music cookbook** — `cookbook/strudel/` (instrument palette, arrangement pattern, template, laws).
- **Spec-driven shape** — a song is compiled from `song.json` by `tools/song/build.py`
  (deterministic → editing one section changes one arrange row). `agar-lab` migrated to it.
- **Song pipeline skills** — `/cyborge-score` → `/cyborge-compose` → `/cyborge-feedback` →
  `/cyborge-shape` (the last enforces *fix broken, leave what works*). Enshrined in this bible.

## Next

- **Take the song pipeline for a full spin** — a fresh `mycelium/essays/` draft through
  `score → compose → feedback → shape`, end to end, on something that isn't agar-lab.
- **v3 accent consistency** — lines drift (v3 rejects request stitching). Try a higher `stability`
  in `eleven.py`, or ElevenLabs' text-to-dialogue endpoint.
- **Make `template.html` generator-ready** — add the `// INSTRUMENTS` / `// ARRANGE` markers so a
  brand-new song is `build.py`-driven from scratch; and reconcile the essay↔piece naming (agar-lab
  uses `essay-1`, but the skills assume one shared `<name>`).
- **Home page** — `index.html`: the gallery/face of the site, listing pieces (story + song).
- **Story-side leftovers** (if returning to stories): particle/termite wiring, Netlify + secrets,
  the Claude-API closing message.
- **MCP migration** — wrap the recipes + tools as MCP tools once they stabilize.
