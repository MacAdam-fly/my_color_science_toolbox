"""Basic two-dimensional plotting primitives."""

from __future__ import annotations

from itertools import cycle
from typing import Iterable, Sequence

import numpy as np

from .common import finish_figure, get_figure_axes


def _as_1d_float_array(value, *, name: str) -> np.ndarray:
    """Return *value* as a finite one-dimensional float array."""
    array = np.asarray(value, dtype=np.float64)
    if array.ndim != 1:
        raise ValueError(f"{name} must be a one-dimensional array")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} values must be finite")
    return array


def _is_xy_pair(value) -> bool:
    """Return whether *value* looks like a single ``(x, y)`` pair."""
    if not isinstance(value, tuple) or len(value) != 2:
        return False
    try:
        x = np.asarray(value[0], dtype=np.float64)
        y = np.asarray(value[1], dtype=np.float64)
    except (TypeError, ValueError):
        return False
    return x.ndim == 1 and y.ndim == 1


def _normalise_line_series(series) -> list[tuple[np.ndarray, np.ndarray]]:
    """Return line series as a list of ``(x, y)`` arrays."""
    raw_series = [series] if _is_xy_pair(series) else list(series)
    if not raw_series:
        raise ValueError("series must not be empty")

    result: list[tuple[np.ndarray, np.ndarray]] = []
    for index, item in enumerate(raw_series):
        if not _is_xy_pair(item):
            raise ValueError("each line series must be a tuple (x, y)")
        x = _as_1d_float_array(item[0], name=f"series[{index}].x")
        y = _as_1d_float_array(item[1], name=f"series[{index}].y")
        if x.shape != y.shape:
            raise ValueError("x and y must have the same length for each line series")
        result.append((x, y))
    return result


def _as_point_group(value, *, name: str) -> np.ndarray:
    """Return *value* as ``(n, 2)`` finite point rows."""
    points = np.asarray(value, dtype=np.float64)
    if points.ndim == 1:
        if points.shape != (2,):
            raise ValueError(f"{name} must have shape (2,) or (n, 2)")
        points = points.reshape(1, 2)
    if points.ndim != 2 or points.shape[-1] != 2:
        raise ValueError(f"{name} must have shape (2,) or (n, 2)")
    if not np.all(np.isfinite(points)):
        raise ValueError(f"{name} values must be finite")
    return points


def _normalise_point_groups(points) -> list[np.ndarray]:
    """Return point input as a list of ``(n, 2)`` arrays."""
    try:
        array = np.asarray(points, dtype=np.float64)
    except (TypeError, ValueError):
        array = None

    if array is not None and array.ndim in (1, 2):
        return [_as_point_group(array, name="points")]

    groups = list(points)
    if not groups:
        raise ValueError("points must not be empty")
    return [_as_point_group(group, name=f"points[{index}]") for index, group in enumerate(groups)]


def _as_segment_group(value, *, name: str) -> np.ndarray:
    """Return *value* as ``(n, 2, 2)`` finite line segments."""
    segments = np.asarray(value, dtype=np.float64)
    if segments.shape == (2, 2):
        segments = segments.reshape(1, 2, 2)
    if segments.ndim != 3 or segments.shape[-2:] != (2, 2):
        raise ValueError(f"{name} must have shape (2, 2) or (n, 2, 2)")
    if not np.all(np.isfinite(segments)):
        raise ValueError(f"{name} values must be finite")
    return segments


def _normalise_segment_groups(segments) -> list[np.ndarray]:
    """Return segment input as a list of ``(n, 2, 2)`` arrays."""
    try:
        array = np.asarray(segments, dtype=np.float64)
    except (TypeError, ValueError):
        array = None

    if array is not None and array.ndim in (2, 3):
        return [_as_segment_group(array, name="segments")]

    groups = list(segments)
    if not groups:
        raise ValueError("segments must not be empty")
    return [_as_segment_group(group, name=f"segments[{index}]") for index, group in enumerate(groups)]


