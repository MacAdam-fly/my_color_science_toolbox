"""Wrap three PMC color-card patches, interpolate to 0.5 nm, and plot."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt

from color.datasets import get_color_card
from color.spectra import SpectralShape, from_columns


def main() -> None:
    raw = get_color_card("pmc")
    patch_names = ("Caucasian", "Carrot", "Blue Sky")

    print("Raw data columns:", list(raw.keys()))

    pmc = from_columns(
        raw,
        x="wavelength",
        ys=patch_names,
        name="PMC selected patches",
        metadata={
            "dataset": "pmc",
            "quantity": "spectral_reflectance",
        },
    )
    pmc_1nm = pmc.reshape(
        SpectralShape(
            float(pmc.wavelengths[0]),
            float(pmc.wavelengths[-1]),
            1.0,
        ),
        method="pchip",
    )

    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "pmc_three_patches_1nm.png"

    fig, ax = plt.subplots(figsize=(8, 4.8))
    for index, label in enumerate(pmc.labels):
        ax.plot(
            pmc_1nm.wavelengths,
            pmc_1nm.values[:, index],
            linewidth=1.5,
            label=f"{label} 1.0 nm",
        )
        ax.scatter(
            pmc.wavelengths,
            pmc.values[:, index],
            s=18,
            marker="o",
            label=f"{label} source",    
        )

    ax.set_title("PMC Color Card Reflectance: Source Samples and 1.0 nm PCHIP")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Reflectance factor")
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)
    ax.legend(ncols=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)

    print("Wrapped object:", type(pmc).__name__)
    print("Labels:", pmc.labels)
    print("Source shape:", pmc.values.shape)
    print("Interpolated shape:", pmc_1nm.values.shape)
    print("Saved:", output_path)


if __name__ == "__main__":
    main()
