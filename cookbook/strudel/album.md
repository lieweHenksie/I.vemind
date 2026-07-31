# Recipe — the album (a hallway of songs)

An album is an ordered list of finished songs that play as one sitting: each track loads, plays
its one loop, and hands to the next. The first (and only) album: `id/album/` —
*tough times ever last, tough people never do*. Built and maintained by **`/cyborge-album`**.

## The hallway page (`id/<album>/index.html`)

A hand-authored page (not a build artifact) with a track strip and one
`<iframe allow="autoplay">`. The running order lives in its own file, `tracks.js`, because two
pages read it — the hallway and the reading room — and a track must never exist in one and not
the other:

```js
// id/<album>/tracks.js
window.ALBUM = {
  band: "I'VEMIND", title: 'tough times ever last, tough people never do',
  tracks: [
    { src: '../demi_demi/', essay: 'demi_demi', name: 'demi demi', sub: 'trance · crate jam' },
    ...
  ],
};
```

`essay` is the source writing under `mycelium/essays/` — usually the folder name, but not
always (agar-lab's essay is `essay-1`), which is exactly why it is written down.

- **`allow="autoplay"` is the whole trick.** The listener clicks once on the album page; the
  attribute delegates that permission into every same-origin track the frame loads. Page-to-page
  navigation would lose it and stall on each song waiting for a click.
- Clicking a track jumps the album there. After the last track, offer *play it again*.
- **Every chip is two doors:** the button plays the room, a small `essay` link reads what is
  said in it. Both the per-track links and the header's `[ read the writing ↗ ]` open in a new
  tab — navigating away would kill the music. The header link follows whatever is playing.

**Double-buffered — no gap between tracks.** Two frames: the visible one plays
(`?album=1` → auto-play at gate-open), while the NEXT track loads hidden with
`?album=1&hold=1` — it boots, fills its load gate, posts `{cyb:'song-ready'}`, and **waits**.
On the visible track's `{cyb:'song-done'}` the album promotes the hidden frame and posts
`{cyb:'go'}`: the next song starts in milliseconds. Route messages by `e.source` (which frame
sent it); if `song-done` arrives before the wings are ready, promote anyway and fire `go` on
its `song-ready`. Cold starts (first track, a jump) load `?album=1` directly. Always remove
the old frame from the DOM — a dead page must not keep an AudioContext.

**Two seams smooth the hand-off, so it reads as a record-gap, not a skipped beat.** (1) The
outgoing track posts `song-done` **~0.3s early** (before its true last bar) and keeps playing its
near-silent fade-out tail; the album keeps the old frame alive and **delays its drop ~800ms** — so
the incoming boots *during* the outgoing's fade-out and their two silent ramps overlap, instead of
cutting to dead air. (2) The held (wings) frame **pre-compiles its score while the AudioContext is
still suspended** (silent), so `go` doesn't pay `evaluate()`'s cost on the critical path. Neither
can beat-match across the independent per-page clocks — the small gap is real — but the seam no
longer lands as a stutter.

## The reading room (`id/<album>/essay.html`)

The songs are the essays out loud; this is the essays on the page. One hand-authored page that
fetches `mycelium/essays/<slug>.md` and renders it — a rail of the album order down the left, the
writing in the story font, arrow keys between rooms, a `hear it ↗` link back to the song.

It parses the markdown **exactly the way `tools/tts/eleven.py` does** (frontmatter out, comments
out, blank line = one block, `#` lines are notes), so the number in the margin beside a paragraph
is the number of the clip you hear: line 03 here is `line-03.wav` there. That parity is the whole
point — if the two ever disagree, the reading room is lying about the song.

Nothing is stripped, though. Comments, `#` notes and frontmatter render as **marginalia** in the
machine font, dim, beside the prose — in this project the notes-to-self are part of the writing,
and a crate jam whose essay is *only* a comment still has something to read. A `margin notes`
toggle folds them away (remembered), except where they're all there is.

*(This is the one place `mycelium/` is rendered. It stays unpublished as a source — the reading
room reads it, it is not built into a page.)*

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

## Intermezzos (a line, given its own room)

When a narrator line has to carry the album's language while the music is busy — landing on an
outro's dissolve, or having to *start* a song before it can settle — it loses. The fix is an
**intermezzo**: a tiny standalone track carrying **only that spoken line**, slotted into the album
order in the gap beside its source song. Less disruptive by construction — the line breathes, the
song is free to just be music.

An intermezzo is a full song folder (essay + `song.json` + `palette.json`), built by `compose.py`
like any other — but:

- **Name it for its line, never number it** — `id/nature-was-a-gift/`, `id/all-good-things/`,
  `id/hes-wrong-of-course/`. Numbered intermezzos have to be renamed the moment one is inserted
  in front of them (folder, essay, `song.json`'s `essay` field, the album's `tracks.js`, every
  comment pointing at them). A name that says what the room holds never goes stale, and the
  running order lives in `tracks.js` where it belongs.

- **Reuse the clip, never re-roll.** Copy the already-rendered `line-NN.wav` from the source song
  into the intermezzo's `audio/voice/line-01.wav`, and seed a matching `.render-manifest.json`
  (`{"lines": ["<the exact line text>"]}`). With the essay text matching, `eleven.py` reports
  *unchanged* and makes zero API calls. `compose.py` still re-sizes `bars` at the intermezzo's BPM.
- **No groove — the intermezzo IS the doorframe.** Three sections: an instrumental `"fade":"in"`,
  the `voice` line (runtime bars), an instrumental `"fade":"out"`. The bed is a whisper of the
  **next** room's key/timbre (reuse its bridge voicings), and the fade-out **resolves onto the
  next track's opening chord** — the bridge philosophy, moved into the interstitial itself
  (`hes-wrong-of-course` holds D-minor gauze into theGodInUrhead; `nature-was-a-gift` walks
  theGodInUrhead's music box into nice_ron's E-minor bells; `all-good-things` rings those bells
  in A minor onto agar-lab's opening A). Keep instrumental sections short (2–4 bars) so it stays
  an interlude.
- **Its source song loses the line.** Drop the block from the source essay (add an HTML comment
  noting where it went), and in `song.json` delete `"voice": N` from that section — give it an
  explicit `bars` if it was a middle section, since it no longer gets its length from a clip —
  then `compose.py` the source (the remaining clips are *unchanged*). Rewrite that section's
  label: the words moved out, so the label must not still say them.
  A source whose only line was the moved one becomes a **pure crate jam** (0 voice blocks — an
  essay of just a comment; `bars`/`VOICE_FILES` compile to `[]`).

*(Moving a line out of a song is a director's re-shape, not an edge pass — do it when asked, not
as routine album work.)*

## The laws

- Voice notes are never touched by album work. Not their text, not their sections, not their bars.
- Bridge instruments are ADDITIVE palette entries (a song with no palette gets one holding
  *only* bridges, sound otherwise cookbook default — see `id/agar-lab/palette.json`).
- **Re-scaffold safety:** before running `compose.py` on an old track, verify
  `audio/voice/.render-manifest.json` matches the essay's blocks — a stale/missing manifest
  re-renders (re-ROLLS) every mismatched line. Crate jams (no voice) rebuild with `build.py` only.
- Tempo never bridges (each page is its own clock); the gap absorbs the tempo change.
- **Serve with `tools/serve.py`, and cache-bust the track iframes.** Two belts for one trouser,
  because staleness here is invisible: the album plays an old version of a song you just fixed,
  and nothing looks wrong.
  - `python3 -m http.server` sends `Last-Modified` and **no** `Cache-Control`, which licenses the
    browser to reuse a page heuristically — no revalidation — for roughly 10% of its age. The
    hallway page itself is the dangerous one: an old copy of it carries an old iframe buster.
    `tools/serve.py` is the same server with `Cache-Control: no-store` on everything.
  - The album still appends `&v=Date.now()` (one stamp per album load) to every iframe `src`,
    which covers anyone serving it another way. The browser caches by full URL *including the
    query string*, so a track's `?album=1` entry is a **separate cache entry** from its standalone
    `/id/<name>/` entry. The song page ignores the extra `v` param (it only reads
    `has('album')`/`has('hold')`).
