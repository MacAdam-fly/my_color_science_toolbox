"""Visualise CAM02 uniform colour-space routing and viewing conditions."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.constants import D65_XYZ
from color.spaces import SpaceSpec, convert_color

from _spaces_plot_helpers import output_dir, plot_swatch_grid


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
VIEWING_DIM = {
    "XYZ_w": D65_XYZ,
    "L_A": 318.31,
    "Y_b": 20.0,
    "surround": "Dim",
}


def _spec(name: str, viewing: dict[str, object] = VIEWING_AVERAGE) -> SpaceSpec:
    return SpaceSpec(name, **viewing)


def _print_table(title: str, values: np.ndarray) -> None:
    print(title)
    for index, row in enumerate(values, start=1):
        print(f"  C{index}: {np.round(row, 6)}")


def _plot_cam_planes(
    CAM02UCS: np.ndarray,
    CAM02LCD: np.ndarray,
    CAM02SCD: np.ndarray,
    out: Path,
) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 3.8))
    planes = [
        ("CAM02-UCS a' / b'", CAM02UCS[:, 1], CAM02UCS[:, 2]),
        ("CAM02-LCD a' / b'", CAM02LCD[:, 1], CAM02LCD[:, 2]),
        ("CAM02-SCD a' / b'", CAM02SCD[:, 1], CAM02SCD[:, 2]),
    ]
    for ax, (title, x, y) in zip(axes, planes):
        ax.scatter(x, y, c=np.clip(SAMPLE_SRGB, 0.0, 1.0), edgecolors="black", s=70)
        for index, (px, py) in enumerate(zip(x, y), start=1):
            ax.annotate(f"C{index}", (px, py), xytext=(5, 5), textcoords="offset points", fontsize=8)
        ax.axhline(0.0, color="0.75", linewidth=0.8)
        ax.axvline(0.0, color="0.75", linewidth=0.8)
        ax.set_title(title)
        ax.set_xlabel("a'")
        ax.set_ylabel("b'")
        ax.grid(True, alpha=0.25)
    fig.tight_layout()
    path = out / "03_cam02_uniform_planes.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def _plot_viewing_condition_shift(
    CAM02UCS_average: np.ndarray,
    CAM02UCS_dim: np.ndarray,
    out: Path,
) -> None:
    delta = np.linalg.norm(CAM02UCS_dim - CAM02UCS_average, axis=1)

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.8))
    ax = axes[0]
    ax.scatter(
        CAM02UCS_average[:, 1],
        CAM02UCS_average[:, 2],
        c=np.clip(SAMPLE_SRGB, 0.0, 1.0),
        edgecolors="black",
        s=70,
        label="Average",
    )
    ax.scatter(
        CAM02UCS_dim[:, 1],
        CAM02UCS_dim[:, 2],
        marker="x",
        color="black",
        s=55,
        label="Dim",
    )
    for index, (start, end) in enumerate(zip(CAM02UCS_average, CAM02UCS_dim), start=1):
        ax.plot([start[1], end[1]], [start[2], end[2]], color="0.55", linewidth=0.9)
        ax.annotate(f"C{index}", (start[1], start[2]), xytext=(5, 5), textcoords="offset points", fontsize=8)
    ax.set_title("CAM02-UCS Shift From Surround")
    ax.set_xlabel("a'")
    ax.set_ylabel("b'")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best", fontsize=8)

    ax = axes[1]
    ax.bar([f"C{i + 1}" for i in range(delta.size)], delta, color="tab:purple")
    ax.set_title("Average -> Dim Coordinate Change")
    ax.set_xlabel("sample")
    ax.set_ylabel("Euclidean CAM02-UCS shift")
    ax.grid(True, axis="y", alpha=0.25)

    fig.tight_layout()
    path = out / "03_cam02_viewing_condition_shift.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def main() -> None:
    out = output_dir()

    XYZ = convert_color(SAMPLE_SRGB, "sRGB", "XYZ")
    CAM02UCS = convert_color(XYZ, "XYZ", _spec("CAM02-UCS"))
    CAM02LCD = convert_color(CAM02UCS, _spec("CAM02-UCS"), _spec("CAM02-LCD"))
    CAM02SCD = convert_color(CAM02LCD, _spec("CAM02-LCD"), _spec("CAM02-SCD"))
    CAM02UCS_roundtrip = convert_color(CAM02SCD, _spec("CAM02-SCD"), _spec("CAM02-UCS"))
    XYZ_roundtrip = convert_color(CAM02UCS_roundtrip, _spec("CAM02-UCS"), "XYZ")
    sRGB_roundtrip = convert_color(XYZ_roundtrip, "XYZ", "sRGB")

    CAM02UCS_dim = convert_color(XYZ, "XYZ", _spec("CAM02-UCS", VIEWING_DIM))

    print("CAM02 uniform colour-space long chain")
    print("sRGB -> XYZ -> CAM02-UCS -> CAM02-LCD -> CAM02-SCD -> CAM02-UCS -> XYZ -> sRGB")
    print(f"Max sRGB round-trip error: {np.max(np.abs(sRGB_roundtrip - SAMPLE_SRGB)):.3e}")
    print(f"Max CAM02-UCS closure error: {np.max(np.abs(CAM02UCS_roundtrip - CAM02UCS)):.3e}")
    _print_table("CAM02-UCS coordinates", CAM02UCS)
    _print_table("CAM02-LCD coordinates", CAM02LCD)
    _print_table("CAM02-SCD coordinates", CAM02SCD)

    fig, ax = plt.subplots(figsize=(8.2, 3.2))
    plot_swatch_grid(
        ax,
        [
            ("input sRGB", SAMPLE_SRGB),
            ("long-chain round-trip", np.clip(sRGB_roundtrip, 0.0, 1.0)),
        ],
        title="CAM02 Uniform Space Long-Chain Round Trip",
    )
    fig.tight_layout()
    path = out / "03_cam02_long_chain_swatches.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")

    _plot_cam_planes(CAM02UCS, CAM02LCD, CAM02SCD, out)
    _plot_viewing_condition_shift(CAM02UCS, CAM02UCS_dim, out)


if __name__ == "__main__":
    main()
