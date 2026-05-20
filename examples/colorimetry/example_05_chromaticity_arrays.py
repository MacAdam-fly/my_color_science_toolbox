"""Convert image-like XYZ arrays to xyY and xy chromaticity."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.colorimetry import XYZ_to_xy, XYZ_to_xyY, xyY_to_XYZ
from _plot_helpers import example_output_dir, plot_srgb_swatches


def main() -> None:
    output_dir = example_output_dir()

    XYZ = np.array([
        [
            [95.047, 100.0, 108.883],
            [41.24, 21.26, 1.93],
        ],
        [
            [10.0, 20.0, 30.0],
            [0.1, 0.2, 0.3],
        ],
    ])

    xyY = XYZ_to_xyY(XYZ)
    xy = XYZ_to_xy(XYZ)
    XYZ_roundtrip = xyY_to_XYZ(xyY)

    print("XYZ shape:", XYZ.shape)
    print("xyY shape:", xyY.shape)
    print("xy shape:", xy.shape)
    print("Round-trip OK:", np.allclose(XYZ_roundtrip, XYZ))
    print("First pixel XYZ:", np.round(XYZ[0, 0], 6))
    print("First pixel xyY:", np.round(xyY[0, 0], 6))
    print("First pixel xy:", np.round(xy[0, 0], 6))

    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4))

    ax = axes[0]
    ax.imshow(XYZ[..., 1], cmap="viridis")
    ax.set_title("Y Channel from XYZ")
    ax.set_xticks(range(XYZ.shape[1]))
    ax.set_yticks(range(XYZ.shape[0]))

    ax = axes[1]
    ax.scatter(xy[..., 0].ravel(), xy[..., 1].ravel(), s=70, color="tab:blue")
    for row in range(xy.shape[0]):
        for col in range(xy.shape[1]):
            ax.annotate(
                f"{row},{col}",
                xy=xy[row, col],
                xytext=(6, 6),
                textcoords="offset points",
                fontsize=8,
            )
    ax.set_title("xy Coordinates")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_xlim(0.0, 0.8)
    ax.set_ylim(0.0, 0.9)
    ax.grid(True, alpha=0.3)

    ax = axes[2]
    labels = [f"{row},{col}" for row in range(XYZ.shape[0]) for col in range(XYZ.shape[1])]
    plot_srgb_swatches(
        ax,
        labels,
        XYZ.reshape(-1, 3),
        white_Y=100.0,
        title="Approximate sRGB Preview",
    )

    fig.tight_layout()
    output_path = output_dir / "05_chromaticity_arrays.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
