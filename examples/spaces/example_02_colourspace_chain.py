"""Visualise a long closed conversion chain across registered spaces."""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.constants import D65_XYZ
from color.plot import plot_swatch_grid, preview_sRGB_from_XYZ
from color.spaces import SpaceSpec, convert_color

from _spaces_plot_helpers import output_dir


SAMPLE_SRGB = np.array(
    [
        [0.90, 0.12, 0.10],
        [0.95, 0.72, 0.10],
        [0.12, 0.68, 0.24],
        [0.08, 0.35, 0.90],
        [0.55, 0.35, 0.75],
        [0.50, 0.50, 0.50],
    ],
    dtype=np.float64,
)

VIEWING_AVERAGE = {
    "XYZ_w": D65_XYZ,
    "L_A": 318.31,
    "Y_b": 20.0,
    "surround": "Average",
}

CHAIN_LABEL = (
    "sRGB -> XYZ -> xyY -> XYZ -> Lab(D65) -> LCHab -> Lab(D65) -> "
    "Luv(D65) -> LCHuv -> Luv(D65) -> UVW(D65) -> XYZ -> Oklab -> "
    "Oklch -> Oklab -> IPT -> XYZ -> Jzazbz -> JzCzhz -> Jzazbz -> "
    "CAM02-UCS -> CAM02-LCD -> CAM02-SCD -> XYZ -> CAM16-UCS -> "
    "CAM16-LCD -> CAM16-SCD -> XYZ -> sRGB"
)


def _xyz_spec() -> SpaceSpec:
    """Return an XYZ hub spec that declares the D65/Y=100 reference domain."""
    return SpaceSpec("XYZ", whitepoint_XYZ=D65_XYZ)


def _whitepoint_spec(name: str) -> SpaceSpec:
    """Return a D65 whitepoint parameterized colour-space spec."""
    return SpaceSpec(name, whitepoint_XYZ=D65_XYZ)


def _cam_spec(name: str) -> SpaceSpec:
    """Return a CAM uniform-space spec using shared viewing conditions."""
    return SpaceSpec(name, **VIEWING_AVERAGE)


def _run_chain() -> dict[str, np.ndarray]:
    """Run the long closed colour-space chain and return key intermediates."""
    XYZ = convert_color(SAMPLE_SRGB, "sRGB", _xyz_spec())
    xyY = convert_color(XYZ, _xyz_spec(), "xyY")
    XYZ_from_xyY = convert_color(xyY, "xyY", _xyz_spec())

    Lab = convert_color(XYZ_from_xyY, _xyz_spec(), _whitepoint_spec("Lab"))
    LCHab = convert_color(Lab, _whitepoint_spec("Lab"), _whitepoint_spec("LCHab"))
    Lab_return = convert_color(LCHab, _whitepoint_spec("LCHab"), _whitepoint_spec("Lab"))

    Luv = convert_color(Lab_return, _whitepoint_spec("Lab"), _whitepoint_spec("Luv"))
    LCHuv = convert_color(Luv, _whitepoint_spec("Luv"), _whitepoint_spec("LCHuv"))
    Luv_return = convert_color(LCHuv, _whitepoint_spec("LCHuv"), _whitepoint_spec("Luv"))

    UVW = convert_color(Luv_return, _whitepoint_spec("Luv"), _whitepoint_spec("UVW"))
    XYZ_from_UVW = convert_color(UVW, _whitepoint_spec("UVW"), _xyz_spec())

    Oklab = convert_color(XYZ_from_UVW, _xyz_spec(), "Oklab")
    Oklch = convert_color(Oklab, "Oklab", "Oklch")
    Oklab_return = convert_color(Oklch, "Oklch", "Oklab")

    IPT = convert_color(Oklab_return, "Oklab", "IPT")
    XYZ_from_IPT = convert_color(IPT, "IPT", _xyz_spec())

    Jzazbz = convert_color(XYZ_from_IPT, _xyz_spec(), "Jzazbz")
    JzCzhz = convert_color(Jzazbz, "Jzazbz", "JzCzhz")
    Jzazbz_return = convert_color(JzCzhz, "JzCzhz", "Jzazbz")

    CAM02_UCS = convert_color(Jzazbz_return, "Jzazbz", _cam_spec("CAM02-UCS"))
    CAM02_LCD = convert_color(CAM02_UCS, _cam_spec("CAM02-UCS"), _cam_spec("CAM02-LCD"))
    CAM02_SCD = convert_color(CAM02_LCD, _cam_spec("CAM02-LCD"), _cam_spec("CAM02-SCD"))
    XYZ_from_CAM02 = convert_color(CAM02_SCD, _cam_spec("CAM02-SCD"), _xyz_spec())

    CAM16_UCS = convert_color(XYZ_from_CAM02, _xyz_spec(), _cam_spec("CAM16-UCS"))
    CAM16_LCD = convert_color(CAM16_UCS, _cam_spec("CAM16-UCS"), _cam_spec("CAM16-LCD"))
    CAM16_SCD = convert_color(CAM16_LCD, _cam_spec("CAM16-LCD"), _cam_spec("CAM16-SCD"))
    XYZ_final = convert_color(CAM16_SCD, _cam_spec("CAM16-SCD"), _xyz_spec())
    sRGB_final = convert_color(XYZ_final, _xyz_spec(), "sRGB")

    return {
        "XYZ": XYZ,
        "xyY": xyY,
        "XYZ_from_xyY": XYZ_from_xyY,
        "Lab": Lab,
        "LCHab": LCHab,
        "Luv": Luv,
        "LCHuv": LCHuv,
        "UVW": UVW,
        "XYZ_from_UVW": XYZ_from_UVW,
        "Oklab": Oklab,
        "Oklch": Oklch,
        "IPT": IPT,
        "XYZ_from_IPT": XYZ_from_IPT,
        "Jzazbz": Jzazbz,
        "JzCzhz": JzCzhz,
        "CAM02_UCS": CAM02_UCS,
        "CAM02_LCD": CAM02_LCD,
        "CAM02_SCD": CAM02_SCD,
        "XYZ_from_CAM02": XYZ_from_CAM02,
        "CAM16_UCS": CAM16_UCS,
        "CAM16_LCD": CAM16_LCD,
        "CAM16_SCD": CAM16_SCD,
        "XYZ_final": XYZ_final,
        "sRGB_final": sRGB_final,
    }


