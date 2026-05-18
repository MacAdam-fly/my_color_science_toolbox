"""Plot interpolation and extrapolation for one spectral distribution."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt

from color.spectra import SpectralDistribution, SpectralShape


def main() -> None:
    sd = SpectralDistribution(
        [400, 450, 500, 550, 600, 650],
        [0.00, 0.12, 0.80, 0.92, 0.35, 0.10],
        name="peaked signal",
    )

    shape = SpectralShape(360, 700, 1)
    aligned_constant = sd.align(shape, extrapolator="constant")
    aligned_linear = sd.align(shape, extrapolator="linear")
    aligned_fill = sd.extrapolate(shape, method="fill", fill_value=0.0)

    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "single_distribution_interpolation.png"

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(sd.wavelengths, sd.values, "o", label="source samples")
    ax.plot(aligned_constant.wavelengths, aligned_constant.values, label="constant")
    ax.plot(aligned_linear.wavelengths, aligned_linear.values, label="linear")
    ax.plot(aligned_fill.wavelengths, aligned_fill.values, label="fill=0")
    ax.set_title("Single Spectral Distribution Alignment")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Value")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)

    print("Saved:", output_path)


if __name__ == "__main__":
    main()
