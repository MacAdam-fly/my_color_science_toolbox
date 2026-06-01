"""Regenerate cached MacAdam optimal-colour limits CSV files."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from color.gamut.macadam import computed_macadam_limits_data
from color.spectra import SpectralDistribution, SpectralShape


DATA_DIR = ROOT / "color" / "data" / "gamut_data"
ILLUMINANTS = ("A", "C", "D65")
Y_LAYERS = (0.0, 1.0, 5.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 95.0, 100.0)
FIELDS = ("x", "y", "Y", "X", "Z", "L", "a", "b", "C", "h")


def _write_csv(path: Path, data: dict[str, object]) -> None:
    """Write MacAdam data columns to *path*."""
    row_count = len(data["Y"])  # type: ignore[arg-type]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(FIELDS)
        for index in range(row_count):
            writer.writerow([f"{float(data[field][index]):.12g}" for field in FIELDS])  # type: ignore[index]


def _illuminant_source(name: str) -> str | SpectralDistribution:
    """Return an illuminant source usable by computed MacAdam generation."""
    if name != "C":
        return name

    import colour

    sd = colour.SDS_ILLUMINANTS["C"]
    return SpectralDistribution(
        sd.wavelengths,
        sd.values,
        name="CIE Illuminant C",
        metadata={"source": "colour.SDS_ILLUMINANTS['C']"},
    )


def main() -> None:
    """Regenerate all cached MacAdam limits tables."""
    shape = SpectralShape(400.0, 700.0, 2.0)
    for illuminant in ILLUMINANTS:
        data = computed_macadam_limits_data(
            illuminant=_illuminant_source(illuminant),
            shape=shape,
            Y_values=Y_LAYERS,
        )
        _write_csv(DATA_DIR / f"MacAdamLimits_{illuminant}.csv", data)


if __name__ == "__main__":
    main()
