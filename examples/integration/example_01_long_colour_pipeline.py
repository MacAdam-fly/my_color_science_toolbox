"""End-to-end colour-science pipeline demonstration.

This script is the runnable companion to the root ``readme.md`` long-chain
example. It demonstrates how the stable modules fit together without implying
that every module is a strict child of another module.

Covered layers:

* datasets / generators -> spectra
* spectra -> colorimetry
* adaptation / appearance / spaces
* difference / gamut / recovery
* plot / io
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.adaptation import adapt_from_D65
from color.appearance import XYZ_to_CIECAM16
from color.colorimetry import (
    XYZ_to_LMS,
    XYZ_to_xy,
    analyze_chromaticity,
    analyze_temperature,
    emission_to_LMS,
    emission_to_XYZ,
    reflectance_to_LMS,
    reflectance_to_XYZ,
)
from color.constants import D50_XYZ, D65_XYZ
from color.datasets import get_color_card
from color.difference import delta_E_CIE2000
from color.gamut import analyze_gamut
from color.generators import multi_led_spd
from color.io import save_figure
from color.plot import plot_lines, plot_style
from color.recovery import recover_reflectance_from_XYZ
from color.spaces import SpaceSpec, convert_color
from color.spectra import (
    from_D65_illuminant,
    from_cie1931_xyz_cmfs,
    from_cie2006_lms_2degree_fundamentals,
    from_columns,
)


OUTPUT_DIR = Path(__file__).resolve().parent / "output"
SRGB_SIGNAL = np.array([0.4, 0.5, 0.6], dtype=np.float64)
SAMPLE_NAMES = (
    "generated three-peak LED",
    "encoded sRGB [0.4, 0.5, 0.6]",
    "Macbeth Blue Sky reflectance",
)


def _make_led_spectrum():
    """Generate and wrap a three-peak LED emission spectrum."""
    wavelengths = np.arange(390.0, 831.0, 1.0)
    raw = multi_led_spd(
        wavelength_nm=wavelengths,
        peak_wavelengths=(460.0, 530.0, 620.0),
        half_spectral_widths=(18.0, 28.0, 22.0),
        peak_power_ratios=(0.4, 0.7, 0.9),
    )
    return from_columns(raw, y="spd", name="generated three-peak LED")


def _make_colour_card_patch(name: str):
    """Read one Macbeth ColorChecker reflectance patch."""
    raw_card = get_color_card("macbeth")
    return from_columns(raw_card, y=name, name=f"Macbeth {name}")


def _print_rows(title: str, values: np.ndarray, columns: tuple[str, ...]) -> None:
    """Print a compact table for one row per sample."""
    print(title)
    print("sample".ljust(32) + "".join(column.rjust(15) for column in columns))
    for name, row in zip(SAMPLE_NAMES, values):
        print(name.ljust(32) + "".join(f"{value:15.6f}" for value in row))
    print()


def main() -> None:
    """Run the full pipeline and save one comparison figure."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    # 1. Data sources -> spectra.
    led = _make_led_spectrum()
    blue_sky = _make_colour_card_patch("Blue Sky")
    foliage = _make_colour_card_patch("Foliage")

    cmfs = from_cie1931_xyz_cmfs(interval_nm=1)
    fundamentals = from_cie2006_lms_2degree_fundamentals(interval_nm=1)
    d65 = from_D65_illuminant()

    # 2. Spectra / RGB signal -> colorimetry products.
    led_XYZ = emission_to_XYZ(led, cmfs=cmfs)
    led_LMS = emission_to_LMS(led, fundamentals=fundamentals)

    xyz_d65 = SpaceSpec("XYZ", whitepoint_XYZ=D65_XYZ)
    srgb_XYZ = convert_color(SRGB_SIGNAL, "sRGB", xyz_d65)
    srgb_LMS = XYZ_to_LMS(srgb_XYZ, observer=2)

    blue_XYZ = reflectance_to_XYZ(blue_sky, illuminant=d65, cmfs=cmfs)
    blue_LMS = reflectance_to_LMS(
        blue_sky,
        illuminant=d65,
        fundamentals=fundamentals,
        normalisation_channel="m",
    )

    XYZ_rows = np.vstack((led_XYZ, srgb_XYZ, blue_XYZ))
    LMS_rows = np.vstack((led_LMS, srgb_LMS, blue_LMS))
    xy_rows = XYZ_to_xy(XYZ_rows)
    relative_Y = XYZ_rows[:, 1]

    temperature = analyze_temperature(xy_rows, method="ohno2013")
    chromaticity = analyze_chromaticity(xy_rows)

    _print_rows("CIE 1931 XYZ", XYZ_rows, ("X", "Y", "Z"))
    _print_rows("CIE 2006 2-degree LMS", LMS_rows, ("L", "M", "S"))
    _print_rows("CIE xy and relative luminance", np.column_stack((xy_rows, relative_Y)), ("x", "y", "Y"))

    print("Temperature and dominant-wavelength analysis")
    print("sample".ljust(32) + "CCT/K".rjust(15) + "Duv".rjust(15) + "wl/nm".rjust(15) + "Pe".rjust(15))
    for index, name in enumerate(SAMPLE_NAMES):
        print(
            name.ljust(32)
            + f"{temperature.CCT[index]:15.3f}"
            + f"{temperature.Duv[index]:15.8f}"
            + f"{chromaticity.wavelength[index]:15.3f}"
            + f"{chromaticity.excitation_purity[index]:15.6f}"
        )
    print()

    # 3. Colorimetry products -> colour spaces and appearance.
    lab_d65 = convert_color(XYZ_rows, xyz_d65, SpaceSpec("Lab", whitepoint_XYZ=D65_XYZ))
    luv_d65 = convert_color(XYZ_rows, xyz_d65, SpaceSpec("Luv", whitepoint_XYZ=D65_XYZ))
    oklab = convert_color(XYZ_rows, xyz_d65, "Oklab")

    # Explicit adaptation keeps the whitepoint operation visible.
    XYZ_D50 = adapt_from_D65(XYZ_rows, target_white_XYZ=D50_XYZ)
    cam16 = XYZ_to_CIECAM16(XYZ_D50, XYZ_w=D50_XYZ, L_A=318.31, Y_b=20.0)
    cam16ucs_d50 = convert_color(
        XYZ_D50,
        SpaceSpec("XYZ", whitepoint_XYZ=D50_XYZ),
        SpaceSpec(
            "CAM16-UCS",
            XYZ_w=D50_XYZ,
            L_A=318.31,
            Y_b=20.0,
            surround="Average",
        ),
    )

    _print_rows("D65 Lab", lab_d65, ("L*", "a*", "b*"))
    _print_rows("D65 Luv", luv_d65, ("L*", "u*", "v*"))
    _print_rows("D65 Oklab", oklab, ("L", "a", "b"))
    _print_rows("D50 CAM16-UCS", cam16ucs_d50, ("J'", "a'", "b'"))
    print("CIECAM16 J, M, h")
    _print_rows("", np.column_stack((cam16.J, cam16.M, cam16.h)), ("J", "M", "h"))

    # 4. Difference: compare Blue Sky against another colour-card patch.
    foliage_XYZ = reflectance_to_XYZ(foliage, illuminant=d65, cmfs=cmfs)
    foliage_lab = convert_color(foliage_XYZ, xyz_d65, SpaceSpec("Lab", whitepoint_XYZ=D65_XYZ))
    blue_vs_foliage_de00 = delta_E_CIE2000(lab_d65[2], foliage_lab)
    print(f"Blue Sky -> Foliage CIEDE2000: {blue_vs_foliage_de00:.6f}\n")

    # 5. Gamut: a coarse analysis is enough for a fast integration example.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        gamut = analyze_gamut(
            "sRGB",
            L_values=np.arange(0.0, 101.0, 20.0),
            hue_values=np.arange(0.0, 361.0, 20.0),
            iterations=6,
        )
    print("sRGB gamut analysis")
    print(f"xy area: {gamut.xy_area:.6f}")
    print(f"Lab volume: {gamut.lab_volume:.6f}")
    print(f"Pointer volume coverage: {gamut.volume_coverage_pointer:.6f}\n")

    # 6. Recovery: reconstruct a bounded smooth reflectance for Blue Sky XYZ.
    recovered = recover_reflectance_from_XYZ(
        blue_XYZ,
        illuminant=d65,
        cmfs=cmfs,
        shape=blue_sky.shape,
    )
    recovered_XYZ = reflectance_to_XYZ(recovered, illuminant=d65, cmfs=cmfs)
    recovery_error = np.linalg.norm(recovered_XYZ - blue_XYZ)
    print(f"Blue Sky recovery XYZ closure error: {recovery_error:.6e}\n")

    # 7. Plot and save one output figure.
    with plot_style("presentation", font_scale=0.75, line_scale=0.9):
        fig, ax = plot_lines(
            [
                (blue_sky.wavelengths, blue_sky.values),
                (recovered.wavelengths, recovered.values),
            ],
            labels=("Macbeth Blue Sky", "Recovered from XYZ"),
            xlabel="Wavelength (nm)",
            ylabel="Reflectance",
        )
    output_path = save_figure(
        OUTPUT_DIR / "01_long_colour_pipeline_reflectance_recovery.png",
        fig=fig,
        close=True,
    )
    print(f"Saved figure: {output_path}")

    assert np.all(np.isfinite(XYZ_rows))
    assert np.all(np.isfinite(LMS_rows))
    assert np.all(np.isfinite(lab_d65))
    assert np.all(np.isfinite(oklab))
    assert np.all(np.isfinite(cam16ucs_d50))
    assert np.isfinite(blue_vs_foliage_de00)
    assert np.isfinite(gamut.lab_volume)
    assert recovery_error < 1e-2
    assert output_path.exists()


if __name__ == "__main__":
    main()
