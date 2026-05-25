"""RGB colourspace plotting helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from color.colorimetry import XYZ_to_xy
from color.spaces import RGB_to_XYZ, get_RGB_colourspace

from .common import finish_figure, get_figure_axes


def plot_rgb_gamuts(
    names: Sequence[str],
    *,
    ax=None,
    colors: dict[str, str] | None = None,
    title: str = "RGB Gamuts In CIE xy",
):
    """Plot RGB primary triangles in CIE xy."""
    fig, ax = get_figure_axes(ax, figsize=(5.8, 5.2))
    default_colors = {
        "sRGB": "tab:blue",
        "Display P3": "tab:green",
        "Rec.2020": "tab:red",
        "DCI-P3": "tab:purple",
    }
    palette = colors or default_colors
    for name in names:
        space = get_RGB_colourspace(name)
        primaries_XYZ = RGB_to_XYZ(
            np.identity(3),
            colourspace=space,
            apply_decoding=False,
        )
        primaries_xy = XYZ_to_xy(primaries_XYZ)
        closed = np.vstack((primaries_xy, primaries_xy[0]))
        color = palette.get(space.name, palette.get(name, None))
        ax.plot(closed[:, 0], closed[:, 1], marker="o", color=color, label=space.name)
        ax.scatter(*space.white_xy, marker="x", color=color, s=55)

    ax.set_title(title)
    ax.set_xlabel("CIE x")
    ax.set_ylabel("CIE y")
    ax.set_xlim(0.0, 0.85)
    ax.set_ylim(0.0, 0.9)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.3)
    ax.legend()
    finish_figure(fig)
    return fig, ax


__all__ = [
    "plot_rgb_gamuts",
]
