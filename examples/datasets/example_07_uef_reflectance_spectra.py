"""Load UEF reflectance spectra, resample them and compute CIE 1931 xy."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from _datasets_plot_helpers import save_figure
from _datasets_plot_helpers import example_output_dir
from color.colorimetry import XYZ_to_xy, reflectance_to_XYZ
from color.datasets import get_reflectance_spectrum, list_reflectance_spectra
from color.plot import (
    plot_chromaticity_points,
    plot_cie1931_diagram,
    plot_lines,
    plot_style,
)
from color.spectra import SpectralDistribution, SpectralShape, from_columns


_DATASET_GRID = (
    ("munsell_matt", "Munsell matt"),
    ("munsell_glossy_all", "Munsell glossy"),
    ("agfa_it872", "Agfa IT8.7/2"),
    ("paper_cardboardsce", "Cardboard SCE"),
    ("paper_cardboardsci", "Cardboard SCI"),
    ("paper_newsprintsce", "Newsprint SCE"),
    ("paper_newsprintsci", "Newsprint SCI"),
    ("paper_papersce", "Paper SCE"),
    ("paper_papersci", "Paper SCI"),
    ("forest_spruce", "Forest spruce"),
    ("forest_birch", "Forest birch"),
    ("forest_pine", "Forest pine"),
)


def _sample_columns(raw: dict[str, np.ndarray], count: int = 4) -> list[str]:
    """Return evenly spaced sample column names from a reflectance dataset."""
    names = [name for name in raw if name != "wavelength"]
    if len(names) <= count:
        return names
    indices = np.linspace(0, len(names) - 1, count, dtype=int)
    return [names[index] for index in indices]


def _short_label(label: str, max_length: int = 16) -> str:
    """Return a compact label for legends and point annotations."""
    return label if len(label) <= max_length else f"{label[: max_length - 1]}..."


def _load_resampled_samples(
    dataset_name: str,
    *,
    shape: SpectralShape,
    sample_count: int = 4,
) -> tuple[list[SpectralDistribution], list[str]]:
    """Load selected UEF samples and resample them to *shape*."""
    raw = get_reflectance_spectrum(dataset_name)
    sample_names = _sample_columns(raw, sample_count)
    spectra = [
        from_columns(raw, x="wavelength", y=sample_name, name=f"{dataset_name}:{sample_name}").align(shape)
        for sample_name in sample_names
    ]
    return spectra, sample_names


def _panel_title(ax, title: str, *, inside: bool = False) -> None:
    """Set a compact subplot title.

    Chromaticity diagrams have fixed equal-aspect axes in a dense 3x4 grid.
    Putting titles outside the axes often causes overlaps after layout
    adjustment, so those panels use an in-axes label placed in the mostly empty
    upper-left xy region.
    """
    if inside:
        ax.text(
            0.03,
            1.00,
            title,
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=8.0,
            fontweight="bold",
            bbox={
                "boxstyle": "round,pad=0.18",
                "facecolor": "white",
                "edgecolor": "none",
                "alpha": 0.78,
            },
            zorder=10,
        )
        return

    ax.set_title(
        title,
        loc="left",
        fontsize=8.0,
        fontweight="bold",
        pad=3.0,
    )


def main() -> None:
    shape = SpectralShape(400, 700, 5)
    available = set(list_reflectance_spectra())
    missing = [name for name, _label in _DATASET_GRID if name not in available]
    if missing:
        raise RuntimeError(f"Missing registered UEF reflectance datasets: {missing}")

    print("UEF reflectance datasets:", ", ".join(sorted(available)))
    print(f"Resampling selected samples to {shape.start:.0f}-{shape.end:.0f} nm / {shape.interval:.0f} nm")

    spectra_by_dataset: dict[str, list[SpectralDistribution]] = {}
    labels_by_dataset: dict[str, list[str]] = {}
    xy_by_dataset: dict[str, np.ndarray] = {}

    for dataset_name, _title in _DATASET_GRID:
        spectra, sample_names = _load_resampled_samples(dataset_name, shape=shape)
        XYZ = np.vstack([reflectance_to_XYZ(spectrum, illuminant="D65", cmfs="cie1931_xyz_1nm", shape=shape) for spectrum in spectra])
        xy = XYZ_to_xy(XYZ)

        spectra_by_dataset[dataset_name] = spectra
        labels_by_dataset[dataset_name] = sample_names
        xy_by_dataset[dataset_name] = xy

        print(f"\n{dataset_name}:")
        for sample_name, xy_row in zip(sample_names, xy):
            print(f"  {sample_name:24s} xy = ({xy_row[0]:.4f}, {xy_row[1]:.4f})")

    with plot_style("journal_double", font_scale=0.85, line_scale=0.85):
        fig, axes = plt.subplots(3, 4, figsize=(13.0, 8.4), sharex=True, sharey=True)
        for ax, (dataset_name, title) in zip(axes.ravel(), _DATASET_GRID):
            spectra = spectra_by_dataset[dataset_name]
            sample_names = labels_by_dataset[dataset_name]
            plot_lines(
                [(spectrum.wavelengths, spectrum.values) for spectrum in spectra],
                ax=ax,
                labels=[_short_label(name, 14) for name in sample_names],
                linewidth=1.0,
                title=None,
                xlabel="Wavelength (nm)",
                ylabel="Reflectance",
                legend=False,
            )
            _panel_title(ax, title, inside=True)
            ax.set_ylim(-0.03, 1.15)
        # fig.suptitle("UEF Reflectance Spectra Resampled to 400-700 nm / 5 nm", y=0.985)
        save_figure(fig, "07_uef_reflectance_resampled_spectra.png", suptitle_top=0.90)

    with plot_style("journal_double", font_scale=0.85, line_scale=0.85):
        fig, axes = plt.subplots(3, 4, figsize=(14.5, 10.8))
        for ax, (dataset_name, title) in zip(axes.ravel(), _DATASET_GRID):
            plot_cie1931_diagram(
                ax=ax,
                title="",
                show_sample_points=False,
                show_background=False,
                whitepoint_xy=None,
            )
            plot_chromaticity_points(
                xy_by_dataset[dataset_name],
                ax=ax,
                color="tab:red",
                sizes=18,
            )
            _panel_title(ax, title, inside=True)
            ax.set_xlim(0.0, 0.8)
            ax.set_ylim(0.0, 0.9)
        output_path = example_output_dir() / "07_uef_reflectance_cie1931_xy.png"
        fig.savefig(output_path, dpi=150)
        plt.close(fig)
        print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
