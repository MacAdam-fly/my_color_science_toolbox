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

from .common import finish_figure, get_figure_axes
from .primitives import plot_labels, plot_points


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


_WAVELENGTH_LABELS_DEFAULT = {
    "CIE 1931": (
        390,
        460,
        470,
        480,
        490,
        500,
        510,
        520,
        540,
        560,
        580,
        600,
        620,
        700,
    ),
    "CIE 1960 UCS": (
        420,
        440,
        450,
        460,
        470,
        480,
        490,
        500,
        510,
        520,
        530,
        540,
        550,
        560,
        570,
        580,
        590,
        600,
        610,
        620,
        630,
        645,
        680,
    ),
    "CIE 1976 UCS": (
        420,
        440,
        450,
        460,
        470,
        480,
        490,
        500,
        510,
        520,
        530,
        540,
        550,
        560,
        570,
        580,
        590,
        600,
        610,
        620,
        630,
        645,
        680,
    ),
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


def _load_cie1931_locus_wavelengths_xy() -> tuple[np.ndarray, np.ndarray]:
    """Return CIE 1931 spectral locus wavelengths and xy coordinates."""
    locus = from_dataset(
        "standard_observers.chromaticity_coordinates",
        "cie1931_chro_1nm",
    )
    x_index = locus.labels.index("x")
    y_index = locus.labels.index("y")
    return (
        np.array(locus.wavelengths, copy=True),
        np.array(locus.values[:, (x_index, y_index)], copy=True),
    )


def load_cie1931_locus_xy() -> np.ndarray:
    """Return CIE 1931 spectral locus xy coordinates."""
    _wavelengths, xy = _load_cie1931_locus_wavelengths_xy()
    return xy


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


def _spectral_locus_wavelengths_for_method(method: str) -> tuple[np.ndarray, np.ndarray]:
    """Return wavelengths and locus coordinates for a chromaticity method."""
    definition = _resolve_chromaticity_method(method)
    wavelengths, xy = _load_cie1931_locus_wavelengths_xy()
    return wavelengths, definition["xy_to_ij"](xy)


def _wavelength_label_indices(
    wavelengths: np.ndarray,
    *,
    labels: Sequence[float] | None,
    interval: int | None,
    wavelength_range: tuple[float, float],
) -> np.ndarray:
    """Return indices of wavelengths to label."""
    if labels is None:
        if interval is None:
            raise ValueError("labels or interval must be provided")
        if interval <= 0:
            raise ValueError("wavelength_label_interval must be positive")
        start, end = wavelength_range
        if start > end:
            raise ValueError("wavelength_label_range start must be <= end")
        targets = np.arange(np.ceil(start / interval) * interval, end + 0.5, interval)
    else:
        targets = np.asarray(labels, dtype=np.float64)
        if targets.ndim != 1:
            raise ValueError("wavelength_labels must be one-dimensional")
        if not np.all(np.isfinite(targets)):
            raise ValueError("wavelength_labels must be finite")
    indices = [int(np.argmin(np.abs(wavelengths - target))) for target in targets]
    return np.array(sorted(set(indices)), dtype=int)


def _locus_label_normals(
    coordinates: np.ndarray,
    indices: np.ndarray,
    *,
    centre: np.ndarray,
) -> np.ndarray:
    """Return outward label normals following the spectral-locus tangent."""
    normals = []
    for index in indices:
        left = coordinates[max(index - 1, 0)]
        right = coordinates[min(index + 1, len(coordinates) - 1)]
        tangent = right - left
        if np.linalg.norm(tangent) == 0:
            direction = coordinates[index] - centre
        else:
            normal_a = np.array([-tangent[1], tangent[0]], dtype=np.float64)
            normal_b = -normal_a
            outward = coordinates[index] - centre
            direction = normal_a if np.dot(normal_a, outward) >= np.dot(normal_b, outward) else normal_b
        norm = np.linalg.norm(direction)
        normals.append(direction / norm if norm > 0 else np.zeros(2, dtype=np.float64))
    return np.asarray(normals, dtype=np.float64)


def plot_locus_wavelength_labels(
    wavelengths: Sequence[float] | np.ndarray,
    coordinates: Sequence[Sequence[float]] | np.ndarray,
    *,
    ax=None,
    labels: Sequence[float] | None = None,
    interval: int | None = None,
    wavelength_range: tuple[float, float] = (400.0, 700.0),
    whitepoint: Sequence[float] | np.ndarray | None = None,
    fontsize: float = 7.0,
    offset_scale: float = 0.025,
    color: str = "0.25",
):
    """Plot wavelength labels along a spectral locus."""
    wavelengths_arr = np.asarray(wavelengths, dtype=np.float64)
    coordinates_arr = np.asarray(coordinates, dtype=np.float64)
    if wavelengths_arr.ndim != 1:
        raise ValueError("wavelengths must be one-dimensional")
    if coordinates_arr.ndim != 2 or coordinates_arr.shape[-1] != 2:
        raise ValueError("coordinates must have shape (n, 2)")
    if coordinates_arr.shape[0] != wavelengths_arr.shape[0]:
        raise ValueError("wavelengths and coordinates must have matching lengths")
    if not np.all(np.isfinite(wavelengths_arr)) or not np.all(np.isfinite(coordinates_arr)):
        raise ValueError("wavelengths and coordinates must be finite")

    fig, ax = get_figure_axes(ax, figsize=(5.2, 5.0))
    indices = _wavelength_label_indices(
        wavelengths_arr,
        labels=labels,
        interval=interval,
        wavelength_range=wavelength_range,
    )
    label_points = coordinates_arr[indices]

    if whitepoint is None:
        centre = np.mean(coordinates_arr, axis=0)
    else:
        centre = np.asarray(whitepoint, dtype=np.float64)
        if centre.shape != (2,):
            raise ValueError("whitepoint must have shape (2,)")

    normals = _locus_label_normals(coordinates_arr, indices, centre=centre)
    offsets = normals * offset_scale
    for point, offset, wavelength in zip(label_points, offsets, wavelengths_arr[indices]):
        ax.annotate(
            f"{int(round(wavelength))}",
            xy=point,
            xytext=point + offset,
            textcoords="data",
            fontsize=fontsize,
            color=color,
            ha="center",
            va="center",
            zorder=5,
        )
    finish_figure(fig)
    return fig, ax


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
    title: str | None = None,
    whitepoint_xy: Sequence[float] | None = D65_XY,
    show_sample_points: bool = True,
    close_locus: bool = True,
    show_background: bool = False,
    background_samples: int = 256,
    background_alpha: float = 1.0,
    background_normalise: bool = True,
    show_wavelength_labels: bool = False,
    wavelength_labels: Sequence[float] | None = None,
    wavelength_label_interval: int | None = None,
    wavelength_label_range: tuple[float, float] = (400.0, 700.0),
    wavelength_label_fontsize: float = 7.0,
):
    """Plot the CIE 1931 xy chromaticity diagram."""
    using_existing_axes = ax is not None
    if show_background:
        fig, ax = plot_xy_chromaticity_background(
            ax=ax,
            samples=background_samples,
            alpha=background_alpha,
            normalise=background_normalise,
        )
    else:
        fig, ax = get_figure_axes(ax, figsize=(5.2, 5.0))
    wavelengths, locus_xy = _load_cie1931_locus_wavelengths_xy()
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
    if show_wavelength_labels:
        plot_locus_wavelength_labels(
            wavelengths,
            locus_xy,
            ax=ax,
            labels=_WAVELENGTH_LABELS_DEFAULT["CIE 1931"] if wavelength_labels is None else wavelength_labels,
            interval=wavelength_label_interval,
            wavelength_range=wavelength_label_range,
            whitepoint=whitepoint_xy if whitepoint_xy is not None else D65_XY,
            fontsize=wavelength_label_fontsize,
        )
    if title:
        ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_xlim(0.0, 0.8)
    ax.set_ylim(0.0, 0.9)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.25)
    finish_figure(fig, tight_layout=not using_existing_axes)
    return fig, ax