def _as_polygon_group(value, *, name: str) -> np.ndarray:
    """Return *value* as ``(n, 2)`` finite polygon vertices."""
    polygon = np.asarray(value, dtype=np.float64)
    if polygon.ndim != 2 or polygon.shape[-1] != 2:
        raise ValueError(f"{name} must have shape (n, 2)")
    if polygon.shape[0] < 3:
        raise ValueError(f"{name} must contain at least three vertices")
    if not np.all(np.isfinite(polygon)):
        raise ValueError(f"{name} values must be finite")
    return polygon


def _normalise_polygon_groups(polygons) -> list[np.ndarray]:
    """Return polygon input as a list of ``(n, 2)`` arrays."""
    try:
        array = np.asarray(polygons, dtype=np.float64)
    except (TypeError, ValueError):
        array = None

    if array is not None and array.ndim == 2:
        return [_as_polygon_group(array, name="polygons")]
    if array is not None and array.ndim == 3 and array.shape[-1] == 2:
        return [_as_polygon_group(item, name=f"polygons[{index}]") for index, item in enumerate(array)]

    groups = list(polygons)
    if not groups:
        raise ValueError("polygons must not be empty")
    return [_as_polygon_group(group, name=f"polygons[{index}]") for index, group in enumerate(groups)]


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


def _as_broadcast_point_pairs(starts, ends) -> tuple[np.ndarray, np.ndarray]:
    """Return matching ``(n, 2)`` start and end point arrays."""
    starts_arr = _as_point_group(starts, name="starts")
    ends_arr = _as_point_group(ends, name="ends")
    if starts_arr.shape[0] == 1 and ends_arr.shape[0] > 1:
        starts_arr = np.broadcast_to(starts_arr, ends_arr.shape)
    elif ends_arr.shape[0] == 1 and starts_arr.shape[0] > 1:
        ends_arr = np.broadcast_to(ends_arr, starts_arr.shape)
    elif starts_arr.shape != ends_arr.shape:
        raise ValueError("starts and ends must have matching point counts")
    return starts_arr, ends_arr


def style_2d_axis(
    ax,
    *,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    grid: bool = True,
    equal_aspect: bool = False,
):
    """Apply common styling to a two-dimensional Matplotlib axes.

    Parameters
    ----------
    ax
        Matplotlib 2D axes.
    title, xlabel, ylabel
        Optional axes text.
    grid
        Whether to show a light grid.
    equal_aspect
        Whether to force equal data aspect.

    Returns
    -------
    axes
        The same axes object.

    Notes
    -----
    This helper only mutates the supplied axes. It does not save, show or
    create figures.
    """
    if title is not None:
        ax.set_title(title)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    if grid:
        ax.grid(True, alpha=0.25)
    if equal_aspect:
        ax.set_aspect("equal", adjustable="box")
    return ax


def plot_lines(
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
    grid: bool = True,
    legend: str | bool = "auto",
    **kwargs,
):
    """Plot one or more 2D line series.

    Parameters
    ----------
    series
        Single ``(x, y)`` tuple or a sequence of ``(x, y)`` tuples. Each
        ``x`` and ``y`` must be a finite one-dimensional array of equal
        length.
    ax
        Optional existing axes. If omitted, a new figure and axes are created.
    labels, colors, linestyles
        Optional per-series styling.

    Returns
    -------
    fig, ax
        Matplotlib figure and axes.

    Notes
    -----
    The function never calls ``show`` or saves files. Style presets set
    Matplotlib defaults; explicit ``colors`` or ``linewidth`` arguments here
    take precedence.

    Examples
    --------
    >>> import numpy as np
    >>> x = np.linspace(0, 1, 5)
    >>> fig, ax = plot_lines((x, x**2), xlabel="x")
    >>> ax.get_xlabel()
    'x'
    """
    line_series = _normalise_line_series(series)
    labels_list = _normalise_optional_sequence(labels, len(line_series), name="labels")
    colors_list = _normalise_optional_sequence(colors, len(line_series), name="colors")
    linestyles_list = _normalise_optional_sequence(linestyles, len(line_series), name="linestyles")

    fig, ax = get_figure_axes(ax)
    color_iter = cycle(colors_list) if colors_list is not None else cycle([None])
    style_iter = cycle(linestyles_list) if linestyles_list is not None else cycle([None])

    for index, (x, y) in enumerate(line_series):
        label = labels_list[index] if labels_list is not None else None
        color = next(color_iter)
        linestyle = next(style_iter)
        line_kwargs = dict(kwargs)
        if color is not None:
            line_kwargs["color"] = color
        if linestyle is not None:
            line_kwargs["linestyle"] = linestyle
        ax.plot(x, y, label=label, linewidth=linewidth, **line_kwargs)

    style_2d_axis(ax, title=title, xlabel=xlabel, ylabel=ylabel, grid=grid)
    if legend is True or (legend == "auto" and labels_list is not None):
        ax.legend()
    finish_figure(fig)
    return fig, ax


