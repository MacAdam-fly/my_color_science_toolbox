"""Plot ideal spectral generator examples."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.generators.ideal import (
    constant_spd,
    equal_energy_spd,
    gaussian_spd,
    zero_spd,
)


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)

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

    fig, ax = plt.subplots(figsize=(9, 5))
    for label, data in curves.items():
        ax.plot(data["wavelength"], data["spd"], label=label, linewidth=1.8)

    ax.set_title("Ideal Spectral Generators")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Relative value")
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    output_path = output_dir / "ideal_generators.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
