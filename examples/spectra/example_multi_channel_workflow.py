"""Work with a multi-channel spectral object."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.spectra import SpectralShape, from_dataset


def main() -> None:
    cmfs = from_dataset("standard_observers.cmfs", "CIE 1931 XYZ 1 nm")
    coarse = cmfs.reshape(SpectralShape(400, 700, 25), method="linear")
    y_bar = coarse.channel("Y")

    print("Labels:", cmfs.labels)
    print("Coarse values shape:", coarse.values.shape)
    print("Y channel object:", type(y_bar).__name__)
    print("Y samples at 450/550/650 nm:", y_bar([450, 550, 650], method="linear"))


if __name__ == "__main__":
    main()
