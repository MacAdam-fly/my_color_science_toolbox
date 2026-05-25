"""Chromaticity diagram overview for color.plot."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.plot import (
    plot_cie1931_diagram,
    plot_cie1960_ucs_diagram,
    plot_cie1976_ucs_diagram,
)


def _output_dir() -> Path:
    path = Path(__file__).resolve().parent / "output"
    path.mkdir(exist_ok=True)
    return path


def _save(fig, path: Path) -> None:
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def _save_pair(plotter, *, output_dir: Path, stem: str, title: str) -> None:
    fig, ax = plotter(title=title, show_background=False)
    _save(fig, output_dir / f"{stem}_locus.png")

    fig, ax = plotter(
        title=f"{title} with approximate sRGB background",
        show_background=True,
        background_samples=192,
        background_alpha=1.0,
    )
    _save(fig, output_dir / f"{stem}_locus_background.png")


def main() -> None:
    out = _output_dir()

    _save_pair(
        plot_cie1931_diagram,
        output_dir=out,
        stem="01_cie1931_xy",
        title="CIE 1931 xy",
    )
    _save_pair(
        plot_cie1960_ucs_diagram,
        output_dir=out,
        stem="01_cie1960_uv",
        title="CIE 1960 UCS uv",
    )
    _save_pair(
        plot_cie1976_ucs_diagram,
        output_dir=out,
        stem="01_cie1976_upvp",
        title="CIE 1976 UCS u'v'",
    )


if __name__ == "__main__":
    main()
