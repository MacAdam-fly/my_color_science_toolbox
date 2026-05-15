"""Type aliases used across the package."""

from __future__ import annotations

from typing import Sequence, Union

import numpy as np

ArrayLike = Union[Sequence[float], np.ndarray]
ColorTriplet = np.ndarray
WhitePoint = np.ndarray
