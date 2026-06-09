"""Export a simple scientific figure with color.io."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.io import save_figure
from color.plot import plot_lines, plot_style


OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    wavelengths = np.linspace(380.0, 780.0, 401)
    spectrum_a = np.exp(-0.5 * ((wavelengths - 520.0) / 42.0) ** 2)
    spectrum_b = 0.72 * np.exp(-0.5 * ((wavelengths - 610.0) / 58.0) ** 2)

    with plot_style("presentation", font_scale=0.75, line_scale=0.9):
        fig, _ax = plot_lines(
            ((wavelengths, spectrum_a), (wavelengths, spectrum_b)),
            labels=("green-like SPD", "red-like SPD"),
            xlabel="Wavelength / nm",
            ylabel="Relative power",
            linewidth=1.8,
        )

    output_path = save_figure(
        OUTPUT_DIR / "01_figure_export.png",
        fig=fig,
        dpi=300,
        close=True,
    )

    print("Figure export example")
    print(f"Output: {output_path}")
    print("Saved with: save_figure(..., dpi=180, close=True)")


if __name__ == "__main__":
    main()
