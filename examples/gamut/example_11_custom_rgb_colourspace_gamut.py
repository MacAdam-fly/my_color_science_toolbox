"""Custom RGB colour-space registration and gamut analysis."""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from color.gamut import (
    DisplayPrimaries,
    analyze_gamut,
    compute_LCH_gamut_boundary,
)
from color.plot import plot_cie1931_diagram, plot_lines, plot_style
from color.spaces import (
    RGB_colourspace_from_primaries_XYZ,
    RGB_colourspace_from_primaries_xy,
    RGB_to_XYZ,
    convert_color,
    get_RGB_colourspace,
    register_RGB_colourspace,
)

from _example_helpers import save_figure


CUSTOM_NAME = "Example Custom RGB"


def _build_custom_spaces():
    """Return xy-created and measured-XYZ custom RGB spaces."""
    custom_xy = RGB_colourspace_from_primaries_xy(
        CUSTOM_NAME,
        primaries_xy=[
            [0.690, 0.310],
            [0.210, 0.720],
            [0.145, 0.055],
        ],
        whitepoint_xy=[0.3127, 0.3290],
        transfer=("gamma", (2.2, 2.3, 2.1)),
        aliases=("ExampleCustomRGB",),
        reference="Synthetic example custom RGB display.",
    )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", UserWarning)
        measured = RGB_colourspace_from_primaries_XYZ(
            "Example Measured RGB",
            custom_xy.matrix_RGB_to_XYZ.T * 1.15,
            transfer=("gamma", 2.2),
            aliases=("ExampleMeasuredRGB",),
            reference="Synthetic measured primaries with preserved XYZ scale.",
        )
    for item in caught:
        print(f"Measured-space warning: {item.message}")
    return custom_xy, measured


def _print_conversion_examples(custom, measured) -> None:
    """Print representative conversion and registration results."""
    RGB = np.array([0.4, 0.5, 0.6])

    register_RGB_colourspace(custom, overwrite=True)

    XYZ_direct = RGB_to_XYZ(RGB, colourspace=custom)
    Lab_routed = convert_color(RGB, CUSTOM_NAME, "Lab")
    primaries = DisplayPrimaries.from_RGB_colourspace(CUSTOM_NAME)

    print("=" * 20 + " custom RGB colour space " + "=" * 20)
    print("Registered name:", get_RGB_colourspace("ExampleCustomRGB").name)
    print("Sample RGB:", RGB)
    print("RGB -> XYZ:", XYZ_direct)
    print("RGB -> Lab through convert_color:", Lab_routed)
    print("DisplayPrimaries names:", primaries.names)
    print("DisplayPrimaries whitepoint XYZ:", primaries.whitepoint_XYZ)
    print("Measured RGB whitepoint XYZ:", np.sum(measured.matrix_RGB_to_XYZ.T, axis=0))


def _compute_custom_boundary_and_analysis():
    """Return a custom RGB boundary and high-level analysis."""
    kwargs = {
        "L_values": np.arange(0.0, 101.0, 5.0),
        "hue_values": np.arange(0.0, 361.0, 5.0),
        "C_upper": 340.0,
        "iterations": 8,
    }
    boundary = compute_LCH_gamut_boundary(CUSTOM_NAME, **kwargs)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", UserWarning)
        analysis = analyze_gamut(CUSTOM_NAME, **kwargs)
    for item in caught:
        print(f"Analysis warning: {item.message}")
    return boundary, analysis


def _plot_custom_gamut(boundary, analysis) -> None:
    """Plot xy boundary comparison and selected coverage metrics."""
    srgb = compute_LCH_gamut_boundary(
        "sRGB",
        L_values=np.arange(0.0, 101.0, 10.0),
        hue_values=np.arange(0.0, 361.0, 10.0),
        C_upper=220.0,
        iterations=7,
    )
    rec2020 = compute_LCH_gamut_boundary(
        "Rec.2020",
        L_values=np.arange(0.0, 101.0, 10.0),
        hue_values=np.arange(0.0, 361.0, 10.0),
        C_upper=340.0,
        iterations=7,
    )

    with plot_style("journal_double"):
        fig, axes = plt.subplots(1, 2, figsize=(7.16, 3.2), constrained_layout=True)

        plot_cie1931_diagram(
            ax=axes[0],
            title="Custom RGB xy Boundary",
            show_background=True,
            background_samples=160,
            show_sample_points=False,
            show_wavelength_labels=True,
        )
        for label, gamut_boundary, color in (
            ("sRGB", srgb, "#0072B2"),
            ("Custom RGB", boundary, "#D55E00"),
            ("Rec.2020", rec2020, "#009E73"),
        ):
            xy = gamut_boundary.xy_boundary()
            plot_lines(
                (xy[:, 0], xy[:, 1]),
                ax=axes[0],
                labels=[label],
                colors=[color],
                linewidth=1.6,
                grid=False,
            )
        axes[0].legend(fontsize=7, loc="upper right")

        labels = [
            "xy Rec.2020",
            "xy Pointer",
            "xy MacAdam",
            "vol Rec.2020",
            "vol Pointer",
            "vol MacAdam",
        ]
        values = [
            analysis.xy_coverage_rec2020,
            analysis.xy_coverage_pointer,
            analysis.xy_coverage_macadam_d65,
            analysis.volume_coverage_rec2020,
            analysis.volume_coverage_pointer,
            analysis.volume_coverage_macadam_d65,
        ]
        x = np.arange(len(labels))
        axes[1].bar(x, values, color="#4C72B0")
        axes[1].set_title("Custom RGB Coverage Summary")
        axes[1].set_xticks(x, labels, rotation=35, ha="right")
        axes[1].set_ylabel("coverage")
        axes[1].set_ylim(0.0, max(1.05, max(values) * 1.15))
        axes[1].grid(True, axis="y", alpha=0.25)

        save_figure(fig, "11_custom_rgb_colourspace_gamut.png")


def main() -> None:
    custom, measured = _build_custom_spaces()
    _print_conversion_examples(custom, measured)
    boundary, analysis = _compute_custom_boundary_and_analysis()

    print("=" * 20 + " custom RGB gamut analysis " + "=" * 20)
    print(f"xy area: {analysis.xy_area:.4f}")
    print(f"Lab volume: {analysis.lab_volume:.1f}")
    print(f"Projected a*b* area: {analysis.projected_ab_area:.1f}")

    _plot_custom_gamut(boundary, analysis)


if __name__ == "__main__":
    main()
