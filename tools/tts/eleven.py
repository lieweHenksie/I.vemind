#!/usr/bin/env python3
"""cyBorge voice render via ElevenLabs — cloud, so ~zero local compute.

    python3 tools/tts/eleven.py mycelium/essays/essay-1.md id/agar-lab/audio/voice \
        --clone id/agar-lab/audio/voice/sample_me.m4a \
        --index id/agar-lab/index.html

Reads the API key from .env (`eleven_labs=...`). `--clone <sample>` uploads the sample
once and caches the resulting voice_id in tools/tts/.eleven_voice (reused after). Renders
each blank-line block of the essay to line-NN.wav, writes timing.md, and rewrites the
auto-managed `bars` array in index.html so the arrangement re-fits the new line lengths.

No pip deps — stdlib urllib for TTS, curl for the multipart clone upload.
"""
import argparse, json, re, math, os, sys, wave, subprocess, pathlib
import urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parents[2]      # repo root
ENV = ROOT / ".env"
VOICE_CACHE = pathlib.Path(__file__).resolve().parent / ".eleven_voice"
API = "https://api.elevenlabs.io/v1"
MODEL = os.environ.get("ELEVEN_MODEL", "eleven_v3")   # eleven_v3 = audio tags ([sigh],[sad]…); v2 = none
OUTPUT_FORMAT = "wav_24000"
# v3: lower stability = more expressive + more responsive to audio tags.
# ~0.0 "Creative" (max drama), 0.5 "Natural", 1.0 "Robust" (tags mostly ignored).
VOICE_SETTINGS = {"stability": 0.5, "similarity_boost": 0.75}


def read_env(key):
    if not ENV.exists():
        sys.exit(f"no .env at {ENV} — add a line: {key}=<your ElevenLabs key>")
    for line in ENV.read_text().splitlines():
        s = line.strip()
        if s.startswith(key + "="):
            v = s.split("=", 1)[1].strip().strip('"').strip("'")
            if not v:
                sys.exit(f"`{key}=` is empty in {ENV} — paste your ElevenLabs key after the =")
            return v
    sys.exit(f"`{key}=` not found in {ENV}")


def read_env_optional(key):
    if not ENV.exists():
        return None
    for line in ENV.read_text().splitlines():
        s = line.strip()
        if s.startswith(key + "="):
            return s.split("=", 1)[1].strip().strip('"').strip("'") or None
    return None


def blocks_from(md):
    md = re.sub(r'^---.*?---', '', md, count=1, flags=re.S)
    md = re.sub(r'<!--.*?-->', '', md, flags=re.S)
    out = []
    for chunk in re.split(r'\n\s*\n', md):
        lines = [l.strip() for l in chunk.splitlines() if l.strip() and not l.strip().startswith('#')]
        if lines:
            out.append(' '.join(lines))
    return out


def clone_voice(key, sample, name="cyBorge"):
    print(f"cloning a voice from {sample} …")
    r = subprocess.run(
        ["curl", "-s", "-X", "POST", f"{API}/voices/add",
         "-H", f"xi-api-key: {key}",
         "-F", f"name={name}",
         "-F", "remove_background_noise=true",
         "-F", f"files=@{sample}"],
        capture_output=True, text=True)
    try:
        vid = json.loads(r.stdout)["voice_id"]
    except Exception:
        sys.exit(f"clone failed:\n{r.stdout or r.stderr}")
    VOICE_CACHE.write_text(vid)
    print(f"  cloned -> voice_id {vid}  (cached in {VOICE_CACHE.name})")
    return vid


def tts(key, voice_id, text, out_path, prev=None, nxt=None):
    url = f"{API}/text-to-speech/{voice_id}?output_format={OUTPUT_FORMAT}"
    payload = {"text": text, "model_id": MODEL, "voice_settings": VOICE_SETTINGS}
    # Request stitching (previous/next text) keeps accent/prosody consistent — but the
    # v3 model rejects it, so only send it on other models (e.g. multilingual_v2).
    if not MODEL.startswith("eleven_v3"):
        if prev:
            payload["previous_text"] = prev
        if nxt:
            payload["next_text"] = nxt
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
        headers={"xi-api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            out_path.write_bytes(resp.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs error {e.code}: {e.read().decode(errors='replace')[:400]}")


