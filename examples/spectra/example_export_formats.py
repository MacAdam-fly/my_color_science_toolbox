"""Export spectral objects to dict, numpy, and pandas."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.spectra import from_dataset


def main() -> None:
    d65 = from_dataset("illuminants", "D65")
    subset = d65.reshape(d65.shape)

    raw = subset.to_dict()
    array = subset.to_numpy()
    frame = subset.to_pandas()

    print("Dict keys:", list(raw.keys()))
    print("Numpy shape:", array.shape)
    print("Pandas columns:", list(frame.columns))
    print("First row:", frame.iloc[0].to_dict())


if __name__ == "__main__":
    main()
