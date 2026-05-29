"""Shared helpers for gamut examples."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from color.constants import D65_XYZ
from color.gamut import DisplayPrimaries, compute_LCH_gamut_boundary

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COLOURS = {
    "sRGB": "#0072B2",
    "RGBC": "#D55E00",
    "Rec.2020": "#009E73",
}


def save_figure(fig, filename: str) -> None:
    """Save *fig* into the gamut example output directory."""
    path = OUTPUT_DIR / filename
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def rgbc_primaries() -> DisplayPrimaries:
    """Return a synthetic four-primary display used by the examples."""
    return DisplayPrimaries(
        [
            [75.35530926, 30.53272055, 0.8324195],
            [ 3.43647492, 35.46933042,  6.55021212], 
            [15.06919248,  3.99794903, 83.44437197], 
            [ 1.18187787, 30.        , 18.06303349]
        ],
        names=("R", "G", "B", "C"),
    )


def compute_example_boundaries():
    """Return representative sRGB, RGBC and Rec.2020 LCH boundaries."""
    L_values = np.arange(1.0, 100.1, 1.0)
    hue_values = np.arange(0.0, 361.0, 1.0)
    rgbc = rgbc_primaries()
    return {
        "sRGB": compute_LCH_gamut_boundary(
            "sRGB",
            whitepoint_XYZ=D65_XYZ,
            L_values=L_values,
            hue_values=hue_values,
            C_upper=180.0,
            iterations=10,
        ),
        "RGBC": compute_LCH_gamut_boundary(
            rgbc,
            whitepoint_XYZ=D65_XYZ,
            L_values=L_values,
            hue_values=hue_values,
            C_upper=260.0,
            iterations=10,
        ),
        "Rec.2020": compute_LCH_gamut_boundary(
            "Rec.2020",
            whitepoint_XYZ=D65_XYZ,
            L_values=L_values,
            hue_values=hue_values,
            C_upper=260.0,
            iterations=10,
        ),
    }


def lch_slice_ab(boundary, L: float) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(a*, b*)`` arrays for the boundary slice nearest *L*."""
    lab = boundary.to_Lab()
    index = int(np.argmin(np.abs(boundary.L_values - L)))
    return lab[index, :, 1], lab[index, :, 2]
