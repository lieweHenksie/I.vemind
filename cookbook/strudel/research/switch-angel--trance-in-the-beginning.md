# Switch Angel — "Coding Trance Music: in the beginning"

- source: https://www.youtube.com/watch?v=YFQm8Hk73ug (short, 1:58)
- studied: 2026-07-14 · transcript: auto-captions via `tools/song/transcribe.py`
- genre: trance

## The moves

1. **One riff is the whole song.** The track grows from a single five-note motif — scale degrees
   (heard as `0 4 0 9 7`) in G minor, running 16ths. The bass is not a new idea: it's the lead
   *cloned* and dropped two octaves. Economy of material is the coherence; trance hypnosis is one
   cell repeating at different heights.
2. **The acid-tamed saw.** The lead is a raw sawtooth "tamed with acid" — a low-pass filter plus
   a filter *envelope* (`lpenv`), the cutoff ridden by hand on a slider. The lead is born dull
   and earns its brightness.
3. **The duck is the engine.** Four-on-the-floor kick, then: "increase the power by ducking our
   lead with the kick." Every melodic layer lives on its own orbit (3, 4, 5, 6); the kick
   sidechains them all — depth 0.8, attack 160 ms. The trance pump isn't an effect on top; it's
   the power source.
4. **Supersaw + random detune = the chaos budget.** The cloned bass becomes a `supersaw`, then
   "more chaos with random detuning." Width and dirt are added deliberately, one parameter at a
   time.
5. **Energy = opening the filter.** "Increase the filter for more power" — the arrangement's
   climb is a cutoff sweep, not new layers.
6. **The top is a loop, fitted.** Final element: a top (hats/percussion loop) "fit to our cycle" —
   a sample stretched to the event duration with `.fit()`.
7. **See everything.** Piano roll on the lead, scope on the kick — visualizers are part of the
   composing loop, not decoration.

## Verified vocabulary

Every function below was checked against strudel.cc (auto-captions garble code terms).

| Move | Strudel | Status |
|------|---------|--------|
| scale-degree melody | `n("0 4 0 9 7").scale("G2:minor")` — octave lives in the scale name; root defaults to octave 3 | doc-verified — our cookbook flags `.scale()` untested on our pages |
| acid filter envelope | `.lpf(300).lpenv(4).lpattack(t).lpdecay(t)` (aliases `lpe`/`lpa`/`lpd`) | doc-verified |
| hand-ridden cutoff | `slider(500, 100, 2000)` | doc-verified · repl-only — our embed equivalent is `sine.range(a,b).slow(n)` |
| sidechain duck | kick: `.duckorbit("3:4:5:6").duckdepth(0.8).duckattack(0.16)`; targets carry `.orbit(3)` … (aliases `duck`/`duckatt`/`datt`; attack is **seconds**) | doc-verified · needs-pin-bump |
| supersaw | `s("supersaw").detune(.3).unison(5).spread(.8)` (+ `detunepower`/`detuneblend`/`detunestack`) | doc-verified · needs-pin-bump |
| loop fitted to tempo | `s("top").fit()` — also `loopAt(n)`, `chop(n)`, `slice(n, "…")` | doc-verified — needs sample assets; our drums are synth by law |
| visualizers | `._pianoroll()` · `._scope()` | doc-verified · repl-only |

Caption garble corrected along the way: "04097" → `0 4 0 9 7` · "tamed with acid" → `lpenv` ·
"targets three, four, five, six" → `.duckorbit("3:4:5:6")` · "point eight" → `.duckdepth(0.8)` ·
"160 milliseconds" → `.duckattack(0.16)`.

Uncertain (heard, not confirmed): the exact motif digits; whether "subtract one octave" is done
via the scale-name octave (`G2:minor`) or a degree shift; "16 notes" is almost certainly
*16th notes*.

## A recipe of ours (not hers)

A generalized trance cell in the cookbook's voice — different key, different motif, same moves:

```js
// needs a pin newer than @strudel/web@1.0.3 (duck*, supersaw) — runtime-verify first
let lead = n("0 2 0 5 3").scale("e2:minor").fast(4).s("sawtooth")
  .lpf(sine.range(300, 2400).slow(16)).lpenv(3).lpdecay(.15).orbit(3)
let bass = n("0 2 0 5 3").scale("e1:minor").fast(4).s("supersaw")
  .detune(.4).lpf(500).orbit(4)
let kick = s("bd*4").duckorbit("3:4").duckdepth(.8).duckattack(.16)
```

## Runtime notes — spending this on OUR pin

- The template pins **`@strudel/web@1.0.3`**; `duck*` and `supersaw` (with its detune family) are
  newer. To spend moves 3–4: **bump the pin** in `cookbook/strudel/template.html` (its own comment
  says "bump the version freely"), re-verify `agar-lab` and `head_god` still parse, then upgrade
  these rows to runtime-verified.
- `slider()` / `._pianoroll()` / `._scope()` are REPL *editor* widgets — they don't exist in an
  embedded page. Her hand-slider becomes `sine.range(a,b).slow(n)` automation (or a JS control).
- The duck idea survives even on the old pin: approximate the pump by shaping the melodic layers'
  `.gain(...)` against the kick's 4/4 until a real `duckorbit` is available.
- `n().scale()` almost certainly parses on 1.0.3 (tonal is old Strudel), but it's on the
  cookbook's untested list — confirm it loads in our template before a song leans on it.
