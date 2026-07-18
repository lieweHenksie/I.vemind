#!/usr/bin/env python3
"""Compile a song spec -> the Strudel score (instruments + arrange), deterministically.

    python3 tools/song/build.py id/<name>/song.json --index id/<name>/index.html

The spec (song.json) is the source of truth for the SHAPE. Editing one section changes
exactly one arrange row — everything else regenerates identically, so iteration never
clobbers untouched parts. Instruments come from cookbook/strudel/palette.json. The `bars`
array + voice-file list are owned separately by tools/tts/eleven.py (different markers).
"""
import argparse, json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
PALETTE = ROOT / "cookbook/strudel/palette.json"


def gen_instruments(used, palette):
    # palette order = definition order; only emit what the song uses (skip _meta keys)
    return "\n".join(f"let {name} = {palette[name]}" for name in palette
                     if name in used and not name.startswith("_"))


def _stack(parts):
    return parts[0] if len(parts) == 1 else "stack(" + ", ".join(parts) + ")"


def _vc(i):
    return 'vo(s("voice:' + str(i) + '"), ' + str(i) + ')'


def gen_arrange(sections, bpm):
    rows = []
    for s in sections:
        label = ("   // " + s["label"]) if s.get("label") else ""
        if "voice" in s:
            i = s["voice"]
            if "split" in s:
                # The voice fires in the FIRST sub-section and rings out on its own; later
                # sub-sections just change the music — so bars can DROP mid-sentence while the
                # line keeps speaking. Sub bar-counts should sum ~ bars[i] (the clip's length).
                for j, (n, plyrs) in enumerate(s["split"]):
                    if j == 0:
                        rows.append("  [%d, %s],%s" % (n, _stack(list(plyrs) + [_vc(i)]), label))
                    else:
                        rows.append("  [%d, %s],   // …voice %d rings on, bars shift" % (n, _stack(list(plyrs)), i))
            else:
                rows.append("  [bars[%d], %s],%s" % (i, _stack(list(s.get("layers", [])) + [_vc(i)]), label))
        else:
            rows.append("  [%s, %s],%s" % (s.get("bars", 4), _stack(list(s.get("layers", []))), label))
    tail = ".fast(%s/120)" % bpm if bpm != 120 else ""
    return "arrange(\n" + "\n".join(rows) + "\n)" + tail


def _rows(sections):
    # The audible row walk shared by timeline + video cues: split voice sections expand to
    # their sub-rows (known bars); plain voice sections have runtime bars (None).
    rows = []
    for s in sections:
        if "voice" in s and "split" in s:
            rows += [(n, list(p)) for n, p in s["split"]]
        elif "voice" in s:
            rows.append((None, list(s.get("layers", []))))
        else:
            rows.append((s.get("bars", 4), list(s.get("layers", []))))
    return rows


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
    for ri, (rbars, layers) in enumerate(_rows(sections)):
        for lname in layers:
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
    # One entry per audible row: [bars, label, punch, energy]. Voice sections emit "V<i>" — the
    # page resolves their length from the score's `bars` array (owned by eleven.py) at play time.
    # punch = the film bounces here — a DROP: set by a section's "punch": true, or auto from
    # a label that says "drop". energy = this row's layer count / the song's max — the sea's
    # height follows the arrangement's density, so the water rises where the music thickens.
    rows = []                                     # (bars_expr, label, punch, layer_count)
    for s in sections:
        lbl = s.get("label", "")
        punch = 1 if (s.get("punch") or "drop" in lbl.lower()) else 0
        label = json.dumps(lbl, ensure_ascii=False)
        if "voice" in s and "split" in s:
            for j, (n, plyrs) in enumerate(s["split"]):
                rows.append((str(n), label, punch, len(plyrs) + (1 if j == 0 else 0)))
        elif "voice" in s:
            rows.append(('"V%d"' % s["voice"], label, punch, len(s.get("layers", [])) + 1))
        else:
            rows.append((str(s.get("bars", 4)), label, punch, len(s.get("layers", []))))
    maxc = max((c for *_, c in rows), default=1) or 1
    out = ", ".join("[%s, %s, %d, %s]" % (b, l, p, round(c / maxc, 2)) for b, l, p, c in rows)
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
        used.update(s.get("layers", []))
        for part in s.get("split", []):          # instruments used only inside a split
            used.update(part[1])
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
