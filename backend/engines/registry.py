from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .base import VoiceEngine

@dataclass
class EngineRegistry:
    _factories: dict[str, Callable[[], VoiceEngine]]

    def __init__(self) -> None:
        self._factories = {}

    def register(self, name: str, factory: Callable[[], VoiceEngine]) -> None:
        self._factories[name] = factory

    def names(self) -> list[str]:
        return sorted(self._factories)

    def available(self) -> list[str]:
        result: list[str] = []
        for name, factory in self._factories.items():
            try:
                if factory().available():
                    result.append(name)
            except Exception:
                continue
        return sorted(result)

    def get(self, name: str) -> VoiceEngine:
        return self._factories[name]()
