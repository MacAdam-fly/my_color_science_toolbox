"""Registry for color space conversion helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Tuple


@dataclass(frozen=True)
class SpaceDefinition:
    name: str
    to_xyz: Callable
    from_xyz: Callable
    aliases: Tuple[str, ...] = ()
    required_context: Tuple[str, ...] = ()


_SPACE_REGISTRY: Dict[str, SpaceDefinition] = {}


def register_space(space: SpaceDefinition) -> None:
    names = (space.name,) + space.aliases
    for name in names:
        _SPACE_REGISTRY[name] = space


def get_space(name: str) -> SpaceDefinition:
    return _SPACE_REGISTRY[name]


def list_spaces() -> Tuple[str, ...]:
    return tuple(sorted({space.name for space in _SPACE_REGISTRY.values()}))
