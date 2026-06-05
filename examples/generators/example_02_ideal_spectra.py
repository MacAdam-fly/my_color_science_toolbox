"""Plot ideal spectral generator examples using basic plot components."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from _generators_plot_helpers import save_figure
from color.generators.ideal import (
    constant_spd,
    equal_energy_spd,
    gaussian_spd,
    zero_spd,
)
from color.plot import plot_lines, plot_style


def main() -> None:
    wavelength = np.arange(400, 701, 1.0)
    curves = {
        "zero": zero_spd(wavelength_nm=wavelength),
        "equal energy": equal_energy_spd(wavelength_nm=wavelength),
        "constant 0.35": constant_spd(wavelength_nm=wavelength, value=0.35),
        "gaussian normal": gaussian_spd(
            wavelength_nm=wavelength,
            peak_wavelength=555,
            width=25,
            method="normal",
        ),
        "gaussian FWHM": gaussian_spd(
            wavelength_nm=wavelength,
            peak_wavelength=555,
            width=50,
            method="fwhm",
        ),
    }

    with plot_style("presentation", font_scale=0.65, line_scale=0.85):
        fig, ax = plt.subplots(figsize=(7.16, 4.2))
        plot_lines(
            [(data["wavelength"], data["spd"]) for data in curves.values()],
            ax=ax,
            labels=list(curves),
            linewidth=1.4,
            title="Ideal Spectral Generators",
            xlabel="Wavelength (nm)",
            ylabel="Relative value",
        )
        save_figure(fig, "02_ideal_spectra.png")


if __name__ == "__main__":
    main()
