#!/usr/bin/env python3
"""Pull a cut of audio from a YouTube link into a song's crate, ready for Strudel.

    python3 tools/song/sample.py <song> <name> <url> <start> <end>
    python3 tools/song/sample.py <song> <name> <url> <start> --bars 2 --bpm 174

Wraps yt-dlp + ffmpeg: downloads the full audio once (cached in .sample-cache/ by
video id, gitignored), cuts [start, end) into id/<song>/audio/samples/<name>.wav,
and registers it in the `_samples` map of id/<song>/palette.json. The page's
prebake loads everything in `_samples`; an INSTRUMENT in the palette then plays it
(s("<name>"), chop, slice, loopAt...) — sample.py only stocks the crate, it never
authors the instrument (that's /cyborge-score's call).

Times are seconds or M:SS(.mmm) or H:MM:SS. --bars N --bpm X cuts a beat-accurate
loop (duration = N bars at the SOURCE's bpm) instead of using <end>. A 5 ms fade
guards both edges against clicks (--no-fade for raw cuts). --mono folds to one
channel (voice-ish material).
"""
import argparse, json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = pathlib.Path(__file__).resolve().parent / ".sample-cache"
FADE = 0.005


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"{cmd[0]} failed:\n{r.stderr.strip()}")
    return r.stdout


def secs(t):
    parts = t.split(":")
    if len(parts) > 3:
        sys.exit(f"bad time {t!r} — use seconds, M:SS or H:MM:SS")
    try:
        return sum(float(p) * 60 ** i for i, p in enumerate(reversed(parts)))
    except ValueError:
        sys.exit(f"bad time {t!r} — use seconds, M:SS or H:MM:SS")


def fetch(url):
    CACHE.mkdir(exist_ok=True)
    vid, title = run(["yt-dlp", "--no-playlist", "--print", "%(id)s",
                      "--print", "%(title)s", url]).strip().split("\n")[:2]
    wav = CACHE / f"{vid}.wav"
    if not wav.exists():
        print(f"downloading audio: {title}")
        run(["yt-dlp", "--no-playlist", "-x", "--audio-format", "wav",
             "-o", str(CACHE / f"{vid}.%(ext)s"), url])
    return wav, title


def cut(src, dst, start, dur, mono, fade):
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", str(src), "-ar", "44100"]
    if mono:
        cmd += ["-ac", "1"]
    if fade:
        cmd += ["-af", f"afade=t=in:d={FADE},afade=t=out:st={max(dur - FADE, 0):.3f}:d={FADE}"]
    run(cmd + [str(dst)])


def register(song_dir, name, title, url):
    pal_path = song_dir / "palette.json"
    pal = json.loads(pal_path.read_text()) if pal_path.exists() else {
        "_comment": "This song's SOUND — instruments authored by /cyborge-score override the cookbook default."}
    pal.setdefault("_samples", {})[name] = f"audio/samples/{name}.wav"
    pal_path.write_text(json.dumps(pal, indent=2) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("song", help="song name — the crate is id/<song>/audio/samples/")
    ap.add_argument("name", help="sample name — how Strudel will address it: s(\"<name>\")")
    ap.add_argument("url")
    ap.add_argument("start")
    ap.add_argument("end", nargs="?", help="cut end (omit with --bars/--bpm)")
    ap.add_argument("--bars", type=float, help="cut this many bars at the SOURCE bpm")
    ap.add_argument("--bpm", type=float, help="the SOURCE's bpm (with --bars)")
    ap.add_argument("--mono", action="store_true")
    ap.add_argument("--no-fade", action="store_true")
    a = ap.parse_args()

    start = secs(a.start)
    if a.bars:
        if not a.bpm:
            sys.exit("--bars needs --bpm (the SOURCE's tempo, not the song's)")
        dur = a.bars * 240 / a.bpm
    elif a.end:
        dur = secs(a.end) - start
        if dur <= 0:
            sys.exit(f"end {a.end} is not after start {a.start}")
    else:
        sys.exit("give an <end> time, or --bars N --bpm X for a beat-accurate loop")

    song_dir = ROOT / "id" / a.song
    crate = song_dir / "audio" / "samples"
    crate.mkdir(parents=True, exist_ok=True)
    dst = crate / f"{a.name}.wav"

    src, title = fetch(a.url)
    cut(src, dst, start, dur, a.mono, not a.no_fade)
    register(song_dir, a.name, title, a.url)

    # bars at the SONG's tempo (one bar = 240/bpm seconds — 4 beats), for the arrange math
    line = f"cut {dur:.2f}s from \"{title}\" -> {dst.relative_to(ROOT)}  (s(\"{a.name}\"))"
    spec = song_dir / "song.json"
    if spec.exists():
        bpm = json.loads(spec.read_text()).get("bpm", 120)
        line += f"\n  at {bpm} bpm: 1 bar = {240 / bpm:.2f}s, this cut = {dur * bpm / 240:.2f} bars"
    print(line)


if __name__ == "__main__":
    main()
