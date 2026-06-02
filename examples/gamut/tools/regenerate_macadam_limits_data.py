"""As a tamplate to Regenerate cached MacAdam optimal-colour limits CSV files."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

# 获取所有父级目录的路径，用于定位到项目根目录，以便导入模块
ROOT = Path(__file__).resolve().parent.parent.parent.parent
TOOLS_DIR = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from color.gamut.macadam import computed_macadam_limits_data
from color.spectra import SpectralDistribution, SpectralShape
import illuminant_C


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

    illuminant_C_data = illuminant_C.illuminant_C
    wavelengths = sorted(illuminant_C_data)
    values = [illuminant_C_data[wavelength] for wavelength in wavelengths]
    return SpectralDistribution(
        wavelengths,
        values,
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
