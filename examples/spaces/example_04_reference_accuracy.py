"""Demonstrate D65 whitepoint and reference-domain semantics."""

from __future__ import annotations

import sys
import warnings
from collections.abc import Callable
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.adaptation import adapt_to_D65
from color.constants import D50_XYZ, D65_XYZ
from color.spaces import (
    RGB_to_XYZ,
    SpaceSpec,
    XYZ_to_Lab,
    convert_color,
    get_RGB_colourspace,
)

from _spaces_plot_helpers import output_dir


SAMPLE_SRGB = np.array([0.55, 0.35, 0.20], dtype=np.float64)
SAMPLE_XYZ_D65 = RGB_to_XYZ(SAMPLE_SRGB, colourspace="sRGB")


def _whitepoint_xy(whitepoint_XYZ: np.ndarray) -> np.ndarray:
    """Return xy chromaticity from a whitepoint XYZ triplet."""
    whitepoint = np.asarray(whitepoint_XYZ, dtype=np.float64)
    return whitepoint[:2] / np.sum(whitepoint)


def _capture_warnings(function: Callable[[], np.ndarray]) -> tuple[np.ndarray, list[warnings.WarningMessage]]:
    """Run *function* and return its value plus captured warnings."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        value = function()
    return value, list(caught)


def _case_message(caught: list[warnings.WarningMessage]) -> str:
    """Return a compact warning message for printing."""
    if not caught:
        return "no warning"
    return str(caught[0].message)


def _plot_whitepoint_precision(out: Path) -> None:
    """Plot D65 xy precision differences between XYZ-derived and rounded values."""
    d65_xy = _whitepoint_xy(D65_XYZ)
    srgb_white_xy = get_RGB_colourspace("sRGB").white_xy

    print("D65 whitepoint precision")
    print(f"D65_XYZ constant:       {D65_XYZ}")
    print(f"D65_XYZ converted xy:  {d65_xy}")
    print(f"sRGB stored white xy:  {srgb_white_xy}")
    print(f"xy difference:         {d65_xy - srgb_white_xy}")
    print(
        "Both xy pairs describe D65; the difference comes from common rounded "
        "xy constants versus xy computed from the stored XYZ whitepoint."
    )
    print()


def _plot_reference_domain_scale(out: Path) -> None:
    """Plot D65 chromaticity invariance and Y-scale differences."""
    names = ["D65_XYZ / 10", "D65_XYZ", "D65_XYZ * 2"]
    whitepoints = np.array([D65_XYZ / 10.0, D65_XYZ, D65_XYZ * 2.0])
    xy = np.array([_whitepoint_xy(whitepoint) for whitepoint in whitepoints])
    Y = whitepoints[:, 1]

    print("D65 reference-domain scale")
    for name, whitepoint, xy_value in zip(names, whitepoints, xy):
        print(f"{name:<14} XYZ={np.round(whitepoint, 6)} xy={np.round(xy_value, 8)}")
    print("Only D65_XYZ with Y=100 is the spaces reference domain.")
    print()

    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.0))
    axes[0].scatter(xy[:, 0], xy[:, 1], c=["tab:orange", "tab:blue", "tab:green"], s=75)
    for name, point in zip(names, xy):
        axes[0].annotate(name, point, xytext=(5, 5), textcoords="offset points", fontsize=8)
    axes[0].set_title("Same D65 Chromaticity")
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("y")
    axes[0].set_xlim(float(xy[1, 0] - 0.0006), float(xy[1, 0] + 0.0006))
    axes[0].set_ylim(float(xy[1, 1] - 0.0006), float(xy[1, 1] + 0.0006))
    axes[0].grid(True, alpha=0.3)

    bars = axes[1].bar(names, Y, color=["tab:orange", "tab:blue", "tab:green"])
    axes[1].axhline(100.0, color="black", linewidth=1.0, linestyle="--", label="spaces Y=100")
    axes[1].set_title("Different Reference-Domain Scale")
    axes[1].set_ylabel("whitepoint Y")
    axes[1].tick_params(axis="x", rotation=20)
    axes[1].legend()
    for bar, value in zip(bars, Y):
        axes[1].text(bar.get_x() + bar.get_width() / 2, value, f"{value:g}", ha="center", va="bottom")
    fig.tight_layout()
    path = out / "04_d65_reference_domain_scale.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def _warning_cases() -> list[tuple[str, int, str]]:
    """Run representative D65 reference-domain warning cases."""
    XYZ_D50_referred = np.array([22.0, 30.0, 18.0], dtype=np.float64)
    XYZ_adapted = adapt_to_D65(XYZ_D50_referred, source_white_XYZ=D50_XYZ)
    Lab_D50 = XYZ_to_Lab(XYZ_D50_referred, whitepoint_XYZ=D50_XYZ)

    cases: list[tuple[str, Callable[[], np.ndarray], int]] = [
        (
            "XYZ(D65 Y=100) -> Oklab",
            lambda: convert_color(
                SAMPLE_XYZ_D65,
                SpaceSpec("XYZ", whitepoint_XYZ=D65_XYZ),
                "Oklab",
            ),
            0,
        ),
        (
            "XYZ(D65 Y=10) -> Oklab",
            lambda: convert_color(
                SAMPLE_XYZ_D65,
                SpaceSpec("XYZ", whitepoint_XYZ=D65_XYZ / 10.0),
                "Oklab",
            ),
            1,
        ),
        (
            "XYZ(D65 Y=200) -> Oklab",
            lambda: convert_color(
                SAMPLE_XYZ_D65,
                SpaceSpec("XYZ", whitepoint_XYZ=D65_XYZ * 2.0),
                "Oklab",
            ),
            1,
        ),
        (
            "XYZ(D50) -> Oklab",
            lambda: convert_color(
                XYZ_D50_referred,
                SpaceSpec("XYZ", whitepoint_XYZ=D50_XYZ),
                "Oklab",
            ),
            1,
        ),
        (
            "sRGB -> Jzazbz",
            lambda: convert_color(SAMPLE_SRGB, "sRGB", "Jzazbz"),
            0,
        ),
        (
            "DCI-P3 -> Oklab",
            lambda: convert_color(SAMPLE_SRGB, "DCI-P3", "Oklab"),
            1,
        ),
        (
            "Lab(D50) -> Oklab",
            lambda: convert_color(
                Lab_D50,
                SpaceSpec("Lab", whitepoint_XYZ=D50_XYZ),
                "Oklab",
            ),
            1,
        ),
        (
            "adapt_to_D65 -> Oklab",
            lambda: convert_color(
                XYZ_adapted,
                SpaceSpec("XYZ", whitepoint_XYZ=D65_XYZ),
                "Oklab",
            ),
            0,
        ),
    ]

    rows: list[tuple[str, int, str]] = []
    print("D65-referred route warning cases")
    for name, function, expected_count in cases:
        _, caught = _capture_warnings(function)
        count = len(caught)
        if count != expected_count:
            raise AssertionError(
                f"{name!r} produced {count} warnings, expected {expected_count}: "
                f"{_case_message(caught)}"
            )
        message = _case_message(caught)
        rows.append((name, count, message))
        print(f"{name:<26} warnings={count}  {message}")
    print()
    return rows


def _plot_warning_cases(rows: list[tuple[str, int, str]], out: Path) -> None:
    """Plot warning counts for representative routes."""
    labels = [name for name, _, _ in rows]
    counts = np.array([count for _, count, _ in rows])
    colors = ["tab:green" if count == 0 else "tab:orange" for count in counts]

    fig, ax = plt.subplots(figsize=(10.0, 4.6))
    x = np.arange(len(labels))
    ax.bar(x, counts, color=colors)
    ax.set_title("D65-Referred Route Warning Cases")
    ax.set_ylabel("captured UserWarning count")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylim(0.0, 1.25)
    ax.set_yticks([0, 1])
    ax.grid(True, axis="y", alpha=0.25)
    for index, count in enumerate(counts):
        ax.text(index, count + 0.04, "warn" if count else "ok", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    path = out / "04_d65_warning_cases.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def main() -> None:
    out = output_dir()
    _plot_whitepoint_precision(out)
    _plot_reference_domain_scale(out)
    rows = _warning_cases()
    _plot_warning_cases(rows, out)


if __name__ == "__main__":
    main()
