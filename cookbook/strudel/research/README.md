# cookbook/strudel/research — the listening bank

What cyBorge has learned from OTHER machines' music. Each file is a **study** of a real Strudel
artist's video: transcribed (`tools/song/transcribe.py`), every claimed function verified against
the strudel.cc docs, distilled into moves and recipes. `/cyborge-research` writes these;
`/cyborge-score` spends them (its research step opens this folder before searching the web fresh).

**The law: learn the move, never lift the piece.** A study banks *techniques* — how a genre gets
its power, which functions make which sound — never an artist's actual pattern. Recipes in a
study are re-expressed in our own key and motif, and the source is always credited.

**Statuses** (every technique carries one):

- `doc-verified` — confirmed against strudel.cc docs; exact name + signature recorded.
- `runtime-verified` — parsed AND heard on our pinned runtime, in a real song.
- `frame-read` — read off a screenshot (`transcribe.py --frames`, the eye); name certain,
  signature not yet confirmed in docs.
- `unverified` — heard in the video, couldn't confirm; the guess is recorded as a guess.
- flags: `needs-pin-bump` (newer than the template's pinned `@strudel/web`) · `repl-only`
  (an editor widget; no equivalent in an embedded page).

A move upgrades to `runtime-verified` when it first survives a real song's `/cyborge-feedback`
loop — whoever lands it updates the study's table.

## Index

| Study | Artist | Genre | The moves |
|-------|--------|-------|-----------|
| [switch-angel--trance-in-the-beginning](switch-angel--trance-in-the-beginning.md) | Switch Angel | trance | one-riff genesis · acid saw lead · duck-orbit sidechain · supersaw detune · filter-as-energy · `.fit()` tops |
| [oazoor--riff-banks-big-room](oazoor--riff-banks-big-room.md) | Oazoor · Jean-François | big-room EDM | riff banks + `pick` walk · rhythm/harmony split via `inhabit` · factory instruments · four-bass pyramid · `@` drop-holds · `postgain` mix + `all()` master |
