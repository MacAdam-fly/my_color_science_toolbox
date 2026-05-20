"""Colour-space conversion graph node definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


ConversionFunction = Callable[..., np.ndarray]


@dataclass(frozen=True)
class ColorSpaceNode:
    """A node in the colour-space conversion graph."""

    name: str
    aliases: tuple[str, ...] = ()
    parent: str | None = None
    to_XYZ: ConversionFunction | None = None
    from_XYZ: ConversionFunction | None = None
    to_parent: ConversionFunction | None = None
    from_parent: ConversionFunction | None = None
    family: str | None = None
    is_rgb_family: bool = False


__all__ = [
    "ColorSpaceNode",
    "ConversionFunction",
]
