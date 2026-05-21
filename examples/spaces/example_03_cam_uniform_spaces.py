"""Visualise CAM02 and CAM16 uniform colour-space routing."""

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


def _uniform_chain(
    XYZ: np.ndarray,
    prefix: str,
    viewing: dict[str, object] = VIEWING_AVERAGE,
) -> dict[str, np.ndarray]:
    """Return UCS/LCD/SCD coordinates and round-trip values for a CAM family."""
    ucs_name = f"{prefix}-UCS"
    lcd_name = f"{prefix}-LCD"
    scd_name = f"{prefix}-SCD"

    ucs = convert_color(XYZ, "XYZ", _spec(ucs_name, viewing))
    lcd = convert_color(ucs, _spec(ucs_name, viewing), _spec(lcd_name, viewing))
    scd = convert_color(lcd, _spec(lcd_name, viewing), _spec(scd_name, viewing))
    ucs_roundtrip = convert_color(scd, _spec(scd_name, viewing), _spec(ucs_name, viewing))
    XYZ_roundtrip = convert_color(ucs_roundtrip, _spec(ucs_name, viewing), "XYZ")
    sRGB_roundtrip = convert_color(XYZ_roundtrip, "XYZ", "sRGB")

    return {
        "UCS": ucs,
        "LCD": lcd,
        "SCD": scd,
        "UCS_roundtrip": ucs_roundtrip,
        "XYZ_roundtrip": XYZ_roundtrip,
        "sRGB_roundtrip": sRGB_roundtrip,
    }


