"""Align spectral objects, export arrays, and use arithmetic."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.spectra import SpectralShape, from_dataset


def main() -> None:
    d65 = from_dataset("illuminants", "D65")

    shape = SpectralShape(260, 800, 10)
    aligned = d65.align(shape)
    scaled = aligned * 0.5

    print("Original wavelengths:", d65.wavelengths[:5], "...", d65.wavelengths[-5:])
    print("Aligned wavelengths:", aligned.wavelengths[:5], "...", aligned.wavelengths[-5:])
    print("Scaled numpy shape:", scaled.to_numpy().shape)



if __name__ == "__main__":
    main()
