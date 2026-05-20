"""Parameterized colour-space specifications."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .node import ColorSpaceNode
from .rgb.colourspace import RGBColorSpace


@dataclass(frozen=True, init=False)
class SpaceSpec:
    """A colour-space instance with parameters attached to it."""

    name: str | ColorSpaceNode | RGBColorSpace
    parameters: Mapping[str, object]

    def __init__(
        self,
        name: str | ColorSpaceNode | RGBColorSpace,
        **parameters: object,
    ) -> None:
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "parameters", MappingProxyType(dict(parameters)))


def as_space_spec(
    value: str | ColorSpaceNode | RGBColorSpace | SpaceSpec,
) -> SpaceSpec:
    """Return *value* as a :class:`SpaceSpec`."""
    if isinstance(value, SpaceSpec):
        return value
    return SpaceSpec(value)


__all__ = [
    "SpaceSpec",
    "as_space_spec",
]
