from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

@dataclass(frozen=True)
class SynthesisOptions:
    language: str = "ar"
    dialect: str = "ar-eg"
    voice: str | None = None
    speed: float = 1.0
    sample_rate: int = 24000

@dataclass(frozen=True)
class AudioResult:
    audio_path: Path
    sample_rate: int
    backend: str

class VoiceEngine(Protocol):
    name: str
    def available(self) -> bool: ...
    def synthesize(self, text: str, options: SynthesisOptions) -> AudioResult: ...
