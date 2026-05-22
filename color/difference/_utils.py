"""Compatibility imports for colour-difference utility helpers."""

from __future__ import annotations

from color.utils.arrays import (
    as_float_result,
    as_last_axis_triplets as as_triplet_array,
    broadcast_triplets,
)


__all__ = [
    "as_triplet_array",
    "broadcast_triplets",
    "as_float_result",
]
