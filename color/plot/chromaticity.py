"""CIE xy chromaticity plotting helpers."""

from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np

from color.colorimetry import (
    xyY_to_XYZ,
    xy_to_upvp1976,
    xy_to_uv1960,
)
from color.spaces import XYZ_to_sRGB
from color.spectra import from_dataset

from .common import as_2d_points, finish_figure, get_figure_axes


D65_XY = np.array([0.3127, 0.3290], dtype=np.float64)
D65_UV1960 = xy_to_uv1960(D65_XY)
D65_UPVP1976 = xy_to_upvp1976(D65_XY)


def _uv1960_to_xy_unchecked(uv: np.ndarray) -> np.ndarray:
    """Convert CIE 1960 uv to xy without raising on singular grid points."""
    u = uv[..., 0]
    v = uv[..., 1]
    denominator = 2.0 * u - 8.0 * v + 4.0
    x = np.divide(3.0 * u, denominator, out=np.full_like(u, np.nan), where=denominator != 0)
    y = np.divide(2.0 * v, denominator, out=np.full_like(v, np.nan), where=denominator != 0)
    return np.stack([x, y], axis=-1)


def _upvp1976_to_xy_unchecked(upvp: np.ndarray) -> np.ndarray:
    """Convert CIE 1976 u'v' to xy without raising on singular grid points."""
    u_p = upvp[..., 0]
    v_p = upvp[..., 1]
    denominator = 6.0 * u_p - 16.0 * v_p + 12.0
    x = np.divide(9.0 * u_p, denominator, out=np.full_like(u_p, np.nan), where=denominator != 0)
    y = np.divide(4.0 * v_p, denominator, out=np.full_like(v_p, np.nan), where=denominator != 0)
    return np.stack([x, y], axis=-1)


_CHROMATICITY_DIAGRAM_METHODS = {
    "CIE 1931": {
        "ij_to_xy": lambda ij: ij,
        "xy_to_ij": lambda xy: xy,
        "default_xlim": (0.0, 0.8),
        "default_ylim": (0.0, 0.9),
        "xlabel": "x",
        "ylabel": "y",
    },
    "CIE 1960 UCS": {
        "ij_to_xy": _uv1960_to_xy_unchecked,
        "xy_to_ij": xy_to_uv1960,
        "default_xlim": (0.0, 0.65),
        "default_ylim": (0.0, 0.42),
        "xlabel": "u",
        "ylabel": "v",
    },
    "CIE 1976 UCS": {
        "ij_to_xy": _upvp1976_to_xy_unchecked,
        "xy_to_ij": xy_to_upvp1976,
        "default_xlim": (0.0, 0.65),
        "default_ylim": (0.0, 0.62),
        "xlabel": "u'",
        "ylabel": "v'",
    },
}


def _resolve_chromaticity_method(method: str) -> dict:
    """Return the chromaticity diagram method definition."""
    if method not in _CHROMATICITY_DIAGRAM_METHODS:
        supported = ", ".join(_CHROMATICITY_DIAGRAM_METHODS)
        raise ValueError(f"unsupported chromaticity diagram method {method!r}; supported: {supported}")
    return _CHROMATICITY_DIAGRAM_METHODS[method]


def _normalise_rgb_maximum(rgb: np.ndarray) -> np.ndarray:
    """Normalise RGB values by their maximum channel."""
    maximum = np.max(rgb, axis=-1, keepdims=True)
    return np.divide(rgb, maximum, out=np.zeros_like(rgb), where=maximum > 0)


def load_cie1931_locus_xy() -> np.ndarray:
    """Return CIE 1931 spectral locus xy coordinates."""
    locus = from_dataset(
        "standard_observers.chromaticity_coordinates",
        "cie1931_chro_1nm",
    )
    x_index = locus.labels.index("x")
    y_index = locus.labels.index("y")
    return np.array(locus.values[:, (x_index, y_index)], copy=True)


def load_cie1931_locus_uv1960() -> np.ndarray:
    """Return CIE 1931 spectral locus coordinates in CIE 1960 UCS uv."""
    return xy_to_uv1960(load_cie1931_locus_xy())


def load_cie1931_locus_upvp1976() -> np.ndarray:
    """Return CIE 1931 spectral locus coordinates in CIE 1976 UCS u'v'."""
    return xy_to_upvp1976(load_cie1931_locus_xy())


