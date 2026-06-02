"""Create, register and use a custom three-primary RGB colour space."""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.spaces import (
    RGB_colourspace_from_primaries_XYZ,
    RGB_colourspace_from_primaries_xy,
    RGB_to_RGB,
    RGB_to_XYZ,
    XYZ_to_RGB,
    convert_color,
    describe_conversion_path,
    get_RGB_colourspace,
    register_RGB_colourspace,
)
from color.spaces.rgb.transfer import decode_transfer

from _spaces_plot_helpers import output_dir, plot_swatch_grid, preview_sRGB_from_XYZ


CUSTOM_NAME = "Example Custom RGB"
SAMPLE_RGB = np.array(
    [
        [0.90, 0.10, 0.10],
        [0.10, 0.70, 0.20],
        [0.10, 0.30, 0.90],
        [0.80, 0.70, 0.20],
        [0.40, 0.50, 0.60],
    ],
    dtype=np.float64,
)


def _create_custom_spaces():
    """Return custom RGB spaces from xy primaries and measured XYZ primaries."""
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
        white_name="D65",
        reference="Synthetic custom RGB space for examples.",
    )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", UserWarning)
        measured = RGB_colourspace_from_primaries_XYZ(
            "Example Measured RGB",
            custom_xy.matrix_RGB_to_XYZ.T * 1.20,
            transfer=("gamma", 2.2),
            aliases=("ExampleMeasuredRGB",),
            reference="Synthetic measured primary XYZ values with preserved scale.",
        )
    for item in caught:
        print("Measured primary constructor warning:", item.message)

    return custom_xy, measured


def _print_route_and_values(custom, measured) -> None:
    """Print compact conversion and registry information."""
    register_RGB_colourspace(custom, overwrite=True)

    sample = np.array([0.4, 0.5, 0.6])
    XYZ = RGB_to_XYZ(sample, colourspace=CUSTOM_NAME)
    recovered = XYZ_to_RGB(XYZ, colourspace=CUSTOM_NAME)
    Lab = convert_color(sample, CUSTOM_NAME, "Lab")
    p3 = RGB_to_RGB(sample, CUSTOM_NAME, "Display P3")

    print("=" * 20 + " custom RGB spaces " + "=" * 20)
    print("Registered custom space:", get_RGB_colourspace("ExampleCustomRGB").name)
    print("Custom transfer:", custom.transfer)
    print("Measured white XYZ:", np.sum(measured.matrix_RGB_to_XYZ.T, axis=0))
    print("Sample custom RGB:", sample)
    print("Custom RGB -> XYZ:", np.round(XYZ, 6))
    print("XYZ -> custom RGB:", np.round(recovered, 6))
    print("Custom RGB -> Lab:", np.round(Lab, 6))
    print("Custom RGB -> Display P3:", np.round(p3, 6))

    path = describe_conversion_path(CUSTOM_NAME, "Lab")
    print("Conversion route:")
    for edge in path.edges:
        print(f"  {edge.source} -> {edge.target}: {edge.description}")


def _plot_custom_conversion(custom) -> None:
    """Plot colour previews before and after conversion."""
    out = output_dir()

    XYZ = RGB_to_XYZ(SAMPLE_RGB, colourspace=custom)
    display_p3 = RGB_to_RGB(SAMPLE_RGB, CUSTOM_NAME, "Display P3")
    rec2020 = RGB_to_RGB(SAMPLE_RGB, CUSTOM_NAME, "Rec.2020")

    rows = [
        ("custom RGB preview", preview_sRGB_from_XYZ(XYZ)),
        ("Display P3 coords", preview_sRGB_from_XYZ(RGB_to_XYZ(display_p3, colourspace="Display P3"))),
        ("Rec.2020 coords", preview_sRGB_from_XYZ(RGB_to_XYZ(rec2020, colourspace="Rec.2020"))),
    ]
    fig, ax = plt.subplots(figsize=(8.5, 2.8))
    plot_swatch_grid(ax, rows, title="Custom RGB Stimuli Routed Through Standard RGB Spaces")
    fig.tight_layout()
    path = out / "07_custom_rgb_conversion_swatches.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def _plot_dynamic_gamma_curves() -> None:
    """Plot scalar and per-channel dynamic gamma transfer curves."""
    out = output_dir()
    encoded = np.linspace(0.0, 1.0, 256)
    rgb = np.stack([encoded, encoded, encoded], axis=-1)
    decoded_per_channel = decode_transfer(rgb, ("gamma", (2.2, 2.3, 2.1)))

    fig, ax = plt.subplots(figsize=(4.8, 3.4), constrained_layout=True)
    ax.plot(encoded, decoded_per_channel[:, 0], label="R gamma 2.2", color="tab:red")
    ax.plot(encoded, decoded_per_channel[:, 1], label="G gamma 2.3", color="tab:green")
    ax.plot(encoded, decoded_per_channel[:, 2], label="B gamma 2.1", color="tab:blue")
    ax.set_title("Per-channel Gamma Decoding")
    ax.set_xlabel("encoded RGB")
    ax.set_ylabel("linear RGB")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)

    path = out / "07_custom_rgb_dynamic_gamma.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def main() -> None:
    custom, measured = _create_custom_spaces()
    _print_route_and_values(custom, measured)
    _plot_custom_conversion(custom)
    _plot_dynamic_gamma_curves()


if __name__ == "__main__":
    main()
