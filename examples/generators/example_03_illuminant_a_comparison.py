"""Compare formula-generated CIE Illuminant A against the static dataset."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from _generators_plot_helpers import save_figure
from color.datasets import get_illuminant
from color.generators.illuminants import illuminant_a_spd
from color.plot import plot_lines, plot_style


def main() -> None:
    dataset = get_illuminant("A")
    generated = illuminant_a_spd(wavelength_nm=dataset["wavelength"])

    wavelength = dataset["wavelength"]
    dataset_spd = dataset["spd"]
    generated_spd = generated["spd"]
    difference = generated_spd - dataset_spd
    relative = np.divide(
        np.abs(difference),
        np.maximum(np.abs(dataset_spd), np.finfo(float).eps),
    )

    print("CIE Illuminant A formula vs dataset")
    print(f"Samples: {wavelength.size}")
    print(f"Max absolute difference: {np.max(np.abs(difference)):.8g}")
    print(f"Max relative difference: {np.max(relative):.8g}")

    with plot_style("journal_double"):
        fig, ax = plt.subplots(figsize=(7.16, 4.0))
        plot_lines(
            [(wavelength, dataset_spd), (wavelength, generated_spd)],
            ax=ax,
            labels=["dataset A", "formula A"],
            linestyles=["-", "--"],
            linewidth=1.4,
            title="CIE Illuminant A: Dataset vs Formula",
            xlabel="Wavelength (nm)",
            ylabel="Relative SPD",
        )
        save_figure(fig, "03_illuminant_a_comparison.png")


if __name__ == "__main__":
    main()
