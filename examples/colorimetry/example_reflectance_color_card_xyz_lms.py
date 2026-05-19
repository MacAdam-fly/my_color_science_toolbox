"""Convert selected PMC color-card reflectances to XYZ and LMS."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.colorimetry import reflectance_to_LMS, reflectance_to_XYZ
from color.datasets import get_color_card
from color.spectra import MultiSpectralDistribution, SpectralShape, from_columns, from_dataset


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)

    shape = SpectralShape(400, 700, 5)
    patch_names = ("Caucasian", "Carrot", "Blue Sky")

    raw = get_color_card("pmc")
    reflectances = from_columns(
        raw,
        x="wavelength",
        ys=patch_names,
        name="PMC selected reflectances",
    )
    if np.nanmax(reflectances.values) > 1.0:
        reflectances = MultiSpectralDistribution(
            reflectances.wavelengths,
            reflectances.values / 100.0,
            reflectances.labels,
            name=reflectances.name,
            metadata={**reflectances.metadata, "scale": "fraction"},
        )
    reflectances = reflectances.align(shape)

    fundamentals = from_dataset(
        "standard_observers.cone_fundamentals",
        "cie2006_lms2_linE_1nm",
        fill_nan=0.0,
    ).align(shape)

    xyz = reflectance_to_XYZ(reflectances, shape=shape)
    lms = reflectance_to_LMS(reflectances, fundamentals=fundamentals, shape=shape)

    print("PMC patches:", patch_names)
    print("XYZ rows match patch order:")
    print(np.round(xyz, 4))
    print("LMS rows match patch order:")
    print(np.round(lms, 4))

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))

    ax = axes[0]
    for index, patch in enumerate(patch_names):
        ax.plot(reflectances.wavelengths, reflectances.values[:, index], label=patch)
    ax.set_title("PMC Reflectance Curves")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Reflectance")
    ax.legend()
    ax.grid(True, alpha=0.3)

    x = np.arange(len(patch_names))
    width = 0.24
    ax = axes[1]
    for offset, label in zip((-width, 0, width), ("X", "Y", "Z")):
        ax.bar(x + offset, xyz[:, ("X", "Y", "Z").index(label)], width, label=label)
    ax.set_title("Reflectance to XYZ under D65")
    ax.set_xticks(x, patch_names, rotation=20)
    ax.set_ylabel("Value")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)

    ax = axes[2]
    for offset, label in zip((-width, 0, width), fundamentals.labels):
        ax.bar(x + offset, lms[:, fundamentals.labels.index(label)], width, label=label)
    ax.set_title("Reflectance to LMS under D65")
    ax.set_xticks(x, patch_names, rotation=20)
    ax.set_ylabel("Value")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)

    fig.tight_layout()
    output_path = output_dir / "reflectance_color_card_xyz_lms.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
