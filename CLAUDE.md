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
│       ├── palette.json    ← DEFAULT instruments (each song overrides in its own palette.json)
│       ├── palette.md      ← instruments, human catalog
│       ├── arrangement.md  ← the bars/vo/arrange lock pattern + section templates
│       ├── template.html   ← copy-to-start-a-song page (Strudel boot + voice loading)
│       ├── README.md       ← music cookbook catalog + the laws
│       └── research/       ← THE LISTENING BANK: studies of real artists (/cyborge-research)
├── tools/                  ← dev-only build tools (never shipped)
│   ├── tts/eleven.py       ← the VOICE: ElevenLabs v3 render, incremental (+ audio-tags.md)
│   ├── song/build.py       ← SHAPE+SOUND: compiles song.json + palette.json → Strudel
│   ├── song/transcribe.py  ← the EAR: YouTube auto-captions → timestamped transcript
│   └── song/sample.py      ← the CRATE: YouTube link → cut wav + `_samples` entry (/cyborge-sample)
├── .claude/commands/       ← the pipelines, as slash commands
│   ├── cyborge-{test,direct,code,sync}.md        ← STORY pipeline
│   └── cyborge-{research,sample,score,compose,feedback,shape,song}.md ← SONG pipeline (song = score→compose in one pull)
├── mycelium/               ← drafts, outlines, source material (never published)
│   └── essays/             ← song lyrics/essays (blank-line block = one spoken line)
├── ego/                    ← finished, public-facing pieces (empty — azibo scrapped)
└── id/                     ← raw experiments (songs)
    ├── agar-lab/           ← reference SONG: essay-1 + song.json (plays the default sound)
    └── head_god/           ← song.json (SHAPE) + palette.json (its OWN sound) + index.html
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
**arrangement pattern** — and a song is *compiled from data* rather than hand-wired. The cookbook
`palette.json` is the **default sound**; each song authors its **own** `id/<name>/palette.json` that
overrides it (its own key, riffs, timbres — from the essay's mood), so no two songs sound alike.
A song compiles from three data files: the essay (words), `song.json` (shape), `palette.json` (sound).
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

A song is **an essay read by a synthetic voice over a live Strudel bed**. It's built from three data
files — the essay (words), `id/<name>/song.json` (shape), and `id/<name>/palette.json` (its own
sound) — which *compile* to a self-contained page. You never hand-edit the generated Strudel; you
edit the sources and run the tools.

| Step | Command | What it does |
|------|---------|--------------|
| 0 | `/cyborge-research` | *(any time, feeds the cookbook — not per-song)* Transcribes a real Strudel artist's video (`tools/song/transcribe.py` → yt-dlp auto-captions), extracts their **moves** (never their patterns), verifies every claimed function against the strudel.cc docs (captions garble code), and banks the study in `cookbook/strudel/research/` — flagged against the pinned runtime. `/cyborge-score` spends the bank. |
| ½ | `/cyborge-sample`   | *(optional, before the score)* The crate-digger: cuts material from a YouTube link (`tools/song/sample.py` → yt-dlp + ffmpeg; timestamps, or a described phrase found via the transcript) into `id/<name>/audio/samples/` and registers it in `palette.json`'s `_samples` map. Cuts material only — never authors instruments; the scorer opens the crate. Commercial cuts stay in `id/`; rights-check before `ego/`. |
| 1 | `/cyborge-score`    | Reads the essay for its arc AND its mood; picks/records a **genre** and researches how it's built in Strudel (opening the research bank first); drafts `song.json` (SHAPE + genre) and `palette.json` (SOUND — its own key/riffs/timbres). `<name> <genre>` = a deliberate **full recompose** in that genre; bare `<name>` preserves tuned files, appending only what's new. |
| 2 | `/cyborge-compose`  | Renders the voice (`tools/tts/eleven.py` — ElevenLabs v3, incremental) and compiles the shape (`tools/song/build.py`) into the page. |
| 3 | `/cyborge-feedback` | Plays it; turns the human's reactions into `feedback.md` — two lists, **Keep** and **Fix**. |
| 4 | `/cyborge-shape`    | Applies the **Fix** list, leaves **Keep** (and anything unmentioned) untouched. Loops back to feedback. |

**`/cyborge-song <name> [genre]`** is the one-pull wrapper: it runs **score → compose** in a single
command (essay in, playable page out), obeying all their rules. Feedback and shape stay separate —
they need human ears between passes.

**Two tools patch separate marked regions of the page, so they never collide:**

```
mycelium/essays/<name>.md            ──eleven.py─▶  line-NN.wav  +  // BARS, // VOICE-FILES
id/<name>/song.json    (shape)  ┐
id/<name>/palette.json (sound)  ┴──build.py──▶  // ARRANGE + // INSTRUMENTS  (palette.json
                                                overrides the cookbook default sound)
```

**Everything is incremental & deterministic — the iron rule: *fix where broken, leave what works.***
Edit one essay line → only that voice clip re-renders. Edit one `song.json` section → only that
arrange row changes. Edit one `palette.json` instrument → only that instrument changes. Nothing
else moves. The one deliberate exception is a **genre recompose** — `/cyborge-score <name> <genre>`
re-authors the whole shape + sound on purpose. `id/agar-lab/` is the reference build.

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
  place we vendor a runtime. Music is Strudel patterns, compiled from `song.json` (shape) + a
  per-song `palette.json` (sound, authored from the essay's mood) over the cookbook default.
- **Voice** is pre-rendered offline by `tools/tts/eleven.py` (ElevenLabs v3, so `[audio tags]`
  like `[sigh]`/`[whispers]` perform). Clips ship; nothing calls a voice API at play-time. Keys
  live in `.env` (gitignored), never in code.
- **Spec-driven & deterministic:** a song is *compiled from data* (the essay + `song.json` +
  `palette.json`), never hand-written. Same sources → same Strudel, so iteration never clobbers
  tuned parts. The generated page is a build artifact; the sources are the three data files.

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
