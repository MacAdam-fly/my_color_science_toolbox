"""Shared plotting helpers for colour-space examples."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from color.spaces import RGB_to_XYZ, XYZ_to_RGB, get_RGB_colourspace


def output_dir() -> Path:
    """Return the spaces example output directory."""
    path = Path(__file__).resolve().parent / "output"
    path.mkdir(exist_ok=True)
    return path


def xy_from_XYZ(XYZ: np.ndarray) -> np.ndarray:
    """Return xy chromaticity coordinates from XYZ values."""
    xyz = np.asarray(XYZ, dtype=np.float64)
    denominator = np.sum(xyz, axis=-1)
    xy = np.zeros((*denominator.shape, 2), dtype=np.float64)
    nonzero = denominator != 0
    np.divide(xyz[..., 0], denominator, out=xy[..., 0], where=nonzero)
    np.divide(xyz[..., 1], denominator, out=xy[..., 1], where=nonzero)
    return xy


def preview_sRGB_from_XYZ(XYZ: np.ndarray) -> np.ndarray:
    """Return clipped sRGB values for visual preview only."""
    rgb = XYZ_to_RGB(XYZ, colourspace="sRGB")
    return np.clip(rgb, 0.0, 1.0)


def plot_rgb_gamuts(ax, names: list[str]) -> None:
    """Plot RGB primary triangles in CIE xy."""
    colors = {
        "sRGB": "tab:blue",
        "Display P3": "tab:green",
        "Rec.2020": "tab:red",
        "DCI-P3": "tab:purple",
    }
    for name in names:
        space = get_RGB_colourspace(name)
        primaries_XYZ = RGB_to_XYZ(
            np.identity(3),
            colourspace=space,
            apply_decoding=False,
        )
        primaries_xy = xy_from_XYZ(primaries_XYZ)
        closed = np.vstack((primaries_xy, primaries_xy[0]))
        color = colors.get(name, None)
        ax.plot(closed[:, 0], closed[:, 1], marker="o", color=color, label=name)
        ax.scatter(*space.white_xy, marker="x", color=color, s=55)

    ax.set_xlabel("CIE x")
    ax.set_ylabel("CIE y")
    ax.set_xlim(0.0, 0.85)
    ax.set_ylim(0.0, 0.9)
    ax.grid(True, alpha=0.3)


def plot_swatch_grid(
    ax,
    rows: list[tuple[str, np.ndarray]],
    *,
    title: str,
) -> None:
    """Plot a labelled grid of clipped sRGB preview swatches."""
    n_rows = len(rows)
    n_cols = max(values.shape[0] for _, values in rows)
    ax.set_title(title)
    ax.set_xlim(0, n_cols)
    ax.set_ylim(0, n_rows)
    ax.set_xticks(np.arange(n_cols) + 0.5)
    ax.set_xticklabels([f"C{i + 1}" for i in range(n_cols)])
    ax.set_yticks(np.arange(n_rows) + 0.5)
    ax.set_yticklabels([label for label, _ in rows])
    ax.tick_params(length=0)

    for row_index, (_, values) in enumerate(rows):
        y = n_rows - row_index - 1
        for col_index, rgb in enumerate(values):
            ax.add_patch(
                plt.Rectangle(
                    (col_index, y),
                    1.0,
                    1.0,
                    facecolor=np.clip(rgb, 0.0, 1.0),
                    edgecolor="white",
                    linewidth=1.0,
                )
            )
    for spine in ax.spines.values():
        spine.set_visible(False)
