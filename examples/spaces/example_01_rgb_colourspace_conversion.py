"""Visualise RGB colour-space conversions and gamut geometry."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.spaces import RGB_to_RGB, RGB_to_XYZ

from _spaces_plot_helpers import (
    output_dir,
    plot_rgb_gamuts,
    plot_swatch_grid,
    preview_sRGB_from_XYZ,
    xy_from_XYZ,
)


SAMPLE_SRGB = np.array(
    [
        [0.90, 0.10, 0.10],
        [0.10, 0.70, 0.20],
        [0.10, 0.30, 0.90],
        [0.80, 0.70, 0.20],
        [0.50, 0.50, 0.50],
    ],
    dtype=np.float64,
)
RGB_SPACES = ["sRGB", "Display P3", "Rec.2020", "DCI-P3"]


def main() -> None:
    out = output_dir()

    XYZ = RGB_to_XYZ(SAMPLE_SRGB, colourspace="sRGB")
    xy = xy_from_XYZ(XYZ)
    converted = {
        name: RGB_to_RGB(SAMPLE_SRGB, "sRGB", name)
        for name in RGB_SPACES
    }

    print("RGB colour-space conversion from sRGB samples")
    for name, values in converted.items():
        print(f"{name} encoded RGB:\n{np.round(values, 6)}")

    dcip3_white = np.ones(3)
    no_adapt = RGB_to_RGB(dcip3_white, "DCI-P3", "sRGB")
    bradford = RGB_to_RGB(
        dcip3_white,
        "DCI-P3",
        "sRGB",
        chromatic_adaptation="Bradford",
    )
    print("DCI-P3 white to sRGB without adaptation:", np.round(no_adapt, 6))
    print("DCI-P3 white to sRGB with Bradford adaptation:", np.round(bradford, 6))

    fig, ax = plt.subplots(figsize=(7.4, 6.0))
    plot_rgb_gamuts(ax, RGB_SPACES)
    ax.scatter(
        xy[:, 0],
        xy[:, 1],
        c=np.clip(SAMPLE_SRGB, 0.0, 1.0),
        edgecolors="black",
        linewidths=0.8,
        s=70,
        label="sRGB samples",
    )
    for index, point in enumerate(xy, start=1):
        ax.annotate(f"C{index}", point + np.array([0.008, 0.006]), fontsize=8)
    ax.set_title("RGB Gamuts And Sample Colours In CIE xy")
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    path = out / "01_rgb_gamuts_xy.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")

    preview_rows = []
    for name, values in converted.items():
        preview_XYZ = RGB_to_XYZ(values, colourspace=name)
        preview_rows.append((name, preview_sRGB_from_XYZ(preview_XYZ)))

    fig, ax = plt.subplots(figsize=(8.4, 3.3))
    plot_swatch_grid(ax, preview_rows, title="Same XYZ Stimuli Previewed In sRGB")
    fig.tight_layout()
    path = out / "01_rgb_conversion_swatches.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")

    matrices = [converted[name] for name in RGB_SPACES]
    fig, axes = plt.subplots(
        1,
        len(RGB_SPACES),
        figsize=(12.5, 3.8),
        sharey=True,
        constrained_layout=True,
    )
    for ax, name, values in zip(axes, RGB_SPACES, matrices):
        im = ax.imshow(values, vmin=0.0, vmax=1.0, cmap="viridis", aspect="auto")
        ax.set_title(name)
        ax.set_xticks([0, 1, 2])
        ax.set_xticklabels(["R", "G", "B"])
        ax.set_yticks(range(SAMPLE_SRGB.shape[0]))
        ax.set_yticklabels([f"C{i + 1}" for i in range(SAMPLE_SRGB.shape[0])])
        for row in range(values.shape[0]):
            for col in range(values.shape[1]):
                ax.text(col, row, f"{values[row, col]:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.82, label="encoded RGB value")
    fig.suptitle("Coordinate Values For The Same Colours In Different RGB Spaces")
    path = out / "01_rgb_coordinate_values.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


if __name__ == "__main__":
    main()
