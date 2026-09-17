from __future__ import annotations

import os
import platform

import psutil

from .hardware import HardwareProfile


def _gpu_vram_mb() -> int:
    try:
        import torch

        if not torch.cuda.is_available():
            return 0
        values = []
        for index in range(torch.cuda.device_count()):
            free_bytes, total_bytes = torch.cuda.mem_get_info(index)
            values.append(int(total_bytes / (1024 * 1024)))
        return max(values, default=0)
    except (ImportError, RuntimeError, AttributeError, OSError):
        return 0


def detect_hardware() -> HardwareProfile:
    """Detect safe local resource information with optional CUDA VRAM."""
    ram_mb = int(psutil.virtual_memory().total / (1024 * 1024))
    threads = os.cpu_count() or 1
    return HardwareProfile(
        gpu_vram_mb=_gpu_vram_mb(),
        ram_mb=ram_mb,
        cpu_threads=threads,
        architecture=platform.machine() or "unknown",
    )
