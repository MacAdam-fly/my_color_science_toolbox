"""Single-channel spectral distribution from a registered illuminant."""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.spectra import SpectralShape, from_dataset


def main() -> None:
    d65 = from_dataset("illuminants", "D65")
    d65_10nm = d65.reshape(SpectralShape(400, 700, 10))
    sampled = d65([450, 550])

    print("Object:", type(d65).__name__)
    print("Name:", d65.name)
    print("Original samples:", len(d65.wavelengths))
    print("Reshaped samples:", len(d65_10nm.wavelengths))
    print("Sampled values at 450/550 nm:", sampled)
    print("First reshaped values:")
    for wavelength, value in zip(d65_10nm.wavelengths[:5], d65_10nm.values[:5]):
        print(f"  {wavelength:.0f} nm -> {value:.4f}")


if __name__ == "__main__":
    main()
