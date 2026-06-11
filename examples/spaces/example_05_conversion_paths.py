"""Visualise colour-space conversion paths."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt

from color.spaces import (
    describe_conversion_path,
)
from color.spaces.plotting import plot_conversion_graph, plot_conversion_path

from _spaces_plot_helpers import output_dir


def _save_path(source, target, filename: str) -> None:
    """Describe, print and plot a conversion path."""
    out = output_dir()
    path = describe_conversion_path(source, target)

    print(f"{path.source} -> {path.target}")
    for edge in path.edges:
        print(f"  {edge.source} -> {edge.target}: {edge.operation} ({edge.description})")

    fig, _ax = plot_conversion_path(path)
    fig.savefig(out / filename, dpi=150)
    plt.close(fig)


def main() -> None:
    _save_path("sRGB", "Display P3", "05_path_srgb_to_display_p3.png")
    _save_path("JzCzhz", "Lab", "05_path_jzczhz_to_lab.png")
    _save_path("sRGB", "CAM16-UCS", "05_path_srgb_to_cam16_ucs.png")

    fig, _ax = plot_conversion_graph()
    fig.savefig(output_dir() / "05_conversion_graph.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
