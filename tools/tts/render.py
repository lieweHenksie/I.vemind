#!/usr/bin/env python
"""cyBorge voice render — offline Piper TTS.

essay markdown -> one clip per line + timing.md + a paced preview.

    tools/tts/.venv/bin/python tools/tts/render.py \
        mycelium/essays/essay-1.md  id/<piece>/audio/voice \
        --model tools/tts/models/en_GB-jenny_dioco-medium.onnx

Each blank-line block in the essay becomes one spoken clip (line-01.wav …).
`#` lines are notes, not spoken. timing.md gives each line's length in bars and
the ready-to-paste `vo(s("voice:i"), n)` counts for the Strudel arrangement.
"""
import argparse, re, math, pathlib, wave, subprocess, tempfile
from piper import PiperVoice
try:
    from piper import SynthesisConfig
except ImportError:
    from piper.config import SynthesisConfig
import piper.phonemize_espeak as pe


def espeak_dir():
    """piper's espeak bridge falls over when handed a path ending in
    'espeak-ng-data', OR a symlink sitting right beside the real data dir — both
    make it strip back to a stale build path. A symlink under a safe name in a
    NEUTRAL (temp) dir is what actually works. This is the whole reason renders run."""
    real = pe.ESPEAK_DATA_DIR
    link = pathlib.Path(tempfile.gettempdir()) / "cyb-espeak-data"
    try:
        if link.is_symlink() and link.resolve() != real.resolve():
            link.unlink()
        if not link.exists():
            link.symlink_to(real, target_is_directory=True)
    except OSError:
        return str(real)
    return str(link)


def blocks_from(md: str):
    md = re.sub(r'^---.*?---', '', md, count=1, flags=re.S)   # frontmatter
    md = re.sub(r'<!--.*?-->', '', md, flags=re.S)            # html comments
    out = []
    for chunk in re.split(r'\n\s*\n', md):
        lines = [l.strip() for l in chunk.splitlines()
                 if l.strip() and not l.strip().startswith('#')]
        if lines:
            out.append(' '.join(lines))
    return out


def wav_dur(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("essay")
    ap.add_argument("outdir")
    ap.add_argument("--model", required=True, help="path to a piper .onnx voice model")
    ap.add_argument("--length-scale", type=float, default=1.15, help=">1 = slower/more deliberate")
    ap.add_argument("--bpm", type=int, default=120, help="tempo used for the bar counts in timing.md")
    a = ap.parse_args()

    out = pathlib.Path(a.outdir); out.mkdir(parents=True, exist_ok=True)
    blocks = blocks_from(pathlib.Path(a.essay).read_text())
    print(f"{len(blocks)} blocks")

    voice = PiperVoice.load(a.model, espeak_data_dir=espeak_dir())
    syn = SynthesisConfig(length_scale=a.length_scale)

    clean, durs = [], []
    for i, b in enumerate(blocks, 1):
        p = out / f"line-{i:02d}.wav"
        with wave.open(str(p), "wb") as wf:
            voice.synthesize_wav(b, wf, syn_config=syn)
        d = wav_dur(p); clean.append(str(p)); durs.append(d)
        print(f"  [{i:02d}] {d:5.2f}s  {b[:46]}")

    # paced preview (real gaps between lines) so pacing can be judged out of context
    sil = out / "_gap.wav"
    subprocess.run(["sox", "-n", "-r", "22050", "-c", "1", "-b", "16", "-e", "signed-integer",
                    str(sil), "trim", "0", "0.9"], check=True)
    seq = []
    for f in clean:
        seq += [f, str(sil)]
    subprocess.run(["sox", *seq[:-1], str(out / "preview.wav")], check=True)
    sil.unlink(missing_ok=True)

    # timing manifest + the arrangement bar counts
    bar_s = 240 / a.bpm
    allots = []
    with open(out / "timing.md", "w") as f:
        f.write(f"# line timing @ {a.bpm} BPM  (1 bar = {bar_s:.2f}s, 1 beat = {60/a.bpm:.2f}s)\n\n")
        f.write("| i | secs | bars | vo(i,n) | text |\n|---|---|---|---|---|\n")
        for i, (b, d) in enumerate(zip(blocks, durs)):
            bars = d / bar_s
            n = math.ceil(bars) + 1
            allots.append(n)
            f.write(f"| {i} | {d:.2f} | {bars:.2f} | {n} | {b[:42]} |\n")

    print("\narrangement rows to paste:")
    for i, n in enumerate(allots):
        print(f'  vo(s("voice:{i}"), {n})')


if __name__ == "__main__":
    main()
