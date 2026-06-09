"""Reference illuminant and whitepoint XYZ constants."""

from __future__ import annotations

import numpy as np


def _readonly_vector(values: list[float]) -> np.ndarray:
	"""Return a read-only XYZ vector."""
	vector = np.array(values, dtype=np.float64)
	vector.setflags(write=False)
	return vector

A_XYZ = _readonly_vector([109.8490612345073, 100.0, 35.579825745490254])
C_XYZ = _readonly_vector([98.0705971659919, 100.0, 118.22494939271255])
D50_XYZ = _readonly_vector([96.4212, 100.0, 82.5188])
D55_XYZ = _readonly_vector([95.682, 100.0, 92.149])
D65_XYZ = _readonly_vector([95.047, 100.0, 108.883])
E_XYZ = _readonly_vector([100.0, 100.0, 100.0])
