# Recipe — the album (a hallway of songs)

An album is an ordered list of finished songs that play as one sitting: each track loads, plays
its one loop, and hands to the next. The first (and only) album: `id/album/` —
*tough times ever last, tough people never do*. Built and maintained by **`/cyborge-album`**.

## The hallway page (`id/<album>/index.html`)

A hand-authored page (not a build artifact) with a `TRACKS` list, a track strip, and one
`<iframe allow="autoplay">`:

```js
const TRACKS = [
  { src: '../demi_demi/', name: 'demi demi', sub: 'trance · crate jam' },
  ...
];
```

- **`allow="autoplay"` is the whole trick.** The listener clicks once on the album page; the
  attribute delegates that permission into every same-origin track the frame loads. Page-to-page
  navigation would lose it and stall on each song waiting for a click.
- Clicking a track jumps the album there. After the last track, offer *play it again*.

**Double-buffered — no gap between tracks.** Two frames: the visible one plays
(`?album=1` → auto-play at gate-open), while the NEXT track loads hidden with
`?album=1&hold=1` — it boots, fills its load gate, posts `{cyb:'song-ready'}`, and **waits**.
On the visible track's `{cyb:'song-done'}` the album promotes the hidden frame and posts
`{cyb:'go'}`: the next song starts in milliseconds. Route messages by `e.source` (which frame
sent it); if `song-done` arrives before the wings are ready, promote anyway and fire `go` on
its `song-ready`. Cold starts (first track, a jump) load `?album=1` directly. Always remove
the old frame from the DOM — a dead page must not keep an AudioContext.

## The template hooks (in `cookbook/strudel/template.html`, so every song is album-ready)

1. `const ALBUM = new URLSearchParams(location.search).has('album') && window.parent !== window;`
2. When the honest load gate opens: `if (ALBUM) { resume the AudioContext; play(); }` — the song
   starts itself, through the same `play()` the button uses. The gate still gates: nothing plays
   until every clip is decoded.
3. In `finishLoop()`: `if (ALBUM) parent.postMessage({ cyb: 'song-done' }, '*');` — the album
   page listens and advances.

## The edges (endings speak to intros)

Between tracks there is a load gap of a few seconds — **the groove silence of a record**. Shape
both sides of it so it feels intended:

- **Every track's last section fades out; every track's first section fades in.** The flag is
  data, in `song.json`: `"fade": "in" | "out"` on an **instrumental** section. `build.py`
  compiles it to `.postgain(saw.range(…).slow(bars))` — a ramp over exactly that section
  (arrange restarts each section's pattern, so the ramp starts at the section's edge).
  Instrumental sections only — voice rows have runtime bars, and **voice lines are untouchable**.
  Inside a fade section, don't rely on a layer's own `.postgain` (the ramp overrides it).
- **The bridge: the outro quotes the next track's intro.** Add edge sections and *additive*
  palette instruments — never alter a tuned instrument. Ways to quote:
  - same key → borrow the next intro's actual voicing/timbre (demi's `gauzeahead`/`monitorghost`
    are theGodInUrhead's gauze + monitor, both D minor);
  - a tone apart → walk the pad down onto the next opening chord (agar's `towardsea` ends on
    oh_dear's exact `[g2,bb2,d3]` swell);
  - a fifth apart → it's a cadence: land the drone on the next tonic (nice_ron's `cadenza`
    leans E onto agar's A — dominant resolution, free of charge);
  - migrate a motif's timbre (theGodInUrhead's `boxtoforest` plays nice_ron's belltale shape
    in the music box).
- Edits are **append/prepend/flag only**: no voice section moves, no voice index shifts, no
  re-render. Rebuild is `build.py` per track — byte-identical everywhere but the edges.

## The laws

- Voice notes are never touched by album work. Not their text, not their sections, not their bars.
- Bridge instruments are ADDITIVE palette entries (a song with no palette gets one holding
  *only* bridges, sound otherwise cookbook default — see `id/agar-lab/palette.json`).
- **Re-scaffold safety:** before running `compose.py` on an old track, verify
  `audio/voice/.render-manifest.json` matches the essay's blocks — a stale/missing manifest
  re-renders (re-ROLLS) every mismatched line. Crate jams (no voice) rebuild with `build.py` only.
- Tempo never bridges (each page is its own clock); the gap absorbs the tempo change.