def _plot_chromaticity_locus(
    *,
    method: str,
    ax=None,
    title: str | None,
    whitepoint: Sequence[float] | None,
    whitepoint_name: str,
    show_sample_points: bool,
    close_locus: bool,
    show_background: bool,
    background_samples: int,
    background_alpha: float,
    background_normalise: bool,
    show_wavelength_labels: bool,
    wavelength_labels: Sequence[float] | None,
    wavelength_label_interval: int | None,
    wavelength_label_range: tuple[float, float],
    wavelength_label_fontsize: float,
):
    """Plot a spectral locus in a configured chromaticity diagram."""
    using_existing_axes = ax is not None
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
    wavelengths, locus = _spectral_locus_wavelengths_for_method(method)
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
    if show_wavelength_labels:
        label_whitepoint = whitepoint
        if label_whitepoint is None:
            if method == "CIE 1960 UCS":
                label_whitepoint = D65_UV1960
            elif method == "CIE 1976 UCS":
                label_whitepoint = D65_UPVP1976
        plot_locus_wavelength_labels(
            wavelengths,
            locus,
            ax=ax,
            labels=_WAVELENGTH_LABELS_DEFAULT[method] if wavelength_labels is None else wavelength_labels,
            interval=wavelength_label_interval,
            wavelength_range=wavelength_label_range,
            whitepoint=label_whitepoint,
            fontsize=wavelength_label_fontsize,
        )
    if title:
        ax.set_title(title)
    ax.set_xlabel(definition["xlabel"])
    ax.set_ylabel(definition["ylabel"])
    ax.set_xlim(*definition["default_xlim"])
    ax.set_ylim(*definition["default_ylim"])
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.25)
    finish_figure(fig, tight_layout=not using_existing_axes)
    return fig, ax


