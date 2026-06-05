"""Annotation helpers for plotting."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any


def panel_label(
    ax: Any,
    label: str = "a",
    *,
    x: float = -0.12,
    y: float = 1.04,
    fontsize: float | None = None,
    fontweight: str = "bold",
    ha: str = "left",
    va: str = "bottom",
    **kwargs: Any,
) -> Any:
    """Add a journal-style panel label to one axes."""
    if fontsize is None:
        import matplotlib.pyplot as plt

        size = plt.rcParams.get("axes.labelsize", plt.rcParams.get("font.size", 9.0))
        fontsize = float(size) if isinstance(size, (int, float)) else None

    text_kwargs = {
        "transform": ax.transAxes,
        "fontsize": fontsize,
        "fontweight": fontweight,
        "ha": ha,
        "va": va,
        "clip_on": False,
    }
    text_kwargs.update(kwargs)
    text2d = getattr(ax, "text2D", None)
    if callable(text2d):
        return text2d(x, y, label, **text_kwargs)
    return ax.text(x, y, label, **text_kwargs)


def _flatten_axes(axes: Any | None) -> list[Any]:
    """Return axes as a flat list without requiring NumPy."""
    import matplotlib.pyplot as plt

    if axes is None:
        return list(plt.gcf().axes)
    if hasattr(axes, "transAxes") and hasattr(axes, "text"):
        return [axes]
    if isinstance(axes, Mapping):
        axes = axes.values()
    if hasattr(axes, "flat"):
        axes = list(axes.flat)
    if not isinstance(axes, Iterable) or isinstance(axes, (str, bytes)):
        return [axes]

    flat: list[Any] = []
    for item in axes:
        if item is None:
            continue
        if hasattr(item, "transAxes") and hasattr(item, "text"):
            flat.append(item)
        elif isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
            flat.extend(_flatten_axes(item))
        else:
            flat.append(item)
    return flat


def _default_panel_labels(n: int, *, case: str = "lower") -> tuple[str, ...]:
    """Return default panel labels for n panels."""
    letters = "abcdefghijklmnopqrstuvwxyz"
    labels = []
    for i in range(n):
        q, r = divmod(i, len(letters))
        label = letters[r] if q == 0 else f"{letters[r]}{q + 1}"
        labels.append(label.upper() if case == "upper" else label)
    return tuple(labels)


def add_panel_labels(
    axes: Any | None = None,
    labels: Sequence[str] | None = None,
    *,
    case: str = "lower",
    x: float = -0.12,
    y: float = 1.04,
    **kwargs: Any,
) -> list[Any]:
    """Add panel labels to a sequence/grid of axes and return text artists."""
    flat_axes = _flatten_axes(axes)
    if labels is None:
        labels = _default_panel_labels(len(flat_axes), case=case)
    if len(labels) < len(flat_axes):
        raise ValueError("not enough labels for the number of axes")
    return [panel_label(ax, label, x=x, y=y, **kwargs) for ax, label in zip(flat_axes, labels)]




__all__ = [
    "add_panel_labels",
    "panel_label",
]
