"""Chromatic adaptation transform matrix constants."""

from __future__ import annotations

from types import MappingProxyType

import numpy as np


def _readonly_matrix(values: list[list[float]]) -> np.ndarray:
    """Return a read-only 3x3 matrix."""
    matrix = np.array(values, dtype=np.float64)
    matrix.setflags(write=False)
    return matrix


CAT_VON_KRIES = _readonly_matrix(
    [
        [0.4002400, 0.7076000, -0.0808100],
        [-0.2263000, 1.1653200, 0.0457000],
        [0.0000000, 0.0000000, 0.9182200],
    ]
)
"""Von Kries chromatic adaptation transform."""


CAT_BRADFORD = _readonly_matrix(
    [
        [0.8951000, 0.2664000, -0.1614000],
        [-0.7502000, 1.7135000, 0.0367000],
        [0.0389000, -0.0685000, 1.0296000],
    ]
)
"""Bradford chromatic adaptation transform."""


CAT_CAT02 = _readonly_matrix(
    [
        [0.7328000, 0.4296000, -0.1624000],
        [-0.7036000, 1.6975000, 0.0061000],
        [0.0030000, 0.0136000, 0.9834000],
    ]
)
"""CAT02 chromatic adaptation transform."""


CAT_CAT16 = _readonly_matrix(
    [
        [0.4012880, 0.6501730, -0.0514610],
        [-0.2502680, 1.2044140, 0.0458540],
        [-0.0020790, 0.0489520, 0.9531270],
    ]
)
"""CAT16 chromatic adaptation transform."""


CHROMATIC_ADAPTATION_TRANSFORMS = MappingProxyType(
    {
        "Von Kries": CAT_VON_KRIES,
        "Bradford": CAT_BRADFORD,
        "CAT02": CAT_CAT02,
        "CAT16": CAT_CAT16,
    }
)
"""Read-only mapping of supported chromatic adaptation transforms."""


__all__ = [
    "CAT_VON_KRIES",
    "CAT_BRADFORD",
    "CAT_CAT02",
    "CAT_CAT16",
    "CHROMATIC_ADAPTATION_TRANSFORMS",
]
