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
    example_output_dir,
    print_xyY_table,
    xy_from_XYZ_rows,
)
from color.colorimetry import emission_to_XYZ, reflectance_to_XYZ
from color.generators.ideal import gaussian_spd
from color.plot import (
    plot_chromaticity_points,
    plot_cie1931_diagram,
    plot_lines,
    plot_style,
    plot_swatch_strip,
    preview_sRGB_from_XYZ,
)
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

    # Create the XYZ CMFs and D65 illuminant explicitly, although they are defaults.
    xyz_cmfs = from_cie1931_xyz_cmfs().align(shape)
    illuminant = from_dataset("illuminants", "D65").align(shape)


    xyz_reflectance = reflectance_to_XYZ(reflectance=reflector, cmfs=xyz_cmfs, illuminant=illuminant, shape=shape)
    xyz_emission = emission_to_XYZ(emission=green_emitter, cmfs=xyz_cmfs, shape=shape)
    xyz_rows = np.vstack([xyz_reflectance, xyz_emission])
    labels = ["Perfect reflector", "Gaussian emitter"]

    print_xyY_table("Spectral conversion overview", labels, xyz_rows)

    with plot_style("presentation"):
        fig, axes = plt.subplots(1, 3, figsize=(14.5, 4.8))

        ax = axes[0]
        plot_lines(
            [
                (reflector.wavelengths, reflector.values),
                (green_emitter.wavelengths, green_emitter.values),
            ],
            ax=ax,
            labels=[reflector.name, green_emitter.name],
            title="Input Spectra",
            xlabel="Wavelength (nm)",
            ylabel="Relative value",
        )

        ax = axes[1]
        plot_cie1931_diagram(ax=ax, title="Converted xy Coordinates")
        plot_chromaticity_points(
            xy_from_XYZ_rows(xyz_rows),
            ax=ax,
            labels=labels,
            color="tab:green",
        )
        ax.legend(loc="upper right", fontsize=8)

        ax = axes[2]
        white_Y = max(float(np.max(xyz_rows[:, 1])) / 0.85, 1.0)
        plot_swatch_strip(
            preview_sRGB_from_XYZ(xyz_rows, white_Y=white_Y),
            ax=ax,
            labels=labels,
            title="Approximate sRGB Preview",
        )

        fig.tight_layout()
        output_path = output_dir / "01_spectral_conversion_overview.png"
        fig.savefig(output_path, dpi=150)
        plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
