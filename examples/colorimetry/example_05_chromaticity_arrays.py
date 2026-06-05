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
from color.plot import (
    plot_chromaticity_points,
    plot_image,
    plot_labels,
    plot_style,
    plot_swatch_strip,
    preview_sRGB_from_XYZ,
)
from _plot_helpers import example_output_dir


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

    with plot_style("presentation", font_scale=0.65, line_scale=0.85):
        fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4))

        ax = axes[0]
        plot_image(
            XYZ[..., 1],
            ax=ax,
            title="Y Channel from XYZ",
            cmap="viridis",
            colorbar=True,
        )
        ax.set_xticks(range(XYZ.shape[1]))
        ax.set_yticks(range(XYZ.shape[0]))

        ax = axes[1]
        xy_rows = xy.reshape(-1, 2)
        labels = [f"{row},{col}" for row in range(XYZ.shape[0]) for col in range(XYZ.shape[1])]
        plot_chromaticity_points(
            xy_rows,
            ax=ax,
            color="tab:blue",
            title="xy Coordinates",
        )
        plot_labels(xy_rows, labels, ax=ax, grid=False)
        ax.set_xlim(0.0, 0.8)
        ax.set_ylim(0.0, 0.9)

        ax = axes[2]
        plot_swatch_strip(
            preview_sRGB_from_XYZ(XYZ.reshape(-1, 3), white_Y=100.0),
            ax=ax,
            labels=labels,
            title="Approximate sRGB Preview",
        )

        fig.tight_layout()
        output_path = output_dir / "05_chromaticity_arrays.png"
        fig.savefig(output_path, dpi=150)
        plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
