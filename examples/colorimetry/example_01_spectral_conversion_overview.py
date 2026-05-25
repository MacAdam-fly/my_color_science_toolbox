"""Overview of spectral conversion to XYZ, xyY and display previews."""

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
from color.colorimetry import emission_to_XYZ, reflectance_to_XYZ
from color.generators.ideal import gaussian_spd
from color.spectra import SpectralDistribution, SpectralShape, from_columns, from_dataset, from_cie1931_xyz_cmfs


def main() -> None:
    output_dir = example_output_dir()
    shape = SpectralShape(400, 700, 1)  

    reflector = SpectralDistribution(
        shape.wavelengths,
        np.ones(len(shape)),
        name="Perfect reflector",
    )
    green_emitter = from_columns(
        gaussian_spd(peak_wavelength=555, width=35, method="fwhm"),
        y="spd",
        name="Gaussian emitter 555 nm",
    ).align(shape)

    # create the XYZ CMFs and D65 illuminant aligned to the same shape as the spectra (they are defaults, but this makes it explicit)
    xyz_cmfs = from_dataset("standard_observers.cmf", "cie1931 xyz_1nm").align(shape)
    xyf_xmfs = from_cie1931_xyz_cmfs().align(shape)
    illuminant = from_dataset("illuminants", "D65").align(shape)


    xyz_reflectance = reflectance_to_XYZ(reflectance=reflector, cmfs=xyz_cmfs, illuminant=illuminant, shape=shape)
    xyz_emission = emission_to_XYZ(emission=green_emitter, cmfs=xyz_cmfs, shape=shape)
    xyz_rows = np.vstack([xyz_reflectance, xyz_emission])
    labels = ["Perfect reflector", "Gaussian emitter"]

    print_xyY_table("Spectral conversion overview", labels, xyz_rows)

    fig, axes = plt.subplots(1, 3, figsize=(14.5, 4.8))

    ax = axes[0]
    ax.plot(reflector.wavelengths, reflector.values, label=reflector.name)
    ax.plot(green_emitter.wavelengths, green_emitter.values, label=green_emitter.name)
    ax.set_title("Input Spectra")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Relative value")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    plot_xy_locus(ax, title="Converted xy Coordinates")
    annotate_xy_points(ax, xy_from_XYZ_rows(xyz_rows), labels, color="tab:green")
    ax.legend(loc="upper right", fontsize=8)

    ax = axes[2]
    white_Y = max(float(np.max(xyz_rows[:, 1])) / 0.85, 1.0)
    plot_srgb_swatches(
        ax,
        labels,
        xyz_rows,
        white_Y=white_Y,
        title="Approximate sRGB Preview",
    )

    fig.tight_layout()
    output_path = output_dir / "01_spectral_conversion_overview.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
