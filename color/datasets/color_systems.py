"""Color notation system data — Munsell renotation, and more.

Usage::

    from color.datasets.color_systems import get_color_system, list_color_systems

    munsell = get_color_system('munsell_srgb')
    munsell["h"]  # array of strings: "10RP", "2.5R", ...
"""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from ._registry import DatasetEntry, register, SpectralDict
from ._utils import data_dir

_DATA_DIR = str(data_dir("color_systems"))

# Column names for the Munsell sRGB dataset
_MUNSELL_NAMES = (
    "file_order", "h", "V", "C",       # Munsell HVC notation
    "x", "y", "Y",                       # Illuminant C chromaticity
    "X_C", "Y_C", "Z_C",                # XYZ under Illuminant C
    "X_D65", "Y_D65", "Z_D65",         # XYZ under D65 (CAT2002)
    "R", "G", "B",                       # Analog sRGB [0, 1]
    "dR", "dG", "dB",                    # 8-bit digital sRGB [0, 255]
)


def _read_munsell(path: str, **_: Any) -> SpectralDict:
    """Read Munsell sRGB XLS, preserving the Hue string column."""
    import xlrd

    wb = xlrd.open_workbook(path)
    ws = wb.sheet_by_name("data")

    # First pass: determine column types from first data row
    ncols = ws.ncols
    col_is_str = []
    for c in range(ncols):
        val = ws.cell_value(1, c)  # row 1 = first data row
        col_is_str.append(isinstance(val, str))

    # Initialize columns
    columns: Dict[str, list] = {name: [] for name in _MUNSELL_NAMES}

    for r in range(1, ws.nrows):  # skip header row 0
        for c, name in enumerate(_MUNSELL_NAMES):
            val = ws.cell_value(r, c)
            if col_is_str[c]:
                # Keep strings as-is
                columns[name].append(str(val) if val else "")
            else:
                # Convert to float
                if isinstance(val, (int, float)):
                    columns[name].append(float(val))
                elif isinstance(val, str) and val.strip():
                    try:
                        columns[name].append(float(val))
                    except ValueError:
                        columns[name].append(float("nan"))
                else:
                    columns[name].append(float("nan"))

    # Build result: string columns as object arrays, numeric as float arrays
    result: SpectralDict = {}
    for name in _MUNSELL_NAMES:
        if col_is_str[list(_MUNSELL_NAMES).index(name)]:
            result[name] = np.array(columns[name], dtype=object)
        else:
            result[name] = np.array(columns[name], dtype=float)
    return result


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

register(DatasetEntry(
    category="color_systems",
    name="munsell_srgb",
    description="RIT Munsell renotation data — 1625 real/obtainable chips",
    source="RIT Munsell Renotation",
    file_path=f"{_DATA_DIR}/real_sRGB.xls",
    parser_fn=_read_munsell,
    metadata={
        "quantity": "color_notation_table",
        "notation_system": "Munsell",
        "sample_count": 1625,
        "illuminants": ("C", "D65"),
        "observer_angle_deg": 2,
        "color_spaces": ("Munsell HVC", "xyY", "XYZ", "sRGB"),
        "rgb_encoding": "sRGB",
    },
))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_color_system(name: str, **kwargs: Any) -> SpectralDict:
    """Load a color notation system dataset.

    Parameters
    ----------
    name : str
        ``'munsell_srgb'``.

    Returns
    -------
    dict[str, ndarray]
        For Munsell: ``'h'`` is a string array (e.g. ``"10RP"``, ``"2.5R"``),
        all other columns are float arrays.
    """
    from ._registry import get
    return get("color_systems", name, **kwargs)


def list_color_systems() -> List[str]:
    """List all registered color system dataset names."""
    from ._registry import list_datasets
    return list_datasets("color_systems")
