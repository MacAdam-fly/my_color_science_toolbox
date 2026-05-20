"""Shared plotting helpers for colorimetry examples."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

import matplotlib.pyplot as plt
import numpy as np

from color.colorimetry import XYZ_to_xy, XYZ_to_xyY
from color.spaces import XYZ_to_sRGB
from color.spectra import from_dataset


D65_XY = np.array([0.3127, 0.3290], dtype=np.float64)


def example_output_dir() -> Path:
    """Return the shared output directory for colorimetry examples."""
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


def load_cie1931_locus_xy() -> np.ndarray:
    """Load the CIE 1931 spectral locus as xy coordinates."""
    locus = from_dataset("standard_observers.chromaticity_coordinates", "cie1931_chro_1nm")
    x_index = locus.labels.index("x")
    y_index = locus.labels.index("y")
    return locus.values[:, (x_index, y_index)]


def plot_xy_locus(ax: plt.Axes, *, title: str = "CIE 1931 xy") -> None:
    """Plot the CIE 1931 spectral locus and D65 white point."""
    locus_xy = load_cie1931_locus_xy()
    closed = np.vstack([locus_xy, locus_xy[0]])
    ax.plot(closed[:, 0], closed[:, 1], color="0.25", linewidth=1.4)
    ax.scatter(locus_xy[::40, 0], locus_xy[::40, 1], s=10, color="0.45", alpha=0.7)
    ax.scatter(*D65_XY, s=42, color="black", label="D65 white")
    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_xlim(0.0, 0.8)
    ax.set_ylim(0.0, 0.9)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.25)


def annotate_xy_points(
    ax: plt.Axes,
    xy: Sequence[Sequence[float]] | np.ndarray,
    labels: Iterable[str],
    *,
    color: str = "tab:red",
    marker: str = "o",
) -> None:
    """Scatter and label xy points on an existing chromaticity diagram."""
    xy_arr = np.asarray(xy, dtype=np.float64)
    ax.scatter(xy_arr[:, 0], xy_arr[:, 1], s=52, color=color, marker=marker, zorder=3)
    for point, label in zip(xy_arr, labels):
        ax.annotate(
            label,
            xy=point,
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=8,
        )


def preview_srgb_from_XYZ(
    XYZ: Sequence[Sequence[float]] | np.ndarray,
    *,
    white_Y: float,
) -> np.ndarray:
    """Convert XYZ to clipped sRGB only for approximate plotting previews."""
    xyz = np.asarray(XYZ, dtype=np.float64)
    if white_Y <= 0:
        raise ValueError("white_Y must be positive")
    rgb = XYZ_to_sRGB(xyz / white_Y)
    return np.clip(rgb, 0.0, 1.0)


def plot_srgb_swatches(
    ax: plt.Axes,
    labels: Sequence[str],
    XYZ: Sequence[Sequence[float]] | np.ndarray,
    *,
    white_Y: float,
    title: str,
) -> None:
    """Plot approximate sRGB swatches for XYZ samples."""
    rgb = preview_srgb_from_XYZ(XYZ, white_Y=white_Y)
    ax.imshow(rgb[np.newaxis, :, :], extent=(0, len(labels), 0, 1), aspect="auto")
    ax.set_title(title)
    ax.set_yticks([])
    ax.set_xticks(np.arange(len(labels)) + 0.5, labels, rotation=20, ha="right")
    for index in range(len(labels) + 1):
        ax.axvline(index, color="white", linewidth=1.0, alpha=0.8)


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
