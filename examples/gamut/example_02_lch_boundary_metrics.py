"""LCH boundary metrics and fixed-lightness slice comparisons."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.plot import finish_figure, plot_lines, plot_style

from _example_helpers import COLOURS, compute_example_boundaries, lch_slice_ab, save_figure


def main() -> None:
    boundaries = compute_example_boundaries()

    print("=" * 20 + " LCH boundary metrics " + "=" * 20)
    for name, boundary in boundaries.items():
        print(f"{name:8s} L*=50 area: {boundary.area_at_L(50.0):10.2f}")
        print(f"{name:8s} Lab volume:  {boundary.lab_volume():10.2f}")
        print(f"{name:8s} projected a*b* area: {boundary.projected_ab_area():10.2f}")

    with plot_style("presentation", font_scale=0.75, line_scale=0.9):
        fig, ax = plot_lines(
            tuple(lch_slice_ab(boundary, 50.0) for boundary in boundaries.values()),
            labels=tuple(f"{name} L*=50" for name in boundaries),
            colors=tuple(COLOURS[name] for name in boundaries),
            linestyles=("-", "--", "-."),
            title="Display-Primary LCH Boundary at L*=50",
            xlabel="a*",
            ylabel="b*",
            grid=True,
        )
        ax.set_aspect("equal", adjustable="box")
        finish_figure(fig)
        save_figure(fig, "02_lch_boundary_L50_comparison.png")


if __name__ == "__main__":
    main()
