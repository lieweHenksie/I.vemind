#!/usr/bin/env python3
"""Pull a clean, timestamped transcript from a YouTube video (auto-captions).

    python3 tools/song/transcribe.py <url> [-o transcript.md] [--lang en] [--frames N]

Wraps yt-dlp: fetches the auto-generated captions as json3, flattens the word
events into readable timestamped paragraphs, and prepends the video metadata.
This is the ear of /cyborge-research — the transcript is raw material for a
study, never a thing we publish. Auto-captions GARBLE code terms ("el pea eff"
for lpf, "jucks rev" for jux(rev)); the study step must verify every function
name against the Strudel docs before banking it.

--frames N is the EYE: N evenly-spaced screenshots into the gitignored
.sample-cache/frames/<id>/ (the video itself caches beside sample.py's).
Strudel videos show the CODE on screen — reading a frame beats un-garbling a
caption, and it works on videos that have no captions at all.
"""
import argparse, datetime, json, pathlib, subprocess, sys, tempfile

PARA_GAP_MS = 4000     # silence longer than this starts a new paragraph
PARA_MAX_CHARS = 400   # wrap paragraphs so the transcript stays scannable
CACHE = pathlib.Path(__file__).resolve().parent / ".sample-cache"   # shared with sample.py


def fetch(url, lang, tmp, need_captions=True):
    out = pathlib.Path(tmp) / "cap"
    cmd = ["yt-dlp", "--skip-download", "--no-simulate", "--no-playlist",
           "--write-auto-subs", "--write-subs",
           "--sub-langs", f"{lang},{lang}.*,{lang}-orig",
           "--sub-format", "json3", "-o", str(out),
           "--print", "%(id)s", "--print", "%(title)s", "--print", "%(uploader)s",
           "--print", "%(webpage_url)s", "--print", "%(duration)s", url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"yt-dlp failed:\n{r.stderr.strip()}")
    vid_id, title, uploader, page_url, duration = r.stdout.strip().split("\n")[:5]
    subs = sorted(pathlib.Path(tmp).glob("cap.*.json3"))
    if not subs and need_captions:
        sys.exit(f"no '{lang}' captions found — check `yt-dlp --list-subs {url}`"
                 " (with --frames N you can still study a caption-less video)")
    cap = json.loads(subs[0].read_text()) if subs else None
    return {"id": vid_id, "title": title, "uploader": uploader, "url": page_url,
            "duration": int(float(duration))}, cap


def grab_frames(url, meta, n):
    # the EYE: n evenly-spaced screenshots (edges skipped — intros/outros rarely show code).
    # The full video caches once by id beside sample.py's downloads; frames land in
    # frames/<id>/f-M-SS.png so a study can cite them against transcript timestamps.
    CACHE.mkdir(exist_ok=True)
    mp4 = CACHE / f"{meta['id']}.mp4"
    if not mp4.exists():
        print("downloading video…", file=sys.stderr)
        r = subprocess.run(["yt-dlp", "-q", "--no-playlist", "-f", "b[ext=mp4]/best",
                            "-o", str(CACHE / f"{meta['id']}.%(ext)s"), url],
                           capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"yt-dlp video failed:\n{r.stderr.strip()}")
    fdir = CACHE / "frames" / meta["id"]
    fdir.mkdir(parents=True, exist_ok=True)
    dur = meta["duration"]
    paths = []
    for i in range(1, n + 1):
        t = dur * (0.04 + 0.92 * (i - 1) / max(n - 1, 1))
        dst = fdir / f"f-{int(t) // 60}-{int(t) % 60:02d}.png"
        if not dst.exists():
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}",
                            "-i", str(mp4), "-frames:v", "1", "-vf", "scale=1280:-2",
                            str(dst)], check=True)
        paths.append(dst)
    return paths


def paragraphs(cap):
    paras, cur, cur_t, last_end = [], [], 0, 0
    for ev in cap.get("events", []):
        text = "".join(seg.get("utf8", "") for seg in ev.get("segs", [])).strip()
        if not text:
            continue
        t = ev.get("tStartMs", 0)
        if cur and (t - last_end > PARA_GAP_MS or sum(map(len, cur)) > PARA_MAX_CHARS):
            paras.append((cur_t, " ".join(cur)))
            cur, cur_t = [], t
        if not cur:
            cur_t = t
        cur.append(text)
        last_end = t + ev.get("dDurationMs", 0)
    if cur:
        paras.append((cur_t, " ".join(cur)))
    return paras


def stamp(ms):
    s = ms // 1000
    return f"{s // 60}:{s % 60:02d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("url")
    ap.add_argument("-o", "--out", help="write transcript here (default: stdout)")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--frames", type=int, metavar="N",
                    help="also grab N evenly-spaced screenshots (the eye — read the code on screen)")
    a = ap.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        meta, cap = fetch(a.url, a.lang, tmp, need_captions=not a.frames)
    lines = [f"# {meta['title']}",
             f"- artist: {meta['uploader']}",
             f"- source: {meta['url']}",
             f"- duration: {stamp(meta['duration'] * 1000)}",
             f"- pulled: {datetime.date.today().isoformat()}", ""]
    if cap:
        lines += [f"[{stamp(t)}] {text}" for t, text in paragraphs(cap)]
    else:
        lines += ["(no captions — frames only)"]
    if a.frames:
        lines += ["", "## frames"] + [f"- {p}" for p in grab_frames(a.url, meta, a.frames)]
    text = "\n".join(lines) + "\n"
    if a.out:
        pathlib.Path(a.out).write_text(text)
        print(f"wrote {a.out} ({len(text)} chars)")
    else:
        print(text)


if __name__ == "__main__":
    main()