def plot_cie1960_ucs_diagram(
    *,
    ax=None,
    title: str | None = None,
    whitepoint_uv: Sequence[float] | None = D65_UV1960,
    show_sample_points: bool = True,
    close_locus: bool = True,
    show_background: bool = False,
    background_samples: int = 256,
    background_alpha: float = 1.0,
    background_normalise: bool = True,
    show_wavelength_labels: bool = False,
    wavelength_labels: Sequence[float] | None = None,
    wavelength_label_interval: int | None = None,
    wavelength_label_range: tuple[float, float] = (400.0, 700.0),
    wavelength_label_fontsize: float = 7.0,
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
        show_wavelength_labels=show_wavelength_labels,
        wavelength_labels=wavelength_labels,
        wavelength_label_interval=wavelength_label_interval,
        wavelength_label_range=wavelength_label_range,
        wavelength_label_fontsize=wavelength_label_fontsize,
    )


def plot_cie1976_ucs_diagram(
    *,
    ax=None,
    title: str | None = None,
    whitepoint_upvp: Sequence[float] | None = D65_UPVP1976,
    show_sample_points: bool = True,
    close_locus: bool = True,
    show_background: bool = False,
    background_samples: int = 256,
    background_alpha: float = 1.0,
    background_normalise: bool = True,
    show_wavelength_labels: bool = False,
    wavelength_labels: Sequence[float] | None = None,
    wavelength_label_interval: int | None = None,
    wavelength_label_range: tuple[float, float] = (400.0, 700.0),
    wavelength_label_fontsize: float = 7.0,
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
        show_wavelength_labels=show_wavelength_labels,
        wavelength_labels=wavelength_labels,
        wavelength_label_interval=wavelength_label_interval,
        wavelength_label_range=wavelength_label_range,
        wavelength_label_fontsize=wavelength_label_fontsize,
    )


def plot_chromaticity_points(
    xy: Sequence[Sequence[float]] | np.ndarray,
    *,
    ax=None,
    labels: Iterable[str] | None = None,
    color: str = "tab:red",
    marker: str = "o",
    title: str | None = None,
    **kwargs,
):
    """Plot chromaticity points on an existing or new axes."""
    fig, ax = plot_points(
        xy,
        ax=ax,
        labels=None,
        colors=color,
        markers=marker,
        title=title,
        annotate=False,
        zorder=3,
        **kwargs,
    )
    if labels is not None:
        plot_labels(xy, labels, ax=ax, grid=False)
    return fig, ax


def plot_xy_points(*args, **kwargs):
    """Plot CIE xy points.

    This compatibility wrapper delegates to ``plot_chromaticity_points``.
    Prefer ``plot_chromaticity_points`` for new code.
    """
    return plot_chromaticity_points(*args, **kwargs)



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
    "plot_chromaticity_points",
    "plot_locus_wavelength_labels",
    "plot_xy_chromaticity_background",
    "plot_xy_points",
]
