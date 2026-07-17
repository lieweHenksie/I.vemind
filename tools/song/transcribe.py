#!/usr/bin/env python3
"""Pull a clean, timestamped transcript from a YouTube video (auto-captions).

    python3 tools/song/transcribe.py <url> [-o transcript.md] [--lang en]

Wraps yt-dlp: fetches the auto-generated captions as json3, flattens the word
events into readable timestamped paragraphs, and prepends the video metadata.
This is the ear of /cyborge-research — the transcript is raw material for a
study, never a thing we publish. Auto-captions GARBLE code terms ("el pea eff"
for lpf, "jucks rev" for jux(rev)); the study step must verify every function
name against the Strudel docs before banking it.
"""
import argparse, datetime, json, pathlib, subprocess, sys, tempfile

PARA_GAP_MS = 4000     # silence longer than this starts a new paragraph
PARA_MAX_CHARS = 400   # wrap paragraphs so the transcript stays scannable


def fetch(url, lang, tmp):
    out = pathlib.Path(tmp) / "cap"
    cmd = ["yt-dlp", "--skip-download", "--no-simulate", "--no-playlist",
           "--write-auto-subs", "--write-subs",
           "--sub-langs", f"{lang},{lang}.*,{lang}-orig",
           "--sub-format", "json3", "-o", str(out),
           "--print", "%(title)s", "--print", "%(uploader)s",
           "--print", "%(webpage_url)s", "--print", "%(duration)s", url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"yt-dlp failed:\n{r.stderr.strip()}")
    title, uploader, page_url, duration = r.stdout.strip().split("\n")[:4]
    subs = sorted(pathlib.Path(tmp).glob("cap.*.json3"))
    if not subs:
        sys.exit(f"no '{lang}' captions found — check `yt-dlp --list-subs {url}`")
    return {"title": title, "uploader": uploader, "url": page_url,
            "duration": int(float(duration))}, json.loads(subs[0].read_text())


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
    a = ap.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        meta, cap = fetch(a.url, a.lang, tmp)
    lines = [f"# {meta['title']}",
             f"- artist: {meta['uploader']}",
             f"- source: {meta['url']}",
             f"- duration: {stamp(meta['duration'] * 1000)}",
             f"- pulled: {datetime.date.today().isoformat()}", ""]
    lines += [f"[{stamp(t)}] {text}" for t, text in paragraphs(cap)]
    text = "\n".join(lines) + "\n"
    if a.out:
        pathlib.Path(a.out).write_text(text)
        print(f"wrote {a.out} ({len(text)} chars)")
    else:
        print(text)


if __name__ == "__main__":
    main()
