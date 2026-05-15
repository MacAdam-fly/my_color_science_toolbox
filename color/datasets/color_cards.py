"""Standard color checker / color card spectral reflectance data.

Usage::

    from color.datasets.color_cards import get_color_card, list_color_cards

    macbeth = get_color_card('macbeth')
    print(macbeth.keys())  # dict of patch name → reflectance array
"""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from ._registry import DatasetEntry, register, SpectralDict
from ._utils import data_dir, read_csv

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_CARDS_DIR = str(data_dir("color_cards"))

MACBETH_PATCH_NAMES: tuple[str, ...] = (
    "Dark Skin", "Light Skin", "Blue Sky", "Foliage", "Blue Flower",
    "Bluish Green", "Orange", "Purplish Blue", "Moderate Red", "Purple",
    "Yellow Green", "Orange Yellow", "Blue", "Green", "Red", "Yellow",
    "Magenta", "Cyan", "White", "Neutral 8", "Neutral 6.5", "Neutral 5",
    "Neutral 3.5", "Black",
)

BCRA_TILE_NAMES: tuple[str, ...] = (
    "Black", "Deep Grey", "Mid Grey", "Light Grey", "White",
    "Orange", "Cyan", "Green", "Deep Blue", "Bright Yellow",
    "Deep Pink", "Red",
)


# ---------------------------------------------------------------------------
# Special loaders
# ---------------------------------------------------------------------------

def _load_macbeth(path: str, **_: Any) -> SpectralDict:
    """Load Macbeth ColorChecker CSV (3 header rows, 24 patches)."""
    raw = read_csv(path, header=False, skiprows=3, usecols=range(26))  # wl + 24 patches
    wl = raw["wavelength"]
    result: SpectralDict = {"wavelength": wl}
    for i, name in enumerate(MACBETH_PATCH_NAMES):
        result[name] = raw[f"col{i + 1}"]
    return result


def _load_pmc(path: str, **_: Any) -> SpectralDict:
    """Load PMC chart XLSX (31 patches, 400–700 nm, 10 nm)."""
    from ._utils import read_xlsx
    raw = read_xlsx(path, sheet=0, header=False, skiprows=1)
    wl = raw["wavelength"]
    result: SpectralDict = {"wavelength": wl}
    # PMC patch categories and names
    pmc_names = (
        "Caucasian", "Oriental", "South Asian", "African",
        "Pork", "Carrot", "Orange", "Orange Yellow", "Banana",
        "Yellow Green", "Green Apple", "Summer Grass", "Bluish Green", "Smurf",
        "Blue Sky", "Lavender", "Purple", "Purple Cabbage",
        "Unitary Red", "Unitary Yellow", "Unitary Green",
        "Unitary Blue", "Unitary Magenta", "Unitary Cyan",
        "White", "Gray-80", "Gray-70", "Gray-50", "Gray-35", "Black",
    )
    for i, name in enumerate(pmc_names):
        col_key = f"col{i + 1}"
        if col_key in raw:
            result[name] = raw[col_key]
    return result


def _load_bcra(path: str, **_: Any) -> SpectralDict:
    """Load BCRA calibration tiles XLS (12 tiles, 380–730 nm, 10 nm)."""
    from ._utils import read_xls
    raw = read_xls(path, sheet=0, header=False, skiprows=1)
    wl = raw["wavelength"]
    result: SpectralDict = {"wavelength": wl}
    for i, name in enumerate(BCRA_TILE_NAMES):
        col_key = f"col{i + 1}"
        if col_key in raw:
            result[name] = raw[col_key]
    return result


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

register(DatasetEntry(
    category="color_cards",
    name="macbeth",
    description="Macbeth ColorChecker Classic — 24 patches, 380–780 nm, 5 nm",
    source="Ohta (1997)",
    file_path=f"{_CARDS_DIR}/MacbethColorChecker(Sheet1).csv",
    metadata={"loader": _load_macbeth, "patches": MACBETH_PATCH_NAMES},
))

register(DatasetEntry(
    category="color_cards",
    name="pmc",
    description="Preferred Memory Color (PMC) chart — 31 patches, 400–700 nm, 10 nm",
    source="Luo (2024)",
    file_path=f"{_CARDS_DIR}/PMC.xlsx",
    metadata={"loader": _load_pmc},
))

register(DatasetEntry(
    category="color_cards",
    name="bcra",
    description="BCRA CERAM Series II calibration tiles — 12 tiles, 380–730 nm, 10 nm",
    source="RIT Munsell Color Science Lab",
    file_path=f"{_CARDS_DIR}/RepresentativeBCRA.xls",
    metadata={"loader": _load_bcra, "patches": BCRA_TILE_NAMES},
))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_color_card(name: str, **kwargs: Any) -> SpectralDict:
    """Load a color card's spectral reflectance data.

    Parameters
    ----------
    name : str
        ``'macbeth'``, ``'pmc'``, or ``'bcra'``.

    Returns
    -------
    dict[str, ndarray]
        ``{'wavelength': ..., patch_name: reflectance, ...}``
    """
    from ._registry import get, describe

    entry = describe("color_cards", name)
    custom_loader = entry.metadata.get("loader")
    if custom_loader is not None:
        # Use the specialized loader with caching
        cache_key = ("color_cards", name)
        from ._registry import _CACHE
        if cache_key not in _CACHE:
            _CACHE[cache_key] = custom_loader(entry.file_path, **kwargs)
        return _CACHE[cache_key]
    return get("color_cards", name, **kwargs)


def list_color_cards() -> List[str]:
    """List all registered color card names."""
    from ._registry import list_datasets
    return list_datasets("color_cards")
