"""Unified conversion entry point."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ..constants.illuminants import D65_XYZ
from ..core.types import ArrayLike
from ..spaces.lab import lab_to_lch, lab_to_xyz, lch_to_lab, xyz_to_lab
from ..spaces.lms import lms_to_xyz, xyz_to_lms
from ..spaces.luv import lch_uv_to_luv, luv_to_lch_uv, luv_to_xyz, xyz_to_luv
from ..spaces.xyz import xyy_to_xyz, xyz_to_xyy


@dataclass
class ColorConversionSuite:
    """Convenience wrapper that groups the current conversion functions."""

    white_point: np.ndarray = field(default_factory=lambda: D65_XYZ.copy())
    lms_fov: int = 10

    def xyz_to_lab(self, xyz: ArrayLike) -> np.ndarray:
        return xyz_to_lab(xyz, self.white_point)

    def lab_to_xyz(self, lab: ArrayLike) -> np.ndarray:
        return lab_to_xyz(lab, self.white_point)

    def lab_to_lch(self, lab: ArrayLike) -> np.ndarray:
        return lab_to_lch(lab)

    def lch_to_lab(self, lch: ArrayLike) -> np.ndarray:
        return lch_to_lab(lch)

    def xyz_to_luv(self, xyz: ArrayLike) -> np.ndarray:
        return xyz_to_luv(xyz, self.white_point)

    def luv_to_xyz(self, luv: ArrayLike) -> np.ndarray:
        return luv_to_xyz(luv, self.white_point)

    def luv_to_lch_uv(self, luv: ArrayLike) -> np.ndarray:
        return luv_to_lch_uv(luv)

    def lch_uv_to_luv(self, lch: ArrayLike) -> np.ndarray:
        return lch_uv_to_luv(lch)

    def xyz_to_xyy(self, xyz: ArrayLike) -> np.ndarray:
        return xyz_to_xyy(xyz)

    def xyy_to_xyz(self, xyy: ArrayLike) -> np.ndarray:
        return xyy_to_xyz(xyy)

    def xyz_to_lms(self, xyz: ArrayLike) -> np.ndarray:
        return xyz_to_lms(xyz, self.lms_fov)

    def lms_to_xyz(self, lms: ArrayLike) -> np.ndarray:
        return lms_to_xyz(lms, self.lms_fov)
