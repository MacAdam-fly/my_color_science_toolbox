"""Convert relative luminance Y to CIE 1976 L* and back."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.colorimetry import Lstar_to_Y, Y_to_Lstar
from _plot_helpers import example_output_dir


def main() -> None:
    output_dir = example_output_dir()

    Y = np.array([0.0, 1.0, 5.0, 18.0, 50.0, 100.0])
    Lstar = Y_to_Lstar(Y)
    Y_roundtrip = Lstar_to_Y(Lstar)

    print("Y:", np.round(Y, 6))
    print("L*:", np.round(Lstar, 6))
    print("Round-trip OK:", np.allclose(Y_roundtrip, Y))
    print("Y from L*:", np.round(Y_roundtrip, 6))

    dense_Y = np.linspace(0.0, 100.0, 256)
    dense_Lstar = Y_to_Lstar(dense_Y)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.plot(dense_Y, dense_Lstar, color="tab:blue", linewidth=2.0)
    ax.scatter(Y, Lstar, color="tab:orange", s=48, zorder=3)
    for y_value, lstar_value in zip(Y, Lstar):
        ax.annotate(
            f"{y_value:g}",
            xy=(y_value, lstar_value),
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=8,
        )
    ax.set_title("CIE 1976 Lightness")
    ax.set_xlabel("Relative luminance Y")
    ax.set_ylabel("L*")
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    output_path = output_dir / "07_lightness.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
