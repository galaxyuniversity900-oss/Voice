from __future__ import annotations

from dataclasses import dataclass

from ..hardware import HardwareProfile, select_engine
from .base import VoiceEngine
from .registry import EngineRegistry

@dataclass(frozen=True)
class RoutedEngine:
    target: str
    engine: VoiceEngine


def route_engine(registry: EngineRegistry, hardware: HardwareProfile, remote_available: bool = True) -> RoutedEngine:
    target = select_engine(hardware, remote_available)
    if target.backend in registry.names():
        return RoutedEngine(target.backend, registry.get(target.backend))
    return RoutedEngine("unconfigured", registry.get("unconfigured"))
