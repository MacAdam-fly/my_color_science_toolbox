"""Compare interpolation methods on one spectral signal."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.spectra import SpectralDistribution


def main() -> None:
    sd = SpectralDistribution(
        [400, 450, 500, 550, 600, 650],
        [0.00, 0.12, 0.80, 0.92, 0.35, 0.10],
        name="peaked signal",
    )
    targets = [425, 475, 525, 575, 625]

    for method in ("nearest", "linear", "pchip", "sprague"):
        values = sd.sample(targets, method=method)
        print(f"{method:>8}:", values)


if __name__ == "__main__":
    main()
