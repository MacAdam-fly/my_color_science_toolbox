"""Colour swatch plotting helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from color.spaces import XYZ_to_sRGB

from .common import as_rgb_rows, finish_figure, get_figure_axes


def preview_sRGB_from_XYZ(
    XYZ: Sequence[Sequence[float]] | np.ndarray,
    *,
    white_Y: float = 100.0,
) -> np.ndarray:
    """Return clipped sRGB values for approximate plotting previews."""
    if white_Y <= 0:
        raise ValueError("white_Y must be positive")
    xyz = np.asarray(XYZ, dtype=np.float64)
    rgb = XYZ_to_sRGB(xyz * (100.0 / white_Y))
    return np.clip(rgb, 0.0, 1.0)


def plot_swatch_strip(
    rgb: Sequence[Sequence[float]] | np.ndarray,
    *,
    ax=None,
    labels: Sequence[str] | None = None,
    title: str | None = None,
):
    """Plot a horizontal strip of sRGB preview swatches."""
    values = as_rgb_rows(rgb)
    fig, ax = get_figure_axes(ax, figsize=(7.0, 1.8))
    ax.imshow(values[np.newaxis, :, :], extent=(0, values.shape[0], 0, 1), aspect="auto")
    ax.set_yticks([])
    ax.set_xlim(0, values.shape[0])
    if labels is not None:
        if len(labels) != values.shape[0]:
            raise ValueError("labels length must match number of swatches")
        ax.set_xticks(np.arange(values.shape[0]) + 0.5, labels, rotation=20, ha="right")
    else:
        ax.set_xticks([])
    for index in range(values.shape[0] + 1):
        ax.axvline(index, color="white", linewidth=1.0, alpha=0.8)
    if title is not None:
        ax.set_title(title)
    finish_figure(fig)
    return fig, ax


def plot_swatch_grid(
    rows: Sequence[tuple[str, Sequence[Sequence[float]] | np.ndarray]],
    *,
    ax=None,
    title: str | None = None,
):
    """Plot a labelled grid of sRGB preview swatches."""
    import matplotlib.pyplot as plt

    if not rows:
        raise ValueError("rows must not be empty")
    rgb_rows = [(label, as_rgb_rows(values)) for label, values in rows]
    n_rows = len(rgb_rows)
    n_cols = max(values.shape[0] for _label, values in rgb_rows)
    fig, ax = get_figure_axes(
        ax,
        figsize=(max(5.0, n_cols * 0.9), max(2.0, n_rows * 0.55)),
    )
    ax.set_xlim(0, n_cols)
    ax.set_ylim(0, n_rows)
    ax.set_xticks(np.arange(n_cols) + 0.5)
    ax.set_xticklabels([f"C{i + 1}" for i in range(n_cols)])
    ax.set_yticks(np.arange(n_rows) + 0.5)
    ax.set_yticklabels([label for label, _values in rgb_rows])
    ax.tick_params(length=0)
    if title is not None:
        ax.set_title(title)

    for row_index, (_label, values) in enumerate(rgb_rows):
        y = n_rows - row_index - 1
        for col_index, rgb in enumerate(values):
            ax.add_patch(
                plt.Rectangle(
                    (col_index, y),
                    1.0,
                    1.0,
                    facecolor=rgb,
                    edgecolor="white",
                    linewidth=1.0,
                )
            )
    for spine in ax.spines.values():
        spine.set_visible(False)
    finish_figure(fig)
    return fig, ax


__all__ = [
    "plot_swatch_grid",
    "plot_swatch_strip",
    "preview_sRGB_from_XYZ",
]
