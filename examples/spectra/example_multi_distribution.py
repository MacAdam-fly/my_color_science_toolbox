"""Multi-channel spectral distribution from standard-observer CMFs."""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np

from color.spectra import SpectralShape, from_dataset


def main() -> None:
    cmfs = from_dataset("Standard Observers CMFS", "CIE 1931 XYZ 1 nm")
    cmfs_20nm = cmfs.reshape(SpectralShape(400, 700, 20))
    y_bar = cmfs.channel("Y")

    print("Object:", type(cmfs).__name__)
    print("Name:", cmfs.name)
    print("Labels:", cmfs.labels)
    print("Original shape:", cmfs.values.shape)
    print("Reshaped shape:", cmfs_20nm.values.shape)
    print("Y-bar peak wavelength:", y_bar.wavelengths[np.argmax(y_bar.values)])
    print("First reshaped row:")
    print("  wavelength:", cmfs_20nm.wavelengths[0])
    print("  values:", cmfs_20nm.values[0])


if __name__ == "__main__":
    main()