def plot_points(
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
    grid: bool = True,
    annotate: bool = False,
    legend: str | bool = "auto",
    **kwargs,
):
    """Plot one or more groups of 2D points.

    Parameters
    ----------
    points
        One ``(n, 2)`` array, one ``(2,)`` point or a sequence of point groups.
    labels
        Group labels by default. With ``annotate=True`` and a single group,
        labels annotate individual points.

    Returns
    -------
    fig, ax
        Matplotlib figure and axes.

    Notes
    -----
    Use ``plot_points(...)`` for markers and ``plot_labels(...)`` for separate
    text placement when you need more control than ``annotate=True``.
    """
    groups = _normalise_point_groups(points)
    labels_list = _normalise_optional_sequence(labels, len(groups), name="labels") if not annotate else labels
    colors_list = _normalise_optional_sequence(colors, len(groups), name="colors")
    markers_list = _normalise_optional_sequence(markers, len(groups), name="markers")

    if np.isscalar(sizes):
        sizes_list = [sizes] * len(groups)
    else:
        sizes_list = list(sizes)
        if len(sizes_list) != len(groups):
            raise ValueError("sizes length must match the number of plotted groups")

    fig, ax = get_figure_axes(ax, figsize=(5.2, 5.0))
    color_iter = cycle(colors_list) if colors_list is not None else cycle([None])
    marker_iter = cycle(markers_list) if markers_list is not None else cycle(["o"])

    for index, group in enumerate(groups):
        label = labels_list[index] if labels_list is not None and not annotate else None
        color = next(color_iter)
        marker = next(marker_iter)
        scatter_kwargs = dict(kwargs)
        if color is not None:
            scatter_kwargs["color"] = color
        ax.scatter(
            group[:, 0],
            group[:, 1],
            label=label,
            marker=marker,
            s=sizes_list[index],
            **scatter_kwargs,
        )

    if annotate:
        if len(groups) != 1:
            raise ValueError("annotate=True supports a single point group")
        if labels is None:
            raise ValueError("labels must be provided when annotate=True")
        point_labels = list(labels)
        if len(point_labels) != groups[0].shape[0]:
            raise ValueError("labels length must match number of points when annotate=True")
        for point, label in zip(groups[0], point_labels):
            ax.annotate(
                label,
                xy=point,
                xytext=(6, 6),
                textcoords="offset points",
                fontsize=8,
            )

    style_2d_axis(ax, title=title, xlabel=xlabel, ylabel=ylabel, grid=grid)
    if legend is True or (legend == "auto" and labels_list is not None and not annotate):
        ax.legend()
    finish_figure(fig)
    return fig, ax


def plot_labels(
    points,
    labels: Sequence[str],
    *,
    ax=None,
    offset: tuple[float, float] = (6.0, 6.0),
    fontsize: float = 8.0,
    bbox=None,
    title: str | None = None,
    grid: bool = True,
    **kwargs,
):
    """Plot text labels at 2D point coordinates.

    Notes
    -----
    This helper only adds text annotations. Plot markers separately with
    ``plot_points`` when needed.
    """
    point_arr = _as_point_group(points, name="points")
    labels_list = list(labels)
    if len(labels_list) != point_arr.shape[0]:
        raise ValueError("labels length must match number of points")

    fig, ax = get_figure_axes(ax, figsize=(5.2, 5.0))
    for point, label in zip(point_arr, labels_list):
        ax.annotate(
            label,
            xy=point,
            xytext=offset,
            textcoords="offset points",
            fontsize=fontsize,
            bbox=bbox,
            **kwargs,
        )
    style_2d_axis(ax, title=title, grid=grid)
    finish_figure(fig)
    return fig, ax


