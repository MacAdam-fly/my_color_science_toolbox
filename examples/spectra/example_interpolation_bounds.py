"""Explicit out-of-domain interpolation behavior."""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.spectra import SpectralDistribution


def main() -> None:
    sd = SpectralDistribution([400, 500, 600], [0.0, 1.0, 0.0], name="triangle")

    try:
        sd.interpolate([350, 450])
    except ValueError as error:
        print("Default bounds_error=True rejects out-of-domain samples:")
        print(" ", error)

    relaxed = sd.interpolate(
        [350, 400, 450, 650],
        bounds_error=False,
        fill_value=-1.0,
    )
    print("\nWith bounds_error=False and fill_value=-1:")
    for wavelength, value in zip(relaxed.wavelengths, relaxed.values):
        print(f"  {wavelength:.0f} nm -> {value:.2f}")


if __name__ == "__main__":
    main()
