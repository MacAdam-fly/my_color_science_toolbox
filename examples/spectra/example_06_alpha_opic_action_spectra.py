"""Load and plot the five CIE S 026 alpha-opic action spectra."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt

from _spectra_plot_helpers import save_figure
from color.plot import plot_lines, plot_style
from color.spectra import from_alpha_opic_action_spectra, from_iprgc_melanopic


def main() -> None:
    melanopic = from_iprgc_melanopic()
    alpha_opic = from_alpha_opic_action_spectra()

    print("Melanopic action spectrum:")
    print(f"  wavelength range: {melanopic.wavelengths[0]:.0f}-{melanopic.wavelengths[-1]:.0f} nm")
    print(f"  peak value: {melanopic.values.max():.6g}")
    print("Alpha-opic labels:", alpha_opic.labels)
    print("Composition note:", alpha_opic.metadata["composition"])

    with plot_style("presentation", font_scale=0.75, line_scale=0.9):
        fig, ax = plt.subplots(figsize=(8.4, 4.8))
        plot_lines(
            [
                (alpha_opic.wavelengths, alpha_opic.values[:, index])
                for index in range(len(alpha_opic.labels))
            ],
            ax=ax,
            labels=alpha_opic.labels,
            title="CIE S 026 Alpha-opic Action Spectra",
            xlabel="Wavelength (nm)",
            ylabel="Relative action spectrum",
            linewidth=1.6,
        )
        ax.set_ylim(bottom=0)
        ax.legend(ncols=3, fontsize=8)
        save_figure(fig, "06_alpha_opic_action_spectra.png")


if __name__ == "__main__":
    main()