def chromaticity_background_image(
    *,
    method: str = "CIE 1931",
    samples: int = 256,
    normalise: bool = True,
) -> np.ndarray:
    """Return a clipped sRGB image for a chromaticity diagram background."""
    if samples <= 1:
        raise ValueError("samples must be greater than 1")
    definition = _resolve_chromaticity_method(method)
    x, y = np.meshgrid(
        np.linspace(0.0, 1.0, samples),
        np.linspace(1.0, 0.0, samples),
    )
    ij = np.stack([x, y], axis=-1)
    xy = definition["ij_to_xy"](ij)
    valid = np.all(np.isfinite(xy), axis=-1)
    xy = np.where(valid[..., None], xy, 0.0)
    xyY = np.concatenate([xy, np.ones((*xy.shape[:-1], 1), dtype=np.float64)], axis=-1)
    XYZ = xyY_to_XYZ(xyY)
    rgb = XYZ_to_sRGB(XYZ * 100.0)
    if normalise:
        rgb = _normalise_rgb_maximum(rgb)
    rgb = np.where(valid[..., None], rgb, 0.0)
    return np.clip(rgb, 0.0, 1.0)


def _spectral_locus_for_method(method: str) -> np.ndarray:
    """Return the CIE spectral locus in the chromaticity diagram coordinates."""
    definition = _resolve_chromaticity_method(method)
    return definition["xy_to_ij"](load_cie1931_locus_xy())


def plot_chromaticity_background(
    *,
    method: str = "CIE 1931",
    ax=None,
    samples: int = 256,
    alpha: float = 1.0,
    normalise: bool = True,
):
    """Plot a clipped chromaticity diagram background."""
    from matplotlib.patches import Polygon

    definition = _resolve_chromaticity_method(method)
    fig, ax = get_figure_axes(ax, figsize=(5.2, 5.0))
    image = chromaticity_background_image(
        method=method,
        samples=samples,
        normalise=normalise,
    )
    locus = _spectral_locus_for_method(method)
    polygon = Polygon(locus, facecolor="none", edgecolor="none")
    polygon.set_gid("chromaticity_background_clip")
    ax.add_patch(polygon)
    artist = ax.imshow(
        image,
        interpolation="bilinear",
        extent=(0.0, 1.0, 0.0, 1.0),
        origin="upper",
        alpha=alpha,
        zorder=0,
    )
    artist.set_clip_path(polygon)
    ax.set_xlabel(definition["xlabel"])
    ax.set_ylabel(definition["ylabel"])
    ax.set_xlim(*definition["default_xlim"])
    ax.set_ylim(*definition["default_ylim"])
    ax.set_aspect("equal", adjustable="box")
    finish_figure(fig)
    return fig, ax


def plot_xy_chromaticity_background(
    *,
    ax=None,
    samples: int = 256,
    alpha: float = 1.0,
    normalise: bool = True,
):
    """Plot the CIE 1931 xy chromaticity diagram background."""
    return plot_chromaticity_background(
        method="CIE 1931",
        ax=ax,
        samples=samples,
        alpha=alpha,
        normalise=normalise,
    )


def plot_cie1931_diagram(
    *,
    ax=None,
    title: str = "CIE 1931 xy",
    whitepoint_xy: Sequence[float] | None = D65_XY,
    show_sample_points: bool = True,
    close_locus: bool = True,
    show_background: bool = False,
    background_samples: int = 256,
    background_alpha: float = 1.0,
    background_normalise: bool = True,
):
    """Plot the CIE 1931 xy chromaticity diagram."""
    if show_background:
        fig, ax = plot_xy_chromaticity_background(
            ax=ax,
            samples=background_samples,
            alpha=background_alpha,
            normalise=background_normalise,
        )
    else:
        fig, ax = get_figure_axes(ax, figsize=(5.2, 5.0))
    locus_xy = load_cie1931_locus_xy()
    line_xy = np.vstack([locus_xy, locus_xy[0]]) if close_locus else locus_xy
    ax.plot(line_xy[:, 0], line_xy[:, 1], color="0.25", linewidth=1.4, zorder=2)
    if show_sample_points:
        ax.scatter(
            locus_xy[::40, 0],
            locus_xy[::40, 1],
            s=10,
            color="0.45",
            alpha=0.7,
            zorder=3,
        )
    if whitepoint_xy is not None:
        white = np.asarray(whitepoint_xy, dtype=np.float64)
        if white.shape != (2,):
            raise ValueError("whitepoint_xy must have shape (2,)")
        ax.scatter(*white, s=42, color="black", label="white", zorder=4)
        ax.legend()
    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_xlim(0.0, 0.8)
    ax.set_ylim(0.0, 0.9)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.25)
    finish_figure(fig)
    return fig, ax


