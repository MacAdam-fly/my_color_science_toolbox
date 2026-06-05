"""Load illuminant datasets and compare generated illuminant SPDs."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from _datasets_plot_helpers import save_figure
from color.datasets import get_illuminant, list_illuminants
from color.generators.blackbody import blackbody_spd
from color.generators.illuminants import daylight_spd
from color.plot import plot_lines, plot_style


def main() -> None:
    print("Static illuminants:", list_illuminants())

    d65 = get_illuminant("D65")
    illuminant_a = get_illuminant("A")
    for label, data in (("D65", d65), ("A", illuminant_a)):
        print(
            f"{label}: {len(data['wavelength'])} points, "
            f"{data['wavelength'][0]:.0f}-{data['wavelength'][-1]:.0f} nm"
        )

    temperatures = [3000, 4000, 5000, 6500, 8000, 10000]
    blackbodies = {temperature: blackbody_spd(temperature=temperature) for temperature in temperatures}
    for temperature, blackbody in blackbodies.items():
        peak = blackbody["wavelength"][np.argmax(blackbody["radiance"])]
        print(
            f"Blackbody {temperature} K: peak at {peak:.0f} nm "
            f"(Wien check: {peak * temperature / 1000:.0f} um*K)"
        )

    ccts = [4000, 5000, 6500, 8000, 10000, 15000]
    daylights = {cct: daylight_spd(cct=cct) for cct in ccts}
    for cct, daylight in daylights.items():
        print(
            f"Daylight {cct} K: {len(daylight['wavelength'])} points, "
            f"{daylight['wavelength'][0]:.0f}-{daylight['wavelength'][-1]:.0f} nm"
        )

    with plot_style("journal_double"):
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))

        plot_lines(
            [
                (d65["wavelength"], d65["spd"]),
                (illuminant_a["wavelength"], illuminant_a["spd"]),
            ],
            ax=axes[0],
            labels=["D65", "A"],
            colors=["royalblue", "orange"],
            title="Static Standard Illuminants",
            xlabel="Wavelength (nm)",
            ylabel="Relative SPD",
        )

        blackbody_colors = [plt.cm.hot(0.15 + 0.13 * index) for index in range(len(temperatures))]
        plot_lines(
            [(blackbodies[t]["wavelength"], blackbodies[t]["radiance"]) for t in temperatures],
            ax=axes[1],
            labels=[f"{t} K" for t in temperatures],
            colors=blackbody_colors,
            title="Generated Blackbody Radiation",
            xlabel="Wavelength (nm)",
            ylabel="Spectral Radiance",
        )
        axes[1].legend(fontsize=8)

        plot_lines(
            [(daylights[cct]["wavelength"], daylights[cct]["spd"]) for cct in ccts],
            ax=axes[2],
            labels=[f"{cct} K" for cct in ccts],
            title="Generated CIE D-Series Daylight",
            xlabel="Wavelength (nm)",
            ylabel="Relative SPD",
        )
        axes[2].legend(fontsize=8)

        save_figure(fig, "01_illuminants.png")


if __name__ == "__main__":
    main()
