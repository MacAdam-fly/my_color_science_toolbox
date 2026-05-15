"""Gamut data: Pointer's real surface colour gamut (Calculations sheet)."""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np
import matplotlib.pyplot as plt

from color.datasets.gamut_data import get_gamut_data, list_gamut_data


def main() -> None:
    # --- 1. List available gamut datasets ---
    print("Available gamut data:", list_gamut_data())

    # --- 2. Pointer's gamut — Calculations sheet ---
    pointer = get_gamut_data("pointer")
    print(f"\nPointer's gamut (Calculations): {len(pointer['L'])} boundary points")
    print(f"  Columns: {list(pointer.keys())}")
    print(f"  L* levels: {sorted(set(pointer['L'].tolist()))}")
    print(f"  Reference white: Xn={pointer['Xn'][0]:.2f}, Yn={pointer['Yn'][0]:.2f}, Zn={pointer['Zn'][0]:.2f}")

    # Single L* level
    p50 = get_gamut_data("pointer", L=50)
    print(f"\n  L*=50: {len(p50['L'])} hue angles, C* range [{p50['C'].min():.1f}, {p50['C'].max():.1f}]")

    # --- 3. Plot ---
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # (a) a*-b* gamut boundary at each L* level
    ax = axes[0]
    for L_val in sorted(set(pointer["L"].tolist())):
        mask = pointer["L"] == L_val
        a_star = pointer["a"][mask]
        b_star = pointer["b"][mask]
        ax.plot(a_star, b_star, linewidth=0.8, label=f"L*={int(L_val)}")
    ax.set_xlabel("a*")
    ax.set_ylabel("b*")
    ax.set_title("Pointer Gamut Boundary (a*-b*)")
    ax.set_aspect("equal")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # (b) C*-hab polar plot at L*=50
    ax = axes[1]
    hab_rad = np.deg2rad(p50["hab"])
    ax = plt.subplot(1, 3, 2, projection="polar")
    ax.plot(hab_rad, p50["C"], linewidth=1.0, color="steelblue")
    ax.set_title("C* vs hab (L*=50)", pad=15)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)

    # (c) x-y chromaticity boundary at each L* level
    ax = axes[2]
    for L_val in sorted(set(pointer["L"].tolist())):
        mask = pointer["L"] == L_val
        ax.plot(pointer["x"][mask], pointer["y"][mask], linewidth=0.8, label=f"L*={int(L_val)}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Pointer Gamut Chromaticity (x-y)")
    ax.set_aspect("equal")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = Path(__file__).resolve().parent / "gamut_data.png"
    plt.savefig(out, dpi=150)
    plt.show()
    print(f"\nPlot saved to {out}")


if __name__ == "__main__":
    main()
