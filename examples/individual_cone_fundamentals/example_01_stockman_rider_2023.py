"""Demonstrate Stockman/Rider 2023 individual cone fundamentals."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np

from color.datasets.standard_observers import (
    get_cie2006_lms_2degree_fundamentals,
    get_cie2006_lms_10degree_fundamentals,
)
from color.individual_cone_fundamentals import generate_individual_cone_fundamentals
from color.plot import add_panel_labels, finish_figure, plot_lines, plot_style


OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CHANNELS = ("l", "m", "s")
CHANNEL_COLORS = ("#b2182b", "#1b9e77", "#2166ac")


def _comparison_series(generated, reference):
    """Return generated/reference line series and finite differences."""
    wavelengths = reference["wavelength"]
    model_series = []
    difference_series = []
    for channel in CHANNELS:
        model = np.interp(wavelengths, generated["wavelength"], generated[channel])
        ref = reference[channel]
        finite = np.isfinite(ref)
        model_series.append((wavelengths, model))
        model_series.append((wavelengths[finite], ref[finite]))
        difference_series.append((wavelengths[finite], model[finite] - ref[finite]))
    return model_series, difference_series


def _plot_standard_dataset_comparison(standard_2, standard_10):
    """Plot generated standard observers against static CIE 2006 datasets."""
    import matplotlib.pyplot as plt

    reference_2 = get_cie2006_lms_2degree_fundamentals(interval_nm=1, energy="linE")
    reference_10 = get_cie2006_lms_10degree_fundamentals(interval_nm=1, energy="linE")
    data = (
        ("2-degree", standard_2, reference_2),
        ("10-degree", standard_10, reference_10),
    )

    fig, axes = plt.subplots(2, 2, figsize=(7.16, 4.8), sharex=True)
    for column, (label, generated, reference) in enumerate(data):
        model_series, difference_series = _comparison_series(generated, reference)
        plot_lines(
            model_series,
            ax=axes[0, column],
            labels=(
                "L generated",
                "L dataset",
                "M generated",
                "M dataset",
                "S generated",
                "S dataset",
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
            title=f"{label}: generated vs CIE 2006 dataset",
            ylabel="Relative sensitivity",
            linewidth=1.1,
            legend=False,
        )
        plot_lines(
            difference_series,
            ax=axes[1, column],
            labels=("L", "M", "S"),
            colors=CHANNEL_COLORS,
            title=f"{label}: generated - dataset",
            xlabel="Wavelength (nm)",
            ylabel="Difference",
            linewidth=1.1,
        )
        max_error = max(np.max(np.abs(y)) for _, y in difference_series)
        print(f"{label} max |generated - dataset|: {max_error:.6f}")

    axes[0, 0].legend(loc="upper right", fontsize=6, ncols=2)
    finish_figure(fig)
    add_panel_labels(axes, labels=("a", "b", "c", "d"), x=0.02, y=0.95, fontsize=12)
    fig.savefig(OUTPUT_DIR / "01_standard_model_vs_dataset.png")


def _plot_individual_parameter_sets(parameter_sets):
    """Plot three individual parameter sets for L, M and S channels."""
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(3, 1, figsize=(7.16, 5.4), sharex=True)
    styles = ("-", "--", ":")
    for axis, channel, color in zip(axes, CHANNELS, CHANNEL_COLORS):
        series = tuple((raw["wavelength"], raw[channel]) for _, raw in parameter_sets)
        plot_lines(
            series,
            ax=axis,
            labels=tuple(label for label, _ in parameter_sets),
            colors=(color, color, color),
            linestyles=styles,
            title=f"{channel.upper()} cone",
            ylabel="Relative sensitivity",
            linewidth=1.2,
        )
    axes[-1].set_xlabel("Wavelength (nm)")
    finish_figure(fig)
    add_panel_labels(axes, labels=("a", "b", "c"), x=0.02, y=0.95, fontsize=12)
    fig.savefig(OUTPUT_DIR / "01_individual_parameter_sets.png")


def main() -> None:
    standard_2 = generate_individual_cone_fundamentals(observer_degree=2)
    standard_10 = generate_individual_cone_fundamentals(observer_degree=10)
    dense_prereceptoral = generate_individual_cone_fundamentals(
        observer_degree=2,
        macular_density_460=0.65,
        lens_density_400=2.1,
    )
    shifted_lm = generate_individual_cone_fundamentals(
        observer_degree=2,
        l_shift_nm=2.0,
        m_shift_nm=-2.0,
        l_template="ser180",
    )

    parameter_sets = (
        ("standard 2-degree", standard_2),
        ("dense macular/lens", dense_prereceptoral),
        ("shifted L/M + ser180", shifted_lm),
    )

    print("Stockman/Rider 2023 individual cone fundamentals")
    print("Columns:", list(standard_2))
    print("2-degree wavelength range:", standard_2["wavelength"][[0, -1]])
    print("2-degree LMS peaks:", [standard_2[k].max() for k in ("l", "m", "s")])

    with plot_style("presentation", font_scale=0.55, line_scale=0.9):
        _plot_standard_dataset_comparison(standard_2, standard_10)
        _plot_individual_parameter_sets(parameter_sets)




if __name__ == "__main__":
    main()
