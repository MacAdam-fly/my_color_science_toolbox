"""Tests for colour-space conversion path plotting."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from color.spaces import describe_conversion_path
from color.spaces.plotting import plot_conversion_graph, plot_conversion_path


def _count_gid(ax, gid: str) -> int:
    """Count Matplotlib patches carrying *gid*."""
    return sum(1 for patch in ax.patches if patch.get_gid() == gid)


def test_plot_conversion_path_from_path_object():
    path = describe_conversion_path("JzCzhz", "Lab")

    fig, ax = plot_conversion_path(path)

    assert fig is ax.figure
    assert _count_gid(ax, "conversion_path_node") == len(path.nodes)
    assert _count_gid(ax, "conversion_path_edge") == len(path.edges)
    plt.close(fig)


def test_plot_conversion_path_from_source_and_target():
    fig, ax = plot_conversion_path("sRGB", "CAM16-UCS")

    assert fig is ax.figure
    assert _count_gid(ax, "conversion_path_node") == 3
    assert _count_gid(ax, "conversion_path_edge") == 2
    plt.close(fig)


def test_plot_conversion_path_rejects_target_with_path_object():
    path = describe_conversion_path("XYZ", "xyY")

    try:
        plot_conversion_path(path, "Lab")
    except ValueError as exc:
        assert "target must be None" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_plot_conversion_graph():
    fig, ax = plot_conversion_graph()

    assert fig is ax.figure
    assert _count_gid(ax, "conversion_graph_node") > 10
    assert _count_gid(ax, "conversion_graph_edge") > 10
    plt.close(fig)


def test_plot_conversion_graph_separates_sibling_derived_nodes():
    fig, ax = plot_conversion_graph()
    positions = {text.get_text(): text.get_position() for text in ax.texts}

    assert abs(positions["LCHuv"][1] - positions["Lshuv"][1]) >= 0.7
    plt.close(fig)
