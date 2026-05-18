"""Plot multi-channel standard observer colour matching functions."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt

from color.spectra import SpectralShape, from_dataset


def main() -> None:
    cmfs = from_dataset("standard_observers.cmfs", "CIE 1931 XYZ 5 nm")
    cmfs_1nm = cmfs.reshape(SpectralShape(380, 780, 1), method="linear")

    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "cie1931_xyz_cmfs.png"

    fig, axes = plt.subplots(2, 1, figsize=(8, 7), sharex=True, sharey=True)
    for ax, data, title in (
        (axes[0], cmfs, "Original CIE 1931 XYZ CMFs, 5 nm samples"),
        (axes[1], cmfs_1nm, "Reshaped CIE 1931 XYZ CMFs, 1 nm interpolation"),
    ):
        for index, label in enumerate(data.labels):
            ax.plot(
                data.wavelengths,
                data.values[:, index],
                marker="o",
                markersize=2.5,
                linewidth=1.2,
                label=label,
            )
        ax.set_title(title)
        ax.set_ylabel("Observer response")
        ax.grid(True, alpha=0.3)
        ax.legend()

    axes[1].set_xlabel("Wavelength (nm)")
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)

    print("Saved:", output_path)


if __name__ == "__main__":
    main()
