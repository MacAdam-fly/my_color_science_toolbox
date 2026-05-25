"""Correlated colour temperature plotting helpers."""

from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np

from color.colorimetry import (
    CCT_to_mired,
    CCT_to_uv,
    CCT_to_xy_CIE_D,
    xy_to_uv1960,
)

from .chromaticity import plot_cie1960_ucs_diagram
from .common import finish_figure, get_figure_axes


DEFAULT_TEMPERATURE_LABELS = {
    "D50": 5003.0,
    "D65": 6504.38938305,
    "D75": 7504.0,
}


def _cct_samples(cct_min: float, cct_max: float, samples: int) -> np.ndarray:
    """Return finite CCT samples for plotting."""
    if samples <= 1:
        raise ValueError("samples must be greater than 1")
    if not np.isfinite(cct_min) or not np.isfinite(cct_max):
        raise ValueError("cct_min and cct_max must be finite")
    if cct_min >= cct_max:
        raise ValueError("cct_min must be smaller than cct_max")
    return np.linspace(float(cct_min), float(cct_max), int(samples))


def _as_1d_finite(value: Sequence[float] | np.ndarray, *, name: str) -> np.ndarray:
    """Return *value* as a finite one-dimensional float array."""
    array = np.asarray(value, dtype=np.float64)
    if array.ndim != 1:
        raise ValueError(f"{name} must be a one-dimensional array")
    if array.size == 0:
        raise ValueError(f"{name} must not be empty")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} values must be finite")
    return array


def planckian_locus_uv1960(
    *,
    cct_min: float = 1667.0,
    cct_max: float = 25000.0,
    samples: int = 220,
    method: str = "ohno2013",
) -> np.ndarray:
    """Return Planckian locus samples in CIE 1960 UCS uv coordinates."""
    cct = _cct_samples(cct_min, cct_max, samples)
    return CCT_to_uv(
        np.column_stack([cct, np.zeros_like(cct)]),
        method=method,
    )


def daylight_locus_uv1960(
    *,
    cct_min: float = 4000.0,
    cct_max: float = 25000.0,
    samples: int = 180,
) -> np.ndarray:
    """Return CIE D-series daylight locus samples in CIE 1960 UCS uv."""
    cct = _cct_samples(cct_min, cct_max, samples)
    return xy_to_uv1960(CCT_to_xy_CIE_D(cct))


def duv_offset_grid_uv1960(
    ccts: Sequence[float] | np.ndarray,
    duvs: Sequence[float] | np.ndarray,
    *,
    method: str = "ohno2013",
) -> np.ndarray:
    """Return a CCT by Duv grid in CIE 1960 UCS uv coordinates."""
    cct_values = _as_1d_finite(ccts, name="ccts")
    duv_values = _as_1d_finite(duvs, name="duvs")
    cct_grid, duv_grid = np.meshgrid(cct_values, duv_values, indexing="ij")
    return CCT_to_uv(
        np.stack([cct_grid, duv_grid], axis=-1),
        method=method,
    )


def plot_temperature_loci_uv1960(
    *,
    ax=None,
    method: str = "ohno2013",
    planckian_cct_min: float = 1667.0,
    planckian_cct_max: float = 25000.0,
    daylight_cct_min: float = 4000.0,
    daylight_cct_max: float = 25000.0,
    samples: int = 220,
    daylight_samples: int = 180,
    named_ccts: Mapping[str, float] | None = DEFAULT_TEMPERATURE_LABELS,
    show_background: bool = True,
    background_samples: int = 192,
    title: str = "CCT Loci in CIE 1960 UCS uv",
):
    """Plot Planckian and CIE D daylight loci in CIE 1960 UCS uv."""
    fig, ax = plot_cie1960_ucs_diagram(
        ax=ax,
        title=title,
        show_sample_points=False,
        show_background=show_background,
        background_samples=background_samples,
    )
    planckian = planckian_locus_uv1960(
        cct_min=planckian_cct_min,
        cct_max=planckian_cct_max,
        samples=samples,
        method=method,
    )
    daylight = daylight_locus_uv1960(
        cct_min=daylight_cct_min,
        cct_max=daylight_cct_max,
        samples=daylight_samples,
    )
    ax.plot(
        planckian[:, 0],
        planckian[:, 1],
        color="0.15",
        linestyle="--",
        linewidth=1.0,
        label=f"Planckian locus ({method})",
        zorder=4,
    )
    ax.plot(
        daylight[:, 0],
        daylight[:, 1],
        color="tab:blue",
        linewidth=1.0,
        label="CIE D daylight locus",
        zorder=4,
    )
    if named_ccts is not None:
        offsets = [(10, 10), (10, 0), (10, -12), (10, -24)]
        for index, (name, cct) in enumerate(named_ccts.items()):
            daylight_point = xy_to_uv1960(CCT_to_xy_CIE_D(cct))
            planckian_point = CCT_to_uv([cct, 0.0], method=method)
            ax.plot(
                [daylight_point[0], planckian_point[0]],
                [daylight_point[1], planckian_point[1]],
                color="0.55",
                linestyle=":",
                linewidth=1.0,
                zorder=3,
            )
            ax.scatter(*daylight_point, s=24, color="tab:blue", zorder=5)
            ax.scatter(*planckian_point, s=24, color="0.15", marker="x", zorder=5)
            ax.annotate(
                f"{name}\n{cct:.0f} K",
                xy=daylight_point,
                xytext=offsets[index % len(offsets)],
                textcoords="offset points",
                fontsize=8,
            )
    ax.legend(loc="upper right", fontsize=8, framealpha=0.92)
    finish_figure(fig)
    return fig, ax


