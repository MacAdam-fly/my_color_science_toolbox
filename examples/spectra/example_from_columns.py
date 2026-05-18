"""Build spectral objects from raw column dictionaries."""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np

from color.spectra import from_columns


def main() -> None:
    raw_single = {
        "wavelength": np.array([400.0, 500.0, 600.0]),
        "reflectance": np.array([0.12, 0.45, 0.31]),
    }
    reflectance = from_columns(raw_single, y="reflectance", name="sample")
    reflectance_450 = reflectance.interpolate([450.0])

    raw_multi = {
        "wavelength": np.array([400.0, 500.0, 600.0]),
        "R": np.array([0.8, 0.5, 0.2]),
        "G": np.array([0.1, 0.7, 0.3]),
        "B": np.array([0.0, 0.2, 0.9]),
    }
    rgb = from_columns(raw_multi, ys=("R", "G", "B"), name="rgb sensitivities")

    print("Single-channel type:", type(reflectance).__name__)
    print("Reflectance at 450 nm:", reflectance_450.values[0])
    print("Multi-channel type:", type(rgb).__name__)
    print("Labels:", rgb.labels)
    print("As raw dict keys:", list(rgb.to_dict().keys()))


if __name__ == "__main__":
    main()
