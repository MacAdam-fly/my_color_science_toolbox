"""Convert generated self-luminous spectra to xyY, XYZ and LMS."""

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
from color.colorimetry import emission_to_LMS, emission_to_XYZ
from color.generators.blackbody import blackbody_spd
from color.generators.ideal import gaussian_spd
from color.generators.illuminants import daylight_spd
from color.generators.leds import multi_led_spd
from color.plot import (
    plot_bars,
    plot_chromaticity_points,
    plot_cie1931_diagram,
    plot_lines,
    plot_style,
    plot_swatch_strip,
    preview_sRGB_from_XYZ,
)
from color.spectra import SpectralDistribution, SpectralShape, from_dataset


def _normalised_sd(raw: dict[str, np.ndarray], y: str, name: str) -> SpectralDistribution:
    values = np.asarray(raw[y], dtype=np.float64)
    scale = np.max(values)
    if scale == 0:
        raise ValueError(f"{name} has no positive values to normalise")
    return SpectralDistribution(raw["wavelength"], values / scale, name=name)


def main() -> None:
    output_dir = example_output_dir()
    shape = SpectralShape(400, 700, 2)
    spectra = [
        _normalised_sd(blackbody_spd(temperature=6500), "radiance", "Blackbody 6500 K"),
        _normalised_sd(daylight_spd(cct=6500), "spd", "CIE D daylight 6500 K"),
        _normalised_sd(
            gaussian_spd(peak_wavelength=555, width=35, method="fwhm"),
            "spd",
            "Ideal Gaussian 555 nm",
        ),
        _normalised_sd(
            multi_led_spd(
                peak_wavelengths=(457, 530, 615),
                half_spectral_widths=(20, 30, 20),
                peak_power_ratios=(0.731, 1.0, 1.66),
            ),
            "spd",
            "RGB LED mixture",
        ),
    ]
    spectra = [sd.align(shape) for sd in spectra]

    fundamentals = from_dataset(
        "standard_observers.cone_fundamentals",
        "cie2006_lms2_linE_1nm",
        fill_nan=0.0,
    ).align(shape)

    xyz = np.vstack([emission_to_XYZ(sd, shape=shape) for sd in spectra])
    lms = np.vstack(
        [emission_to_LMS(sd, fundamentals=fundamentals, shape=shape) for sd in spectra]
    )
    names = [sd.name for sd in spectra]
    xy = xy_from_XYZ_rows(xyz)

    print_xyY_table("Generated emission spectra", names, xyz)
    print("LMS rows match spectrum order:")
    print(np.round(lms, 5))

    with plot_style("presentation"):
        fig, axes = plt.subplots(2, 2, figsize=(13.5, 9.2))

        ax = axes[0, 0]
        plot_lines(
            [(sd.wavelengths, sd.values) for sd in spectra],
            ax=ax,
            labels=names,
            title="Normalised Emission Spectra",
            xlabel="Wavelength (nm)",
            ylabel="Relative SPD",
        )
        ax.legend(fontsize=7)

        ax = axes[0, 1]
        plot_cie1931_diagram(ax=ax, title="Emission Chromaticity")
        plot_chromaticity_points(xy, ax=ax, labels=names, color="tab:red")
        ax.legend(loc="upper right", fontsize=8)

        ax = axes[1, 0]
        plot_bars(
            lms.T,
            ax=ax,
            labels=names,
            group_labels=fundamentals.labels,
            title="Cone Responses",
            ylabel="Integrated LMS",
        )
        ax.tick_params(axis="x", labelrotation=25)

        ax = axes[1, 1]
        white_Y = max(float(np.max(xyz[:, 1])) / 0.85, 1.0)
        plot_swatch_strip(
            preview_sRGB_from_XYZ(xyz, white_Y=white_Y),
            ax=ax,
            labels=names,
            title="Approximate sRGB Preview",
        )

        fig.tight_layout()
        output_path = output_dir / "03_emission_spectra.png"
        fig.savefig(output_path, dpi=150)
        plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
