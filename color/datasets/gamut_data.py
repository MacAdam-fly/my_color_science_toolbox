"""Real-surface color gamut data.

Usage::

    from color.datasets.gamut_data import get_gamut_data, list_gamut_data

    # Calculations sheet (default) — Pointer gamut boundary at each L* level
    pointer = get_gamut_data('pointer')                  # all L* levels
    pointer_50 = get_gamut_data('pointer', L=50)         # single L* level

    # Other sheets via generic reader
    data = get_gamut_data('pointer', sheet='SpecLoc')
"""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from ._registry import DatasetEntry, register, SpectralDict
from ._utils import data_dir

_GAMUT_DIR = str(data_dir("gamut_data"))

# Column names for the Calculations sheet sections
_CALC_COLUMNS = ("L", "C", "a", "b", "X'", "Y'", "Z'", "x", "y", "u'", "v'")

# L* section start columns in the Calculations sheet
_LSTAR_OFFSETS = {
    20: 1, 30: 13, 40: 25, 50: 39,
    60: 53, 70: 67, 80: 81, 90: 95,
}

# Data rows: row 9 (1-based) = row 8 (0-based), 37 hue angles (0°–360° in 10° steps)
_DATA_START_ROW = 8
_N_HUE_ROWS = 37


def _read_pointer_calculations(**kwargs: Any) -> SpectralDict:
    """Parse the Pointer Calculations sheet.

    The sheet has 8 L* sections arranged side-by-side, each with 37 hue-angle
    boundary rows and columns (L*, C*, a*, b*, X', Y', Z', x, y, u', v').

    Parameters
    ----------
    **kwargs
        ``L`` — if given (20, 30, …, 90), return only that L* section.
        Otherwise all sections are concatenated.
    """
    import xlrd

    path = f"{_GAMUT_DIR}/PointerData.xls"
    wb = xlrd.open_workbook(path)
    ws = wb.sheet_by_name("Calculations")

    # Reference white metadata (rows 2–5, cols 1–3)
    ref_xn = ws.cell_value(3, 1)
    ref_yn = ws.cell_value(3, 2)
    ref_zn = ws.cell_value(3, 3)

    L_filter = kwargs.get("L")

    # Collect sections
    all_L = []
    all_hab = []
    columns: Dict[str, list] = {name: [] for name in _CALC_COLUMNS}

    for L_val, col_start in _LSTAR_OFFSETS.items():
        if L_filter is not None and L_val != L_filter:
            continue

        for i in range(_N_HUE_ROWS):
            r = _DATA_START_ROW + i
            hab = ws.cell_value(r, 0)
            all_L.append(float(L_val))
            all_hab.append(float(hab))
            for j, name in enumerate(_CALC_COLUMNS):
                val = ws.cell_value(r, col_start + j)
                if isinstance(val, (int, float)):
                    columns[name].append(float(val))
                elif isinstance(val, str) and val.strip():
                    try:
                        columns[name].append(float(val))
                    except ValueError:
                        columns[name].append(float("nan"))
                else:
                    columns[name].append(float("nan"))

    result: SpectralDict = {
        "L": np.array(all_L, dtype=float),
        "hab": np.array(all_hab, dtype=float),
        "Xn": np.array([ref_xn]),
        "Yn": np.array([ref_yn]),
        "Zn": np.array([ref_zn]),
    }
    for name in _CALC_COLUMNS:
        result[name] = np.array(columns[name], dtype=float)
    return result


def _read_pointer_sheet(**kwargs: Any) -> SpectralDict:
    """Generic reader for Pointer XLS sheets (Data, SpecLoc, IllumDat)."""
    from ._utils import read_xls

    path = f"{_GAMUT_DIR}/PointerData.xls"
    sheet = kwargs.get("sheet", "Data")
    return read_xls(path, sheet=sheet)


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

register(DatasetEntry(
    category="gamut_data",
    name="pointer",
    description="Pointer's gamut of real surface colours — Calculations sheet boundary data",
    source="Pointer (1980)",
    computed=True,
    compute_fn=_read_pointer_calculations,
    metadata={
        "sheets": ("Data", "Calculations", "IllumDat", "SpecLoc"),
    },
))

register(DatasetEntry(
    category="gamut_data",
    name="pointer_raw",
    description="Pointer's gamut — raw multi-sheet XLS (pass sheet= to select)",
    source="Pointer (1980)",
    file_path=f"{_GAMUT_DIR}/PointerData.xls",
    metadata={
        "sheet": "Data",
        "header": 8,
        "sheets": ("Data", "Calculations", "IllumDat", "SpecLoc"),
    },
))

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_gamut_data(name: str, **kwargs: Any) -> SpectralDict:
    """Load gamut boundary data.

    Parameters
    ----------
    name : str
        ``'pointer'`` or ``'pointer_raw'``.
    **kwargs
        For ``'pointer'``: ``L`` — filter by L* level (20, 30, …, 90).
        For ``'pointer_raw'``: ``sheet`` — sheet name (default ``'Data'``).

    Returns
    -------
    dict[str, ndarray]
    """
    from ._registry import get
    return get("gamut_data", name, **kwargs)


def list_gamut_data() -> List[str]:
    """List all registered gamut data names."""
    from ._registry import list_datasets
    return list_datasets("gamut_data")
