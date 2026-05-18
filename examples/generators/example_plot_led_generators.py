"""Plot LED spectral generator examples."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.generators.leds import multi_led_spd, single_led_spd


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)

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

    fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

    ax = axes[0]
    ax.plot(blue["wavelength"], blue["spd"], label="blue LED 457 nm", color="royalblue")
    ax.plot(green["wavelength"], green["spd"], label="green LED 530 nm", color="seagreen")
    ax.plot(red["wavelength"], red["spd"], label="red LED 615 nm", color="crimson")
    ax.set_title("Single LED Components")
    ax.set_ylabel("Relative SPD")
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    ax.plot(rgb["wavelength"], rgb["spd"], label="weighted RGB LED mixture", color="black")
    ax.set_title("Multi-LED Mixture")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Relative SPD")
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    output_path = output_dir / "led_generators.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
