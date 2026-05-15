"""Color difference utilities."""

from __future__ import annotations

import numpy as np

from ..core.types import ArrayLike
from ..utils.CIEDE2000 import CIEDE2000


class DeltaEToolkit:
    """Facade for color-difference calculations."""

    @staticmethod
    def ciede2000(lab1: ArrayLike, lab2: ArrayLike, kL: float = 1.0, kC: float = 1.0, kH: float = 1.0) -> float:
        return float(CIEDE2000.calculate(np.asarray(lab1, dtype=float), np.asarray(lab2, dtype=float), kL=kL, kC=kC, kH=kH))
