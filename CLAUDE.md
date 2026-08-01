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
│   ├── serve.py            ← THE DEV SERVER: http.server + `no-store` (nothing ever plays stale)
│   ├── tts/eleven.py       ← the VOICE: ElevenLabs v3 render, incremental (+ audio-tags.md)
│   ├── song/build.py       ← SHAPE+SOUND: compiles song.json + palette.json → Strudel
│   ├── song/compose.py     ← one pull: eleven.py + build.py for a song
│   ├── song/reshell.py     ← re-drops a built song onto TODAY's template (shell forward, score kept)
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
    ├── head_god/           ← song.json (SHAPE) + palette.json (its OWN sound) + index.html
    └── album/              ← THE HALLWAY: index.html (plays all tracks) + tracks.js (the running
                              order, shared) + essay.html (THE READING ROOM — the writing behind
                              each track). Intermezzos are named for their line, never numbered.
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

**Before you trust a palette edit, run the bench ear:** `python3 tools/song/check.py id/<name>`
(add `--all` for the album, `--static` to skip the browser). It exists because raw Strudel has
three failure modes the build cannot see: **one bad instrument kills the whole score** (all
instruments share one evaluated block, so a single syntax error means the song plays *nothing*
— it bisects and names the culprit); **an instrument can render silent with no error at all**
(`s("x").freq(…).sustain(0)` is silent in 1.0.3 — it listens to each one alone through the same
analyser the stage uses); and **enriching an instrument can move the film** (`gen_cues` regex-reads
instrument code, so it shows the region drift before you build). Always muted — a checker that
plays thirty-five instruments at you is an ambush. **Adding a palette entry is free**:
`gen_instruments` only emits what a section names, so a staged instrument changes zero bytes
until you wire it in.

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

1. Update the `## Last Session

**Nothing was broken that anyone could hear; three things were broken that nobody could.**

*(The previous session's work — the analyser sea, the reading room, `reshell.py`, `serve.py`, the
cast, oh_dear's EAS ending, the three intermezzos — sat uncommitted for a week. It is now in
`fac780a` and `cc4c37c`, with the full account in those commit messages.)*

- **The album played with no film at all** — and with no error anywhere, which is what made it
  hard to see. The page defined a top-level `async function gate(tr)` to preload a track's assets.
  `initStrudel()` assigns Strudel's ENTIRE control vocabulary onto `globalThis`, and it runs
  *after* the page script is evaluated, so `window.gate` was quietly replaced by Strudel's `gate`
  control. `await gate(tr)` called that control, got a Pattern, awaited a non-promise (resolves
  instantly) and returned — so the voice/sample preload, the name registration and `buildFilm()`
  never ran. **The player script is now wrapped in an IIFE** so none of its declarations touch
  `globalThis`; `gate` is renamed `gateAssets` as belt and braces. **Never name anything in a page
  that also evaluates Strudel after a Strudel control.**
- **`tools/song/check.py` — THE BENCH EAR.** Static pass + region-drift pass + a browser pass that
  evaluates each instrument alone and LISTENS to it. It exists so the palettes can get as rich as
  they want without the three failure modes the build cannot see. It imports `build.py` rather
  than restating it. Always `--mute-audio`.
- **Four bugs it caught in ITSELF**, each of which would have made it lie — worth knowing, because
  they are all traps for any future audio harness:
  1. Evaluating each instrument against the full block meant one broken entry poisoned every
     verdict. It only bisects when the block is broken now.
  2. `hush()` does not silence what is still ringing, and half this cookbook runs `room(0.9)`. A
     palette of literal `silence` scored **18/18 sounding**. The verdict is now a DELTA over the
     residual tail — you cannot wait a reverb out.
  3. **`initStrudel()` does not load the AudioWorklets.** A real page reaches `initAudio()` when
     the human clicks play; a headless harness never clicks, so `shape`/`crush`/`coarse` threw
     "no valid AudioWorkletGlobalScope" per event and rendered silent — **19 false accusations**
     across nice_ron and oh_dear. `distort` (a WaveShaper) worked throughout, which is what made
     it legible. The checker now calls `initAudio()` and *proves* it with a `shape()` probe.
  4. `getByteTimeDomainData` quantises to 8 bits — one step is 1/128 ≈ 0.0078 — so anything
     quieter read as exactly 0, below the default threshold itself. Now `getFloatTimeDomainData`.
- **Strudel gotchas, learned the hard way**: `s("x").freq(…).decay(…).sustain(0)` with no explicit
  attack/release renders **silent** in 1.0.3 (`note(…).s("x")` is fine). And **`crush()` can
  quantise a quiet signal away to nothing** — see chiparp under Next.

## Next

- **nice_ron's `chiparp` makes NO SOUND** — verified, and the one real finding the bench ear
  turned up. Bisected off its own definition: drop `.crush(4)` and it sounds; keep the crush and
  lift `gain` 0.2 → 0.9 and it sounds; exactly as written it is zero. It is wired into **section 8,
  "DROP II — the hook doubles down"**, so that section has been playing ten layers, not eleven —
  the chiptune arp meant to crown the drop has never been in it. Left alone deliberately: which
  way to fix it is a sound decision, not a code one.
- **nice_ron has 16 of its own palette entries unwired** (`dropkick`, `droplead`, `technobass`,
  `dropsnare`, `sneezestab`…) — leftovers from the v10/v11 drop A/B. They cost nothing (unused
  entries emit no bytes), but check whether any were meant to be in the drop.
- **Listen to oh_dear and agar-lab.** Both were re-scored and verified only mechanically (they
  play, the tones are at pitch, every block is spoken once) — nobody has heard them.
- **Lengthen the intermezzos** — the human is doing this pass (they are 4/3/4-bar rooms now).
- **agar-lab sections 1, 2 and 3 have no labels at all** (verified) — the hero title is blank
  on screen for the first ~8 bars. Sections 4–29 are all named.
- **head_god is retired** (the human deleted its essay: "it was bad, we did it better in
  theGod"). `id/head_god/` still exists and is the only page left on the old shell; `reshell.py`
  refuses it correctly. Delete it or leave it as a fossil.
- **Feedback loops**: theGodInUrhead (split points vs sentences, the bell/music-box gains, v3
  accent drift over 16 lines), fenton, nice_ron — all await another ear pass. The album wants a
  full sitting now that the order changed.
- **agar-lab**: labels are mostly blank (its titles don't sing yet); the essay-1 naming is still
  unreconciled (folder `agar-lab`, essay `essay-1`).
- **Standing**: home page (`index.html` gallery), Netlify hookup + secrets, MCP migration,
  v3 accent consistency (higher stability / text-to-dialogue).
