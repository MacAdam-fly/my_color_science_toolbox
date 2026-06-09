"""Demonstrate Asano et al. 2016 individual observer cone fundamentals."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np

from color.datasets.standard_observers import get_cie2006_lms_2degree_fundamentals
from color.individual_cone_fundamentals import (
    generate_asano2016_individual_cone_fundamentals,
)
from color.plot import add_panel_labels, finish_figure, plot_lines, plot_style


OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CHANNELS = ("l", "m", "s")
CHANNEL_COLORS = ("#b2182b", "#1b9e77", "#2166ac")


def _plot_average_observer_check(default_observer):
    """Compare zero-deviation Asano output with CIE 2006 LMS data."""
    import matplotlib.pyplot as plt

    reference = get_cie2006_lms_2degree_fundamentals(interval_nm=5, energy="linE")
    fig, axes = plt.subplots(2, 1, figsize=(7.16, 4.8), sharex=True)

    series = []
    difference_series = []
    for channel in CHANNELS:
        model = default_observer[channel]
        ref = reference[channel]
        finite = np.isfinite(ref)
        series.append((default_observer["wavelength"], model))
        series.append((reference["wavelength"][finite], ref[finite]))
        difference_series.append((reference["wavelength"][finite], model[finite] - ref[finite]))

    plot_lines(
        series,
        ax=axes[0],
        labels=(
            "L Asano",
            "L CIE 2006",
            "M Asano",
            "M CIE 2006",
            "S Asano",
            "S CIE 2006",
        ),
        colors=(
            CHANNEL_COLORS[0],
            CHANNEL_COLORS[0],
            CHANNEL_COLORS[1],
            CHANNEL_COLORS[1],
            CHANNEL_COLORS[2],
            CHANNEL_COLORS[2],
        ),
        linestyles=("-", "--", "-", "--", "-", "--"),
        ylabel="Relative sensitivity",
        linewidth=1.1,
        legend=True,
    )
    plot_lines(
        difference_series,
        ax=axes[1],
        labels=("L", "M", "S"),
        colors=CHANNEL_COLORS,
        xlabel="Wavelength (nm)",
        ylabel="Asano - CIE 2006",
        linewidth=1.1,
    )
    finish_figure(fig)
    add_panel_labels(axes, labels=("a", "b"), x=0.02, y=0.95, fontsize=12)
    fig.savefig(OUTPUT_DIR / "02_asano2016_average_observer_check.png")

    max_error = max(np.max(np.abs(y)) for _, y in difference_series)
    print(f"Asano default vs CIE 2006 2-degree max error: {max_error:.6f}")


def _plot_parameter_effects(parameter_sets):
    """Plot Asano parameter changes for each LMS channel."""
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(3, 1, figsize=(7.16, 5.4), sharex=True)
    styles = ("-", "--", ":", "-.")
    for axis, channel, color in zip(axes, CHANNELS, CHANNEL_COLORS):
        series = tuple((raw["wavelength"], raw[channel]) for _, raw in parameter_sets)
        plot_lines(
            series,
            ax=axis,
            labels=tuple(label for label, _ in parameter_sets),
            colors=(color,) * len(parameter_sets),
            linestyles=styles,
            ylabel=f"{channel.upper()} sensitivity",
            linewidth=1.2,
        )
    axes[-1].set_xlabel("Wavelength (nm)")
    finish_figure(fig)
    add_panel_labels(axes, labels=("a", "b", "c"), x=0.02, y=0.95, fontsize=12)
    fig.savefig(OUTPUT_DIR / "02_asano2016_parameter_effects.png")


def main() -> None:
    default_observer = generate_asano2016_individual_cone_fundamentals()
    older_observer = generate_asano2016_individual_cone_fundamentals(age=70.0)
    wide_field = generate_asano2016_individual_cone_fundamentals(
        field_size_degree=10.0
    )
    shifted = generate_asano2016_individual_cone_fundamentals(
        lens_density_deviation=25.0,
        macular_density_deviation=35.0,
        photopigment_shift_nm=(4.0, -2.0, 0.0),
    )

    parameter_sets = (
        ("default 32y / 2-degree", default_observer),
        ("older 70y", older_observer),
        ("10-degree field", wide_field),
        ("dense filters + L/M shift", shifted),
    )

    print("Asano et al. 2016 individual colorimetric observer model")
    print("Columns:", list(default_observer))
    print("Wavelength range:", default_observer["wavelength"][[0, -1]])
    print("LMS peaks:", [default_observer[k].max() for k in CHANNELS])

    with plot_style("presentation", font_scale=0.6, line_scale=0.9):
        _plot_average_observer_check(default_observer)
        _plot_parameter_effects(parameter_sets)


if __name__ == "__main__":
    main()
