"""Visualize common spectral object workflows."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from _spectra_plot_helpers import save_figure, style_spectral_axis
from color.datasets import get_color_card
from color.spectra import SpectralDistribution, SpectralShape, from_columns, from_dataset


def _plot_single_distribution() -> None:
    signal = SpectralDistribution(
        [400, 450, 500, 550, 600, 650, 700],
        [0.00, 0.12, 0.80, 0.92, 0.35, 0.10, 0.03],
        name="peaked signal",
    )
    shape = SpectralShape(360, 740, 2)
    constant = signal.align(shape, interpolator="pchip", extrapolator="constant")
    linear = signal.align(shape, interpolator="linear", extrapolator="linear")
    filled = signal.extrapolate(
        shape,
        interpolator="linear",
        method="fill",
        fill_value=0.0,
    )

    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.scatter(signal.wavelengths, signal.values, s=36, color="black", label="source")
    ax.plot(constant.wavelengths, constant.values, label="pchip + constant")
    ax.plot(linear.wavelengths, linear.values, "--", label="linear + linear")
    ax.plot(filled.wavelengths, filled.values, ":", label="linear + fill=0")
    style_spectral_axis(ax, title="Single Signal Interpolation and Extrapolation")
    ax.legend(fontsize=8)
    save_figure(fig, "05a_single_distribution_alignment.png")


def _plot_cmfs() -> None:
    cmfs = from_dataset("standard_observers.cmfs", "CIE 1931 XYZ 5 nm")
    cmfs_1nm = cmfs.reshape(SpectralShape(380, 780, 1), method="auto")

    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.8), sharey=True)
    for ax, data, title in (
        (axes[0], cmfs, "Source 5 nm CMFs"),
        (axes[1], cmfs_1nm, "Reshaped 1 nm CMFs"),
    ):
        for index, label in enumerate(data.labels):
            ax.plot(data.wavelengths, data.values[:, index], label=label)
        style_spectral_axis(ax, title=title, ylabel="Response")
        ax.legend(fontsize=8)
    save_figure(fig, "05b_cmfs_reshape.png")


def _plot_pmc_color_card() -> None:
    raw = get_color_card("pmc")
    patch_names = ("Caucasian", "Carrot", "Blue Sky")
    pmc = from_columns(
        raw,
        x="wavelength",
        ys=patch_names,
        name="PMC selected patches",
        metadata={"dataset": "pmc", "quantity": "spectral_reflectance"},
    )
    pmc_1nm = pmc.reshape(
        SpectralShape(float(pmc.wavelengths[0]), float(pmc.wavelengths[-1]), 1.0),
        method="pchip",
    )

    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    for index, label in enumerate(pmc.labels):
        ax.plot(
            pmc_1nm.wavelengths,
            pmc_1nm.values[:, index],
            linewidth=1.5,
            label=f"{label} 1 nm PCHIP",
        )
        ax.scatter(
            pmc.wavelengths,
            pmc.values[:, index],
            s=14,
            marker="o",
            alpha=0.75,
            label=f"{label} source",
        )
    style_spectral_axis(ax, title="PMC Reflectance: Source Samples and PCHIP")
    ax.set_ylabel("Reflectance factor")
    ax.set_ylim(bottom=0)
    ax.legend(ncols=2, fontsize=7)
    save_figure(fig, "05c_pmc_color_card_pchip.png")


def main() -> None:
    _plot_single_distribution()
    _plot_cmfs()
    _plot_pmc_color_card()


if __name__ == "__main__":
    main()
