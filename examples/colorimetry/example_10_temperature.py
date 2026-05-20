"""Compute and plot correlated colour temperature relationships."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.colorimetry import (
    CCT_Duv_to_xy,
    CCT_to_mired,
    CCT_to_uv,
    CCT_to_xy,
    CCT_to_xy_CIE_D,
    analyze_temperature,
    mired_to_CCT,
    uv1960_to_xy,
    xy_to_CCT,
    xy_to_CCT_Duv,
)


def _save(
    fig: plt.Figure,
    output_dir: Path,
    filename: str,
    *,
    close: bool = True,
) -> None:
    """Save *fig* into the example output directory."""
    output_path = output_dir / filename
    fig.savefig(output_path, dpi=150)
    if close:
        plt.close(fig)
    print(f"Plot saved to {output_path}")


def _plot_loci_comparison(
    output_dir: Path,
    named_ccts: dict[str, float],
) -> None:
    """Plot CIE D daylight locus against the Planckian locus in xy."""
    daylight_cct = np.linspace(4000.0, 25000.0, 180)
    daylight_xy = CCT_to_xy_CIE_D(daylight_cct)
    planckian_cct = np.linspace(1667.0, 25000.0, 220)
    planckian_xy = uv1960_to_xy(
        CCT_to_uv(
            np.column_stack([planckian_cct, np.zeros_like(planckian_cct)]),
            method="ohno2013",
        )
    )

    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    ax.plot(
        daylight_xy[:, 0],
        daylight_xy[:, 1],
        color="tab:blue",
        linewidth=2.0,
        label="CIE D daylight locus",
    )
    ax.plot(
        planckian_xy[:, 0],
        planckian_xy[:, 1],
        color="0.20",
        linestyle="--",
        linewidth=2.0,
        label="Planckian locus, Duv=0",
    )

    label_offsets = {
        "D50": (12, 12),
        "D65": (12, 2),
        "D75": (12, -14),
    }
    for name, cct in named_ccts.items():
        daylight_point = CCT_to_xy_CIE_D(cct)
        planckian_point = CCT_Duv_to_xy([cct, 0.0], method="ohno2013")
        ax.plot(
            [daylight_point[0], planckian_point[0]],
            [daylight_point[1], planckian_point[1]],
            color="0.65",
            linestyle=":",
            linewidth=1.0,
        )
        ax.scatter(*daylight_point, s=58, color="tab:blue")
        ax.scatter(*planckian_point, s=46, color="0.20", marker="x")
        ax.annotate(
            f"{name}\n{cct:.0f} K",
            xy=daylight_point,
            xytext=label_offsets[name],
            textcoords="offset points",
            fontsize=9,
        )

    ax.set_title("CIE D Daylight Locus vs Planckian Locus")
    ax.set_xlabel("CIE x")
    ax.set_ylabel("CIE y")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", fontsize=9, framealpha=0.92)
    fig.tight_layout()
    _save(fig, output_dir, "10_temperature_cie_d_locus.png", close=False)
    _save(fig, output_dir, "10_temperature_loci_comparison.png")


def _plot_duv_offsets(output_dir: Path) -> None:
    """Plot Duv offsets around the Planckian locus in CIE 1960 uv."""
    ccts = np.array([3000.0, 5000.0, 6500.0, 10000.0])
    duvs = np.array([-0.02, -0.01, 0.0, 0.01, 0.02])
    planckian_cct = np.linspace(2000.0, 12000.0, 180)
    planckian_uv = CCT_to_uv(
        np.column_stack([planckian_cct, np.zeros_like(planckian_cct)]),
        method="ohno2013",
    )

    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    ax.plot(
        planckian_uv[:, 0],
        planckian_uv[:, 1],
        color="0.20",
        linewidth=2.0,
        label="Planckian locus",
    )

    colors = plt.cm.viridis(np.linspace(0.15, 0.85, len(ccts)))
    for cct, color in zip(ccts, colors):
        samples = np.column_stack([
            np.full_like(duvs, cct),
            duvs,
        ])
        uv = CCT_to_uv(samples, method="ohno2013")
        ax.plot(uv[:, 0], uv[:, 1], marker="o", color=color, label=f"{cct:.0f} K")
        for duv, point in zip(duvs, uv):
            if duv in {-0.02, 0.0, 0.02}:
                ax.annotate(
                    f"{duv:+.2f}",
                    xy=point,
                    xytext=(6, 4),
                    textcoords="offset points",
                    fontsize=8,
                    color=color,
                )

    ax.set_title("Duv Offsets in CIE 1960 UCS")
    ax.set_xlabel("u")
    ax.set_ylabel("v")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=9, framealpha=0.92)
    fig.tight_layout()
    _save(fig, output_dir, "10_temperature_duv_offsets_uv.png")


def _plot_method_comparison(
    output_dir: Path,
    named_ccts: dict[str, float],
) -> None:
    """Compare McCamy, Robertson and Ohno estimates for several xy samples."""
    sample_names = ["D50", "D65", "D75", "Warm +Duv", "Cool -Duv"]
    sample_xy = [
        CCT_to_xy_CIE_D(named_ccts["D50"]),
        CCT_to_xy_CIE_D(named_ccts["D65"]),
        CCT_to_xy_CIE_D(named_ccts["D75"]),
        CCT_Duv_to_xy([3000.0, 0.015], method="ohno2013"),
        CCT_Duv_to_xy([10000.0, -0.015], method="ohno2013"),
    ]

    mccamy = np.array([xy_to_CCT(xy) for xy in sample_xy])
    robertson = np.array([xy_to_CCT_Duv(xy) for xy in sample_xy])
    ohno = np.array([xy_to_CCT_Duv(xy, method="ohno2013") for xy in sample_xy])

    x = np.arange(len(sample_names))
    fig, (ax0, ax1, ax2) = plt.subplots(3, 1, figsize=(8.8, 9.2), sharex=True)
    ax0.plot(x, mccamy, marker="o", label="McCamy CCT")
    ax0.plot(x, robertson[:, 0], marker="s", label="Robertson CCT")
    ax0.plot(x, ohno[:, 0], marker="^", label="Ohno CCT")
    ax0.set_ylabel("CCT (K)")
    ax0.set_title("CCT Estimates for the Same xy Samples")
    ax0.grid(True, alpha=0.3)
    ax0.legend(ncol=3, fontsize=9)

    width = 0.36
    ax1.bar(
        x - width / 2,
        mccamy - ohno[:, 0],
        width,
        label="McCamy - Ohno",
    )
    ax1.bar(
        x + width / 2,
        robertson[:, 0] - ohno[:, 0],
        width,
        label="Robertson - Ohno",
    )
    ax1.axhline(0.0, color="0.25", linewidth=1.0)
    ax1.set_ylabel("CCT difference (K)")
    ax1.grid(True, axis="y", alpha=0.3)
    ax1.legend(ncol=2, fontsize=9)

    width = 0.36
    ax2.bar(x - width / 2, robertson[:, 1], width, label="Robertson Duv")
    ax2.bar(x + width / 2, ohno[:, 1], width, label="Ohno Duv")
    ax2.axhline(0.0, color="0.25", linewidth=1.0)
    ax2.set_ylabel("Duv")
    ax2.set_xticks(x, sample_names, rotation=20, ha="right")
    ax2.grid(True, axis="y", alpha=0.3)
    ax2.legend(ncol=2, fontsize=9)

    fig.tight_layout()
    _save(fig, output_dir, "10_temperature_method_comparison.png")


def _plot_mired_curve(output_dir: Path) -> None:
    """Plot the nonlinear relationship between CCT and mired."""
    cct = np.linspace(2000.0, 12000.0, 300)
    mired = CCT_to_mired(cct)
    named = np.array([2856.0, 5003.0, 6504.38938305, 10000.0])
    named_mired = CCT_to_mired(named)

    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    ax.plot(cct, mired, color="tab:purple", linewidth=2.0)
    ax.scatter(named, named_mired, color="tab:purple", s=48)
    for cct_value, mired_value in zip(named, named_mired):
        ax.annotate(
            f"{cct_value:.0f} K\n{mired_value:.1f} mired",
            xy=(cct_value, mired_value),
            xytext=(8, 8),
            textcoords="offset points",
            fontsize=8,
        )
    ax.set_title("CCT and Mired Relationship")
    ax.set_xlabel("CCT (K)")
    ax.set_ylabel("Mired")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save(fig, output_dir, "10_temperature_mired_curve.png")


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)

    named_ccts = {
        "D50": 5003.0,
        "D65": 6504.38938305,
        "D75": 7504.0,
    }

    print("CIE D-series daylight xy")
    for name, cct in named_ccts.items():
        xy = CCT_to_xy(cct)
        print(f"{name}: CCT={cct:.3f} K, xy={np.round(xy, 6)}")

    d65_xy = CCT_to_xy_CIE_D(named_ccts["D65"])
    d65_mccamy = xy_to_CCT(d65_xy)
    d65_robertson = xy_to_CCT_Duv(d65_xy)
    d65_ohno = xy_to_CCT_Duv(d65_xy, method="ohno2013")
    d65_mired = CCT_to_mired(named_ccts["D65"])
    d65_analysis = analyze_temperature(d65_xy, method="ohno2013")

    print("D65 McCamy estimate:", np.round(d65_mccamy, 6))
    print("D65 Robertson CCT+Duv:", np.round(d65_robertson, 6))
    print("D65 Ohno CCT+Duv:", np.round(d65_ohno, 6))
    print(
        "D65 Ohno CCT+Duv -> xy:",
        np.round(CCT_Duv_to_xy(d65_ohno, method="ohno2013"), 6),
    )
    print(
        "D65 TemperatureAnalysis:",
        f"CCT={d65_analysis.CCT:.3f} K,",
        f"Duv={d65_analysis.Duv:.6f},",
        f"method={d65_analysis.method}",
    )
    print("D65 mired:", np.round(d65_mired, 6))
    print("D65 mired -> CCT:", np.round(mired_to_CCT(d65_mired), 6))

    _plot_loci_comparison(output_dir, named_ccts)
    _plot_duv_offsets(output_dir)
    _plot_method_comparison(output_dir, named_ccts)
    _plot_mired_curve(output_dir)

    # test the analyze_temperature function with a non-standard xy sample
    test_xy = np.array([0.31, 0.33])  # D65
    analysis = analyze_temperature(test_xy, method="ohno2013")
    print(analysis)


if __name__ == "__main__":
    main()
