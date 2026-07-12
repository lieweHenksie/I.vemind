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
    # palette order = definition order; only emit what the song uses
    return "\n".join(f"let {name} = {palette[name]}" for name in palette if name in used)


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


def patch(txt, start, end, content):
    if start not in txt or end not in txt:
        raise SystemExit(f"markers {start}/{end} not found in index.html — add them first")
    return re.sub(re.escape(start) + r".*?" + re.escape(end),
                  f"{start}\n{content}\n{end}", txt, flags=re.S)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--index", required=True)
    a = ap.parse_args()

    spec = json.loads(pathlib.Path(a.spec).read_text())
    palette = json.loads(PALETTE.read_text())
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
    idx.write_text(txt)
    n_voice = sum(1 for s in sections if "voice" in s)
    print(f"built {len(sections)} sections ({n_voice} voice), {len(used)} instruments -> {idx.name}")


if __name__ == "__main__":
    main()
