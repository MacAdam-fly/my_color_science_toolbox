"""Computed MacAdam limits from L*-derived brightness factors."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


from color.colorimetry import Y_to_Lstar
from color.gamut import macadam_limits, macadam_limits_published_xy_boundary
from color.gamut.macadam import computed_macadam_limits_data
from color.plot import plot_cie1931_diagram, plot_lines, plot_style, style_2d_axis
from color.spectra import SpectralShape, from_columns
from color.generators import generate_illuminant
from _example_helpers import save_figure



def _plot_computed_vs_published() -> None:
    wavelengths = np.arange(400.0, 701.0, 2.0)
    shape = SpectralShape(400.0, 701.0, 2.0)
    Y_values = np.arange(0.0, 101.0, 10.0)
    L_values = Y_to_Lstar(Y_values)
    hue_values = np.arange(0.0, 361.0, 2.0)

    published = macadam_limits(
        "D65",
        L_values=L_values,
        hue_values=hue_values,
        C_upper=300.0,
        iterations=10,
    )
    computed = macadam_limits(
        "D65",
        source="computed",
        shape=shape,
        L_values=L_values,
        hue_values=hue_values,
        C_upper=300.0,
    )

    D80_computed = generate_illuminant("cie_d_daylight", cct=8000.0, wavelength_nm=wavelengths)
    D80_spetra = from_columns(D80_computed, y="spd", name="D80 (computed)")

    # cause the input illuminant is not in the static database, the computation will be automatically enabled
    computed_D80 = macadam_limits(
        D80_spetra,
        L_values=L_values,
        hue_values=hue_values,
        C_upper=300.0,
    )

    print("=" * 20 + " Computed MacAdam limits " + "=" * 20)
    print(f"Computed whitepoint XYZ: {computed.whitepoint_XYZ}")
    print(f"Computed boundary grid: {computed.C_max.shape}")
    print(f"Published D65 vertices: {published.vertices_XYZ.shape[0]}")
    print(f"Computed D65 vertices: {computed.vertices_XYZ.shape[0]}")

    with plot_style("journal_double"):
        fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.5), constrained_layout=True)

        ax = axes[0]
        plot_cie1931_diagram(
            ax=ax,
            show_background=True,
            background_samples=160,
            title="xy Boundary",
        )

        # The xy boundary for C/A/D65 can be directly obtained from the published data, while the boundary for D80 needs to be obtained from the computed data since it's not in the published data
        published_xy = macadam_limits_published_xy_boundary("D65")
        computed_xy = computed.xy_boundary()
        for label, xy, color in (
            ("published/cache", published_xy, "black"),
            ("computed", computed_xy, "#D55E00"),
            ("computed (D80)", computed_D80.xy_boundary(), "#0072B2"),
        ):
            plot_lines((xy[:, 0], xy[:, 1]), ax=ax, labels=[label], colors=[color], linewidth=1.2, grid=False)
        ax.legend(fontsize=7)

        ax = axes[1]
        for label, ab, color in (
            ("published/cache", published.projected_ab_boundary(), "black"),
            ("computed", computed.projected_ab_boundary(), "#D55E00"),
            ("computed (D80)", computed_D80.projected_ab_boundary(), "#0072B2"),
        ):
            plot_lines((ab[:, 0], ab[:, 1]), ax=ax, labels=[label], colors=[color], linewidth=1.2, grid=False)
        style_2d_axis(ax, title="Projected Lab a*b* Boundary", xlabel="a*", ylabel="b*", equal_aspect=True)
        ax.legend(fontsize=7)

        ax = axes[2]
        published_lch = published.slice_L(50.0)
        computed_lch = computed.slice_L(50.0)
        for label, lch, color in (
            ("published/cache", published_lch, "black"),
            ("computed", computed_lch, "#D55E00"),
            ("computed (D80)", computed_D80.slice_L(50.0), "#0072B2"),
        ):
            plot_lines((lch[:, 2], lch[:, 1]), ax=ax, labels=[label], colors=[color], linewidth=1.2, grid=False)
        style_2d_axis(ax, title="L*=50 Chroma Boundary", xlabel="hue angle (deg)", ylabel="C*")
        ax.legend(fontsize=7)

        save_figure(fig, "08_computed_macadam_limits.png")


def main() -> None:
    _plot_computed_vs_published()


if __name__ == "__main__":
    main()
