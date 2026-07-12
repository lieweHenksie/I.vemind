# cookbook

**The toolkit.** A small library of copy-me recipes for turning a story into a
beautiful, atmospheric HTML page — cyBorge's storytelling apparatus, laid out on the bench.

Not a framework. Not a runtime. There is no `engine.js` that every page imports. Each recipe
is a self-contained, heavily-commented file you **copy into a piece and adapt**. A story in
`ego/` links the shared soul (`theme.css` + `base.css`) and carries its own copies of whatever
recipes it needs. That keeps every piece a standalone folder you can open, read, and understand
without chasing imports.

---

## The two rules

1. **`theme.css` + `base.css` are LINKED, never copied.** They are the one shared soul — the
   palette, the type, the default look of a story. Every piece points at them:
   ```html
   <link rel="stylesheet" href="../../cookbook/theme.css">
   <link rel="stylesheet" href="../../cookbook/base.css">
   ```
   Retheme a single piece by overriding the CSS vars in that piece's own `<name>.css`.

2. **Everything in `*.js` is COPIED into the piece.** The coder drops the needed recipe files
   into `ego/<name>/lib/`, loads them, then writes a small `<name>.js` that wires them to this
   story's beats. Adapt the copy freely — it belongs to the piece now.

All JS recipes attach their functions to a shared `window.cyb` namespace, so copying one or
copying all of them never collides.

---

## Recipes

| File | `cyb.*` functions | What it does | CUT type it satisfies |
|------|-------------------|--------------|-----------------------|
| `audio.js` | `createAudio` → `layerLoop`, `oneShot`, `unlock` | Layered looping ambience beds + one-shot hits, through a shared compressor. | **SOUND** |
| `reveal.js` | `onReveal`, `stagger`, `sectionProgress`, `scrollResist` | Scroll reactions: fire-once-on-view, boot-in line by line, 0→1 section progress for reactive audio/visuals, and heavy/underwater scrolling. | **SCROLL**, **PAUSE** |
| `flash.js` | `flash` | A full-screen wash of colour, then fade — a strike, a cut, a scene change mask. Returns a promise. | **VISUAL** |
| `particles.js` | `particleField` → `spawn`, `rain`, `stop` | A canvas of little agents that fall and settle — termites, dust, snow, ash. | **PIXEL** |
| `textfx.js` | `glitch`, `degrade`, `typewriter` | The text misbehaves: scramble-and-recover, permanent rot, type-itself-out. | **TEXT_FX** |
| `loader.js` | `loader` | The boot screen: preload assets with a status line, then a `[ start story ]` gate whose click unlocks audio. | *(framing — most pieces open with it)* |

### CUT → recipe map (for `cyborge-code`)

```
SOUND   → audio.js      (layerLoop, oneShot)
SCROLL  → reveal.js     (onReveal, stagger, sectionProgress, scrollResist)
VISUAL  → flash.js      (flash)  +  theme.css / a body class
PIXEL   → particles.js  (particleField)
TEXT_FX → textfx.js     (glitch, degrade, typewriter)
PAUSE   → reveal.js     (scrollResist, or a stagger delay)
```

The `NEEDS` field of a CUT lists the assets a recipe requires (an mp3 per SOUND layer, a colour
per VISUAL, etc.). `cyborge-code` collects every NEED before building and asks the human for it.

---

## Anatomy of a finished piece

```
ego/<name>/
├── index.html      links cookbook/theme.css + base.css; prose in <article class="piece">
├── <name>.css      ONLY story-specific styles (a background video, a special voice)
├── <name>.js       the wiring — calls into the copied recipes for THIS story's beats
├── lib/            copied recipe files (audio.js, reveal.js, …) — the standalone toolkit
└── audio/ …        the piece's own assets
```

## Reference implementation

`ego/azibo/` is built entirely on these recipes — read it to see the cookbook in use.

## Future

Each recipe has a deliberately small, single-purpose API so it can become an MCP tool later
(`add_audio_layer`, `add_reveal`, `add_flash`, `add_particles`, `scaffold_piece`). The `cyb`
namespace and the copy-not-import model are what make that migration mechanical rather than a
rewrite. The `automata` living-body pixel component is a planned future recipe.
