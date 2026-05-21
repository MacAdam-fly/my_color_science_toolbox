"""Plotting helpers for colour-space conversion paths."""

from __future__ import annotations

from typing import Any

import numpy as np

from .conversion import ConversionPath, describe_conversion_path
from .registry import SPACE_REGISTRY
from .rgb import RGB_COLORSPACES


def _resolve_path(path_or_source: Any, target: Any | None) -> ConversionPath:
    """Return a :class:`ConversionPath` from a path object or source/target pair."""
    if isinstance(path_or_source, ConversionPath):
        if target is not None:
            raise ValueError("target must be None when path_or_source is a ConversionPath")
        return path_or_source
    if target is None:
        raise ValueError("target is required when path_or_source is not a ConversionPath")
    return describe_conversion_path(path_or_source, target)


def plot_conversion_path(
    path_or_source,
    target=None,
    *,
    ax=None,
    show_edge_labels: bool = True,
):
    """Plot a colour-space conversion path as nodes and directed edges."""
    path = _resolve_path(path_or_source, target)

    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    node_count = max(len(path.nodes), 1)
    if ax is None:
        fig, ax = plt.subplots(figsize=(max(6.0, 1.9 * node_count), 2.8))
    else:
        fig = ax.figure

    x_positions = np.arange(node_count, dtype=float)
    y = 0.0
    box_width = 1.08
    box_height = 0.44
    colours = {
        "rgb": "#cfe5ff",
        "generic": "#d8ead2",
        "hub": "#fff2b3",
    }

    for index, node in enumerate(path.nodes):
        patch = FancyBboxPatch(
            (x_positions[index] - box_width / 2.0, y - box_height / 2.0),
            box_width,
            box_height,
            boxstyle="round,pad=0.08,rounding_size=0.08",
            facecolor=colours.get(node.kind, "#eeeeee"),
            edgecolor="#333333",
            linewidth=1.0,
        )
        patch.set_gid("conversion_path_node")
        ax.add_patch(patch)
        ax.text(
            x_positions[index],
            y,
            node.name,
            ha="center",
            va="center",
            fontsize=10,
        )

    for index, edge in enumerate(path.edges):
        if len(path.nodes) == 1:
            x0 = x_positions[0] - 0.26
            x1 = x_positions[0] + 0.26
        else:
            x0 = x_positions[min(index, len(path.nodes) - 1)] + box_width / 2.0
            x1 = x_positions[min(index + 1, len(path.nodes) - 1)] - box_width / 2.0
        y_edge = y
        arrow = FancyArrowPatch(
            (x0, y_edge),
            (x1, y_edge),
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.2,
            color="#444444",
        )
        arrow.set_gid("conversion_path_edge")
        ax.add_patch(arrow)
        if show_edge_labels:
            ax.text(
                (x0 + x1) / 2.0,
                y_edge + 0.33,
                edge.operation,
                ha="center",
                va="center",
                fontsize=8,
                color="#444444",
            )

    ax.set_xlim(-0.8, max(node_count - 1, 0) + 0.8)
    ax.set_ylim(-0.7, 0.8)
    ax.set_axis_off()
    ax.set_title(f"{path.source} to {path.target}")
    fig.tight_layout()
    return fig, ax


def _draw_graph_node(ax, name: str, x: float, y: float, kind: str) -> None:
    """Draw a graph node at *x*, *y*."""
    from matplotlib.patches import FancyBboxPatch

    colours = {
        "rgb": "#cfe5ff",
        "generic": "#d8ead2",
        "hub": "#fff2b3",
        "derived": "#eadcf8",
    }
    box_width = max(1.18, min(1.9, 0.12 * len(name) + 0.52))
    box_height = 0.42
    patch = FancyBboxPatch(
        (x - box_width / 2.0, y - box_height / 2.0),
        box_width,
        box_height,
        boxstyle="round,pad=0.08,rounding_size=0.08",
        facecolor=colours.get(kind, "#eeeeee"),
        edgecolor="#333333",
        linewidth=0.9,
    )
    patch.set_gid("conversion_graph_node")
    ax.add_patch(patch)
    ax.text(x, y, name, ha="center", va="center", fontsize=8.5)


