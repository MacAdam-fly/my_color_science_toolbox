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
    example_output_dir,
    print_xyY_table,
    xy_from_XYZ_rows,
)
from color.colorimetry import reflectance_to_LMS, reflectance_to_XYZ
from color.datasets import get_color_card
from color.plot import (
    plot_bars,
    plot_chromaticity_points,
    plot_cie1931_diagram,
    plot_lines,
    plot_style,
    plot_swatch_strip,
    preview_sRGB_from_XYZ,
)
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

    with plot_style("journal_double"):
        fig, axes = plt.subplots(2, 2, figsize=(12.5, 9.0))

        ax = axes[0, 0]
        plot_lines(
            [
                (reflectances.wavelengths, reflectances.values[:, index])
                for index in range(len(patch_names))
            ],
            ax=ax,
            labels=patch_names,
            title="PMC Reflectance Curves",
            xlabel="Wavelength (nm)",
            ylabel="Reflectance",
        )

        ax = axes[0, 1]
        plot_cie1931_diagram(ax=ax, title="Chromaticity under D65")
        plot_chromaticity_points(
            xy,
            ax=ax,
            labels=patch_names,
            color="tab:orange",
        )
        ax.legend(loc="upper right", fontsize=8)

        ax = axes[1, 0]
        plot_bars(
            xyz[:, 1],
            ax=ax,
            labels=patch_names,
            colors="tab:blue",
            title="Relative Luminance Y",
            ylabel="Y",
        )
        ax.tick_params(axis="x", labelrotation=20)

        ax = axes[1, 1]
        plot_swatch_strip(
            preview_sRGB_from_XYZ(xyz, white_Y=100.0),
            ax=ax,
            labels=patch_names,
            title="Approximate sRGB Preview",
        )

        fig.tight_layout()
        output_path = output_dir / "02_reflectance_color_cards.png"
        fig.savefig(output_path, dpi=150)
        plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