def plot_segments(
    segments,
    *,
    ax=None,
    labels: Sequence[str] | None = None,
    colors: Sequence[str] | str | None = None,
    linestyles: Sequence[str] | str | None = None,
    linewidth: float = 1.5,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    grid: bool = True,
    legend: str | bool = "auto",
    **kwargs,
):
    """Plot one or more groups of 2D line segments.

    Notes
    -----
    Segment input has shape ``(n, 2, 2)`` where each row is
    ``[[x0, y0], [x1, y1]]``. This is useful for dominant-wavelength rays,
    Duv offsets and gamut edges.
    """
    groups = _normalise_segment_groups(segments)
    labels_list = _normalise_optional_sequence(labels, len(groups), name="labels")
    colors_list = _normalise_optional_sequence(colors, len(groups), name="colors")
    linestyles_list = _normalise_optional_sequence(linestyles, len(groups), name="linestyles")

    fig, ax = get_figure_axes(ax, figsize=(5.2, 5.0))
    color_iter = cycle(colors_list) if colors_list is not None else cycle([None])
    style_iter = cycle(linestyles_list) if linestyles_list is not None else cycle([None])

    for index, group in enumerate(groups):
        color = next(color_iter)
        linestyle = next(style_iter)
        for segment_index, segment in enumerate(group):
            label = labels_list[index] if labels_list is not None and segment_index == 0 else None
            line_kwargs = dict(kwargs)
            if color is not None:
                line_kwargs["color"] = color
            if linestyle is not None:
                line_kwargs["linestyle"] = linestyle
            ax.plot(
                segment[:, 0],
                segment[:, 1],
                label=label,
                linewidth=linewidth,
                **line_kwargs,
            )

    style_2d_axis(ax, title=title, xlabel=xlabel, ylabel=ylabel, grid=grid)
    if legend is True or (legend == "auto" and labels_list is not None):
        ax.legend()
    finish_figure(fig)
    return fig, ax


def plot_polygons(
    polygons,
    *,
    ax=None,
    labels: Sequence[str] | None = None,
    edgecolors: Sequence[str] | str | None = None,
    facecolors: Sequence[str] | str | None = None,
    fill: bool = False,
    alpha: float = 1.0,
    linewidth: float = 1.5,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    grid: bool = True,
    legend: str | bool = "auto",
    **kwargs,
):
    """Plot one or more 2D polygons.

    Notes
    -----
    Polygons are drawing primitives only. The function does not compute
    convex hulls or perform colour-science geometry.
    """
    from matplotlib.patches import Polygon

    groups = _normalise_polygon_groups(polygons)
    labels_list = _normalise_optional_sequence(labels, len(groups), name="labels")
    edgecolors_list = _normalise_optional_sequence(edgecolors, len(groups), name="edgecolors")
    facecolors_list = _normalise_optional_sequence(facecolors, len(groups), name="facecolors")

    fig, ax = get_figure_axes(ax, figsize=(5.2, 5.0))
    edge_iter = cycle(edgecolors_list) if edgecolors_list is not None else cycle([None])
    face_iter = cycle(facecolors_list) if facecolors_list is not None else cycle([None])

    for index, polygon in enumerate(groups):
        edgecolor = next(edge_iter)
        facecolor = next(face_iter)
        if not fill and facecolor is None:
            facecolor = "none"
        patch = Polygon(
            polygon,
            closed=True,
            fill=fill,
            label=labels_list[index] if labels_list is not None else None,
            edgecolor=edgecolor,
            facecolor=facecolor,
            alpha=alpha,
            linewidth=linewidth,
            **kwargs,
        )
        ax.add_patch(patch)

    style_2d_axis(ax, title=title, xlabel=xlabel, ylabel=ylabel, grid=grid)
    if legend is True or (legend == "auto" and labels_list is not None):
        ax.legend()
    finish_figure(fig)
    return fig, ax


