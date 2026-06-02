"""Plot LED spectral generator examples using basic plot components."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from _generators_plot_helpers import save_figure
from color.generators.leds import multi_led_spd, single_led_spd
from color.plot import plot_lines, plot_style


def main() -> None:
    wavelength = np.arange(380, 781, 1.0)
    blue = single_led_spd(
        wavelength_nm=wavelength,
        peak_wavelength=457,
        half_spectral_width=20,
    )
    green = single_led_spd(
        wavelength_nm=wavelength,
        peak_wavelength=530,
        half_spectral_width=30,
    )
    red = single_led_spd(
        wavelength_nm=wavelength,
        peak_wavelength=615,
        half_spectral_width=20,
    )
    rgb = multi_led_spd(
        wavelength_nm=wavelength,
        peak_wavelengths=(457, 530, 615),
        half_spectral_widths=(20, 30, 20),
        peak_power_ratios=(0.731, 1.0, 1.66),
    )

    with plot_style("journal_double"):
        fig, axes = plt.subplots(2, 1, figsize=(7.16, 5.2), sharex=True)
        plot_lines(
            [
                (blue["wavelength"], blue["spd"]),
                (green["wavelength"], green["spd"]),
                (red["wavelength"], red["spd"]),
            ],
            ax=axes[0],
            labels=["blue LED 457 nm", "green LED 530 nm", "red LED 615 nm"],
            colors=["royalblue", "seagreen", "crimson"],
            linewidth=1.4,
            title="Single LED Components",
            ylabel="Relative SPD",
        )
        plot_lines(
            (rgb["wavelength"], rgb["spd"]),
            ax=axes[1],
            labels=["weighted RGB LED mixture"],
            colors=["black"],
            linewidth=1.4,
            title="Multi-LED Mixture",
            xlabel="Wavelength (nm)",
            ylabel="Relative SPD",
        )
        save_figure(fig, "04_led_spectra.png")


if __name__ == "__main__":
    main()
