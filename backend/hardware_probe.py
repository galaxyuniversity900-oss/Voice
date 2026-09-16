from __future__ import annotations

import os
import platform

import psutil

from .hardware import HardwareProfile


def detect_hardware() -> HardwareProfile:
    """Detect safe local resource information without requiring a GPU package."""
    ram_mb = int(psutil.virtual_memory().total / (1024 * 1024))
    threads = os.cpu_count() or 1
    return HardwareProfile(
        gpu_vram_mb=0,
        ram_mb=ram_mb,
        cpu_threads=threads,
        architecture=platform.machine() or "unknown",
    )
