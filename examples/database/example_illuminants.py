"""Illuminant datasets and generators: load, generate, and plot SPDs."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.datasets import get_illuminant, list_illuminants
from color.generators.blackbody import blackbody_spd
from color.generators.illuminants import daylight_spd


def main() -> None:
    print("Static illuminants:", list_illuminants())

    d65 = get_illuminant("D65")
    ill_a = get_illuminant("A")
    print(
        f"D65: {len(d65['wavelength'])} points, "
        f"{d65['wavelength'][0]:.0f}-{d65['wavelength'][-1]:.0f} nm"
    )
    print(
        f"A: {len(ill_a['wavelength'])} points, "
        f"{ill_a['wavelength'][0]:.0f}-{ill_a['wavelength'][-1]:.0f} nm"
    )

    temperatures = [3000, 4000, 5000, 6500, 8000, 10000]
    blackbodies = {}
    for temperature in temperatures:
        blackbody = blackbody_spd(temperature=temperature)
        blackbodies[temperature] = blackbody
        peak = blackbody["wavelength"][np.argmax(blackbody["radiance"])]
        print(
            f"Blackbody {temperature} K: peak at {peak:.0f} nm "
            f"(Wien check: {peak * temperature / 1000:.0f} um*K)"
        )

    ccts = [4000, 5000, 6500, 8000, 10000, 15000]
    daylights = {}
    for cct in ccts:
        daylight = daylight_spd(cct=cct)
        daylights[cct] = daylight
        print(
            f"Daylight {cct} K: {len(daylight['wavelength'])} points, "
            f"{daylight['wavelength'][0]:.0f}-{daylight['wavelength'][-1]:.0f} nm"
        )

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    ax = axes[0]
    ax.plot(d65["wavelength"], d65["spd"], label="D65", color="royalblue")
    ax.plot(ill_a["wavelength"], ill_a["spd"], label="A", color="orange")
    ax.set_title("Static Standard Illuminants")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Relative SPD")
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    cmap = plt.cm.hot
    for index, temperature in enumerate(temperatures):
        blackbody = blackbodies[temperature]
        color = cmap(0.15 + 0.13 * index)
        ax.plot(
            blackbody["wavelength"],
            blackbody["radiance"],
            label=f"{temperature} K",
            color=color,
        )
    ax.set_title("Generated Blackbody Radiation")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Spectral Radiance")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    ax = axes[2]
    for cct in ccts:
        daylight = daylights[cct]
        ax.plot(daylight["wavelength"], daylight["spd"], label=f"{cct} K")
    ax.set_title("Generated CIE D-Series Daylight")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Relative SPD")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    output_path = Path(__file__).resolve().parent / "illuminants.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