def _draw_graph_edge(
    ax,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    bidirectional: bool,
) -> None:
    """Draw a graph edge from *start* to *end*."""
    from matplotlib.patches import FancyArrowPatch

    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="<->" if bidirectional else "-|>",
        mutation_scale=10,
        linewidth=0.85,
        color="#555555",
        alpha=0.72,
        shrinkA=12,
        shrinkB=12,
    )
    arrow.set_gid("conversion_graph_edge")
    ax.add_patch(arrow)


def _spaced_positions(count: int, spacing: float = 0.72) -> list[float]:
    """Return vertically centred positions for *count* items."""
    if count <= 0:
        return []
    start = (count - 1) * spacing / 2.0
    return [start - index * spacing for index in range(count)]


def plot_conversion_graph(
    *,
    ax=None,
    include_rgb: bool = True,
    include_generic: bool = True,
):
    """Plot the registered colour-space conversion graph."""
    import matplotlib.pyplot as plt

    rgb_names = tuple(sorted(RGB_COLORSPACES)) if include_rgb else ()
    generic_nodes = tuple(SPACE_REGISTRY.values()) if include_generic else ()
    direct_nodes = tuple(
        node
        for node in generic_nodes
        if node.name != "XYZ" and node.parent is None
    )
    derived_nodes = tuple(node for node in generic_nodes if node.parent is not None)

    max_rows = max(len(rgb_names), len(direct_nodes), 1)
    if ax is None:
        fig, ax = plt.subplots(figsize=(13.5, max(7.0, 0.55 * max_rows + 2.0)))
    else:
        fig = ax.figure

    positions: dict[str, tuple[float, float]] = {"XYZ": (2.0, 0.0)}

    for name, y in zip(rgb_names, _spaced_positions(len(rgb_names))):
        positions[name] = (0.0, y)

    for node, y in zip(direct_nodes, _spaced_positions(len(direct_nodes))):
        positions[node.name] = (4.2, y)

    child_counts: dict[str, int] = {}
    for node in derived_nodes:
        parent = node.parent or "XYZ"
        index = child_counts.get(parent, 0)
        child_counts[parent] = index + 1
        parent_y = positions.get(parent, (4.2, 0.0))[1]
        offset = 0.0 if index == 0 else (index - 0.5) * 0.5
        positions[node.name] = (6.45, parent_y - offset)

    for name in rgb_names:
        _draw_graph_node(ax, name, *positions[name], kind="rgb")
    _draw_graph_node(ax, "XYZ", *positions["XYZ"], kind="hub")
    for node in direct_nodes:
        _draw_graph_node(ax, node.name, *positions[node.name], kind="generic")
    for node in derived_nodes:
        _draw_graph_node(ax, node.name, *positions[node.name], kind="derived")

    for name in rgb_names:
        _draw_graph_edge(ax, positions[name], positions["XYZ"], bidirectional=True)

    for node in direct_nodes:
        bidirectional = node.to_XYZ is not None and node.from_XYZ is not None
        if node.to_XYZ is not None or node.from_XYZ is not None:
            _draw_graph_edge(
                ax,
                positions["XYZ"],
                positions[node.name],
                bidirectional=bidirectional,
            )

    for node in derived_nodes:
        if node.parent is None:
            continue
        bidirectional = node.to_parent is not None and node.from_parent is not None
        if node.to_parent is not None or node.from_parent is not None:
            _draw_graph_edge(
                ax,
                positions[node.parent],
                positions[node.name],
                bidirectional=bidirectional,
            )

    xs = [x for x, _y in positions.values()]
    ys = [y for _x, y in positions.values()]
    ax.set_xlim(min(xs) - 1.1, max(xs) + 1.1)
    ax.set_ylim(min(ys) - 0.9, max(ys) + 0.9)
    ax.set_axis_off()
    ax.set_title("Colour-Space Conversion Graph")
    fig.tight_layout()
    return fig, ax


__all__ = [
    "plot_conversion_graph",
    "plot_conversion_path",
]
