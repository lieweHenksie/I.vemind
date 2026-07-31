#!/usr/bin/env python3
"""Compile a song spec -> the Strudel score (instruments + arrange), deterministically.

    python3 tools/song/build.py id/<name>/song.json --index id/<name>/index.html

The spec (song.json) is the source of truth for the SHAPE. Editing one section changes
exactly one arrange row — everything else regenerates identically, so iteration never
clobbers untouched parts. Instruments come from cookbook/strudel/palette.json. The `bars`
array + voice-file list are owned separately by tools/tts/eleven.py (different markers).

RICHNESS (so an arrangement isn't just static loops stacked):
  • a layer may carry a `vary` — a preset transform that makes THAT instrument evolve in THIS
    section without a new palette entry:  "bass"  ->  ["bass", "double"]  or  {"l":"bass","vary":"ghost"}.
  • an instrumental section may carry a `fill` — an instrument that plays ONLY the last bar
    (the lift before a change):  {"bars":4, "layers":[...], "fill":"snareroll"}.
Both are additive: a song using neither compiles byte-identically to before.
"""
import argparse, json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
PALETTE = ROOT / "cookbook/strudel/palette.json"

# ── vary presets · a small, SAFE vocabulary of per-layer moves (all core Strudel, pinned-runtime
#    verified). They COMPOSE onto any instrument (appended method chains) — they never override an
#    instrument's own filter/gain the way a fade's postgain does. Add moves here, not raw Strudel
#    in song.json, so the shape stays declarative and every song draws from the same catalog. ──
VARY = {
    "double":  ".fast(2)",                             # twice as busy
    "half":    ".slow(2)",                             # half as busy — thin it out
    "ghost":   ".sometimesBy(0.3, x=>x.gain(0.5))",    # scattered quiet ghost notes (humanises)
    "stutter": ".every(4, x=>x.fast(2))",              # a doubling FILL every 4th bar
    "build":   ".every(2, x=>x.fast(2))",              # tightening every other bar (tension)
    "ply2":    ".ply(2)",                              # each hit retriggered twice (rolls)
    "thin":    ".degradeBy(0.3)",                      # drop ~30% of events (sparser, less mechanical)
    "echo":    ".off(0.125, x=>x.gain(0.4))",          # an eighth-note echo tap trailing each event
}


def _lname(entry):
    """The instrument NAME of a layer entry (used for palette lookup, cues, energy count)."""
    if isinstance(entry, str):  return entry
    if isinstance(entry, list): return entry[0]
    if isinstance(entry, dict): return entry["l"]
    raise SystemExit(f"bad layer entry (want name, [name,vary] or {{'l':..,'vary':..}}): {entry!r}")


def _lvary(entry):
    if isinstance(entry, list): return entry[1] if len(entry) > 1 else None
    if isinstance(entry, dict): return entry.get("vary")
    return None


def _lexpr(entry):
    """The Strudel expression for a layer: the bare name, or name + a vary preset's method chain."""
    name = _lname(entry); vary = _lvary(entry)
    if not vary:
        return name
    tail = VARY.get(vary)
    if tail is None:
        raise SystemExit(f"unknown vary preset '{vary}' on layer '{name}' — known: {sorted(VARY)}")
    return name + tail


def _stack(parts):
    if not parts:
        return "silence"                      # a voice line truly alone: the music plays nothing
    return parts[0] if len(parts) == 1 else "stack(" + ", ".join(parts) + ")"


def expand_rows(sections):
    """Flatten sections into the flat list of audible ROWS that EVERY generator consumes, so row
    indices (which video cues reference) can never desync. Each row is a dict:
        bars   int  (a literal length)  |  ('V', i)  (a runtime voice length, from bars[i])
        layers list of layer entries (str | [name,vary] | {l,vary})
        label  the section's label (same on every sub-row of a split, so the hero title persists)
        punch  1 if this row is a drop (bounces the film)
        fade   'in' | 'out' | None  (album-edge ramp; literal-bars rows only)
        voice  the line index that FIRES on this row, else None
        note   the arrange-row comment (head = label, split continuation = 'rings on', fill = 'fill')
    A split expands to its sub-rows; a `fill` expands an instrumental section into [n-1] + [1]."""
    rows = []
    for s in sections:
        lbl = s.get("label", "")
        punch = 1 if (s.get("punch") or "drop" in lbl.lower()) else 0
        note_head = ("   // " + lbl) if lbl else ""

        if "voice" in s and "split" in s:
            vi = s["voice"]
            for j, (n, plyrs) in enumerate(s["split"]):
                rows.append(dict(bars=n, layers=list(plyrs), label=lbl, punch=punch, fade=None,
                                 voice=(vi if j == 0 else None),
                                 note=(note_head if j == 0
                                       else "   // …voice %d rings on, bars shift" % vi)))
            continue

        if "voice" in s:
            layers = list(s.get("layers", []))
            if "bars" in s:                   # a line over a fixed-length section (e.g. a fading outro)
                rows.append(dict(bars=s["bars"], layers=layers, label=lbl, punch=punch,
                                 fade=s.get("fade"), voice=s["voice"], note=note_head))
            else:                             # the usual voice slot: length is runtime bars[i]
                rows.append(dict(bars=("V", s["voice"]), layers=layers, label=lbl, punch=punch,
                                 fade=None, voice=s["voice"], note=note_head))
            continue

        # instrumental
        layers = list(s.get("layers", []))
        n = s.get("bars", 4); fade = s.get("fade"); fill = s.get("fill")
        if fill and not fade and isinstance(n, int) and n >= 2:
            # the fill instrument lifts only the LAST bar; the section otherwise plays as before
            rows.append(dict(bars=n - 1, layers=layers, label=lbl, punch=punch, fade=None,
                             voice=None, note=note_head))
            rows.append(dict(bars=1, layers=layers + [fill], label=lbl, punch=punch, fade=None,
                             voice=None, note="   // …fill"))
        else:
            if fill:
                # fills don't compose with an album fade (postgain ramp) or runtime bars — skip, warn
                print(f"(fill on '{lbl or 'section'}' skipped — needs an instrumental section with "
                      f"a fixed bars>=2 and no fade)")
            rows.append(dict(bars=n, layers=layers, label=lbl, punch=punch, fade=fade,
                             voice=None, note=note_head))
    return rows


