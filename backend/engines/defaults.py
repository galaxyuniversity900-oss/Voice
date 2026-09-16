from .kemetone import KemeToneEngine
from .registry import EngineRegistry
from .unconfigured import UnconfiguredEngine


def build_registry() -> EngineRegistry:
    registry = EngineRegistry()
    registry.register("kemetone", KemeToneEngine)
    # Map all local resource tiers to the same lightweight Egyptian runtime.
    registry.register("cpu", KemeToneEngine)
    registry.register("gguf", KemeToneEngine)
    registry.register("local", KemeToneEngine)
    registry.register("unconfigured", UnconfiguredEngine)
    return registry
