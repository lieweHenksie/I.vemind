#!/usr/bin/env python3
"""One command to build a song: voice render + shape compile.

    python3 tools/song/compose.py <name> [--only N] [--all]

Reads `id/<name>/song.json` for the essay path (its "essay" field; falls back to
`mycelium/essays/<name>.md`), then runs the voice render (tools/tts/eleven.py) and the
shape compiler (tools/song/build.py). Both are incremental/deterministic, so this only
touches what actually changed.
"""
import argparse, json, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name", help="piece name under id/ (e.g. agar-lab)")
    ap.add_argument("--only", help="passed to the voice render: re-render only these 1-based lines")
    ap.add_argument("--all", action="store_true", help="passed to the voice render: force every line")
    a = ap.parse_args()

    piece = ROOT / "id" / a.name
    spec = piece / "song.json"
    index = piece / "index.html"
    voice = piece / "audio" / "voice"
    if not spec.exists():
        sys.exit(f"no song.json at {spec} — run /cyborge-score first")
    if not index.exists():
        sys.exit(f"no index.html at {index} — copy cookbook/strudel/template.html there first")

    data = json.loads(spec.read_text())
    essay = data.get("essay") or f"mycelium/essays/{a.name}.md"
    essay = pathlib.Path(essay)
    if not essay.is_absolute():
        essay = ROOT / essay
    if not essay.exists():
        sys.exit(f'essay not found: {essay} — set "essay" in {spec.name}')

    # Size the bars array at the SONG's tempo (a bar = 240/bpm seconds), so a voice line's slot
    # fits its clip at any BPM. Without this, a slow song leaves huge gaps and a fast one clips.
    bpm = data.get("bpm", 120)

    py = sys.executable
    print(f"● voice  ({essay}) @ {bpm} BPM")
    cmd = [py, str(ROOT / "tools/tts/eleven.py"), str(essay), str(voice),
           "--index", str(index), "--bpm", str(bpm)]
    if a.only:
        cmd += ["--only", a.only]
    if a.all:
        cmd += ["--all"]
    subprocess.run(cmd, check=True)

    print(f"● shape  ({spec})")
    subprocess.run([py, str(ROOT / "tools/song/build.py"), str(spec), "--index", str(index)], check=True)

    print(f"✓ composed id/{a.name} — reload http://localhost:8000/id/{a.name}/")


if __name__ == "__main__":
    main()
