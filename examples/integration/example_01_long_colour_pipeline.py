"""Long cross-module colour pipeline demonstration.

This example intentionally connects several layers:

generators -> spectra -> colorimetry -> spaces -> adaptation -> difference

It uses three samples:

* a generated three-peak LED spectrum.
* an encoded sRGB triplet [0.4, 0.5, 0.6].
* a Macbeth ColorChecker "Blue Sky" reflectance patch under D65.

All samples are converted to XYZ and CIE 2006 2-degree LMS. The XYZ values then
follow a long reversible colour-space chain:

XYZ(D65) -> Luv(D65) -> XYZ(D65)
-> adapt to D50 -> CAM02-UCS(D50) -> XYZ(D50)
-> adapt to D65 -> Oklab -> XYZ(D65)
-> Lab(D65) -> CIEDE2000.

The final XYZ values are also analysed with dominant wavelength / purity and
CCT + Duv, then reconstructed back to xy coordinates through their inverse
helpers.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.adaptation import adapt_from_D65, adapt_to_D65
from color.colorimetry import (
    CCT_Duv_to_xy,
    XYZ_to_LMS,
    XYZ_to_xy,
    analyze_chromaticity,
    analyze_temperature,
    emission_to_LMS,
    emission_to_XYZ,
    is_inside_chromaticity_locus,
    reflectance_to_LMS,
    reflectance_to_XYZ,
    xy_from_dominant_wavelength_pc,
    xy_from_dominant_wavelength_pe,
)
from color.constants import D50_XYZ, D65_XYZ
from color.datasets.color_cards import get_color_card
from color.difference import delta_E_CIE2000
from color.generators.leds import multi_led_spd
from color.spaces import SpaceSpec, convert_color
from color.spectra import (
    from_D65_illuminant,
    from_cie1931_xyz_cmfs,
    from_cie2006_lms_2degree_fundamentals,
    from_columns,
)


SRGB_SIGNAL = np.array([0.4, 0.5, 0.6], dtype=np.float64)
SAMPLE_NAMES = (
    "three-peak LED",
    "sRGB [0.4, 0.5, 0.6]",
    "Macbeth Blue Sky",
)

VIEWING_D50_AVERAGE = {
    "XYZ_w": D50_XYZ,
    "L_A": 318.31,
    "Y_b": 20.0,
    "surround": "Average",
}


def _make_led_spectrum():
    """Generate and wrap a three-peak LED spectral distribution."""
    wavelengths = np.arange(390, 831, 1.0, dtype=np.float64)
    raw = multi_led_spd(
        wavelength_nm=wavelengths,
        peak_wavelengths=(460.0, 530.0, 620.0),
        half_spectral_widths=(18.0, 28.0, 22.0),
        peak_power_ratios=(0.4, 0.7, 0.9),
    )
    return from_columns(
        raw,
        y="spd",
        name="three-peak LED spectrum",
        metadata={"source": "generated Ohno 2005 LED mixture"},
    )



def _make_reflectance_spectrum():
    """Read and wrap one colour-card patch as a reflectance spectrum."""
    raw_card = get_color_card("macbeth")
    return from_columns(
        raw_card,
        y="Blue Sky",
        name="Macbeth ColorChecker Blue Sky reflectance",
        metadata={
            "source": "Macbeth ColorChecker",
            "patch": "Blue Sky",
            "quantity": "spectral_reflectance",
            "value_unit": "reflectance_factor",
        },
    )


def _compute_initial_responses() -> tuple[np.ndarray, np.ndarray]:
    """Return XYZ and LMS rows for LED, sRGB and D65 reflectance samples."""
    led = _make_led_spectrum()
    reflectance = _make_reflectance_spectrum()
    d65 = from_D65_illuminant()
    cmfs = from_cie1931_xyz_cmfs(interval_nm=1)
    print("cmfs keys:", cmfs.keys())
    fundamentals = from_cie2006_lms_2degree_fundamentals(
        interval_nm=1,
    )

    led_XYZ = emission_to_XYZ(led, cmfs=cmfs)
    led_LMS = emission_to_LMS(led, fundamentals=fundamentals)
    reflectance_XYZ = reflectance_to_XYZ(
        reflectance,
        illuminant=d65,
        cmfs=cmfs,
    )
    reflectance_LMS = reflectance_to_LMS(
        reflectance,
        illuminant=d65,
        fundamentals=fundamentals,
        normalisation_channel="m",
    )

    xyz_spec_d65 = SpaceSpec("XYZ", whitepoint_XYZ=D65_XYZ)
    srgb_XYZ = convert_color(SRGB_SIGNAL, "sRGB", xyz_spec_d65)
    srgb_LMS = XYZ_to_LMS(srgb_XYZ, observer=2)

    XYZ_D65 = np.vstack((led_XYZ, srgb_XYZ, reflectance_XYZ))
    LMS_2006_2 = np.vstack((led_LMS, srgb_LMS, reflectance_LMS))
    return XYZ_D65, LMS_2006_2


def _run_colour_chain(XYZ_D65: np.ndarray) -> dict[str, np.ndarray]:
    """Run the long XYZ/Luv/CAM02/Oklab/Lab chain."""
    xyz_spec_d65 = SpaceSpec("XYZ", whitepoint_XYZ=D65_XYZ)
    xyz_spec_d50 = SpaceSpec("XYZ", whitepoint_XYZ=D50_XYZ)
    luv_spec_d65 = SpaceSpec("Luv", whitepoint_XYZ=D65_XYZ)
    lab_spec_d65 = SpaceSpec("Lab", whitepoint_XYZ=D65_XYZ)
    cam02ucs_d50 = SpaceSpec("CAM02-UCS", **VIEWING_D50_AVERAGE)

    Luv_D65 = convert_color(XYZ_D65, xyz_spec_d65, luv_spec_d65)
    XYZ_from_Luv_D65 = convert_color(Luv_D65, luv_spec_d65, xyz_spec_d65)

    XYZ_D50 = adapt_from_D65(XYZ_from_Luv_D65, target_white_XYZ=D50_XYZ)
    CAM02UCS_D50 = convert_color(XYZ_D50, xyz_spec_d50, cam02ucs_d50)
    XYZ_from_CAM02_D50 = convert_color(CAM02UCS_D50, cam02ucs_d50, xyz_spec_d50)

    XYZ_for_Oklab_D65 = adapt_to_D65(
        XYZ_from_CAM02_D50,
        source_white_XYZ=D50_XYZ,
    )
    Oklab = convert_color(XYZ_for_Oklab_D65, xyz_spec_d65, "Oklab")
    XYZ_roundtrip_D65 = convert_color(Oklab, "Oklab", xyz_spec_d65)

    Lab_D65 = convert_color(XYZ_roundtrip_D65, xyz_spec_d65, lab_spec_d65)
    return {
        "Luv_D65": Luv_D65,
        "XYZ_from_Luv_D65": XYZ_from_Luv_D65,
        "XYZ_D50": XYZ_D50,
        "CAM02UCS_D50": CAM02UCS_D50,
        "XYZ_from_CAM02_D50": XYZ_from_CAM02_D50,
        "XYZ_for_Oklab_D65": XYZ_for_Oklab_D65,
        "Oklab": Oklab,
        "XYZ_roundtrip_D65": XYZ_roundtrip_D65,
        "Lab_D65": Lab_D65,
    }


def _row_table(title: str, values: np.ndarray, labels: tuple[str, ...]) -> None:
    """Print a compact numeric table."""
    print(title)
    header = "sample".ljust(24) + " ".join(label.rjust(14) for label in labels)
    print(header)
    for name, row in zip(SAMPLE_NAMES, values):
        print(name.ljust(24) + " ".join(f"{value:14.6f}" for value in row))
    print()


def _print_chromaticity_analysis(xy: np.ndarray) -> tuple[float, float]:
    """Print dominant wavelength and purity analysis, then test inverse paths."""
    analysis = analyze_chromaticity(xy)
    xy_from_pe = xy_from_dominant_wavelength_pe(
        analysis.wavelength,
        analysis.excitation_purity,
    )
    xy_from_pc = xy_from_dominant_wavelength_pc(
        analysis.wavelength,
        analysis.colorimetric_purity,
    )
    pe_error = np.linalg.norm(xy_from_pe - xy, axis=1)
    pc_error = np.linalg.norm(xy_from_pc - xy, axis=1)
    inside = is_inside_chromaticity_locus(xy)

    print("Chromaticity analysis")
    header = (
        "sample".ljust(24)
        + "x".rjust(12)
        + "y".rjust(12)
        + "wl/nm".rjust(12)
        + "Pe".rjust(12)
        + "Pc".rjust(12)
        + "inside".rjust(12)
    )
    print(header)
    for index, name in enumerate(SAMPLE_NAMES):
        print(
            name.ljust(24)
            + f"{xy[index, 0]:12.6f}"
            + f"{xy[index, 1]:12.6f}"
            + f"{analysis.wavelength[index]:12.3f}"
            + f"{analysis.excitation_purity[index]:12.6f}"
            + f"{analysis.colorimetric_purity[index]:12.6f}"
            + f"{str(bool(inside[index])):>12}"
        )
    print(f"xy from dominant wavelength + Pe max error: {np.max(pe_error):.3e}")
    print(f"xy from dominant wavelength + Pc max error: {np.max(pc_error):.3e}")
    print()
    return float(np.max(pe_error)), float(np.max(pc_error))


def _print_temperature_analysis(xy: np.ndarray) -> tuple[float, float]:
    """Print CCT + Duv analysis and inverse reconstruction checks."""
    max_errors: list[float] = []

    for method in ("robertson1968", "ohno2013"):
        analysis = analyze_temperature(xy, method=method)
        cct_duv = np.stack((analysis.CCT, analysis.Duv), axis=-1)
        xy_reconstructed = CCT_Duv_to_xy(cct_duv, method=method)
        error = np.linalg.norm(xy_reconstructed - xy, axis=1)
        max_errors.append(float(np.max(error)))

        print(f"Temperature analysis ({method})")
        header = (
            "sample".ljust(24)
            + "CCT/K".rjust(14)
            + "Duv".rjust(14)
            + "xy error".rjust(14)
        )
        print(header)
        for index, name in enumerate(SAMPLE_NAMES):
            print(
                name.ljust(24)
                + f"{analysis.CCT[index]:14.3f}"
                + f"{analysis.Duv[index]:14.8f}"
                + f"{error[index]:14.3e}"
            )
        print()

    return max_errors[0], max_errors[1]


def _print_delta_e_pairs(Lab: np.ndarray) -> np.ndarray:
    """Print pairwise CIEDE2000 values between all final Lab samples."""
    pairs = (
        (0, 1),
        (0, 2),
        (1, 2),
    )
    values = np.array(
        [delta_E_CIE2000(Lab[left], Lab[right]) for left, right in pairs],
        dtype=np.float64,
    )

    print("Pairwise CIEDE2000 between final D65 Lab rows")
    for value, (left, right) in zip(values, pairs):
        print(f"{SAMPLE_NAMES[left]} -> {SAMPLE_NAMES[right]}: {value:.6f}")
    print()
    return values


def main() -> None:
    XYZ_D65, LMS_2006_2 = _compute_initial_responses()

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        chain = _run_colour_chain(XYZ_D65)
    if caught:
        messages = "\n".join(str(warning.message) for warning in caught)
        raise AssertionError(f"Unexpected conversion warning(s):\n{messages}")

    luv_error = np.linalg.norm(chain["XYZ_from_Luv_D65"] - XYZ_D65, axis=1)
    cam02_error = np.linalg.norm(chain["XYZ_from_CAM02_D50"] - chain["XYZ_D50"], axis=1)
    oklab_error = np.linalg.norm(
        chain["XYZ_roundtrip_D65"] - chain["XYZ_for_Oklab_D65"],
        axis=1,
    )
    full_error = np.linalg.norm(chain["XYZ_roundtrip_D65"] - XYZ_D65, axis=1)
    xy_final = XYZ_to_xy(chain["XYZ_roundtrip_D65"])

    _row_table("Initial XYZ from CIE 1931 / sRGB conversion", XYZ_D65, ("X", "Y", "Z"))
    _row_table("Initial LMS using CIE 2006 2-degree fundamentals", LMS_2006_2, ("L", "M", "S"))
    _row_table("Luv under D65", chain["Luv_D65"], ("L*", "u*", "v*"))
    _row_table("CAM02-UCS under D50 viewing white", chain["CAM02UCS_D50"], ("J'", "a'", "b'"))
    _row_table("Oklab after explicit D50 -> D65 adaptation", chain["Oklab"], ("L", "a", "b"))
    _row_table("Final Lab under D65", chain["Lab_D65"], ("L*", "a*", "b*"))

    print("Closure checks")
    for name, values in (
        ("XYZ -> Luv -> XYZ", luv_error),
        ("XYZ(D50) -> CAM02-UCS -> XYZ(D50)", cam02_error),
        ("XYZ(D65) -> Oklab -> XYZ(D65)", oklab_error),
        ("full chain compared with initial D65 XYZ", full_error),
    ):
        print(f"{name:<44} max={np.max(values):.3e}")
    print()
    delta_e = _print_delta_e_pairs(chain["Lab_D65"])

    pe_error, pc_error = _print_chromaticity_analysis(xy_final)
    robertson_error, ohno_error = _print_temperature_analysis(xy_final)

    assert np.max(luv_error) < 1e-9
    assert np.max(cam02_error) < 1e-8
    assert np.max(oklab_error) < 1e-4
    assert np.max(full_error) < 1e-4
    assert np.all(np.isfinite(delta_e))
    assert pe_error < 1e-12
    assert pc_error < 1e-12
    assert robertson_error < 1e-6
    assert ohno_error < 1e-6


if __name__ == "__main__":
    main()
