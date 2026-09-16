from __future__ import annotations

import os
from pathlib import Path

MODEL_ID = os.getenv("VOICE_KEMETONE_MODEL", "Rabe3/kemetone")
CACHE_DIR = Path(os.getenv("VOICE_MODEL_CACHE", "~/.cache/voice/models")).expanduser()
PATTERNS = [
    "config.json",
    "kemetone.pth",
    "voices/kemetone.pt",
    "kemetone/**",
]


def main() -> None:
    from huggingface_hub import snapshot_download

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = snapshot_download(
        repo_id=MODEL_ID,
        cache_dir=str(CACHE_DIR),
        allow_patterns=PATTERNS,
    )
    print(f"KemeTone assets ready: {path}")


if __name__ == "__main__":
    main()