def gen_instruments(used, palette):
    # palette order = definition order; only emit what the song uses (skip _meta keys)
    return "\n".join(f"let {name} = {palette[name]}" for name in palette
                     if name in used and not name.startswith("_"))


def gen_arrange(sections, bpm):
    # The score shapes the MUSIC only. Voice clips are NOT strudel events: the page arms every
    # line on the WebAudio clock itself (sample-accurate, immune to main-thread jank) — a
    # one-shot strudel event could start late or be skipped under render load, and a voice line
    # only fires once. Voice rows still size themselves from bars[i] (owned by eleven.py).
    out = []
    for r in expand_rows(sections):
        core = _stack([_lexpr(e) for e in r["layers"]])
        b = r["bars"]
        barsexpr = ("bars[%d]" % b[1]) if isinstance(b, tuple) else str(b)
        # "fade": "in" | "out" — an album-edge ramp over exactly this row's bars. postgain
        # multiplies AFTER each layer's own gain/fx (mix balance survives), and arrange restarts
        # each section's pattern, so the saw ramps from the section's edge. Literal-bars rows only:
        # voice slots have runtime bars, and voice is untouchable.
        if r["fade"] in ("in", "out") and core != "silence" and not isinstance(b, tuple):
            core = '%s.postgain(saw.range(%s).slow(%s))' % (core, "0,1" if r["fade"] == "in" else "1,0", b)
        out.append("  [%s, %s],%s" % (barsexpr, core, r["note"]))
    tail = ".fast(%s/120)" % bpm if bpm != 120 else ""
    return "arrange(\n" + "\n".join(out) + "\n)" + tail


def gen_cues(sections, palette, bpm):
    # Video sync: for every row, find crate samples the layers trigger and emit
    # [row, offsetBars, durBars, clipName, clipOffsetSec] cues. The page plays the small
    # pre-cut clip `clipName` (from clipOffsetSec, ~0) while the cue's bar window is live —
    # no big-file seeking. Only samples with a "clip" (sample.py --video) can cue video.
    samples = {n: m for n, m in palette.get("_samples", {}).items()
               if isinstance(m, dict) and m.get("clip")}
    filler = palette.get("_filler", [])
    # The viz backdrop is the shared cookbook default (linked, like theme.css), so EVERY song shows
    # the hidden face — even ones with no samples. A song overrides with its own "_viz_image" path,
    # or sets it to "" to opt out.
    viz = palette.get("_viz_image", "../../cookbook/strudel/laughing-man.png")
    head_js = ("    const VIZ_IMAGE = %s;\n    const FILLER_CLIPS = %s;\n"
               % (json.dumps(viz), json.dumps(filler)))
    if not samples:
        return head_js + '    const VIDEO_CLIPS = {};\n    const VIDEO_CUES = [];'
    clips = {n: m["clip"] for n, m in samples.items()}
    cues = []
    for ri, r in enumerate(expand_rows(sections)):
        rbars = None if isinstance(r["bars"], tuple) else r["bars"]   # runtime voice row -> None
        for lname in (_lname(e) for e in r["layers"]):
            code = palette.get(lname, "")
            m = re.search(r's\("([^"]+)"', code)
            if not m:
                continue
            tokens = m.group(1).split()
            slow = re.search(r"\.slow\(([\d.]+)\)", code)
            period = float(slow.group(1)) if slow else 1.0
            for i, tok in enumerate(tokens):
                if tok not in samples:
                    continue
                slen = (samples[tok]["end"] - samples[tok]["start"]) * bpm / 240
                if ".slice(" in code:                     # region: show the clip from its start
                    cues.append((ri, 0.0, round(min(rbars or slen, slen), 3), tok, 0.0))
                    continue
                t0 = (i / len(tokens)) * period
                if rbars is None:                          # voice row: first fire only, page clamps
                    cues.append((ri, round(t0, 3), round(slen, 3), tok, 0.0))
                    continue
                while t0 < rbars:
                    cues.append((ri, round(t0, 3), round(min(slen, rbars - t0), 3), tok, 0.0))
                    t0 += period
    clips_js = ", ".join("%s: %s" % (json.dumps(n), json.dumps(p)) for n, p in clips.items())
    rows_js = ", ".join("[%s, %s, %s, %s, %s]" % (r, o, d, json.dumps(c), off) for r, o, d, c, off in cues)
    return (head_js
            + '    const VIDEO_CLIPS = {%s};\n' % clips_js
            + '    const VIDEO_CUES = [%s];  // [row, offBars, durBars, clip, clipOffSec]' % rows_js)


