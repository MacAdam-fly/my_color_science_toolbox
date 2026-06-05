"""3D plotting primitive examples for colour-solid style figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.plot import (
    add_panel_labels,
    plot_3d_lines,
    plot_3d_points,
    plot_3d_surface,
    plot_3d_wireframe,
    plot_style,
    set_3d_axis_limits_from_data,
)


def _output_dir() -> Path:
    path = Path(__file__).resolve().parent / "output"
    path.mkdir(exist_ok=True)
    return path


def _save(fig, path: Path) -> None:
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def _surface_wireframe(out: Path) -> None:
    """Show how a colour solid boundary can be drawn as a 3D surface."""
    L = np.linspace(0.0, 100.0, 36)
    h = np.deg2rad(np.linspace(0.0, 360.0, 73))
    H, LL = np.meshgrid(h, L)

    # Synthetic LCH-like boundary: real gamut figures can replace C with
    # GamutBoundary.C_max and use a*=C*cos(h), b*=C*sin(h), L*=L.
    C = 65.0 * np.sin(np.pi * LL / 100.0) * (0.82 + 0.18 * np.cos(3.0 * H))
    A = C * np.cos(H)
    B = C * np.sin(H)

    with plot_style("presentation", font_scale=0.65, line_scale=0.85):
        fig, ax = plot_3d_surface(
            A,
            B,
            LL,
            cmap="viridis",
            alpha=0.78,
            linewidth=0.0,
            xlabel="a*",
            ylabel="b*",
            zlabel="L*",
            view=(24.0, -55.0),
        )
        plot_3d_wireframe(
            A,
            B,
            LL,
            ax=ax,
            color="0.25",
            linewidth=0.35,
            rstride=4,
            cstride=8,
            grid=False,
        )
        set_3d_axis_limits_from_data(ax, np.stack([A, B, LL], axis=-1), padding=0.08, equal_aspect=False)
        add_panel_labels(ax, labels=("a",), x=-0.08, y=1.03)
    _save(fig, out / "08_3d_surface_wireframe.png")


def _points_lines(out: Path) -> None:
    """Show separate 3D points and line components."""
    t = np.linspace(0.0, 2.0 * np.pi, 160)
    helix = (45.0 * np.cos(t), 45.0 * np.sin(t), 100.0 * t / t[-1])

    samples_t = np.linspace(0.0, 2.0 * np.pi, 9)
    samples = np.column_stack(
        [
            45.0 * np.cos(samples_t),
            45.0 * np.sin(samples_t),
            100.0 * samples_t / samples_t[-1],
        ]
    )

    with plot_style("presentation", font_scale=0.75, line_scale=0.9):
        fig, ax = plot_3d_lines(
            helix,
            labels=("trajectory",),
            colors=("tab:blue",),
            linewidth=1.1,
            xlabel="a*",
            ylabel="b*",
            zlabel="L*",
            view=(25.0, -60.0),
        )
        plot_3d_points(
            samples,
            ax=ax,
            colors="tab:orange",
            sizes=28,
            grid=False,
            legend=False,
        )
        set_3d_axis_limits_from_data(ax, samples, padding=0.2, equal_aspect=True)
        add_panel_labels(ax, labels=("b",), x=-0.08, y=1.03)
    _save(fig, out / "08_3d_points_lines.png")


def main() -> None:
    out = _output_dir()
    _surface_wireframe(out)
    _points_lines(out)


if __name__ == "__main__":
    main()
