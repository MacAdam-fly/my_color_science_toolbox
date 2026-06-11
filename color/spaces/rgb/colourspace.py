"""RGB colour-space definition object."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence, Tuple, Union

import numpy as np

RGBTransfer = Union[str, Tuple[str, Union[float, Tuple[float, float, float]]]]


def _readonly_array(
    value: Sequence[float] | np.ndarray,
    *,
    shape: tuple[int, ...],
    name: str,
) -> np.ndarray:
    """Return *value* as a read-only float array with *shape*."""
    arr = np.array(value, dtype=np.float64, copy=True)
    if arr.shape != shape:
        raise ValueError(f"{name} must have shape {shape}, got {arr.shape}")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be finite")
    arr.setflags(write=False)
    return arr


@dataclass(frozen=True)
class RGBColorSpace:
    """RGB colour-space definition for three-primary RGB systems.

    The matrices operate on linear RGB and project XYZ values in the same
    numeric scale as the stored matrix, normally the project Y=100 XYZ domain.
    ``transfer`` describes the opto-electronic/electro-optical encoding used by
    ``RGB_to_XYZ`` and ``XYZ_to_RGB`` when decoding or encoding is enabled.

    Parameters
    ----------
    name
        Primary RGB colour-space name.
    aliases
        Alternative names accepted by the RGB registry.
    primaries
        RGB primary chromaticities with shape ``(3, 2)``.
    white_xy
        RGB whitepoint chromaticity.
    transfer
        Transfer-function identifier or gamma descriptor.

    Returns
    -------
    RGBColorSpace
        Immutable RGB colour-space definition.

    Notes
    -----
    Custom RGB spaces are ordinary objects until explicitly registered with
    ``register_RGB_colourspace``.

    Examples
    --------
    >>> from color.spaces import get_RGB_colourspace
    >>> get_RGB_colourspace("sRGB").name
    'sRGB'
    """

    name: str
    aliases: tuple[str, ...]
    primaries: np.ndarray
    white_xy: np.ndarray
    white_name: str
    transfer: RGBTransfer
    matrix_RGB_to_XYZ: np.ndarray
    matrix_XYZ_to_RGB: np.ndarray
    reference: str = ""

    @classmethod
    def from_definition(cls, definition: Mapping[str, object]) -> "RGBColorSpace":
        """Build an RGB colour space from a constants definition mapping."""
        aliases = tuple(str(alias) for alias in definition["aliases"])  # type: ignore[index]
        return cls(
            name=str(definition["name"]),
            aliases=aliases,
            primaries=_readonly_array(
                definition["primaries"],  # type: ignore[arg-type,index]
                shape=(3, 2),
                name="primaries",
            ),
            white_xy=_readonly_array(
                definition["white_xy"],  # type: ignore[arg-type,index]
                shape=(2,),
                name="white_xy",
            ),
            white_name=str(definition["white_name"]),
            transfer=str(definition["transfer"]),
            matrix_RGB_to_XYZ=_readonly_array(
                definition["matrix_RGB_to_XYZ"],  # type: ignore[arg-type,index]
                shape=(3, 3),
                name="matrix_RGB_to_XYZ",
            ),
            matrix_XYZ_to_RGB=_readonly_array(
                definition["matrix_XYZ_to_RGB"],  # type: ignore[arg-type,index]
                shape=(3, 3),
                name="matrix_XYZ_to_RGB",
            ),
            reference=str(definition.get("reference", "")),
        )
