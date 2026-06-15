"""Basic three-dimensional plotting primitives."""

from __future__ import annotations

from itertools import cycle
from typing import Sequence

import numpy as np

from .common import finish_figure


def get_3d_figure_axes(
    ax=None,
    *,
    figsize: tuple[float, float] = (5.2, 4.2),
):
    """Return ``(fig, ax)`` using an existing or new 3D axes.

    Notes
    -----
    Existing axes must be Matplotlib 3D axes. New axes are created with
    ``projection="3d"``.
    """
    import matplotlib.pyplot as plt

    if ax is None:
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection="3d")
        return fig, ax

    if getattr(ax, "name", None) != "3d":
        raise ValueError("ax must be a 3D matplotlib axes")
    return ax.figure, ax


def _as_1d_float_array(value, *, name: str) -> np.ndarray:
    """Return *value* as a finite one-dimensional float array."""
    array = np.asarray(value, dtype=np.float64)
    if array.ndim != 1:
        raise ValueError(f"{name} must be a one-dimensional array")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} values must be finite")
    return array


def _as_3d_point_group(value, *, name: str) -> np.ndarray:
    """Return *value* as ``(n, 3)`` finite point rows."""
    points = np.asarray(value, dtype=np.float64)
    if points.ndim == 1:
        if points.shape != (3,):
            raise ValueError(f"{name} must have shape (3,) or (n, 3)")
        points = points.reshape(1, 3)
    if points.ndim != 2 or points.shape[-1] != 3:
        raise ValueError(f"{name} must have shape (3,) or (n, 3)")
    if not np.all(np.isfinite(points)):
        raise ValueError(f"{name} values must be finite")
    return points


def _normalise_3d_point_groups(points) -> list[np.ndarray]:
    """Return point input as a list of ``(n, 3)`` arrays."""
    try:
        array = np.asarray(points, dtype=np.float64)
    except (TypeError, ValueError):
        array = None

    if array is not None and array.ndim in (1, 2):
        return [_as_3d_point_group(array, name="points")]

    groups = list(points)
    if not groups:
        raise ValueError("points must not be empty")
    return [_as_3d_point_group(group, name=f"points[{index}]") for index, group in enumerate(groups)]


def _is_xyz_series(value) -> bool:
    """Return whether *value* looks like a single ``(x, y, z)`` series."""
    if not isinstance(value, tuple) or len(value) != 3:
        return False
    try:
        x = np.asarray(value[0], dtype=np.float64)
        y = np.asarray(value[1], dtype=np.float64)
        z = np.asarray(value[2], dtype=np.float64)
    except (TypeError, ValueError):
        return False
    return x.ndim == 1 and y.ndim == 1 and z.ndim == 1


