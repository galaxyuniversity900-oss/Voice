from dataclasses import dataclass
from typing import Literal

BackendKind = Literal["local", "gguf", "cpu", "remote"]

@dataclass(frozen=True)
class HardwareProfile:
    gpu_vram_mb: int = 0
    ram_mb: int = 0
    cpu_threads: int = 1
    architecture: str = "unknown"

@dataclass(frozen=True)
class EngineTarget:
    backend: BackendKind
    reason: str


def select_engine(hw: HardwareProfile, remote_available: bool = True) -> EngineTarget:
    """Select the lightest viable backend; never require a high-end GPU."""
    if hw.gpu_vram_mb >= 6000:
        return EngineTarget("local", "GPU meets full-model target")
    if hw.gpu_vram_mb >= 1000 or hw.ram_mb >= 4096:
        return EngineTarget("gguf", "quantized backend fits lower-memory hardware")
    if hw.ram_mb >= 2048:
        return EngineTarget("cpu", "CPU-safe low-memory path")
    if remote_available:
        return EngineTarget("remote", "local resources are below safe generation floor")
    return EngineTarget("cpu", "remote unavailable; use constrained local path")
