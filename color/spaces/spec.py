"""Parameterized colour-space specifications."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .node import ColorSpaceNode
from .rgb.colourspace import RGBColorSpace


@dataclass(frozen=True, init=False)
class SpaceSpec:
    """A colour-space endpoint with conversion parameters attached.

    Use ``SpaceSpec`` when a route needs endpoint-specific parameters such as
    ``whitepoint_XYZ`` for Lab/Luv, ``XYZ_w``/``L_A``/``Y_b`` for CAM spaces, or
    RGB transfer flags. Parameters are immutable after construction and are
    merged into the relevant endpoint conversion only.

    Parameters
    ----------
    name
        Colour-space name, registered node, or RGB colour-space object.
    **parameters
        Endpoint-specific conversion parameters.

    Returns
    -------
    SpaceSpec
        Immutable colour-space endpoint specification.

    Notes
    -----
    ``SpaceSpec`` does not imply chromatic adaptation. It only attaches
    parameters to one source or target endpoint for ``convert_color``.

    Examples
    --------
    >>> from color.constants import D50_XYZ
    >>> spec = SpaceSpec("Lab", whitepoint_XYZ=D50_XYZ)
    >>> spec.name
    'Lab'
    """

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