def _plot_roundtrip_swatches(
    cam02: dict[str, np.ndarray],
    cam16: dict[str, np.ndarray],
    out: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 3.4))
    plot_swatch_grid(
        ax,
        [
            ("input sRGB", SAMPLE_SRGB),
            ("CAM02 round-trip", np.clip(cam02["sRGB_roundtrip"], 0.0, 1.0)),
            ("CAM16 round-trip", np.clip(cam16["sRGB_roundtrip"], 0.0, 1.0)),
        ],
        title="CAM02/CAM16 Uniform Space Long-Chain Round Trip",
    )
    fig.tight_layout()
    path = out / "03_cam_uniform_roundtrip_swatches.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def _plot_cam_planes(
    cam02: dict[str, np.ndarray],
    cam16: dict[str, np.ndarray],
    out: Path,
) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(12.0, 7.0), sharex=False, sharey=False)
    planes = [
        ("CAM02-UCS", cam02["UCS"]),
        ("CAM02-LCD", cam02["LCD"]),
        ("CAM02-SCD", cam02["SCD"]),
        ("CAM16-UCS", cam16["UCS"]),
        ("CAM16-LCD", cam16["LCD"]),
        ("CAM16-SCD", cam16["SCD"]),
    ]
    for ax, (title, values) in zip(axes.ravel(), planes):
        ax.scatter(values[:, 1], values[:, 2], c=np.clip(SAMPLE_SRGB, 0.0, 1.0), edgecolors="black", s=70)
        for index, (px, py) in enumerate(values[:, 1:3], start=1):
            ax.annotate(f"C{index}", (px, py), xytext=(5, 5), textcoords="offset points", fontsize=8)
        ax.axhline(0.0, color="0.75", linewidth=0.8)
        ax.axvline(0.0, color="0.75", linewidth=0.8)
        ax.set_title(f"{title} a' / b'")
        ax.set_xlabel("a'")
        ax.set_ylabel("b'")
        ax.grid(True, alpha=0.25)

    fig.tight_layout()
    path = out / "03_cam02_cam16_uniform_planes.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def _plot_cam02_vs_cam16_delta(
    CAM02UCS: np.ndarray,
    CAM16UCS: np.ndarray,
    out: Path,
) -> None:
    delta = CAM16UCS - CAM02UCS
    distance = np.linalg.norm(delta, axis=1)

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 3.8))
    ax = axes[0]
    ax.scatter(CAM02UCS[:, 1], CAM02UCS[:, 2], c=np.clip(SAMPLE_SRGB, 0.0, 1.0), edgecolors="black", s=70)
    ax.scatter(CAM16UCS[:, 1], CAM16UCS[:, 2], marker="x", color="black", s=55)
    for index, (start, end) in enumerate(zip(CAM02UCS, CAM16UCS), start=1):
        ax.plot([start[1], end[1]], [start[2], end[2]], color="0.5", linewidth=0.9)
        ax.annotate(f"C{index}", (start[1], start[2]), xytext=(5, 5), textcoords="offset points", fontsize=8)
    ax.set_title("CAM02-UCS To CAM16-UCS Shift")
    ax.set_xlabel("a'")
    ax.set_ylabel("b'")
    ax.grid(True, alpha=0.25)

    ax = axes[1]
    ax.bar([f"C{i + 1}" for i in range(distance.size)], distance, color="tab:orange")
    ax.set_title("CAM02-UCS vs CAM16-UCS Distance")
    ax.set_xlabel("sample")
    ax.set_ylabel("Euclidean J'a'b' distance")
    ax.grid(True, axis="y", alpha=0.25)

    fig.tight_layout()
    path = out / "03_cam02_vs_cam16_coordinate_delta.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def _plot_viewing_condition_shift(
    CAM02_average: np.ndarray,
    CAM02_dim: np.ndarray,
    CAM16_average: np.ndarray,
    CAM16_dim: np.ndarray,
    out: Path,
) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(13.0, 3.8))
    for ax, title, average, dim in [
        (axes[0], "CAM02-UCS Average -> Dim", CAM02_average, CAM02_dim),
        (axes[1], "CAM16-UCS Average -> Dim", CAM16_average, CAM16_dim),
    ]:
        ax.scatter(average[:, 1], average[:, 2], c=np.clip(SAMPLE_SRGB, 0.0, 1.0), edgecolors="black", s=70)
        ax.scatter(dim[:, 1], dim[:, 2], marker="x", color="black", s=55)
        for index, (start, end) in enumerate(zip(average, dim), start=1):
            ax.plot([start[1], end[1]], [start[2], end[2]], color="0.55", linewidth=0.9)
            ax.annotate(f"C{index}", (start[1], start[2]), xytext=(5, 5), textcoords="offset points", fontsize=8)
        ax.set_title(title)
        ax.set_xlabel("a'")
        ax.set_ylabel("b'")
        ax.grid(True, alpha=0.25)

    cam02_delta = np.linalg.norm(CAM02_dim - CAM02_average, axis=1)
    cam16_delta = np.linalg.norm(CAM16_dim - CAM16_average, axis=1)
    x = np.arange(cam02_delta.size)
    width = 0.38
    ax = axes[2]
    ax.bar(x - width / 2, cam02_delta, width=width, label="CAM02", color="tab:blue")
    ax.bar(x + width / 2, cam16_delta, width=width, label="CAM16", color="tab:green")
    ax.set_xticks(x)
    ax.set_xticklabels([f"C{i + 1}" for i in range(cam02_delta.size)])
    ax.set_title("Surround Shift Magnitude")
    ax.set_xlabel("sample")
    ax.set_ylabel("Euclidean J'a'b' shift")
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(fontsize=8)

    fig.tight_layout()
    path = out / "03_cam_viewing_condition_shift.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def main() -> None:
    out = output_dir()

    XYZ = convert_color(SAMPLE_SRGB, "sRGB", "XYZ")
    cam02 = _uniform_chain(XYZ, "CAM02")
    cam16 = _uniform_chain(XYZ, "CAM16")
    cam02_dim = _uniform_chain(XYZ, "CAM02", VIEWING_DIM)
    cam16_dim = _uniform_chain(XYZ, "CAM16", VIEWING_DIM)

    cam02_cam16_delta = np.linalg.norm(cam16["UCS"] - cam02["UCS"], axis=1)

    print("CAM02/CAM16 uniform colour-space long chains")
    print("sRGB -> XYZ -> CAMxx-UCS -> CAMxx-LCD -> CAMxx-SCD -> CAMxx-UCS -> XYZ -> sRGB")
    print(f"Max CAM02 sRGB round-trip error: {np.max(np.abs(cam02['sRGB_roundtrip'] - SAMPLE_SRGB)):.3e}")
    print(f"Max CAM16 sRGB round-trip error: {np.max(np.abs(cam16['sRGB_roundtrip'] - SAMPLE_SRGB)):.3e}")
    print(f"Max CAM02-UCS closure error: {np.max(np.abs(cam02['UCS_roundtrip'] - cam02['UCS'])):.3e}")
    print(f"Max CAM16-UCS closure error: {np.max(np.abs(cam16['UCS_roundtrip'] - cam16['UCS'])):.3e}")
    _print_table("CAM02-UCS coordinates", cam02["UCS"])
    _print_table("CAM16-UCS coordinates", cam16["UCS"])
    _print_table("CAM02-UCS vs CAM16-UCS Euclidean differences", cam02_cam16_delta[:, np.newaxis])

    _plot_roundtrip_swatches(cam02, cam16, out)
    _plot_cam_planes(cam02, cam16, out)
    _plot_cam02_vs_cam16_delta(cam02["UCS"], cam16["UCS"], out)
    _plot_viewing_condition_shift(cam02["UCS"], cam02_dim["UCS"], cam16["UCS"], cam16_dim["UCS"], out)


if __name__ == "__main__":
    main()
