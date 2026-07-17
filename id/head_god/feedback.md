# head_god — feedback

Genre: trip-hop / dark downtempo · 86 BPM. Listened back 2026-07-13. Two fixes; the rest stands.

## Keep
- The whole **trip-hop direction** — 86 BPM, the dusty groove, deep sub, Rhodes stabs, vinyl
  crackle. Not mentioned = protected: the shaper leaves the sound / `palette.json` alone.
- The mid-line **beat-drops** on L2 ("die virgins") and L7 (the mechanism) — untouched.
- Every section not named in Fix — left byte-identical.

## Fix
1. **Intro is too long.** The build before the first word is **12 bars** (crackle 4 → sub 4 →
   +kick 2 → dusty beat 2) ≈ 33s at 86 BPM. Roughly **halve it — target ~6 bars** (e.g. 2 / 2 / 1 /
   1). Edit the four intro sections' `bars` in `song.json`; leave their layers.

2. **Render L8 + L9 as one line** (they should be tight, spoken as one thought):
   - **Essay** (`mycelium/essays/head_god.md`): remove the blank line between
     *"…Except when I speak to pretty people."* and *"There I am allowed to embarrass myself."* so
     the two blocks become **one**. This re-renders just that clip (now line 08) and drops the line
     count **10 → 9**.
   - **`song.json`**: the merged block is the new final voice line (`voice: 8`). **Drop the old
     `voice: 9` section** ("embarrass myself — bare") — with only 9 lines it would dangle (no clip,
     no `bars[9]`) and break the build.
   - *Shaper's call:* consider making the merged `voice: 8` a **split** — fuller for "She does the
     talking…", then drop to bare `["wash","bass"]` on "There I am allowed to embarrass myself." —
     to keep the deflating ending now that L9 no longer stands alone.
