#!/usr/bin/env bash
set -euo pipefail

python -m pip install -e '.[tts]'

if command -v apt-get >/dev/null 2>&1; then
  if command -v sudo >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y espeak-ng
  elif [ "$(id -u)" -eq 0 ]; then
    apt-get update
    apt-get install -y espeak-ng
  else
    echo 'espeak-ng is required. Install it with your system package manager.' >&2
    exit 1
  fi
fi

python scripts/download_models.py
printf '%s\n' 'TTS runtime and KemeTone model assets are ready.'
