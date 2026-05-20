"""Convert CIE 2006 LMS values to XYZ and back."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.colorimetry import LMS_to_XYZ, XYZ_to_LMS
from _plot_helpers import example_output_dir


def main() -> None:
    output_dir = example_output_dir()

    LMS = np.array([
        [0.2, 0.3, 0.4],
        [0.5, 0.4, 0.1],
    ])

    XYZ = LMS_to_XYZ(LMS, observer=2)
    LMS_roundtrip = XYZ_to_LMS(XYZ, observer=2)

    print("LMS:")
    print(np.round(LMS, 6))
    print("XYZ:")
    print(np.round(XYZ, 6))
    print("Round-trip OK:", np.allclose(LMS_roundtrip, LMS))

    labels = ["sample 1", "sample 2"]
    channels = np.arange(3)
    width = 0.35

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))

    ax = axes[0]
    for index, label in enumerate(labels):
        ax.bar(channels + (index - 0.5) * width, LMS[index], width=width, label=label)
    ax.set_title("Input LMS")
    ax.set_xticks(channels, ("L", "M", "S"))
    ax.set_ylabel("Response")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)

    ax = axes[1]
    for index, label in enumerate(labels):
        ax.bar(channels + (index - 0.5) * width, XYZ[index], width=width, label=label)
    ax.set_title("Converted XYZ")
    ax.set_xticks(channels, ("X", "Y", "Z"))
    ax.set_ylabel("Tristimulus value")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)

    fig.tight_layout()
    output_path = output_dir / "08_lms_xyz_transformations.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