def _normalise_3d_line_series(series) -> list[tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """Return line series as a list of ``(x, y, z)`` arrays."""
    raw_series = [series] if _is_xyz_series(series) else list(series)
    if not raw_series:
        raise ValueError("series must not be empty")

    result: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []
    for index, item in enumerate(raw_series):
        if not _is_xyz_series(item):
            raise ValueError("each 3D line series must be a tuple (x, y, z)")
        x = _as_1d_float_array(item[0], name=f"series[{index}].x")
        y = _as_1d_float_array(item[1], name=f"series[{index}].y")
        z = _as_1d_float_array(item[2], name=f"series[{index}].z")
        if x.shape != y.shape or x.shape != z.shape:
            raise ValueError("x, y and z must have the same length for each line series")
        result.append((x, y, z))
    return result


def _normalise_optional_sequence(value, count: int, *, name: str):
    """Return *value* as a list matching *count*, or ``None``."""
    if value is None:
        return None
    if isinstance(value, str):
        values = [value]
    else:
        values = list(value)
    if len(values) != count:
        raise ValueError(f"{name} length must match the number of plotted groups")
    return values


def _pop_marker_size_alias(kwargs: dict, sizes):
    """Return marker sizes after consuming Matplotlib's ``s`` alias."""
    if "s" not in kwargs:
        return sizes
    if not (np.isscalar(sizes) and sizes == 36):
        raise ValueError("use either sizes or s, not both")
    return kwargs.pop("s")


def _as_surface_grid(X, Y, Z) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return finite matching 2D surface grids."""
    x = np.asarray(X, dtype=np.float64)
    y = np.asarray(Y, dtype=np.float64)
    z = np.asarray(Z, dtype=np.float64)
    if x.ndim != 2 or y.ndim != 2 or z.ndim != 2:
        raise ValueError("X, Y and Z must be two-dimensional arrays")
    if x.shape != y.shape or x.shape != z.shape:
        raise ValueError("X, Y and Z must have matching shapes")
    if x.size == 0:
        raise ValueError("surface grids must not be empty")
    if not (np.all(np.isfinite(x)) and np.all(np.isfinite(y)) and np.all(np.isfinite(z))):
        raise ValueError("surface grid values must be finite")
    return x, y, z


def style_3d_axis(
    ax,
    *,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    zlabel: str | None = None,
    grid: bool = True,
    equal_aspect: bool = False,
    view: tuple[float, float] | None = None,
):
    """Apply common styling to a three-dimensional Matplotlib axes.

    Notes
    -----
    This helper only styles axes. It does not compute or rescale 3D data.
    """
    if getattr(ax, "name", None) != "3d":
        raise ValueError("ax must be a 3D matplotlib axes")
    if title is not None:
        ax.set_title(title)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    if zlabel is not None:
        ax.set_zlabel(zlabel)
    ax.grid(grid)
    if equal_aspect:
        ax.set_box_aspect((1.0, 1.0, 1.0))
    if view is not None:
        if len(view) != 2:
            raise ValueError("view must be a tuple (elev, azim)")
        ax.view_init(elev=float(view[0]), azim=float(view[1]))
    return ax


def plot_3d_points(
    points,
    *,
    ax=None,
    labels: Sequence[str] | None = None,
    colors: Sequence[str] | str | None = None,
    markers: Sequence[str] | str | None = None,
    sizes: Sequence[float] | float = 36,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    zlabel: str | None = None,
    grid: bool = True,
    legend: str | bool = "auto",
    view: tuple[float, float] | None = None,
    **kwargs,
):
    """Plot one or more groups of 3D points.

    Notes
    -----
    ``points`` accepts one ``(n, 3)`` array or multiple point groups. The
    function returns ``(fig, ax)`` and never saves or shows the figure.
    """
    if "label" in kwargs:
        if labels is not None:
            raise ValueError("use either labels or label, not both")
        labels = kwargs.pop("label")
    if "marker" in kwargs:
        if markers is not None:
            raise ValueError("use either markers or marker, not both")
        markers = kwargs.pop("marker")
    sizes = _pop_marker_size_alias(kwargs, sizes)

    groups = _normalise_3d_point_groups(points)
    labels_list = _normalise_optional_sequence(labels, len(groups), name="labels")
    colors_list = _normalise_optional_sequence(colors, len(groups), name="colors")
    markers_list = _normalise_optional_sequence(markers, len(groups), name="markers")

    if np.isscalar(sizes):
        sizes_list = [sizes] * len(groups)
    else:
        sizes_list = list(sizes)
        if len(sizes_list) != len(groups):
            raise ValueError("sizes length must match the number of plotted groups")

    fig, ax = get_3d_figure_axes(ax)
    color_iter = cycle(colors_list) if colors_list is not None else cycle([None])
    marker_iter = cycle(markers_list) if markers_list is not None else cycle(["o"])

    for index, group in enumerate(groups):
        scatter_kwargs = dict(kwargs)
        color = next(color_iter)
        if color is not None:
            scatter_kwargs["color"] = color
        ax.scatter(
            group[:, 0],
            group[:, 1],
            group[:, 2],
            label=labels_list[index] if labels_list is not None else None,
            marker=next(marker_iter),
            s=sizes_list[index],
            **scatter_kwargs,
        )

    style_3d_axis(
        ax,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        zlabel=zlabel,
        grid=grid,
        view=view,
    )
    if legend is True or (legend == "auto" and labels_list is not None):
        ax.legend()
    finish_figure(fig)
    return fig, ax


def plot_3d_lines(
    series,
    *,
    ax=None,
    labels: Sequence[str] | None = None,
    colors: Sequence[str] | None = None,
    linestyles: Sequence[str] | None = None,
    linewidth: float = 1.5,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    zlabel: str | None = None,
    grid: bool = True,
    legend: str | bool = "auto",
    view: tuple[float, float] | None = None,
    **kwargs,
):
    """Plot one or more 3D line series.

    Notes
    -----
    ``series`` follows the 2D ``plot_lines`` pattern, but each series is an
    ``(x, y, z)`` tuple of equal-length one-dimensional arrays.
    """
    if "label" in kwargs:
        if labels is not None:
            raise ValueError("use either labels or label, not both")
        labels = kwargs.pop("label")

    line_series = _normalise_3d_line_series(series)
    labels_list = _normalise_optional_sequence(labels, len(line_series), name="labels")
    colors_list = _normalise_optional_sequence(colors, len(line_series), name="colors")
    linestyles_list = _normalise_optional_sequence(linestyles, len(line_series), name="linestyles")

    fig, ax = get_3d_figure_axes(ax)
    color_iter = cycle(colors_list) if colors_list is not None else cycle([None])
    style_iter = cycle(linestyles_list) if linestyles_list is not None else cycle([None])

    for index, (x, y, z) in enumerate(line_series):
        line_kwargs = dict(kwargs)
        color = next(color_iter)
        linestyle = next(style_iter)
        if color is not None:
            line_kwargs["color"] = color
        if linestyle is not None:
            line_kwargs["linestyle"] = linestyle
        ax.plot(
            x,
            y,
            z,
            label=labels_list[index] if labels_list is not None else None,
            linewidth=linewidth,
            **line_kwargs,
        )

    style_3d_axis(
        ax,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        zlabel=zlabel,
        grid=grid,
        view=view,
    )
    if legend is True or (legend == "auto" and labels_list is not None):
        ax.legend()
    finish_figure(fig)
    return fig, ax


def plot_3d_surface(
    X,
    Y,
    Z,
    *,
    ax=None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    zlabel: str | None = None,
    cmap: str | None = None,
    color: str | None = None,
    alpha: float = 0.75,
    linewidth: float = 0.0,
    antialiased: bool = True,
    colorbar: bool = False,
    grid: bool = True,
    view: tuple[float, float] | None = None,
    **kwargs,
):
    """Plot a 3D surface from matching ``X``, ``Y`` and ``Z`` grids.

    Notes
    -----
    Surface grids must be finite matching 2D arrays. This is a plotting
    primitive; gamut or colour-space surfaces must be computed elsewhere.
    """
    x, y, z = _as_surface_grid(X, Y, Z)
    fig, ax = get_3d_figure_axes(ax)
    surface = ax.plot_surface(
        x,
        y,
        z,
        cmap=cmap,
        color=color,
        alpha=alpha,
        linewidth=linewidth,
        antialiased=antialiased,
        **kwargs,
    )
    style_3d_axis(
        ax,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        zlabel=zlabel,
        grid=grid,
        view=view,
    )
    if colorbar:
        fig.colorbar(surface, ax=ax, shrink=0.7, pad=0.1)
    finish_figure(fig)
    return fig, ax


def plot_3d_wireframe(
    X,
    Y,
    Z,
    *,
    ax=None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    zlabel: str | None = None,
    color: str | None = None,
    linewidth: float = 0.8,
    rstride: int = 1,
    cstride: int = 1,
    grid: bool = True,
    view: tuple[float, float] | None = None,
    **kwargs,
):
    """Plot a 3D wireframe from matching ``X``, ``Y`` and ``Z`` grids."""
    x, y, z = _as_surface_grid(X, Y, Z)
    fig, ax = get_3d_figure_axes(ax)
    wire_kwargs = dict(kwargs)
    if color is not None:
        wire_kwargs["color"] = color
    ax.plot_wireframe(
        x,
        y,
        z,
        linewidth=linewidth,
        rstride=rstride,
        cstride=cstride,
        **wire_kwargs,
    )
    style_3d_axis(
        ax,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        zlabel=zlabel,
        grid=grid,
        view=view,
    )
    finish_figure(fig)
    return fig, ax


def set_3d_axis_limits_from_data(
    ax,
    data,
    *,
    padding: float = 0.05,
    equal_aspect: bool = False,
):
    """Set 3D axis limits from finite data with final dimension 3.

    Notes
    -----
    Use ``equal_aspect=True`` for colour solids when geometric proportions
    matter more than filling the subplot rectangle.
    """
    if getattr(ax, "name", None) != "3d":
        raise ValueError("ax must be a 3D matplotlib axes")
    if padding < 0:
        raise ValueError("padding must be non-negative")

    values = np.asarray(data, dtype=np.float64)
    if values.size == 0:
        raise ValueError("data must not be empty")
    if values.shape[-1] != 3:
        raise ValueError("data must have a final dimension of 3")
    points = values.reshape(-1, 3)
    if not np.all(np.isfinite(points)):
        raise ValueError("data values must be finite")

    minimum = np.min(points, axis=0)
    maximum = np.max(points, axis=0)
    span = maximum - minimum
    fallback = np.where(span > 0.0, span, 1.0)
    pad = fallback * padding

    if equal_aspect:
        center = (minimum + maximum) / 2.0
        radius = np.max((fallback + 2.0 * pad) / 2.0)
        ax.set_xlim(center[0] - radius, center[0] + radius)
        ax.set_ylim(center[1] - radius, center[1] + radius)
        ax.set_zlim(center[2] - radius, center[2] + radius)
        ax.set_box_aspect((1.0, 1.0, 1.0))
    else:
        ax.set_xlim(minimum[0] - pad[0], maximum[0] + pad[0])
        ax.set_ylim(minimum[1] - pad[1], maximum[1] + pad[1])
        ax.set_zlim(minimum[2] - pad[2], maximum[2] + pad[2])
    return ax


__all__ = [
    "get_3d_figure_axes",
    "plot_3d_lines",
    "plot_3d_points",
    "plot_3d_surface",
    "plot_3d_wireframe",
    "set_3d_axis_limits_from_data",
    "style_3d_axis",
]
