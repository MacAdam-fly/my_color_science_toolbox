"""Temperature visualisation helpers from color.plot."""

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
    plot_duv_offsets_uv1960,
    plot_mired_curve,
    plot_temperature_loci_uv1960,
)


def _output_dir() -> Path:
    path = Path(__file__).resolve().parent / "output"
    path.mkdir(exist_ok=True)
    return path


def _save(fig, path: Path) -> None:
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def main() -> None:
    output_dir = _output_dir()

    fig, ax = plot_temperature_loci_uv1960(background_samples=192)
    _save(fig, output_dir / "02_temperature_loci_uv1960.png")

    fig, ax = plot_duv_offsets_uv1960()
    _save(fig, output_dir / "02_duv_offsets_uv1960.png")

    fig, ax = plot_mired_curve()
    _save(fig, output_dir / "02_mired_curve.png")


if __name__ == "__main__":
    main()
