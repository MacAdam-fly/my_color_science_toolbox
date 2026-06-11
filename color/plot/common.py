"""Common helpers for plotting modules."""

from __future__ import annotations

from typing import Sequence

import numpy as np


def get_figure_axes(
    ax=None,
    *,
    figsize: tuple[float, float] = (7.0, 4.0),
):
    """Return ``(fig, ax)`` using *ax* or creating a new figure.

    Notes
    -----
    Plot functions use this helper to support both standalone calls and
    caller-managed subplot layouts.
    """
    import matplotlib.pyplot as plt

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure
    return fig, ax


def finish_figure(fig, *, tight_layout: bool = True):
    """Apply final figure layout settings and return *fig*.

    Notes
    -----
    This does not save or show the figure. Saving belongs to ``color.io`` or
    the caller.
    """
    if tight_layout:
        fig.tight_layout()
    return fig


def as_2d_points(
    value: Sequence[Sequence[float]] | np.ndarray,
    *,
    size: int,
    name: str = "value",
) -> np.ndarray:
    """Return *value* as ``(n, size)`` float points."""
    points = np.asarray(value, dtype=np.float64)
    if points.ndim == 1:
        if points.shape != (size,):
            raise ValueError(f"{name} must have shape ({size},) or (n, {size})")
        points = points.reshape(1, size)
    if points.ndim != 2 or points.shape[-1] != size:
        raise ValueError(f"{name} must have shape ({size},) or (n, {size})")
    if not np.all(np.isfinite(points)):
        raise ValueError(f"{name} values must be finite")
    return points


def as_rgb_rows(
    rgb: Sequence[Sequence[float]] | np.ndarray,
    *,
    name: str = "rgb",
    clip: bool = True,
) -> np.ndarray:
    """Return RGB values as ``(n, 3)`` rows."""
    values = as_2d_points(rgb, size=3, name=name)
    return np.clip(values, 0.0, 1.0) if clip else values


__all__ = [
    "as_2d_points",
    "as_rgb_rows",
    "finish_figure",
    "get_figure_axes",
]
