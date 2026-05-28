"""Compose CCT loci using low-level color.plot primitives."""

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

from color.colorimetry import xy_to_uv1960
from color.colorimetry.temperature import CCT_to_uv, CCT_to_xy_CIE_D
from color.plot import plot_cie1960_ucs_diagram, plot_labels, plot_lines, plot_points


def _output_dir() -> Path:
    path = Path(__file__).resolve().parent / "output"
    path.mkdir(exist_ok=True)
    return path


def _save(fig, path: Path) -> None:
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def main() -> None:
    ccts = np.geomspace(2500.0, 25000.0, 90)
    planckian_uv = CCT_to_uv(
        np.column_stack([ccts, np.zeros_like(ccts)]),
        method="robertson1968",
    )

    daylight_ccts = np.linspace(4000.0, 25000.0, 90)
    daylight_uv = xy_to_uv1960(CCT_to_xy_CIE_D(daylight_ccts))

    fig, ax = plot_cie1960_ucs_diagram(
        title="CCT Loci Composed From Plot Primitives",
        show_background=True,
        background_samples=160,
        whitepoint_uv=None,
    )
    plot_lines(
        [(planckian_uv[:, 0], planckian_uv[:, 1]), (daylight_uv[:, 0], daylight_uv[:, 1])],
        ax=ax,
        labels=("Planckian locus", "CIE D daylight locus"),
        colors=("black", "tab:blue"),
        linestyles=("-", "--"),
        grid=False,
    )

    labelled_ccts = np.array([3000.0, 5000.0, 6500.0, 10000.0])
    labelled_uv = CCT_to_uv(
        np.column_stack([labelled_ccts, np.zeros_like(labelled_ccts)]),
        method="robertson1968",
    )
    plot_points(
        labelled_uv,
        ax=ax,
        colors="black",
        sizes=24,
        grid=False,
    )
    plot_labels(
        labelled_uv,
        [f"{int(cct)} K" for cct in labelled_ccts],
        ax=ax,
        grid=False,
    )
    ax.legend(loc="upper right", fontsize=8)
    _save(fig, _output_dir() / "02_cct_loci_composed.png")


if __name__ == "__main__":
    main()
