"""Illuminant datasets: load, compute, and plot spectral power distributions."""

import sys
from pathlib import Path

# Ensure project root is on sys.path so ``import color`` works from any CWD.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np
import matplotlib.pyplot as plt

from color.datasets import get_illuminant, list_illuminants


def _get_values(data: dict) -> np.ndarray:
    """Extract the spectral values from an illuminant dict (key varies)."""
    for key in ("spd", "radiance"):
        if key in data:
            return data[key]
    # Fluorescents: return first lamp
    keys = [k for k in data if k != "wavelength"]
    return data[keys[0]]


def main() -> None:
    # --- 1. List available illuminants ---
    print("Available illuminants:", list_illuminants())

    # --- 2. Load tabulated illuminants ---
    d65 = get_illuminant("D65")
    ill_a = get_illuminant("A")
    print(f"\nD65: {len(d65['wavelength'])} points, "
          f"{d65['wavelength'][0]:.0f}–{d65['wavelength'][-1]:.0f} nm")
    print(f"A:   {len(ill_a['wavelength'])} points, "
          f"{ill_a['wavelength'][0]:.0f}–{ill_a['wavelength'][-1]:.0f} nm")

    # --- 3. Compute blackbody at different temperatures ---
    temperatures = [3000, 4000, 5000, 6500, 8000, 10000]
    blackbodies = {}
    for t in temperatures:
        bb = get_illuminant("blackbody", temperature=t)
        blackbodies[t] = bb
        peak_idx = np.argmax(bb["radiance"])
        peak_wl = bb["wavelength"][peak_idx]
        # Wien's displacement law: λ_max * T ≈ 2898 μm·K
        print(f"Blackbody {t}K: peak at {peak_wl:.0f} nm "
              f"(Wien check: {peak_wl * t / 1000:.0f} μm·K)")

    # --- 4. Compute daylight at different CCTs ---
    ccts = [4000, 5000, 6500, 8000, 10000, 15000]
    daylights = {}
    for cct in ccts:
        dl = get_illuminant("daylight", cct=cct)
        daylights[cct] = dl
        print(f"Daylight {cct}K: {len(dl['wavelength'])} points, "
              f"{dl['wavelength'][0]:.0f}–{dl['wavelength'][-1]:.0f} nm")

    # --- 5. Load fluorescent lamps ---
    fluo = get_illuminant("fluorescents")
    fluo_keys = [k for k in fluo.keys() if k != "wavelength"]
    print(f"\nFluorescent lamps: {len(fluo_keys)} ({', '.join(fluo_keys[:6])}...)")

    # --- 6. Plot ---
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # (a) Standard illuminants
    ax = axes[0]
    ax.plot(d65["wavelength"], d65["spd"], label="D65", color="royalblue")
    ax.plot(ill_a["wavelength"], ill_a["spd"], label="A", color="orange")
    ax.set_title("Standard Illuminants")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Relative SPD")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # (b) Blackbody radiation
    ax = axes[1]
    cmap = plt.cm.hot
    for i, t in enumerate(temperatures):
        bb = blackbodies[t]
        color = cmap(0.15 + 0.13 * i)
        ax.plot(bb["wavelength"], bb["radiance"], label=f"{t}K", color=color)
    ax.set_title("Planck Blackbody Radiation")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Spectral Radiance")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # (c) CIE Daylight series
    ax = axes[2]
    for cct in ccts:
        dl = daylights[cct]
        ax.plot(dl["wavelength"], dl["spd"], label=f"{cct}K")
    ax.set_title("CIE Daylight D Series")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Relative SPD")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = Path(__file__).resolve().parent / "illuminants.png"
    plt.savefig(out, dpi=150)
    plt.show()
    print(f"\nPlot saved to {out}")


if __name__ == "__main__":
    main()
