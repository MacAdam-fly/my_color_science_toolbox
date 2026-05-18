"""Compare formula-generated CIE Illuminant A against the static dataset."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.datasets import get_illuminant
from color.generators.illuminants import illuminant_a_spd


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)

    dataset = get_illuminant("A")
    generated = illuminant_a_spd(wavelength_nm=dataset["wavelength"])

    wavelength = dataset["wavelength"]
    dataset_spd = dataset["spd"]
    generated_spd = generated["spd"]
    difference = generated_spd - dataset_spd
    relative = np.divide(
        np.abs(difference),
        np.maximum(np.abs(dataset_spd), np.finfo(float).eps),
    )

    print("CIE Illuminant A formula vs dataset")
    print(f"Samples: {wavelength.size}")
    print(f"Max absolute difference: {np.max(np.abs(difference)):.8g}")
    print(f"Max relative difference: {np.max(relative):.8g}")

    fig, ax = plt.subplots(1, 1, figsize=(9, 7), sharex=True)

    ax.plot(wavelength, dataset_spd, label="dataset A", linewidth=2.0)
    ax.plot(
        wavelength,
        generated_spd,
        "--",
        label="formula A",
        linewidth=1.6,
    )
    ax.set_title("CIE Illuminant A: Dataset vs Formula")
    ax.set_ylabel("Relative SPD")
    ax.legend()
    ax.grid(True, alpha=0.3)


    fig.tight_layout()
    output_path = output_dir / "illuminant_a_formula_vs_dataset.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
