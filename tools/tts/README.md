# tools/tts — cyBorge's voice (offline Piper TTS)

Turns an essay into one audio clip per line, for laying under Strudel music.
**Dev tooling only** — nothing here ships. The site plays the rendered `.wav`s; it
never calls a TTS service.

## Setup (once)

```bash
tools/tts/setup.sh                       # venv + piper-tts + Jenny (GB female)
tools/tts/setup.sh en_US-amy-medium      # …or add another voice
```

Creates `tools/tts/.venv` and `tools/tts/models/`. Both are large and gitignored.

## Render

```bash
tools/tts/.venv/bin/python tools/tts/render.py \
    mycelium/essays/essay-1.md  id/agar-lab/audio/voice \
    --model tools/tts/models/en_GB-jenny_dioco-medium.onnx
```

Writes `line-01.wav …`, `preview.wav`, and `timing.md` (each line's length in bars
+ the `vo(s("voice:i"), n)` rows to paste into the Strudel arrangement).

- **Words** live in the essay markdown — blank-line blocks = one clip each; `#` lines aren't spoken.
- **Length/pacing** — `--length-scale 1.15` (bigger = slower). `--bpm` sets the bar maths in `timing.md`.
- After re-rendering, the page auto-loads fresh clips (it cache-busts the URLs).

## The one gotcha (handled)

`piper-tts` crashes if its espeak data path ends in `espeak-ng-data`. `render.py`
symlinks the data under a safe name and passes that — don't remove it.