def plot_arrows(
    starts,
    ends,
    *,
    ax=None,
    color: str | None = None,
    linewidth: float = 1.2,
    mutation_scale: float = 12.0,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    grid: bool = True,
    **kwargs,
):
    """Plot one or more arrows from start points to end points.

    Notes
    -----
    ``starts`` and ``ends`` accept ``(2,)`` or ``(n, 2)`` arrays. A single
    start or end point is broadcast against multiple counterpart points.
    """
    from matplotlib.patches import FancyArrowPatch

    starts_arr, ends_arr = _as_broadcast_point_pairs(starts, ends)
    fig, ax = get_figure_axes(ax, figsize=(5.2, 5.0))
    for start, end in zip(starts_arr, ends_arr):
        arrow_kwargs = dict(kwargs)
        if color is not None:
            arrow_kwargs["color"] = color
        patch = FancyArrowPatch(
            start,
            end,
            arrowstyle="->",
            linewidth=linewidth,
            mutation_scale=mutation_scale,
            **arrow_kwargs,
        )
        ax.add_patch(patch)

    style_2d_axis(ax, title=title, xlabel=xlabel, ylabel=ylabel, grid=grid)
    finish_figure(fig)
    return fig, ax


def _as_image_array(value, *, name: str = "image", clip: bool = True) -> np.ndarray:
    """Return *value* as a finite 2D scalar or RGB(A) image array."""
    image = np.asarray(value, dtype=np.float64)
    if image.ndim == 2:
        pass
    elif image.ndim == 3 and image.shape[-1] in (3, 4):
        if clip:
            image = np.clip(image, 0.0, 1.0)
    else:
        raise ValueError(f"{name} must have shape (height, width) or (height, width, 3/4)")
    if image.shape[0] == 0 or image.shape[1] == 0:
        raise ValueError(f"{name} must not be empty")
    if not np.all(np.isfinite(image)):
        raise ValueError(f"{name} values must be finite")
    return image


def plot_image(
    image,
    *,
    ax=None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    extent: tuple[float, float, float, float] | None = None,
    origin: str = "upper",
    cmap: str | None = None,
    colorbar: bool = False,
    vmin: float | None = None,
    vmax: float | None = None,
    interpolation: str = "nearest",
    aspect: str = "auto",
    show_ticks: bool = True,
    clip: bool = True,
    **kwargs,
):
    """Plot a scalar image or RGB(A) image array.

    Parameters
    ----------
    image
        ``(height, width)`` scalar image or ``(height, width, 3/4)`` RGB(A)
        image. RGB(A) floats are clipped to ``[0, 1]`` by default.

    Returns
    -------
    fig, ax
        Matplotlib figure and axes.

    Notes
    -----
    This is a plotting helper, not image IO. Use ``color.io.read_image`` and
    ``color.io.write_image`` for file access.
    """
    image_arr = _as_image_array(image, clip=clip)
    fig, ax = get_figure_axes(ax, figsize=(5.2, 4.2))
    artist = ax.imshow(
        image_arr,
        extent=extent,
        origin=origin,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        interpolation=interpolation,
        aspect=aspect,
        **kwargs,
    )
    style_2d_axis(ax, title=title, xlabel=xlabel, ylabel=ylabel, grid=False)
    if not show_ticks:
        ax.set_xticks([])
        ax.set_yticks([])
    if colorbar:
        fig.colorbar(artist, ax=ax)
    finish_figure(fig)
    return fig, ax


def _as_bar_values(value) -> np.ndarray:
    """Return bar values as ``(groups, categories)``."""
    values = np.asarray(value, dtype=np.float64)
    if values.ndim == 1:
        values = values.reshape(1, -1)
    if values.ndim != 2:
        raise ValueError("values must have shape (n,) or (groups, n)")
    if values.shape[0] == 0 or values.shape[1] == 0:
        raise ValueError("values must not be empty")
    if not np.all(np.isfinite(values)):
        raise ValueError("values must be finite")
    return values


