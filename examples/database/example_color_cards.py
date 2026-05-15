"""Color card datasets: load and plot reflectance spectra."""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np
import matplotlib.pyplot as plt

from color.datasets import get_color_card, list_color_cards
from color.datasets.color_cards import MACBETH_PATCH_NAMES, BCRA_TILE_NAMES


def main() -> None:
    # --- 1. List available color cards ---
    print("Available color cards:", list_color_cards())

    # --- 2. Macbeth ColorChecker ---
    macbeth = get_color_card("macbeth")
    wl = macbeth["wavelength"]
    print(f"\nMacbeth ColorChecker: {len(MACBETH_PATCH_NAMES)} patches, "
          f"{wl[0]:.0f}–{wl[-1]:.0f} nm, step {wl[1] - wl[0]:.0f} nm")

    # Print reflectance of a few patches at 550nm
    idx_550 = int((550 - wl[0]) / (wl[1] - wl[0]))
    for name in ["Dark Skin", "White", "Black", "Red", "Green", "Blue"]:
        print(f"  {name:15s} @ 550nm: {macbeth[name][idx_550]:.3f}")

    # --- 3. BCRA calibration tiles ---
    bcra = get_color_card("bcra")
    wl_bcra = bcra["wavelength"]
    print(f"\nBCRA tiles: {len(BCRA_TILE_NAMES)} tiles, "
          f"{wl_bcra[0]:.0f}–{wl_bcra[-1]:.0f} nm")

    # --- 4. Plot Macbeth spectra ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    ax = axes[0]
    # Color mapping for neutral patches
    neutral_names = {"White", "Neutral 8", "Neutral 6.5", "Neutral 5", "Neutral 3.5", "Black"}
    for name in MACBETH_PATCH_NAMES:
        if name in neutral_names:
            ax.plot(wl, macbeth[name], color="grey", alpha=0.6, linewidth=0.8)
        else:
            ax.plot(wl, macbeth[name], linewidth=0.8)
    ax.set_title(f"Macbeth ColorChecker ({len(MACBETH_PATCH_NAMES)} patches)")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Reflectance")
    ax.set_ylim(-0.02, 1.02)
    ax.grid(True, alpha=0.3)

    # Annotate a few key patches
    for name, color in [("Red", "red"), ("Green", "green"), ("Blue", "blue"),
                         ("White", "grey"), ("Black", "black")]:
        peak_wl = wl[np.argmax(macbeth[name])] if name != "Black" else 550
        ax.annotate(name, xy=(peak_wl, macbeth[name][int((peak_wl - wl[0]) / (wl[1] - wl[0]))]),
                    fontsize=7, ha="center", va="bottom")

    # --- 5. Plot BCRA spectra ---
    ax = axes[1]
    for name in BCRA_TILE_NAMES:
        color_map = {
            "Black": "black", "White": "grey", "Red": "red",
            "Green": "green", "Deep Blue": "blue", "Orange": "orange",
            "Cyan": "cyan", "Bright Yellow": "gold", "Deep Pink": "magenta",
        }
        c = color_map.get(name, None)
        ax.plot(wl_bcra, bcra[name], label=name, color=c, linewidth=1.2)
    ax.set_title(f"BCRA CERAM Series II ({len(BCRA_TILE_NAMES)} tiles)")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Reflectance")
    ax.set_ylim(-0.02, 1.02)
    ax.legend(fontsize=7, loc="upper right")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = Path(__file__).resolve().parent / "color_cards.png"
    plt.savefig(out, dpi=150)
    plt.show()
    print(f"\nPlot saved to {out}")


if __name__ == "__main__":
    main()
