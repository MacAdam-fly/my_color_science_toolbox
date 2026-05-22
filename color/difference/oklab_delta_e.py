"""Oklab colour-difference formula."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from ._utils import as_float_result, broadcast_triplets


def delta_E_Oklab(
    Oklab_1: Sequence[float] | np.ndarray,
    Oklab_2: Sequence[float] | np.ndarray,
) -> np.ndarray | np.float64:
    """Return the Euclidean distance between two Oklab coordinate arrays."""
    oklab_1, oklab_2 = broadcast_triplets(
        Oklab_1,
        Oklab_2,
        name_1="Oklab_1",
        name_2="Oklab_2",
    )
    return as_float_result(np.linalg.norm(oklab_1 - oklab_2, axis=-1))


__all__ = [
    "delta_E_Oklab",
]