def plot_bars(
    values,
    *,
    ax=None,
    labels: Sequence[str] | None = None,
    group_labels: Sequence[str] | None = None,
    colors: Sequence[str] | str | None = None,
    orientation: str = "vertical",
    width: float = 0.8,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    grid: bool = True,
    legend: str | bool = "auto",
    **kwargs,
):
    """Plot one or more groups of bars.

    Parameters
    ----------
    values
        Bar values with shape ``(n,)`` or ``(groups, n)``.
    labels
        Category labels.
    group_labels
        Labels for grouped bars.
    orientation
        ``"vertical"`` or ``"horizontal"``.

    Returns
    -------
    fig, ax
        Matplotlib figure and axes.

    Notes
    -----
    ``values`` may be one-dimensional or ``(groups, categories)``. The helper
    supports vertical and horizontal bars but does not compute summary
    statistics.
    """
    if orientation not in {"vertical", "horizontal"}:
        raise ValueError("orientation must be 'vertical' or 'horizontal'")
    if width <= 0:
        raise ValueError("width must be positive")

    bar_values = _as_bar_values(values)
    n_groups, n_categories = bar_values.shape
    labels_list = _normalise_optional_sequence(labels, n_categories, name="labels")
    group_labels_list = _normalise_optional_sequence(group_labels, n_groups, name="group_labels")
    colors_list = _normalise_optional_sequence(colors, n_groups, name="colors")

    fig, ax = get_figure_axes(ax, figsize=(6.0, 4.0))
    positions = np.arange(n_categories, dtype=np.float64)
    group_width = width / n_groups
    offsets = (np.arange(n_groups, dtype=np.float64) - (n_groups - 1) / 2.0) * group_width
    color_iter = cycle(colors_list) if colors_list is not None else cycle([None])

    for group_index in range(n_groups):
        label = group_labels_list[group_index] if group_labels_list is not None else None
        color = next(color_iter)
        bar_kwargs = dict(kwargs)
        if color is not None:
            bar_kwargs["color"] = color
        if orientation == "vertical":
            ax.bar(
                positions + offsets[group_index],
                bar_values[group_index],
                width=group_width,
                label=label,
                **bar_kwargs,
            )
        else:
            ax.barh(
                positions + offsets[group_index],
                bar_values[group_index],
                height=group_width,
                label=label,
                **bar_kwargs,
            )

    if labels_list is not None:
        if orientation == "vertical":
            ax.set_xticks(positions, labels_list)
        else:
            ax.set_yticks(positions, labels_list)

    style_2d_axis(ax, title=title, xlabel=xlabel, ylabel=ylabel, grid=grid)
    if legend is True or (legend == "auto" and group_labels_list is not None):
        ax.legend()
    finish_figure(fig)
    return fig, ax


def set_axis_limits_from_data(
    ax,
    data,
    *,
    padding: float = 0.05,
    equal_aspect: bool = False,
):
    """Set axis limits from finite 2D data with fractional padding.

    Notes
    -----
    ``data`` may contain any leading dimensions as long as the final dimension
    is 2.
    """
    if padding < 0:
        raise ValueError("padding must be non-negative")
    values = np.asarray(data, dtype=np.float64)
    if values.size == 0:
        raise ValueError("data must not be empty")
    if values.shape[-1] != 2:
        raise ValueError("data must have a final dimension of 2")
    points = values.reshape(-1, 2)
    if not np.all(np.isfinite(points)):
        raise ValueError("data values must be finite")

    minimum = np.min(points, axis=0)
    maximum = np.max(points, axis=0)
    span = maximum - minimum
    fallback = np.where(span > 0.0, span, 1.0)
    pad = fallback * padding
    ax.set_xlim(minimum[0] - pad[0], maximum[0] + pad[0])
    ax.set_ylim(minimum[1] - pad[1], maximum[1] + pad[1])
    if equal_aspect:
        ax.set_aspect("equal", adjustable="box")
    return ax


__all__ = [
    "plot_arrows",
    "plot_bars",
    "plot_image",
    "plot_labels",
    "plot_lines",
    "plot_polygons",
    "plot_points",
    "plot_segments",
    "set_axis_limits_from_data",
    "style_2d_axis",
]