def gen_timeline(sections, bpm):
    # One entry per audible row: [bars, label, punch, energy, voice]. Voice rows emit "V<i>" — the
    # page resolves their length from the score's `bars` array (owned by eleven.py) at play time.
    # punch = the film bounces here — a DROP: set by a section's "punch": true, or auto from
    # a label that says "drop". energy = this row's layer count / the song's max — the sea's
    # height follows the arrangement's density, so the water rises where the music thickens.
    trows = []
    for r in expand_rows(sections):
        b = r["bars"]
        barsexpr = ('"V%d"' % b[1]) if isinstance(b, tuple) else str(b)
        count = len(r["layers"]) + (1 if r["voice"] is not None else 0)   # the voice counts as a layer
        trows.append((barsexpr, json.dumps(r["label"], ensure_ascii=False), r["punch"], count, r["voice"]))
    maxc = max((c for *_, c, _v in trows), default=1) or 1
    out = ", ".join("[%s, %s, %d, %s, %s]" % (b, l, p, round(c / maxc, 2),
                                              "null" if v is None else v)
                    for b, l, p, c, v in trows)
    return ("    const TIMELINE = [%s];\n    const SONG_BPM = %s;" % (out, bpm))


def patch(txt, start, end, content, indent=""):
    if start not in txt or end not in txt:
        raise SystemExit(f"markers {start}/{end} not found in index.html — add them first")
    # lambda replacement: content is literal text, never regex escapes (labels may hold \u…)
    return re.sub(re.escape(start) + r".*?" + re.escape(end),
                  lambda m: f"{start}\n{content}\n{indent}{end}", txt, flags=re.S)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--index", required=True)
    a = ap.parse_args()

    spec_path = pathlib.Path(a.spec)
    spec = json.loads(spec_path.read_text())
    palette = json.loads(PALETTE.read_text())
    # Per-song palette: id/<name>/palette.json overrides/extends the cookbook default so each
    # song owns its instruments (its own key, riffs, timbres — authored from the essay's mood).
    # Anything the song doesn't redefine falls back to the shared recipe. The sound is DATA,
    # so builds stay deterministic and incremental.
    song_palette = spec_path.parent / "palette.json"
    if song_palette.exists():
        palette = {**palette, **json.loads(song_palette.read_text())}
    sections = spec["sections"]
    bpm = spec.get("bpm", 120)

    used = set()
    for s in sections:
        used.update(_lname(e) for e in s.get("layers", []))
        for part in s.get("split", []):          # instruments used only inside a split
            used.update(_lname(e) for e in part[1])
        if s.get("fill"):                        # a fill instrument is a real layer too
            used.add(s["fill"])
    unknown = used - set(palette)
    if unknown:
        raise SystemExit(f"unknown instruments (not in palette.json): {sorted(unknown)}")

    idx = pathlib.Path(a.index)
    txt = idx.read_text()
    txt = patch(txt, "// INSTRUMENTS-START", "// INSTRUMENTS-END", gen_instruments(used, palette))
    txt = patch(txt, "// ARRANGE-START", "// ARRANGE-END", gen_arrange(sections, bpm))
    # The crate: `_samples` in palette.json (stocked by tools/song/sample.py) registers extra
    # audio for prebake. Instruments PLAY them — a sample name isn't a layer by itself.
    crate = palette.get("_samples", {})
    if crate or "// SAMPLE-FILES-START" in txt:
        files = ", ".join(
            f"{json.dumps(n)}: {json.dumps(f['file'] if isinstance(f, dict) else f)}"
            for n, f in crate.items())
        txt = patch(txt, "// SAMPLE-FILES-START", "// SAMPLE-FILES-END",
                    "    const SAMPLE_FILES = {%s};" % (" " + files + " " if files else ""),
                    indent="    ")
    if "// TIMELINE-START" in txt:
        txt = patch(txt, "// TIMELINE-START", "// TIMELINE-END",
                    gen_timeline(sections, bpm), indent="    ")
    if "// VIDEO-CUES-START" in txt:
        txt = patch(txt, "// VIDEO-CUES-START", "// VIDEO-CUES-END",
                    gen_cues(sections, palette, bpm), indent="    ")
    idx.write_text(txt)
    n_voice = sum(1 for s in sections if "voice" in s)
    crate_note = f", {len(crate)} crate samples" if crate else ""
    print(f"built {len(sections)} sections ({n_voice} voice), {len(used)} instruments{crate_note} -> {idx.name}")


if __name__ == "__main__":
    main()
