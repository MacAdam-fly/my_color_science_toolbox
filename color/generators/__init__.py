"""Formula and procedural data generators."""

from __future__ import annotations

from . import illuminants  # noqa: F401
from ._registry import (
    GeneratorEntry,
    clear_cache,
    describe,
    generate,
    list_categories,
    list_generators,
    register,
)
from .illuminants import (
    blackbody_spd,
    daylight_spd,
    generate_illuminant,
    list_illuminant_generators,
)

__all__ = [
    "GeneratorEntry",
    "generate",
    "describe",
    "clear_cache",
    "list_categories",
    "list_generators",
    "register",
    "blackbody_spd",
    "daylight_spd",
    "generate_illuminant",
    "list_illuminant_generators",
]
