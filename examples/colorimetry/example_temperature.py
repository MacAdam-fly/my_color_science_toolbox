"""Compute and plot basic correlated colour temperature relationships."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.colorimetry import (
    CCT_to_mired,
    CCT_to_uv,
    CCT_to_xy,
    CCT_to_xy_CIE_D,
    mired_to_CCT,
    uv1960_to_xy,
    xy_to_CCT_Duv,
    xy_to_CCT,
)


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
    d65_mired = CCT_to_mired(named_ccts["D65"])
    print("D65 McCamy estimate:", np.round(d65_mccamy, 6))
    print("D65 Robertson CCT+Duv:", np.round(d65_robertson, 6))
    print("D65 mired:", np.round(d65_mired, 6))
    print("D65 mired -> CCT:", np.round(mired_to_CCT(d65_mired), 6))

    daylight_cct = np.linspace(4000.0, 25000.0, 120)
    daylight_xy = CCT_to_xy_CIE_D(daylight_cct)
    planckian_cct = np.linspace(1667.0, 25000.0, 160)
    planckian_xy = uv1960_to_xy(
        CCT_to_uv(np.column_stack([planckian_cct, np.zeros_like(planckian_cct)]))
    )

    fig, ax = plt.subplots(figsize=(8.4, 5.6))
    ax.plot(
        daylight_xy[:, 0],
        daylight_xy[:, 1],
        color="tab:blue",
        label="CIE D daylight locus",
    )
    ax.plot(
        planckian_xy[:, 0],
        planckian_xy[:, 1],
        color="0.25",
        linestyle="--",
        label="Planckian locus, Duv=0",
    )

    label_offsets = {
        "D50": (10, 12),
        "D65": (10, 4),
        "D75": (10, -14),
    }
    for name, cct in named_ccts.items():
        xy = CCT_to_xy_CIE_D(cct)
        ax.scatter(*xy, s=55, label=name)
        ax.annotate(
            f"{name}\n{cct:.0f} K",
            xy=xy,
            xytext=label_offsets[name],
            textcoords="offset points",
            fontsize=9,
        )

    duv_samples = np.array([
        [named_ccts["D65"], -0.02],
        [named_ccts["D65"], 0.0],
        [named_ccts["D65"], 0.02],
    ])
    duv_xy = uv1960_to_xy(CCT_to_uv(duv_samples))
    ax.scatter(
        duv_xy[:, 0],
        duv_xy[:, 1],
        marker="x",
        s=65,
        color="tab:red",
        label="D65 CCT with Duv offsets",
    )
    for cct_duv, xy in zip(duv_samples, duv_xy):
        ax.annotate(
            f"{cct_duv[1]:+.2f}",
            xy=xy,
            xytext=(10, -4),
            textcoords="offset points",
            fontsize=9,
            color="tab:red",
        )

    ax.set_title("CIE D Daylight Locus and Planckian Locus")
    ax.set_xlabel("CIE x")
    ax.set_ylabel("CIE y")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), borderaxespad=0.0)
    fig.tight_layout(rect=(0, 0, 0.78, 1))

    output_path = output_dir / "temperature_cie_d_locus.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
