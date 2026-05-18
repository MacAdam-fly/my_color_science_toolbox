"""Use sample/call and domain/range aliases."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.spectra import SpectralDistribution


def main() -> None:
    reflectance = SpectralDistribution(
        [400, 500, 600, 700],
        [0.05, 0.25, 0.65, 0.55],
        name="sample reflectance",
    )

    print("Domain alias:", reflectance.domain)
    print("Range alias:", reflectance.range)
    print("sample([450, 550]):", reflectance.sample([450, 550], method="linear"))
    print("__call__([450, 550]):", reflectance([450, 550], method="auto"))


if __name__ == "__main__":
    main()
