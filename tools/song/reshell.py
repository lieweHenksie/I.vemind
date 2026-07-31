#!/usr/bin/env python3
"""Re-shell built songs onto the CURRENT cookbook template.

    python3 tools/song/reshell.py <name>...          # e.g. nice_ron oh_dear
    python3 tools/song/reshell.py --all              # every page already on this shell
    python3 tools/song/reshell.py --all --check      # report only, write nothing

A song page is a build artifact: `cookbook/strudel/template.html` (the SHELL — the stage, the
voice bus, the visualizer, the controls) with a handful of marked regions filled in by the
tools (the SCORE — instruments, bars, arrange, voice files, samples, video cues, timeline).

`build.py` and `eleven.py` only ever patch the regions, so a change to the shell — a new
visualizer, a part of the stage removed — never reaches songs that were built before it.
This tool closes that gap the other way round: it keeps each song's regions exactly as they
are and re-drops them into today's template. Sound and shape are untouched, byte for byte;
only the machinery around them moves forward. No re-render, no recompile.

A page whose shell has drifted (missing markers, an older stage) is REFUSED, not guessed at —
those need a real recompose, not a swap.
"""
import argparse, difflib, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "cookbook" / "strudel" / "template.html"
# every generated region, in the order they appear in the page
MARKERS = ["INSTRUMENTS", "BARS", "ARRANGE", "VOICE-FILES", "SAMPLE-FILES", "VIDEO-CUES", "TIMELINE"]


def region(text, mark):
    """The generated body between a marker pair (exclusive), or None if the pair is missing."""
    m = re.search(r"// %s-START\n(.*?)([ \t]*// %s-END)" % (mark, mark), text, re.S)
    return None if m is None else m.group(1)


def voice_bus_ready(page_text):
    """True unless this page has voice lines but a TIMELINE from before the voice bus.

    The bus arms each line off the timeline's 5th field (the voice index). A page built by an
    older build.py has 4-field rows — re-shelling it onto today's stage would leave every line
    silent, without a single error. That is a recompile (build.py), not a re-shell.
    """
    files = region(page_text, "VOICE-FILES") or ""
    m = re.search(r"const VOICE_FILES = \[(.*?)\];", files, re.S)   # a JS literal: 'single' quotes
    if not m or not m.group(1).strip():
        return True                                     # no voice at all — nothing to lose
    tl = re.search(r"const TIMELINE = (\[.*?\]);", region(page_text, "TIMELINE") or "", re.S)
    if not tl:
        return False
    try:
        rows = json.loads(tl.group(1))
    except json.JSONDecodeError:
        return True                                     # unparseable: don't block on a guess
    return any(len(r) >= 5 for r in rows)


def reshell(page_text, template_text):
    """Today's template carrying this page's regions. Raises if the page is missing any."""
    missing = [m for m in MARKERS if region(page_text, m) is None]
    if missing:
        raise ValueError("missing marker regions: " + ", ".join(missing))
    if not voice_bus_ready(page_text):
        raise ValueError("its TIMELINE predates the voice bus (4-field rows, no voice index)")
    out = template_text
    for m in MARKERS:
        body = region(page_text, m)
        out = re.sub(r"(// %s-START\n).*?([ \t]*// %s-END)" % (m, m),
                     lambda mm, b=body: mm.group(1) + b + mm.group(2), out, flags=re.S)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", help="piece names under id/ (e.g. nice_ron)")
    ap.add_argument("--all", action="store_true", help="every id/*/ page that is on this shell")
    ap.add_argument("--check", action="store_true", help="report what would change; write nothing")
    a = ap.parse_args()
    if not a.names and not a.all:
        ap.error("name(s) or --all")

    template = TEMPLATE.read_text()
    if a.all:
        names = sorted(p.parent.name for p in ROOT.glob("id/*/index.html")
                       if region(p.read_text(), "TIMELINE") is not None)
    else:
        names = a.names

    changed = skipped = 0
    for name in names:
        index = ROOT / "id" / name / "index.html"
        if not index.exists():
            print(f"  ⊘ {name}: no index.html")
            skipped += 1
            continue
        page = index.read_text()
        try:
            out = reshell(page, template)
        except ValueError as e:
            print(f"  ⊘ {name}: {e}")
            print(f"      recompile it first — python3 tools/song/build.py id/{name}/song.json"
                  f" --index id/{name}/index.html")
            skipped += 1
            continue
        if out == page:
            print(f"  · {name}: already current")
            continue
        n = sum(1 for l in difflib.unified_diff(page.splitlines(), out.splitlines(), n=0)
                if l[:1] in "+-" and l[:3] not in ("+++", "---"))
        if a.check:
            print(f"  ~ {name}: {n} shell lines would change")
        else:
            index.write_text(out)
            print(f"  ✓ {name}: {n} shell lines updated")
        changed += 1

    verb = "would change" if a.check else "re-shelled"
    print(f"{verb}: {changed} · skipped: {skipped}")
    return 1 if skipped else 0


if __name__ == "__main__":
    sys.exit(main())
