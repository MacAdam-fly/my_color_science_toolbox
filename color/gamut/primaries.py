"""Display primary definitions for gamut computations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from color.spaces.rgb import RGBColorSpace, get_RGB_colourspace


def _as_primaries_XYZ(value: Sequence[Sequence[float]] | np.ndarray) -> np.ndarray:
    """Return display primaries as a read-only ``(n, 3)`` XYZ array."""
    primaries = np.array(value, dtype=np.float64, copy=True)
    if primaries.ndim != 2 or primaries.shape[1] != 3:
        raise ValueError("primaries_XYZ must have shape (n, 3)")
    if primaries.shape[0] < 3:
        raise ValueError("primaries_XYZ must contain at least three primaries")
    if not np.all(np.isfinite(primaries)):
        raise ValueError("primaries_XYZ must be finite")
    if np.linalg.matrix_rank(primaries) < 3:
        raise ValueError("primaries_XYZ must span a three-dimensional volume")
    primaries.setflags(write=False)
    return primaries


def _as_whitepoint_XYZ(value: Sequence[float] | np.ndarray) -> np.ndarray:
    """Return a read-only display whitepoint XYZ triplet."""
    whitepoint = np.array(value, dtype=np.float64, copy=True)
    if whitepoint.shape != (3,):
        raise ValueError("whitepoint_XYZ must have shape (3,)")
    if not np.all(np.isfinite(whitepoint)):
        raise ValueError("whitepoint_XYZ must be finite")
    if np.any(whitepoint <= 0):
        raise ValueError("whitepoint_XYZ values must be positive")
    whitepoint.setflags(write=False)
    return whitepoint


@dataclass(frozen=True)
class DisplayPrimaries:
    """Linear display-primary definition.

    ``primaries_XYZ`` uses the project-wide ``XYZ`` scale where the reference
    white commonly has ``Y=100``. Rows are primary stimuli, not chromaticity
    coordinates.
    """

    primaries_XYZ: np.ndarray
    names: tuple[str, ...] | None = None
    whitepoint_XYZ: np.ndarray | None = None

    def __post_init__(self) -> None:
        primaries = _as_primaries_XYZ(self.primaries_XYZ)
        object.__setattr__(self, "primaries_XYZ", primaries)

        if self.names is None:
            names = tuple(f"P{i}" for i in range(primaries.shape[0]))
        else:
            names = tuple(str(name) for name in self.names)
        if len(names) != primaries.shape[0]:
            raise ValueError("names length must match the number of primaries")
        object.__setattr__(self, "names", names)

        whitepoint = (
            np.sum(primaries, axis=0)
            if self.whitepoint_XYZ is None
            else self.whitepoint_XYZ
        )
        object.__setattr__(self, "whitepoint_XYZ", _as_whitepoint_XYZ(whitepoint))

    @property
    def count(self) -> int:
        """Return the number of primaries."""
        return self.primaries_XYZ.shape[0]

    @classmethod
    def from_RGB_colourspace(
        cls,
        colourspace: str | RGBColorSpace,
    ) -> "DisplayPrimaries":
        """Build display primaries from a registered RGB colour space."""
        rgb_space = get_RGB_colourspace(colourspace)
        return cls(
            primaries_XYZ=rgb_space.matrix_RGB_to_XYZ.T,
            names=("R", "G", "B"),
            whitepoint_XYZ=np.sum(rgb_space.matrix_RGB_to_XYZ.T, axis=0),
        )


def as_display_primaries(
    primaries: DisplayPrimaries | RGBColorSpace | str | Sequence[Sequence[float]] | np.ndarray,
) -> DisplayPrimaries:
    """Return *primaries* as a :class:`DisplayPrimaries` instance."""
    if isinstance(primaries, DisplayPrimaries):
        return primaries
    if isinstance(primaries, (str, RGBColorSpace)):
        return DisplayPrimaries.from_RGB_colourspace(primaries)
    return DisplayPrimaries(primaries)


__all__ = ["DisplayPrimaries", "as_display_primaries"]
