"""Jzazbz colour-difference formula."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from ._utils import as_float_result, broadcast_triplets


def delta_E_Jzazbz(
    Jzazbz_1: Sequence[float] | np.ndarray,
    Jzazbz_2: Sequence[float] | np.ndarray,
) -> np.ndarray | np.float64:
    """Return Euclidean distance between two Jzazbz coordinate arrays.

    Inputs must already be Jzazbz coordinates. This is a direct coordinate
    distance, not a CIE standard Delta E formula.
    """
    jzazbz_1, jzazbz_2 = broadcast_triplets(
        Jzazbz_1,
        Jzazbz_2,
        name_1="Jzazbz_1",
        name_2="Jzazbz_2",
    )
    return as_float_result(np.linalg.norm(jzazbz_1 - jzazbz_2, axis=-1))


__all__ = [
    "delta_E_Jzazbz",
]
