"""Load colour-card datasets and plot reflectance spectra."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from _datasets_plot_helpers import save_figure
from color.datasets import get_color_card, list_color_cards
from color.datasets.color_cards import BCRA_TILE_NAMES, MACBETH_PATCH_NAMES
from color.plot import plot_labels, plot_lines, plot_style


def main() -> None:
    print("Available color cards:", list_color_cards())

    macbeth = get_color_card("macbeth")
    wl = macbeth["wavelength"]
    print(
        f"\nMacbeth ColorChecker: {len(MACBETH_PATCH_NAMES)} patches, "
        f"{wl[0]:.0f}-{wl[-1]:.0f} nm, step {wl[1] - wl[0]:.0f} nm"
    )
    idx_550 = int((550 - wl[0]) / (wl[1] - wl[0]))
    for name in ["Dark Skin", "White", "Black", "Red", "Green", "Blue"]:
        print(f"  {name:15s} @ 550 nm: {macbeth[name][idx_550]:.3f}")

    bcra = get_color_card("bcra")
    wl_bcra = bcra["wavelength"]
    print(
        f"\nBCRA tiles: {len(BCRA_TILE_NAMES)} tiles, "
        f"{wl_bcra[0]:.0f}-{wl_bcra[-1]:.0f} nm"
    )

    with plot_style("journal_double"):
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        neutral_names = {"White", "Neutral 8", "Neutral 6.5", "Neutral 5", "Neutral 3.5", "Black"}
        plot_lines(
            [(wl, macbeth[name]) for name in MACBETH_PATCH_NAMES],
            ax=axes[0],
            colors=["grey" if name in neutral_names else None for name in MACBETH_PATCH_NAMES],
            linewidth=0.8,
            title=f"Macbeth ColorChecker ({len(MACBETH_PATCH_NAMES)} patches)",
            xlabel="Wavelength (nm)",
            ylabel="Reflectance",
            legend=False,
            alpha=0.8,
        )
        label_points = []
        label_names = []
        for name in ["Red", "Green", "Blue", "White", "Black"]:
            peak_wl = wl[np.argmax(macbeth[name])] if name != "Black" else 550
            index = int((peak_wl - wl[0]) / (wl[1] - wl[0]))
            label_points.append((peak_wl, macbeth[name][index]))
            label_names.append(name)
        plot_labels(label_points, label_names, ax=axes[0], offset=(0, 6), fontsize=7, ha="center", grid=False)
        axes[0].set_ylim(-0.02, 1.02)

        color_map = {
            "Black": "black",
            "White": "grey",
            "Red": "red",
            "Green": "green",
            "Deep Blue": "blue",
            "Orange": "orange",
            "Cyan": "cyan",
            "Bright Yellow": "gold",
            "Deep Pink": "magenta",
        }
        plot_lines(
            [(wl_bcra, bcra[name]) for name in BCRA_TILE_NAMES],
            ax=axes[1],
            labels=BCRA_TILE_NAMES,
            colors=[color_map.get(name) for name in BCRA_TILE_NAMES],
            linewidth=1.2,
            title=f"BCRA CERAM Series II ({len(BCRA_TILE_NAMES)} tiles)",
            xlabel="Wavelength (nm)",
            ylabel="Reflectance",
        )
        axes[1].set_ylim(-0.02, 1.02)
        axes[1].legend(fontsize=7, loc="upper right")

        save_figure(fig, "02_color_cards.png")


if __name__ == "__main__":
    main()
