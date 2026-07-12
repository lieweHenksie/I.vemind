#!/usr/bin/env bash
# One-time setup for cyBorge's offline voice (Piper TTS). Dev tooling only —
# nothing here ships; it just turns essays into audio clips.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
VENV="$HERE/.venv"
MODELS="$HERE/models"
mkdir -p "$MODELS"

echo "→ venv + piper-tts (onnxruntime is the big download)…"
python3 -m venv "$VENV"
"$VENV/bin/pip" -q install --upgrade pip
"$VENV/bin/pip" -q install piper-tts

# Female voices. Default: Jenny (GB). Add more by name -> HuggingFace path.
declare -A VOICES=(
  [en_GB-jenny_dioco-medium]=en/en_GB/jenny_dioco/medium
  [en_US-amy-medium]=en/en_US/amy/medium
  [en_US-lessac-medium]=en/en_US/lessac/medium
)
BASE=https://huggingface.co/rhasspy/piper-voices/resolve/main
for VOICE in "${@:-en_GB-jenny_dioco-medium}"; do
  P="${VOICES[$VOICE]:-}"
  [ -n "$P" ] || { echo "unknown voice '$VOICE' — add its HF path to setup.sh"; continue; }
  for EXT in onnx onnx.json; do
    if [ ! -f "$MODELS/$VOICE.$EXT" ]; then
      echo "→ downloading $VOICE.$EXT…"
      curl -sL -o "$MODELS/$VOICE.$EXT" "$BASE/$P/$VOICE.$EXT"
    fi
  done
done

echo "✓ done.  render with:"
echo "  $VENV/bin/python $HERE/render.py <essay.md> <outdir> --model $MODELS/en_GB-jenny_dioco-medium.onnx"