def _plot_chromaticity_locus(
    *,
    method: str,
    ax=None,
    title: str,
    whitepoint: Sequence[float] | None,
    whitepoint_name: str,
    show_sample_points: bool,
    close_locus: bool,
    show_background: bool,
    background_samples: int,
    background_alpha: float,
    background_normalise: bool,
):
    """Plot a spectral locus in a configured chromaticity diagram."""
    definition = _resolve_chromaticity_method(method)
    if show_background:
        fig, ax = plot_chromaticity_background(
            method=method,
            ax=ax,
            samples=background_samples,
            alpha=background_alpha,
            normalise=background_normalise,
        )
    else:
        fig, ax = get_figure_axes(ax, figsize=(5.2, 5.0))
    locus = _spectral_locus_for_method(method)
    line = np.vstack([locus, locus[0]]) if close_locus else locus
    ax.plot(line[:, 0], line[:, 1], color="0.25", linewidth=1.4, zorder=2)
    if show_sample_points:
        ax.scatter(
            locus[::40, 0],
            locus[::40, 1],
            s=10,
            color="0.45",
            alpha=0.7,
            zorder=3,
        )
    if whitepoint is not None:
        white = np.asarray(whitepoint, dtype=np.float64)
        if white.shape != (2,):
            raise ValueError(f"{whitepoint_name} must have shape (2,)")
        ax.scatter(*white, s=42, color="black", label="white", zorder=4)
        ax.legend()
    ax.set_title(title)
    ax.set_xlabel(definition["xlabel"])
    ax.set_ylabel(definition["ylabel"])
    ax.set_xlim(*definition["default_xlim"])
    ax.set_ylim(*definition["default_ylim"])
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.25)
    finish_figure(fig)
    return fig, ax


def plot_cie1960_ucs_diagram(
    *,
    ax=None,
    title: str = "CIE 1960 UCS uv",
    whitepoint_uv: Sequence[float] | None = D65_UV1960,
    show_sample_points: bool = True,
    close_locus: bool = True,
    show_background: bool = False,
    background_samples: int = 256,
    background_alpha: float = 1.0,
    background_normalise: bool = True,
):
    """Plot the CIE 1960 UCS uv chromaticity diagram."""
    return _plot_chromaticity_locus(
        method="CIE 1960 UCS",
        ax=ax,
        title=title,
        whitepoint=whitepoint_uv,
        whitepoint_name="whitepoint_uv",
        show_sample_points=show_sample_points,
        close_locus=close_locus,
        show_background=show_background,
        background_samples=background_samples,
        background_alpha=background_alpha,
        background_normalise=background_normalise,
    )


def plot_cie1976_ucs_diagram(
    *,
    ax=None,
    title: str = "CIE 1976 UCS u'v'",
    whitepoint_upvp: Sequence[float] | None = D65_UPVP1976,
    show_sample_points: bool = True,
    close_locus: bool = True,
    show_background: bool = False,
    background_samples: int = 256,
    background_alpha: float = 1.0,
    background_normalise: bool = True,
):
    """Plot the CIE 1976 UCS u'v' chromaticity diagram."""
    return _plot_chromaticity_locus(
        method="CIE 1976 UCS",
        ax=ax,
        title=title,
        whitepoint=whitepoint_upvp,
        whitepoint_name="whitepoint_upvp",
        show_sample_points=show_sample_points,
        close_locus=close_locus,
        show_background=show_background,
        background_samples=background_samples,
        background_alpha=background_alpha,
        background_normalise=background_normalise,
    )


def plot_xy_points(
    xy: Sequence[Sequence[float]] | np.ndarray,
    *,
    ax=None,
    labels: Iterable[str] | None = None,
    color: str = "tab:red",
    marker: str = "o",
    title: str | None = None,
    **kwargs,
):
    """Plot xy points on an existing or new axes."""
    fig, ax = get_figure_axes(ax, figsize=(5.2, 5.0))
    xy_arr = as_2d_points(xy, size=2, name="xy")
    ax.scatter(xy_arr[:, 0], xy_arr[:, 1], color=color, marker=marker, zorder=3, **kwargs)
    if labels is not None:
        for point, label in zip(xy_arr, labels):
            ax.annotate(
                label,
                xy=point,
                xytext=(6, 6),
                textcoords="offset points",
                fontsize=8,
            )
    if title is not None:
        ax.set_title(title)
    finish_figure(fig)
    return fig, ax


plot_xy_locus = plot_cie1931_diagram
plot_uv1960_locus = plot_cie1960_ucs_diagram
plot_upvp1976_locus = plot_cie1976_ucs_diagram


__all__ = [
    "D65_XY",
    "D65_UV1960",
    "D65_UPVP1976",
    "chromaticity_background_image",
    "load_cie1931_locus_uv1960",
    "load_cie1931_locus_upvp1976",
    "load_cie1931_locus_xy",
    "plot_chromaticity_background",
    "plot_cie1931_diagram",
    "plot_cie1960_ucs_diagram",
    "plot_cie1976_ucs_diagram",
    "plot_upvp1976_locus",
    "plot_uv1960_locus",
    "plot_xy_chromaticity_background",
    "plot_xy_locus",
    "plot_xy_points",
]
