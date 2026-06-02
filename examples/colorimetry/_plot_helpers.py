"""Shared non-plotting helpers for colorimetry examples."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np

from color.colorimetry import XYZ_to_xy, XYZ_to_xyY


def example_output_dir() -> Path:
    """Return the shared output directory for colorimetry examples."""
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


def print_xyY_table(title: str, labels: Sequence[str], XYZ: np.ndarray) -> None:
    """Print XYZ converted to xyY rows."""
    xyY = XYZ_to_xyY(XYZ)
    print(title)
    for label, xyz_row, xyy_row in zip(labels, np.asarray(XYZ), xyY):
        print(
            f"{label}: XYZ={np.round(xyz_row, 5)} "
            f"xyY={np.round(xyy_row, 5)}"
        )


def xy_from_XYZ_rows(XYZ: Sequence[Sequence[float]] | np.ndarray) -> np.ndarray:
    """Convert row-wise XYZ values to xy coordinates."""
    return XYZ_to_xy(np.asarray(XYZ, dtype=np.float64))
