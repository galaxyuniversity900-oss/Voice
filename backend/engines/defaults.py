from .registry import EngineRegistry
from .unconfigured import UnconfiguredEngine


def build_registry() -> EngineRegistry:
    registry = EngineRegistry()
    registry.register("unconfigured", UnconfiguredEngine)
    return registry
