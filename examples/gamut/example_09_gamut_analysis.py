"""High-level gamut analysis summaries."""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from color.gamut import analyze_gamut
from color.plot import plot_style

from _example_helpers import rgbc_primaries, save_figure


def _analyse_examples():
    """Return analysis results for representative gamuts."""
    kwargs = {
        "L_values": np.arange(0.0, 101.0, 2.0),
        "hue_values": np.arange(0.0, 361.0, 2.0),
        "C_upper": 360.0,
        "iterations": 8,
    }
    inputs = {
        "sRGB": "sRGB",
        "Display P3": "Display P3",
        "Rec.2020": "Rec.2020",
        "RGBC": rgbc_primaries(),
    }
    results = []
    for name, gamut in inputs.items():
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always", UserWarning)
            results.append(analyze_gamut(gamut, name=name, **kwargs))
    return results


def _print_table(results) -> None:
    """Print compact analysis table."""
    print("=" * 20 + " gamut analysis " + "=" * 20)
    header = (
        "name".ljust(12)
        + "xy_area".rjust(10)
        + "Lab_vol".rjust(12)
        + "xy Rec2020".rjust(12)
        + "xy Pointer".rjust(12)
        + "xy MacAdam".rjust(12)
        + "vol Rec2020".rjust(13)
        + "vol Pointer".rjust(13)
        + "vol MacAdam".rjust(13)
    )
    print(header)
    for item in results:
        print(
            item.name.ljust(12)
            + f"{item.xy_area:10.4f}"
            + f"{item.lab_volume:12.1f}"
            + f"{item.xy_coverage_rec2020:12.3f}"
            + f"{item.xy_coverage_pointer:12.3f}"
            + f"{item.xy_coverage_macadam_d65:12.3f}"
            + f"{item.volume_coverage_rec2020:13.3f}"
            + f"{item.volume_coverage_pointer:13.3f}"
            + f"{item.volume_coverage_macadam_d65:13.3f}"
        )


def _plot_coverage_bars(results) -> None:
    """Plot selected coverage metrics."""
    names = [item.name for item in results]
    x = np.arange(len(names))
    width = 0.26
    with plot_style("journal_double"):
        fig, axes = plt.subplots(1, 2, figsize=(7.16, 3.2), constrained_layout=True)

        axes[0].bar(x - width, [r.xy_coverage_rec2020 for r in results], width, label="Rec.2020")
        axes[0].bar(x, [r.xy_coverage_pointer for r in results], width, label="Pointer")
        axes[0].bar(x + width, [r.xy_coverage_macadam_d65 for r in results], width, label="MacAdam D65")
        axes[0].set_title("xy Area Coverage")
        axes[0].set_xticks(x, names, rotation=25, ha="right")
        axes[0].set_ylim(0.0, 1.1)
        axes[0].set_ylabel("coverage")
        axes[0].grid(True, axis="y", alpha=0.25)
        axes[0].legend(fontsize=7)

        axes[1].bar(x - width, [r.volume_coverage_rec2020 for r in results], width, label="Rec.2020")
        axes[1].bar(x, [r.volume_coverage_pointer for r in results], width, label="Pointer")
        axes[1].bar(x + width, [r.volume_coverage_macadam_d65 for r in results], width, label="MacAdam D65")
        axes[1].set_title("Lab Volume Coverage")
        axes[1].set_xticks(x, names, rotation=25, ha="right")
        axes[1].set_ylim(0.0, 1.1)
        axes[1].set_ylabel("coverage")
        axes[1].grid(True, axis="y", alpha=0.25)
        axes[1].legend(fontsize=7)

        save_figure(fig, "09_gamut_analysis_summary.png")


def main() -> None:
    results = _analyse_examples()
    _print_table(results)
    _plot_coverage_bars(results)


if __name__ == "__main__":
    main()