def plot_duv_offsets_uv1960(
    *,
    ax=None,
    ccts: Sequence[float] | np.ndarray = (3000.0, 5000.0, 6500.0, 10000.0),
    duvs: Sequence[float] | np.ndarray = (-0.02, -0.01, 0.0, 0.01, 0.02),
    method: str = "ohno2013",
    show_background: bool = False,
    background_samples: int = 192,
    title: str = "Duv Offsets in CIE 1960 UCS uv",
):
    """Plot Duv offsets around the Planckian locus in CIE 1960 UCS uv."""
    cct_values = _as_1d_finite(ccts, name="ccts")
    duv_values = _as_1d_finite(duvs, name="duvs")
    fig, ax = plot_cie1960_ucs_diagram(
        ax=ax,
        title=title,
        show_sample_points=False,
        show_background=show_background,
        background_samples=background_samples,
    )
    cct_min = max(1000.0, float(np.min(cct_values)) * 0.75)
    cct_max = float(np.max(cct_values)) * 1.25
    planckian = planckian_locus_uv1960(
        cct_min=cct_min,
        cct_max=cct_max,
        samples=180,
        method=method,
    )
    ax.plot(
        planckian[:, 0],
        planckian[:, 1],
        color="0.15",
        linewidth=1.0,
        label=f"Planckian locus ({method})",
        zorder=4,
    )

    grid = duv_offset_grid_uv1960(cct_values, duv_values, method=method)
    import matplotlib.pyplot as plt

    color_values = plt.cm.viridis(np.linspace(0.15, 0.85, len(cct_values)))
    for cct, row, color in zip(cct_values, grid, color_values):
        ax.plot(row[:, 0], row[:, 1], marker="o", color=color, label=f"{cct:.0f} K", zorder=5)
        for duv, point in zip(duv_values, row):
            if np.isclose(duv, np.min(duv_values)) or np.isclose(duv, 0.0) or np.isclose(duv, np.max(duv_values)):
                ax.annotate(
                    f"{duv:+.2f}",
                    xy=point,
                    xytext=(5, 4),
                    textcoords="offset points",
                    fontsize=7,
                    color=color,
                )
    ax.legend(loc="upper right", fontsize=8, framealpha=0.92)
    finish_figure(fig)
    return fig, ax


def plot_mired_curve(
    *,
    ax=None,
    cct_min: float = 2000.0,
    cct_max: float = 12000.0,
    samples: int = 300,
    title: str = "CCT and Mired Relationship",
):
    """Plot the nonlinear relationship between CCT and mired."""
    cct = _cct_samples(cct_min, cct_max, samples)
    mired = CCT_to_mired(cct)
    fig, ax = get_figure_axes(ax, figsize=(7.2, 4.6))
    ax.plot(cct, mired, color="tab:purple", linewidth=2.0)
    ax.set_title(title)
    ax.set_xlabel("CCT (K)")
    ax.set_ylabel("Mired")
    ax.grid(True, alpha=0.3)
    finish_figure(fig)
    return fig, ax


__all__ = [
    "DEFAULT_TEMPERATURE_LABELS",
    "daylight_locus_uv1960",
    "duv_offset_grid_uv1960",
    "planckian_locus_uv1960",
    "plot_duv_offsets_uv1960",
    "plot_mired_curve",
    "plot_temperature_loci_uv1960",
]
