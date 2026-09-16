from __future__ import annotations

import importlib
import os
import sys
import threading
from pathlib import Path

from .base import AudioResult, SynthesisOptions

MODEL_ID = os.getenv("VOICE_KEMETONE_MODEL", "Rabe3/kemetone")
CACHE_DIR = Path(os.getenv("VOICE_MODEL_CACHE", "~/.cache/voice/models")).expanduser()
SAMPLE_RATE = 24000


class KemeToneEngine:
    """Lazy, online-downloaded Egyptian Arabic KemeTone runtime."""

    name = "kemetone"
    _lock = threading.Lock()
    _model = None
    _voice = None
    _g2p = None
    _device = None
    _model_dir: Path | None = None

    def available(self) -> bool:
        try:
            importlib.import_module("torch")
            importlib.import_module("kokoro")
            importlib.import_module("soundfile")
            importlib.import_module("huggingface_hub")
            return True
        except ImportError:
            return False

    def _load(self) -> None:
        if self._model is not None:
            return
        with self._lock:
            if self._model is not None:
                return

            import torch
            from huggingface_hub import snapshot_download
            from kokoro import KModel

            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            model_dir = Path(
                snapshot_download(
                    repo_id=MODEL_ID,
                    cache_dir=str(CACHE_DIR),
                    allow_patterns=[
                        "config.json",
                        "kemetone.pth",
                        "voices/kemetone.pt",
                        "kemetone/**",
                    ],
                )
            )
            self._model_dir = model_dir
            sys.path.insert(0, str(model_dir))
            from kemetone import EgyptianG2P

            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = KModel(
                repo_id=MODEL_ID,
                config=str(model_dir / "config.json"),
                model=str(model_dir / "kemetone.pth"),
            ).to(device).eval()
            voice = torch.load(model_dir / "voices" / "kemetone.pt", map_location=device)

            self._device = device
            self._model = model
            self._voice = voice
            self._g2p = EgyptianG2P()

    def synthesize(self, text: str, options: SynthesisOptions) -> AudioResult:
        if options.dialect.lower() not in {"ar-eg", "egyptian"}:
            raise ValueError("KemeTone supports Egyptian Arabic (ar-EG) only")
        if options.speed != 1.0:
            raise ValueError("KemeTone currently supports speed=1.0")

        self._load()
        import soundfile as sf
        import torch

        ipa = self._g2p(text)
        if not ipa:
            raise ValueError("Text produced no phonemes")

        with torch.no_grad():
            audio = self._model(ipa, self._voice[len(ipa) - 1])

        output_dir = Path(os.getenv("VOICE_OUTPUT_DIR", "./outputs")).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "voice.wav"
        tmp_path = output_dir / "voice.tmp.wav"
        sf.write(tmp_path, audio.detach().cpu().numpy(), SAMPLE_RATE, format="WAV")
        os.replace(tmp_path, output_path)
        return AudioResult(output_path, SAMPLE_RATE, self.name)