def wav_dur(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def patch_bars(index_path, bars):
    """Rewrite the auto-managed bars array between markers in index.html."""
    if not index_path.exists():
        print(f"(no index at {index_path} — skipped bars patch)"); return
    txt = index_path.read_text()
    S, E = "// BARS-START", "// BARS-END"
    if S not in txt or E not in txt:
        print("(no BARS markers in index.html — skipped; add them to enable auto-fit)"); return
    block = f"{S}\nlet bars = {json.dumps(bars)}   // auto-generated per line length — do not hand-edit\n{E}"
    txt = re.sub(re.escape(S) + r".*?" + re.escape(E), block, txt, flags=re.S)
    index_path.write_text(txt)
    print(f"patched bars in {index_path.name}: {bars}")


def patch_voice_files(index_path, blocks):
    """Sync VOICE_FILES + VOICE_TEXTS in index.html to the current lines. The texts feed the
    page's typewriter (words appear as spoken); [tags] are performance notes — stripped."""
    n = len(blocks)
    if not index_path.exists():
        return
    txt = index_path.read_text()
    S, E = "// VOICE-FILES-START", "// VOICE-FILES-END"
    if S not in txt or E not in txt:
        print("(no VOICE-FILES markers in index.html — skipped)"); return
    files = ", ".join(f"'line-{i:02d}.wav'" for i in range(1, n + 1))
    texts = ", ".join(json.dumps(re.sub(r"\[[^\]]*\]", "", b).replace("\n", " ").strip(),
                                 ensure_ascii=False) for b in blocks)
    block = f"{S}\n    const VOICE_FILES = [{files}];\n    const VOICE_TEXTS = [{texts}];\n    {E}"
    # lambda replacement: texts hold escapes (\" …) that re.sub would misread as group refs
    txt = re.sub(re.escape(S) + r".*?" + re.escape(E), lambda m: block, txt, flags=re.S)
    index_path.write_text(txt)
    print(f"patched VOICE_FILES: {n} lines (+ texts)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("essay")
    ap.add_argument("outdir")
    ap.add_argument("--clone", help="audio sample to clone a voice from (one-time)")
    ap.add_argument("--voice-id", help="use this ElevenLabs voice_id directly")
    ap.add_argument("--index", help="index.html to auto-patch the bars array")
    ap.add_argument("--only", help="comma-separated 1-based line numbers to re-render; others reused from disk")
    ap.add_argument("--all", action="store_true", help="force re-render EVERY line (ignore change detection)")
    ap.add_argument("--bpm", type=int, default=120)
    a = ap.parse_args()

    key = read_env("eleven_labs")
    out = pathlib.Path(a.outdir); out.mkdir(parents=True, exist_ok=True)

    if a.voice_id:
        voice_id = a.voice_id
    elif a.clone:
        voice_id = clone_voice(key, a.clone)
    else:
        voice_id = read_env_optional("eleven_voice_id") \
            or (VOICE_CACHE.read_text().strip() if VOICE_CACHE.exists() else None)
        if not voice_id:
            sys.exit("no voice: add `eleven_voice_id=<id>` to .env (copy one from the "
                     "ElevenLabs site), or pass --voice-id <id> / --clone <sample>")

    # incremental: remember each line's text; only re-render the ones that changed.
    manifest_path = out / ".render-manifest.json"
    prev = []
    if manifest_path.exists():
        try:
            prev = json.loads(manifest_path.read_text()).get("lines", [])
        except Exception:
            prev = []

    blocks = blocks_from(pathlib.Path(a.essay).read_text())
    only = {int(x) for x in a.only.split(",")} if a.only else None
    print(f"{len(blocks)} blocks · model {MODEL} · voice {voice_id}"
          + (f" · only {sorted(only)}" if only else "") + (" · --all" if a.all else ""))
    bar_s = 240 / a.bpm
    bars, durs = [], []
    for i, b in enumerate(blocks, 1):
        p = out / f"line-{i:02d}.wav"
        is_new = i - 1 >= len(prev)
        changed = is_new or prev[i - 1] != b or not p.exists()
        if only is not None:
            do = i in only
        elif a.all:
            do = True
        else:
            do = changed                      # default: only edited / new / missing lines
        if do:
            prev_ctx = blocks[i - 2] if i >= 2 else None
            nxt_ctx = blocks[i] if i < len(blocks) else None
            tts(key, voice_id, b, p, prev_ctx, nxt_ctx)
            note = "NEW" if is_new else ("changed" if changed else "forced")
        else:
            note = "unchanged"
        d = wav_dur(p); durs.append(d)
        bars.append(math.ceil(d / bar_s) + 1)
        print(f"  [{i:02d}] {d:5.2f}s  {bars[-1]}b  {(b[:34]):34}  ({note})")

    # remember what we rendered from, so the next run only touches edited lines
    manifest_path.write_text(json.dumps({"lines": blocks}))

    with open(out / "timing.md", "w") as f:
        f.write(f"# essay timing @ {a.bpm} BPM (voice {voice_id})\n\n| i | secs | bars | text |\n|---|---|---|---|\n")
        for i, (b, d, n) in enumerate(zip(blocks, durs, bars)):
            f.write(f"| {i} | {d:.2f} | {n} | {b[:44]} |\n")

    if a.index:
        patch_bars(pathlib.Path(a.index), bars)
        patch_voice_files(pathlib.Path(a.index), blocks)
    print("done. bars:", bars)


if __name__ == "__main__":
    main()
