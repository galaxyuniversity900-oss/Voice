from __future__ import annotations

from .base import AudioResult, SynthesisOptions

class UnconfiguredEngine:
    """Explicit adapter until a licensed local TTS runtime/model is configured."""
    name = "unconfigured"

    def available(self) -> bool:
        return False

    def synthesize(self, text: str, options: SynthesisOptions) -> AudioResult:
        raise RuntimeError("No TTS engine is configured. Install/configure a supported backend and model.")
