"""Compare basic colour-space conversions against the colour library."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

import colour

from color.constants import D65_XYZ
from color.spaces import (
    IPT_to_XYZ,
    JzCzhz_to_Jzazbz,
    Jzazbz_to_JzCzhz,
    Jzazbz_to_XYZ,
    Lab_to_LCHab,
    Lab_to_XYZ,
    LCHab_to_Lab,
    LCHuv_to_Luv,
    Luv_to_LCHuv,
    Luv_to_XYZ,
    Oklab_to_XYZ,
    RGB_to_XYZ,
    UVW_to_XYZ,
    XYZ_to_IPT,
    XYZ_to_Jzazbz,
    XYZ_to_Lab,
    XYZ_to_Luv,
    XYZ_to_Oklab,
    XYZ_to_RGB,
    XYZ_to_UVW,
    XYZ_to_xyY,
    xyY_to_XYZ,
    convert_color,
)

from _spaces_plot_helpers import output_dir


SAMPLE_SRGB = np.array(
    [
        [0.90, 0.10, 0.10],
        [0.10, 0.70, 0.20],
        [0.10, 0.30, 0.90],
        [0.80, 0.70, 0.20],
        [0.50, 0.50, 0.50],
    ],
    dtype=np.float64,
)


def _whitepoint_xy(whitepoint_XYZ: np.ndarray) -> np.ndarray:
    whitepoint = np.asarray(whitepoint_XYZ, dtype=np.float64)
    return whitepoint[:2] / np.sum(whitepoint)


def _max_abs_error(actual: np.ndarray, expected: np.ndarray) -> float:
    return float(np.max(np.abs(np.asarray(actual) - np.asarray(expected))))


def _record(
    rows: list[tuple[str, float, float]],
    name: str,
    actual: np.ndarray,
    expected: np.ndarray,
    tolerance: float,
) -> None:
    error = _max_abs_error(actual, expected)
    rows.append((name, error, tolerance))
    if error > tolerance:
        raise AssertionError(
            f"{name} max abs error {error:.3e} exceeds tolerance {tolerance:.3e}"
        )


def main() -> None:
    out = output_dir()
    d65_xy = _whitepoint_xy(D65_XYZ)
    rows: list[tuple[str, float, float]] = []

    XYZ = RGB_to_XYZ(SAMPLE_SRGB, colourspace="sRGB")
    XYZ_colour = colour.sRGB_to_XYZ(SAMPLE_SRGB) * 100.0
    _record(rows, "sRGB -> XYZ", XYZ, XYZ_colour, 2e-4)

    sRGB = XYZ_to_RGB(XYZ, colourspace="sRGB")
    sRGB_colour = colour.XYZ_to_sRGB(XYZ / 100.0)
    _record(rows, "XYZ -> sRGB", sRGB, sRGB_colour, 2e-4)

    xyY = XYZ_to_xyY(XYZ)
    xyY_colour = colour.XYZ_to_xyY(XYZ / 100.0)
    xyY_colour[..., 2] *= 100.0
    _record(rows, "XYZ -> xyY", xyY, xyY_colour, 2e-12)
    _record(rows, "xyY -> XYZ", xyY_to_XYZ(xyY), XYZ, 2e-10)

    Lab = XYZ_to_Lab(XYZ, whitepoint_XYZ=D65_XYZ)
    Lab_colour = colour.XYZ_to_Lab(XYZ / 100.0, illuminant=d65_xy)
    _record(rows, "XYZ -> Lab", Lab, Lab_colour, 2e-8)
    _record(rows, "Lab -> XYZ", Lab_to_XYZ(Lab, whitepoint_XYZ=D65_XYZ), XYZ, 2e-8)

    LCHab = Lab_to_LCHab(Lab)
    LCHab_colour = colour.Lab_to_LCHab(Lab)
    _record(rows, "Lab -> LCHab", LCHab, LCHab_colour, 2e-12)
    _record(rows, "LCHab -> Lab", LCHab_to_Lab(LCHab), Lab, 2e-12)

    Luv = XYZ_to_Luv(XYZ, whitepoint_XYZ=D65_XYZ)
    Luv_colour = colour.XYZ_to_Luv(XYZ / 100.0, illuminant=d65_xy)
    _record(rows, "XYZ -> Luv", Luv, Luv_colour, 2e-8)
    _record(rows, "Luv -> XYZ", Luv_to_XYZ(Luv, whitepoint_XYZ=D65_XYZ), XYZ, 2e-8)

    LCHuv = Luv_to_LCHuv(Luv)
    LCHuv_colour = colour.Luv_to_LCHuv(Luv)
    _record(rows, "Luv -> LCHuv", LCHuv, LCHuv_colour, 2e-12)
    _record(rows, "LCHuv -> Luv", LCHuv_to_Luv(LCHuv), Luv, 2e-12)

    UVW = XYZ_to_UVW(XYZ, whitepoint_XYZ=D65_XYZ)
    UVW_colour = colour.XYZ_to_UVW(XYZ, illuminant=d65_xy)
    _record(rows, "XYZ -> UVW", UVW, UVW_colour, 2e-4)
    _record(rows, "UVW -> XYZ", UVW_to_XYZ(UVW, whitepoint_XYZ=D65_XYZ), XYZ, 2e-8)

    Oklab = XYZ_to_Oklab(XYZ_D65_referred=XYZ)
    Oklab_colour = colour.XYZ_to_Oklab(XYZ / 100.0)
    _record(rows, "XYZ -> Oklab", Oklab, Oklab_colour, 2e-10)
    _record(rows, "Oklab -> XYZ", Oklab_to_XYZ(Oklab), XYZ, 1e-5)

    IPT = XYZ_to_IPT(XYZ_D65_referred=XYZ)
    IPT_colour = colour.XYZ_to_IPT(XYZ / 100.0)
    _record(rows, "XYZ -> IPT", IPT, IPT_colour, 2e-10)
    _record(rows, "IPT -> XYZ", IPT_to_XYZ(IPT), XYZ, 2e-8)

    Jzazbz = XYZ_to_Jzazbz(XYZ_D65_referred=XYZ)
    Jzazbz_colour = colour.XYZ_to_Jzazbz(XYZ / 100.0)
    _record(rows, "XYZ -> Jzazbz", Jzazbz, Jzazbz_colour, 2e-10)
    _record(rows, "Jzazbz -> XYZ", Jzazbz_to_XYZ(Jzazbz), XYZ, 2e-5)

    JzCzhz = Jzazbz_to_JzCzhz(Jzazbz)
    _record(rows, "Jzazbz -> JzCzhz -> Jzazbz", JzCzhz_to_Jzazbz(JzCzhz), Jzazbz, 2e-14)

    routed = convert_color(SAMPLE_SRGB, "sRGB", "Jzazbz")
    _record(rows, "convert sRGB -> Jzazbz", routed, Jzazbz_colour, 2e-10)

    print("Reference accuracy against colour")
    print(f"{'conversion':<24} {'max abs error':>14} {'tolerance':>12}")
    for name, error, tolerance in rows:
        print(f"{name:<24} {error:>14.3e} {tolerance:>12.3e}")

    labels = [name for name, _, _ in rows]
    errors = np.array([max(error, 1e-16) for _, error, _ in rows])
    tolerances = np.array([tolerance for _, _, tolerance in rows])

    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    x = np.arange(len(labels))
    ax.bar(x, errors, color="tab:blue", label="max abs error")
    ax.plot(x, tolerances, color="tab:red", marker="o", linewidth=1.2, label="tolerance")
    ax.set_yscale("log")
    ax.set_ylabel("absolute error")
    ax.set_title("Basic Spaces Accuracy Compared With colour")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=55, ha="right")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    path = out / "04_reference_accuracy_errors.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


if __name__ == "__main__":
    main()