def _print_summary(values: dict[str, np.ndarray]) -> None:
    """Print chain metadata and closure errors."""
    sRGB_error = np.linalg.norm(values["sRGB_final"] - SAMPLE_SRGB, axis=1)
    XYZ_error = np.linalg.norm(values["XYZ_final"] - values["XYZ"], axis=1)

    print("Long closed colour-space conversion chain")
    print(CHAIN_LABEL)
    print()
    for name in (
        "XYZ",
        "xyY",
        "Lab",
        "Luv",
        "Oklab",
        "IPT",
        "Jzazbz",
        "CAM02_UCS",
        "CAM16_UCS",
        "sRGB_final",
    ):
        print(f"{name:<14} shape={values[name].shape}")
    print()
    print(f"Max XYZ closure error:  {np.max(XYZ_error):.3e}")
    print(f"Max sRGB closure error: {np.max(sRGB_error):.3e}")


def _plot_swatches(values: dict[str, np.ndarray], out: Path) -> None:
    """Plot input and selected round-trip preview swatches."""
    rows = [
        ("input sRGB", SAMPLE_SRGB),
        ("after xyY", preview_sRGB_from_XYZ(values["XYZ_from_xyY"])),
        ("after IPT", preview_sRGB_from_XYZ(values["XYZ_from_IPT"])),
        ("after CAM02", preview_sRGB_from_XYZ(values["XYZ_from_CAM02"])),
        ("final sRGB", np.clip(values["sRGB_final"], 0.0, 1.0)),
    ]
    fig, _ax = plot_swatch_grid(rows, title="Long Closed Chain Preview")
    path = out / "02_long_chain_swatches.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def _plot_planes(values: dict[str, np.ndarray], out: Path) -> None:
    """Plot selected opponent planes from the chain."""
    fig, axes = plt.subplots(2, 2, figsize=(10.4, 8.0))
    planes = [
        ("Lab a* / b*", values["Lab"][:, 1], values["Lab"][:, 2], "a*", "b*"),
        ("Oklab a / b", values["Oklab"][:, 1], values["Oklab"][:, 2], "a", "b"),
        ("Jzazbz az / bz", values["Jzazbz"][:, 1], values["Jzazbz"][:, 2], "az", "bz"),
        ("CAM16-UCS a' / b'", values["CAM16_UCS"][:, 1], values["CAM16_UCS"][:, 2], "a'", "b'"),
    ]
    for ax, (title, x, y, xlabel, ylabel) in zip(axes.flat, planes):
        ax.scatter(x, y, c=np.clip(SAMPLE_SRGB, 0.0, 1.0), edgecolors="black", s=68)
        for index, (px, py) in enumerate(zip(x, y), start=1):
            ax.annotate(f"C{index}", (px, py), xytext=(5, 5), textcoords="offset points", fontsize=8)
        ax.axhline(0.0, color="0.75", linewidth=0.8)
        ax.axvline(0.0, color="0.75", linewidth=0.8)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.25)
    fig.tight_layout()
    path = out / "02_long_chain_planes.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def _plot_errors(values: dict[str, np.ndarray], out: Path) -> None:
    """Plot final closure errors in XYZ and sRGB."""
    labels = [f"C{i + 1}" for i in range(SAMPLE_SRGB.shape[0])]
    sRGB_error = np.linalg.norm(values["sRGB_final"] - SAMPLE_SRGB, axis=1)
    XYZ_error = np.linalg.norm(values["XYZ_final"] - values["XYZ"], axis=1)

    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    x = np.arange(len(labels))
    width = 0.36
    ax.bar(x - width / 2, np.maximum(XYZ_error, 1e-16), width=width, label="XYZ error", color="tab:blue")
    ax.bar(x + width / 2, np.maximum(sRGB_error, 1e-16), width=width, label="sRGB error", color="tab:green")
    ax.set_yscale("log")
    ax.set_title("Long Chain Closure Error")
    ax.set_xlabel("sample")
    ax.set_ylabel("Euclidean error")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    path = out / "02_long_chain_roundtrip_error.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def main() -> None:
    out = output_dir()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        values = _run_chain()
    if caught:
        messages = "\n".join(str(warning.message) for warning in caught)
        raise AssertionError(f"Example 02 should not emit D65 route warnings:\n{messages}")

    _print_summary(values)
    _plot_swatches(values, out)
    _plot_planes(values, out)
    _plot_errors(values, out)


if __name__ == "__main__":
    main()
