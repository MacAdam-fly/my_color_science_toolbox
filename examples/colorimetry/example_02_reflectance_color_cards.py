"""Convert selected PMC colour-card reflectances to xyY, XYZ and LMS."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from _plot_helpers import (
    annotate_xy_points,
    example_output_dir,
    plot_srgb_swatches,
    plot_xy_locus,
    print_xyY_table,
    xy_from_XYZ_rows,
)
from color.colorimetry import reflectance_to_LMS, reflectance_to_XYZ
from color.datasets import get_color_card
from color.spectra import MultiSpectralDistribution, SpectralShape, from_columns, from_dataset


def main() -> None:
    output_dir = example_output_dir()
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
    xy = xy_from_XYZ_rows(xyz)

    print_xyY_table("PMC reflectance patches under D65", patch_names, xyz)
    print("LMS rows match patch order:")
    print(np.round(lms, 5))

    fig, axes = plt.subplots(2, 2, figsize=(12.5, 9.0))

    ax = axes[0, 0]
    for index, patch in enumerate(patch_names):
        ax.plot(reflectances.wavelengths, reflectances.values[:, index], label=patch)
    ax.set_title("PMC Reflectance Curves")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Reflectance")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    ax = axes[0, 1]
    plot_xy_locus(ax, title="Chromaticity under D65")
    annotate_xy_points(ax, xy, patch_names, color="tab:orange")
    ax.legend(loc="upper right", fontsize=8)

    ax = axes[1, 0]
    x = np.arange(len(patch_names))
    ax.bar(x, xyz[:, 1], color="tab:blue", alpha=0.8)
    ax.set_title("Relative Luminance Y")
    ax.set_xticks(x, patch_names, rotation=20, ha="right")
    ax.set_ylabel("Y")
    ax.grid(True, axis="y", alpha=0.3)

    ax = axes[1, 1]
    plot_srgb_swatches(
        ax,
        patch_names,
        xyz,
        white_Y=100.0,
        title="Approximate sRGB Preview",
    )

    fig.tight_layout()
    output_path = output_dir / "02_reflectance_color_cards.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
