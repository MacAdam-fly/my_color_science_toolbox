"""Visualise chained conversions across RGB, XYZ, Lab, Luv and Oklab."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.constants import D50_XYZ, D65_XYZ
from color.spaces import SpaceSpec, convert_color

from _spaces_plot_helpers import output_dir, plot_swatch_grid, preview_sRGB_from_XYZ


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


def main() -> None:
    out = output_dir()

    XYZ = convert_color(SAMPLE_SRGB, "sRGB", "XYZ")
    Lab_D65 = convert_color(XYZ, "XYZ", SpaceSpec("Lab", whitepoint_XYZ=D65_XYZ))
    LCHab_D65 = convert_color(
        Lab_D65,
        SpaceSpec("Lab", whitepoint_XYZ=D65_XYZ),
        SpaceSpec("LCHab", whitepoint_XYZ=D65_XYZ),
    )
    Luv_D65 = convert_color(
        LCHab_D65,
        SpaceSpec("LCHab", whitepoint_XYZ=D65_XYZ),
        SpaceSpec("Luv", whitepoint_XYZ=D65_XYZ),
    )
    LCHuv_D65 = convert_color(
        Luv_D65,
        SpaceSpec("Luv", whitepoint_XYZ=D65_XYZ),
        SpaceSpec("LCHuv", whitepoint_XYZ=D65_XYZ),
    )
    Oklab = convert_color(LCHuv_D65, SpaceSpec("LCHuv", whitepoint_XYZ=D65_XYZ), "Oklab")
    Oklch = convert_color(Oklab, "Oklab", "Oklch")
    XYZ_roundtrip = convert_color(Oklch, "Oklch", "XYZ")
    sRGB_roundtrip = convert_color(XYZ_roundtrip, "XYZ", "sRGB")

    Lab_D50 = convert_color(XYZ, "XYZ", SpaceSpec("Lab", whitepoint_XYZ=D50_XYZ))
    Luv_D65_from_Lab_D50 = convert_color(
        Lab_D50,
        SpaceSpec("Lab", whitepoint_XYZ=D50_XYZ),
        SpaceSpec("Luv", whitepoint_XYZ=D65_XYZ),
    )

    print("Colour-space conversion chain")
    print("XYZ:\n", np.round(XYZ, 6))
    print("Lab D65:\n", np.round(Lab_D65, 6))
    print("Luv D65:\n", np.round(Luv_D65, 6))
    print("Oklab:\n", np.round(Oklab, 6))
    print("Oklch:\n", np.round(Oklch, 6))
    print("Round-trip sRGB:\n", np.round(sRGB_roundtrip, 6))
    print("Lab(D50) -> Luv(D65), no chromatic adaptation:\n", np.round(Luv_D65_from_Lab_D50, 6))

    fig, ax = plt.subplots(figsize=(7.8, 3.0))
    rows = [
        ("input sRGB", SAMPLE_SRGB),
        ("round-trip", np.clip(sRGB_roundtrip, 0.0, 1.0)),
        ("Lab D50 -> Luv D65", preview_sRGB_from_XYZ(
            convert_color(
                Luv_D65_from_Lab_D50,
                SpaceSpec("Luv", whitepoint_XYZ=D65_XYZ),
                "XYZ",
            )
        )),
    ]
    plot_swatch_grid(ax, rows, title="Input And Chained Conversion Preview")
    fig.tight_layout()
    path = out / "02_space_chain_swatches.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")

    fig, axes = plt.subplots(1, 3, figsize=(12.0, 3.8))
    planes = [
        ("Lab a* / b*", Lab_D65[:, 1], Lab_D65[:, 2], "a*", "b*"),
        ("Luv u* / v*", Luv_D65[:, 1], Luv_D65[:, 2], "u*", "v*"),
        ("Oklab a / b", Oklab[:, 1], Oklab[:, 2], "a", "b"),
    ]
    for ax, (title, x, y, xlabel, ylabel) in zip(axes, planes):
        ax.scatter(x, y, c=np.clip(SAMPLE_SRGB, 0.0, 1.0), edgecolors="black", s=70)
        for index, (px, py) in enumerate(zip(x, y), start=1):
            ax.annotate(f"C{index}", (px, py), xytext=(5, 5), textcoords="offset points", fontsize=8)
        ax.axhline(0.0, color="0.75", linewidth=0.8)
        ax.axvline(0.0, color="0.75", linewidth=0.8)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.25)
    fig.tight_layout()
    path = out / "02_lab_luv_oklab_planes.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")

    error = np.linalg.norm(sRGB_roundtrip - SAMPLE_SRGB, axis=1)
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.bar([f"C{i + 1}" for i in range(error.size)], error, color="tab:blue")
    ax.set_title("sRGB Round-Trip Error Through XYZ/Lab/Luv/Oklab")
    ax.set_xlabel("sample")
    ax.set_ylabel("Euclidean RGB error")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    path = out / "02_chain_roundtrip_error.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


if __name__ == "__main__":
    main()
