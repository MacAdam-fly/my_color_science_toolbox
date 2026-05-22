"""Convert the whitespace-separated merbnath data file to comma-separated CSV.

This script does not overwrite the source file. It writes a converted candidate
next to the original file so it can be inspected before replacement.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np


SOURCE = (
    Path(__file__).resolve().parent
    / "color"
    / "data"
    / "standard_observer_data"
    / "photopigments"
    / "merbnath.csv"
)
TARGET = SOURCE.with_name("merbnath_converted.csv")


def main() -> None:
    data = np.loadtxt(SOURCE, dtype=np.float64)
    if data.ndim != 2 or data.shape[1] != 6:
        raise ValueError(f"expected a 2D table with 6 columns, got shape {data.shape}")

    np.savetxt(
        TARGET,
        data,
        delimiter=",",
        fmt=["%.10g", "%.10g", "%.10g", "%.10g", "%.10g", "%.10g"],
    )
    print(f"source: {SOURCE}")
    print(f"target: {TARGET}")
    print(f"shape:  {data.shape}")
    print("first row:", data[0])
    print("last row: ", data[-1])


if __name__ == "__main__":
    main()
