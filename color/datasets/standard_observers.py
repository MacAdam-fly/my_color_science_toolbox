"""CVRL standard observer data — auto-discovered from 106 CSV files.

Covers six categories of human visual system fundamentals:

* **cmfs** — CIE 1931/1964/2012 XYZ colour matching functions
* **cone_fundamentals** — Stockman & Sharpe, CIE 2006 LMS, Smith-Pokorny, …
* **luminous_efficiency** — CIE 2008 V(λ), CIE 1924 V(λ), scotopic V'(λ)
* **prereceptoral_filters** — macular pigment & lens density
* **chromaticity_coordinates** — CIE & MacLeod-Boynton chromaticity coords
* **photopigments** — photopigment absorption spectra

All CSV files are auto-scanned and registered at import time.

Usage::

    from color.datasets.standard_observers import get_standard_observer, list_standard_observers

    xyz31 = get_standard_observer('cmfs', 'cie1931_xyz_1nm')
    lms = get_standard_observer('cone_fundamentals', 'ss2_logE')
    v_lambda = get_standard_observer('luminous_efficiency', 'cie2008_v2_linE_1nm')

    # List all files in a category
    list_standard_observers('cmfs')
    # List all categories
    list_standard_observer_categories()
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ._registry import DatasetEntry, register, register_category_alias, SpectralDict
from ._registry import canonicalize_name
from ._utils import data_dir

# ---------------------------------------------------------------------------
# Column-name inference
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Custom registration — add new categories / files here (one dict per entry)
# ---------------------------------------------------------------------------
#
# Supported fields:
#   category    - folder name under standard_observer_data/ (required)
#   stem        - CSV filename without .csv (required)
#   columns     - column name tuple, e.g. ("wavelength", "l", "m", "s") (optional)
#                 Controls column names.
#   description - human-readable description (optional, falls back to filename pattern)
#   category_aliases - category aliases for this custom category (optional)
#                 These aliases resolve standard_observers categories only; they are
#                 not dataset name aliases.
#   aliases     - deprecated compatibility spelling for category_aliases (optional)
#   read_options - dict of read_csv options (optional), e.g.:
#                 {"skiprows": 3, "header": 3}
#                 Supported keys: header, skiprows, usecols.
#                 "names" is ignored; use "columns" instead.
#   metadata    - descriptive fields that do not affect reading (optional)
#
# Note: by default, header is auto-detected (header=True). If the CSV has a
# text header row, those names are used. If all-numeric, *columns* (if provided)
# or filename-pattern inference takes over.
#
# Column name priority: file header > columns > filename-pattern inference
#
# Example:
#     {"category": "mesopic",
#      "stem": "v_meso_5nm",
#      "columns": ("wavelength", "V_meso"),
#      "description": "CIE 201x Mesopic V(λ) (5 nm)",
#      "aliases": ["meso", "mesopic"]},
#
#     # File with metadata rows to skip:
#     {"category": "my_data", "stem": "with_meta",
#      "columns": ("wavelength", "value"),
#      "read_options": {"header": 3}},

_CUSTOM_ENTRIES: list[dict[str, Any]] = [
    # Add your custom entries here
]


# Patterns for inferring column names from file stems
_COLUMN_PATTERNS: list[tuple[str, tuple[str, ...]]] = [
    ("xyz", ("wavelength", "X", "Y", "Z")),
    ("sbrgb", ("wavelength", "R", "G", "B")),
    ("_lms_", ("wavelength", "l", "m", "s")),
    ("lms", ("wavelength", "l", "m", "s")),
    # Cone fundamentals: smj, vew, sp, dpse
    ("smj", ("wavelength", "l", "m", "s")),
    ("vew_", ("wavelength", "l", "m", "s")),
    ("sp_", ("wavelength", "l", "m", "s")),
    ("dpse", ("wavelength", "l", "m", "s")),
    # Luminous efficiency: single value
    ("_v2_", ("wavelength", "V")),
    ("_v10_", ("wavelength", "V")),
    ("vl1924", ("wavelength", "V")),
    ("vl_judd", ("wavelength", "V")),
    ("scotopic", ("wavelength", "V_prime")),
    # Chromaticity coordinates
    ("mb", ("wavelength", "l", "s", "B")),
    ("chro", ("wavelength", "x", "y", "z")),
    # Prereceptoral filters: single value
    ("macular", ("wavelength", "optical_density")),
    ("lens_", ("wavelength", "optical_density")),
    # Photopigments — multi-column (4+ cols)
    ("succone", ("wavelength", "l", "m", "s")),
    ("ss_psycho", ("wavelength", "l", "m", "s")),
    ("msprhes", ("wavelength", "l", "m", "s")),
    ("msphum", ("wavelength", "rod", "l", "m", "s")),
    ("merbnath", ("wavelength", "p1", "p2", "p3", "p4", "p5")),
    # Photopigments — single pigment (2 cols)
    ("sucrodsh", ("wavelength", "absorption")),
    ("sucrodsm", ("wavelength", "absorption")),
]


def _infer_col_names(stem: str, ncols: int) -> Tuple[str, ...]:
    """Infer column names from the file stem and column count."""
    lower = stem.lower()
    for pattern, names in _COLUMN_PATTERNS:
        if pattern in lower:
            if len(names) == ncols:
                return names
            # If mismatch, fall through to generic
            break

    # Generic fallback
    if ncols == 1:
        return ("wavelength",)
    if ncols == 2:
        return ("wavelength", "value")
    return ("wavelength",) + tuple(f"col{i}" for i in range(1, ncols))


# ---------------------------------------------------------------------------
# Friendly descriptions for known file patterns
# ---------------------------------------------------------------------------

_DESCRIPTION_OVERRIDES: dict[str, str] = {
    # --- cmfs ---
    "cie1931_xyz_5nm": "CIE 1931 2° XYZ CMFs (5 nm)",
    "cie1931_xyz_1nm": "CIE 1931 2° XYZ CMFs (1 nm)",
    "cie1964_xyz_5nm": "CIE 1964 10° XYZ CMFs (5 nm)",
    "cie1964_xyz_1nm": "CIE 1964 10° XYZ CMFs (1 nm)",
    "ciexyz_judd": "CIE 1931 XYZ modified by Judd (1951)",
    "ciexyz_judd_vos": "CIE 1931 XYZ modified by Judd (1951) & Vos (1978)",
    "sbrgb2": "Stiles & Burch (1955) 2° RGB CMFs",
    "sbrgb10_5nm": "Stiles & Burch (1959) 10° RGB CMFs (5 nm)",
    "sbrgb10_1nm": "Stiles & Burch (1959) 10° RGB CMFs (1 nm)",
    "cie2012_xyz2_5nm": "CIE 2012 2° XYZ CMFs from CIE 2006 LMS (5 nm)",
    "cie2012_xyz2_1nm": "CIE 2012 2° XYZ CMFs from CIE 2006 LMS (1 nm)",
    "cie2012_xyz2_0p1nm": "CIE 2012 2° XYZ CMFs from CIE 2006 LMS (0.1 nm)",
    "cie2012_xyz10_5nm": "CIE 2012 10° XYZ CMFs from CIE 2006 LMS (5 nm)",
    "cie2012_xyz10_1nm": "CIE 2012 10° XYZ CMFs from CIE 2006 LMS (1 nm)",
    "cie2012_xyz10_0p1nm": "CIE 2012 10° XYZ CMFs from CIE 2006 LMS (0.1 nm)",
    # --- cone_fundamentals: CIE 2006 ---
    "cie2006_lms2_logE_5nm": "CIE 2006 2° LMS, log energy (5 nm)",
    "cie2006_lms2_logE_1nm": "CIE 2006 2° LMS, log energy (1 nm)",
    "cie2006_lms2_logE_0p1nm": "CIE 2006 2° LMS, log energy (0.1 nm)",
    "cie2006_lms2_logQ_5nm": "CIE 2006 2° LMS, log quantal (5 nm)",
    "cie2006_lms2_logQ_1nm": "CIE 2006 2° LMS, log quantal (1 nm)",
    "cie2006_lms2_logQ_0p1nm": "CIE 2006 2° LMS, log quantal (0.1 nm)",
    "cie2006_lms2_linE_5nm": "CIE 2006 2° LMS, linear energy (5 nm)",
    "cie2006_lms2_linE_1nm": "CIE 2006 2° LMS, linear energy (1 nm)",
    "cie2006_lms2_linE_0p1nm": "CIE 2006 2° LMS, linear energy (0.1 nm)",
    "cie2006_lms10_logE_5nm": "CIE 2006 10° LMS, log energy (5 nm)",
    "cie2006_lms10_logE_1nm": "CIE 2006 10° LMS, log energy (1 nm)",
    "cie2006_lms10_logE_0p1nm": "CIE 2006 10° LMS, log energy (0.1 nm)",
    "cie2006_lms10_logQ_5nm": "CIE 2006 10° LMS, log quantal (5 nm)",
    "cie2006_lms10_logQ_1nm": "CIE 2006 10° LMS, log quantal (1 nm)",
    "cie2006_lms10_logQ_0p1nm": "CIE 2006 10° LMS, log quantal (0.1 nm)",
    "cie2006_lms10_linE_5nm": "CIE 2006 10° LMS, linear energy (5 nm)",
    "cie2006_lms10_linE_1nm": "CIE 2006 10° LMS, linear energy (1 nm)",
    "cie2006_lms10_linE_0p1nm": "CIE 2006 10° LMS, linear energy (0.1 nm)",
    # --- cone_fundamentals: other sources ---
    "smj2_logE": "Stockman, MacLeod & Johnson (1993) 2°, log energy",
    "smj2_logQ": "Stockman, MacLeod & Johnson (1993) 2°, log quantal",
    "smj10_logE": "Stockman, MacLeod & Johnson (1993) 10°, log energy",
    "smj10_logQ": "Stockman, MacLeod & Johnson (1993) 10°, log quantal",
    "vew_logE": "Vos, Estevez & Walraven (1990) 2°, log energy",
    "vew_logQ": "Vos, Estevez & Walraven (1990) 2°, log quantal",
    "sp_logE": "Smith & Pokorny (1975) 2°, log energy",
    "sp_logQ": "Smith & Pokorny (1975) 2°, log quantal",
    "dpse_logE": "DeMarco, Pokorny & Smith (1992), log energy",
    # --- luminous_efficiency ---
    "cie2008_v2_linE_5nm": "CIE 2008 2° V(λ), linear energy (5 nm)",
    "cie2008_v2_linE_1nm": "CIE 2008 2° V(λ), linear energy (1 nm)",
    "cie2008_v2_linE_0p1nm": "CIE 2008 2° V(λ), linear energy (0.1 nm)",
    "cie2008_v2_logE_5nm": "CIE 2008 2° V(λ), log energy (5 nm)",
    "cie2008_v2_logE_1nm": "CIE 2008 2° V(λ), log energy (1 nm)",
    "cie2008_v2_logE_0P1nm": "CIE 2008 2° V(λ), log energy (0.1 nm)",
    "cie2008_v2_logQ_5nm": "CIE 2008 2° V(λ), log quantal (5 nm)",
    "cie2008_v2_logQ_1nm": "CIE 2008 2° V(λ), log quantal (1 nm)",
    "cie2008_v2_logQ_0p1nm": "CIE 2008 2° V(λ), log quantal (0.1 nm)",
    "cie2008_v10_linE_5nm": "CIE 2008 10° V(λ), linear energy (5 nm)",
    "cie2008_v10_linE_1nm": "CIE 2008 10° V(λ), linear energy (1 nm)",
    "cie2008_v10_linE_0p1nm": "CIE 2008 10° V(λ), linear energy (0.1 nm)",
    "cie2008_v10_logE_5nm": "CIE 2008 10° V(λ), log energy (5 nm)",
    "cie2008_v10_logE_1nm": "CIE 2008 10° V(λ), log energy (1 nm)",
    "cie2008_v10_logE_0P1nm": "CIE 2008 10° V(λ), log energy (0.1 nm)",
    "cie2008_v10_logQ_5nm": "CIE 2008 10° V(λ), log quantal (5 nm)",
    "cie2008_v10_logQ_1nm": "CIE 2008 10° V(λ), log quantal (1 nm)",
    "cie2008_v10_logQ_0p1nm": "CIE 2008 10° V(λ), log quantal (0.1 nm)",
    "vl1924_5nm": "CIE 1924 Photopic V(λ) (5 nm)",
    "vl1924_1nm": "CIE 1924 Photopic V(λ) (1 nm)",
    "vl1924_logE": "CIE 1924 Photopic V(λ), log energy",
    "vl1924_logQ": "CIE 1924 Photopic V(λ), log quantal",
    "vl_judd_logE": "V(λ) modified by Judd (1951), log energy",
    "vl_judd_vos_5nm": "V(λ) modified by Judd & Vos (5 nm)",
    "vl_judd_vos_1nm": "V(λ) modified by Judd & Vos (1 nm)",
    "scotopic_v_5nm": "CIE 1951 Scotopic V'(λ) (5 nm)",
    "scotopic_v_1nm": "CIE 1951 Scotopic V'(λ) (1 nm)",
    "scotopic_v_logE": "CIE 1951 Scotopic V'(λ), log energy",
    "scotopic_v_logQ": "CIE 1951 Scotopic V'(λ), log quantal",
    # --- prereceptoral_filters ---
    "macular_ss_5nm": "Macular pigment optical density, Stockman & Sharpe (5 nm)",
    "macular_ss_1nm": "Macular pigment optical density, Stockman & Sharpe (1 nm)",
    "macular_ss_0p1nm": "Macular pigment optical density, Stockman & Sharpe (0.1 nm)",
    "macular_vos": "Macular pigment density, Vos (1972)",
    "macular_ws": "Macular pigment density, Wyszecki & Stiles (1967)",
    "lens_ss_5nm": "Lens density spectrum, Stockman & Sharpe (5 nm)",
    "lens_ss_1nm": "Lens density spectrum, Stockman & Sharpe (1 nm)",
    "lens_ss_0p1nm": "Lens density spectrum, Stockman & Sharpe (0.1 nm)",
    "lens_ciepo06_components_5nm": (
        "CIEPO06 ocular media lens density components D_ocul,1 and D_ocul,2 (5 nm)"
    ),
    "lens_smj": "Lens density, Stockman, MacLeod & Johnson (1993)",
    "lens_vnv": "Lens density, van Norren & Vos (1974)",
    "lens_ws": "Lens density, Wyszecki & Stiles (1967)",
    # --- chromaticity_coordinates ---
    "cie1931_chro_5nm": "CIE 1931 2° x,y chromaticity (5 nm)",
    "cie1931_chro_1nm": "CIE 1931 2° x,y chromaticity (1 nm)",
    "cie1964_chro_5nm": "CIE 1964 10° x,y chromaticity (5 nm)",
    "cie1964_chro_1nm": "CIE 1964 10° x,y chromaticity (1 nm)",
    "cie2012_chro2_5nm": "CIE 2012 2° x,y,z chromaticity (5 nm)",
    "cie2012_chro2_1nm": "CIE 2012 2° x,y,z chromaticity (1 nm)",
    "cie2012_chro2_0p1nm": "CIE 2012 2° x,y,z chromaticity (0.1 nm)",
    "cie2012_chro10_5nm": "CIE 2012 10° x,y,z chromaticity (5 nm)",
    "cie2012_chro10_1nm": "CIE 2012 10° x,y,z chromaticity (1 nm)",
    "cie2012_chro10_0p1nm": "CIE 2012 10° x,y,z chromaticity (0.1 nm)",
    "mb2_chro2_5nm": "MacLeod-Boynton 2° chromaticity (5 nm)",
    "mb2_chro2_1nm": "MacLeod-Boynton 2° chromaticity (1 nm)",
    "mb2_chro2_0p1nm": "MacLeod-Boynton 2° chromaticity (0.1 nm)",
    "mb_chro10_5nm": "MacLeod-Boynton 10° chromaticity (5 nm)",
    "mb_chro10_1nm": "MacLeod-Boynton 10° chromaticity (1 nm)",
    "mb_chro10_0p1nm": "MacLeod-Boynton 10° chromaticity (0.1 nm)",
    # --- photopigments ---
    "ss_psycho_5nm": "Stockman & Sharpe template pigment (5 nm)",
    "sucrodsm": "Baylor, Nunn & Schnapf (1984) monkey rods",
    "sucrodsh": "Kraft, Schneeweis & Schnapf (1993) human rods",
    "succones": "Baylor, Nunn & Schnapf (1987) monkey cones",
    "msprhes": "Bowmaker et al. (1978) rhesus monkey MSP",
    "msphum": "Dartnall, Bowmaker & Mollon (1983) human MSP",
    "merbnath": "Merbs & Nathans (1992) human cone pigments",
}

# Friendly category names
_CATEGORY_NAMES: dict[str, str] = {
    "cmfs": "Colour Matching Functions",
    "cone_fundamentals": "Cone Spectral Sensitivities",
    "luminous_efficiency": "Luminous Efficiency Functions",
    "prereceptoral_filters": "Prereceptoral Filters",
    "chromaticity_coordinates": "Chromaticity Coordinates",
    "photopigments": "Photopigment Absorption Spectra",
}

# Category aliases are grouped by canonical standard_observers subcategory.
_CATEGORY_ALIAS_GROUPS: dict[str, tuple[str, ...]] = {
    "cmfs": ("cmf", "xyz"),
    "cone_fundamentals": ("cone", "cones", "lms", "fundamentals"),
    "luminous_efficiency": ("luminous", "v_lambda", "vl", "efficiency"),
    "prereceptoral_filters": ("filter", "filters", "prereceptoral", "macular", "lens"),
    "chromaticity_coordinates": ("chromaticity", "chroma", "chro", "xy"),
    "photopigments": ("photopigment", "pigment", "pigments"),
}

_CATEGORY_ALIASES: dict[str, str] = {
    canonicalize_name(alias): category
    for category, aliases in _CATEGORY_ALIAS_GROUPS.items()
    for alias in (category, *aliases)
}


def _resolve_category(category: str) -> str:
    """Resolve a category alias to its canonical name."""
    cat = canonicalize_name(category)
    canonical = _CATEGORY_ALIASES.get(cat)
    if canonical is not None:
        return canonical
    # Zero-config: accept any folder that was auto-discovered
    for candidate in _OBSERVER_ROOT.iterdir():
        if candidate.is_dir() and canonicalize_name(candidate.name) == cat:
            return candidate.name
    raise KeyError(
        f"Unknown standard observer category: {category!r}. "
        f"Valid categories: {list(_CATEGORY_NAMES.keys())}"
    )


_INTERVAL_TOKENS: dict[float, str] = {
    0.1: "0p1",
    1.0: "1",
    5.0: "5",
}

_ENERGY_TOKENS: dict[str, str] = {
    "line": "linE",
    "loge": "logE",
    "logq": "logQ",
}


def _interval_token(interval_nm: float, *, supported: tuple[float, ...]) -> str:
    """Return the filename token for a supported sampling interval."""
    try:
        interval = float(interval_nm)
    except (TypeError, ValueError) as exc:
        supported_text = ", ".join(str(v).rstrip("0").rstrip(".") for v in supported)
        raise ValueError(f"interval_nm must be one of: {supported_text}") from exc

    if interval not in supported:
        supported_text = ", ".join(str(v).rstrip("0").rstrip(".") for v in supported)
        raise ValueError(
            f"Unsupported interval_nm {interval_nm!r}; valid values: {supported_text}"
        )
    return _INTERVAL_TOKENS[interval]


def _energy_token(energy: str) -> str:
    """Return the canonical filename token for a CIE 2006 LMS energy scale."""
    key = canonicalize_name(energy)
    token = _ENERGY_TOKENS.get(key)
    if token is None:
        valid = ", ".join(_ENERGY_TOKENS.values())
        raise ValueError(f"Unsupported energy {energy!r}; valid values: {valid}")
    return token


def _cie1931_xyz_cmfs_stem(interval_nm: float) -> str:
    interval = _interval_token(interval_nm, supported=(1.0, 5.0))
    return f"cie1931_xyz_{interval}nm"


def _cie1964_xyz_cmfs_stem(interval_nm: float) -> str:
    interval = _interval_token(interval_nm, supported=(1.0, 5.0))
    return f"cie1964_xyz_{interval}nm"


def _cie2012_xyz_cmfs_stem(observer_degree: int, interval_nm: float) -> str:
    interval = _interval_token(interval_nm, supported=(0.1, 1.0, 5.0))
    return f"cie2012_xyz{observer_degree}_{interval}nm"


def _cie2006_lms_fundamentals_stem(
    observer_degree: int,
    interval_nm: float,
    energy: str,
) -> str:
    interval = _interval_token(interval_nm, supported=(0.1, 1.0, 5.0))
    energy_token = _energy_token(energy)
    return f"cie2006_lms{observer_degree}_{energy_token}_{interval}nm"


# ---------------------------------------------------------------------------
# Auto-discovery & registration
# ---------------------------------------------------------------------------

_OBSERVER_ROOT = data_dir("standard_observer_data")

# Built from _CUSTOM_ENTRIES at module load time
_CUSTOM_COL_OVERRIDES: dict[tuple[str, str], Tuple[str, ...]] = {}
_CUSTOM_READ_OPTIONS_OVERRIDES: dict[tuple[str, str], dict[str, Any]] = {}
_CUSTOM_META_OVERRIDES: dict[tuple[str, str], dict[str, Any]] = {}


def _process_custom_entries() -> None:
    """Inject custom entries into aliases, descriptions, and column overrides."""
    for entry in _CUSTOM_ENTRIES:
        cat = entry["category"]
        stem = entry["stem"]

        # Column override
        if "columns" in entry:
            _CUSTOM_COL_OVERRIDES[(cat, stem)] = tuple(entry["columns"])

        # Read-option override (header, skiprows, etc.)
        if "read_options" in entry:
            _CUSTOM_READ_OPTIONS_OVERRIDES[(cat, stem)] = entry["read_options"]

        # Descriptive metadata override
        if "metadata" in entry:
            _CUSTOM_META_OVERRIDES[(cat, stem)] = entry["metadata"]

        # Description override
        if "description" in entry:
            _DESCRIPTION_OVERRIDES[f"{cat}/{stem}"] = entry["description"]

        # Category aliases: always register the canonical category itself.
        _CATEGORY_ALIASES[canonicalize_name(cat)] = cat
        category_aliases = (
            *entry.get("category_aliases", ()),
            *entry.get("aliases", ()),
        )
        for alias in category_aliases:
            _CATEGORY_ALIASES[canonicalize_name(alias)] = cat


_process_custom_entries()


def _count_csv_cols(path: Path) -> int:
    """Read the first data line to determine column count."""
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                if "," in line:
                    return line.count(",") + 1
                # Space-separated fallback
                return len(line.split())
    return 0


def _infer_sampling_interval_nm(stem: str) -> Optional[float]:
    """Infer spectral sampling interval from common filename suffixes."""
    lower = stem.lower()
    if "0p1nm" in lower or "0p1" in lower:
        return 0.1
    if "1nm" in lower:
        return 1.0
    if "5nm" in lower:
        return 5.0
    return None


def _infer_observer_angle(category: str, stem: str) -> Optional[int]:
    """Infer CIE observer field size when encoded in the filename/category."""
    lower = stem.lower()
    if "10" in lower or "1964" in lower or category.endswith("10"):
        return 10
    if "2" in lower or "1931" in lower:
        return 2
    return None


def _metadata_for_standard_observer(category: str, stem: str) -> dict[str, Any]:
    """Build descriptive metadata for an auto-discovered observer dataset."""
    meta: dict[str, Any] = {
        "wavelength_unit": "nm",
        "domain": "spectral",
        "source_collection": "CVRL",
    }
    sampling = _infer_sampling_interval_nm(stem)
    if sampling is not None:
        meta["sampling_interval_nm"] = sampling

    observer_angle = _infer_observer_angle(category, stem)
    if observer_angle is not None:
        meta["observer_angle_deg"] = observer_angle

    if category == "cmfs":
        meta["quantity"] = "colour_matching_function"
        meta["value_unit"] = "relative"
        if "xyz" in stem.lower():
            meta["color_space"] = "XYZ"
        elif "sbrgb" in stem.lower():
            meta["color_space"] = "RGB"
    elif category == "cone_fundamentals":
        meta["quantity"] = "cone_fundamental"
        meta["value_unit"] = "relative"
        if "logq" in stem.lower():
            meta["energy_basis"] = "quantal"
            meta["scale"] = "logarithmic"
        elif "loge" in stem.lower():
            meta["energy_basis"] = "energy"
            meta["scale"] = "logarithmic"
        elif "line" in stem.lower():
            meta["energy_basis"] = "energy"
            meta["scale"] = "linear"
    elif category == "luminous_efficiency":
        meta["quantity"] = "luminous_efficiency"
        meta["value_unit"] = "relative"
        if "scotopic" in stem.lower():
            meta["vision_regime"] = "scotopic"
        else:
            meta["vision_regime"] = "photopic"
    elif category == "prereceptoral_filters":
        meta["quantity"] = "optical_density"
        meta["value_unit"] = "density"
        if "lens_ciepo06_components" in stem.lower():
            meta["quantity"] = "ocular_media_lens_density_components"
            meta["standard"] = "CIEPO06"
            meta["component_columns"] = ("d_ocul1", "d_ocul2", "d_ocul_32")
    elif category == "chromaticity_coordinates":
        meta["quantity"] = "chromaticity_coordinate"
        meta["value_unit"] = "dimensionless"
        if "mb" in stem.lower():
            meta["chromaticity_system"] = "MacLeod-Boynton"
        else:
            meta["chromaticity_system"] = "CIE"
    elif category == "photopigments":
        meta["quantity"] = "photopigment_absorption"
        meta["value_unit"] = "relative"

    return meta


def _scan_and_register() -> None:
    """Walk ``standard_observer_data/`` and register every CSV file."""
    if not _OBSERVER_ROOT.exists():
        return

    for subdir in sorted(_OBSERVER_ROOT.iterdir()):
        if not subdir.is_dir():
            continue
        category = subdir.name
        for csv_file in sorted(subdir.glob("*.csv")):
            stem = csv_file.stem
            ncols = _count_csv_cols(csv_file)

            # Custom column override takes priority
            col_override = _CUSTOM_COL_OVERRIDES.get((category, stem))
            desc = _DESCRIPTION_OVERRIDES.get(
                f"{category}/{stem}",
                _DESCRIPTION_OVERRIDES.get(stem, f"{stem} ({ncols - 1} channels)"),
            )

            # Read options: auto-detect header, merge custom overrides
            read_options: dict[str, Any] = {"header": True}
            read_options_over = _CUSTOM_READ_OPTIONS_OVERRIDES.get((category, stem))
            if read_options_over is not None:
                read_options.update(read_options_over)

            # Metadata: add descriptive fields, merge custom overrides
            meta = _metadata_for_standard_observer(category, stem)
            meta_over = _CUSTOM_META_OVERRIDES.get((category, stem))
            if meta_over is not None:
                meta.update(meta_over)

            # Column names: only set when explicitly customized.
            # File header and filename-pattern inference are handled at read time.
            cols = col_override  # None unless in _CUSTOM_COL_OVERRIDES

            register(DatasetEntry(
                category=f"standard_observers.{category}",
                name=stem,
                description=desc,
                columns=cols,
                source="CVRL (UCL)",
                file_path=str(csv_file),
                read_options=read_options,
                metadata=meta,
            ))


def _register_category_aliases() -> None:
    """Expose standard_observers subcategory aliases to the global registry."""
    for alias, category in _CATEGORY_ALIASES.items():
        register_category_alias(
            f"standard_observers.{alias}",
            f"standard_observers.{category}",
        )


# Run discovery at import time
_scan_and_register()
_register_category_aliases()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_standard_observer(
    category: str,
    name: str,
    **kwargs: Any,
) -> SpectralDict:
    """Load a standard observer dataset.

    Parameters
    ----------
    category : str
        Sub-category or alias.  Canonical names: ``'cmfs'``,
        ``'cone_fundamentals'``, ``'luminous_efficiency'``,
        ``'prereceptoral_filters'``, ``'chromaticity_coordinates'``,
        ``'photopigments'``.  Aliases such as ``'cone'``, ``'lms'``,
        ``'xyz'``, ``'luminous'``, ``'filter'``, ``'chroma'``,
        ``'pigment'`` are also accepted.
    name : str
        File stem, e.g. ``'cie1931_xyz_1nm'``, ``'cie2006_lms2_logE_5nm'``.

    Returns
    -------
    dict[str, ndarray]
        ``{'wavelength': ..., 'x_bar': ..., 'y_bar': ..., 'z_bar': ...}``
        (keys depend on the dataset).
    """
    from ._registry import get
    return get(f"standard_observers.{_resolve_category(category)}", name, **kwargs)


def get_cie1931_xyz_cmfs(interval_nm: float = 1) -> SpectralDict:
    """Return CIE 1931 2-degree XYZ colour matching functions."""
    return get_standard_observer("cmfs", _cie1931_xyz_cmfs_stem(interval_nm))


def get_cie1964_xyz_cmfs(interval_nm: float = 1) -> SpectralDict:
    """Return CIE 1964 10-degree XYZ colour matching functions."""
    return get_standard_observer("cmfs", _cie1964_xyz_cmfs_stem(interval_nm))


def get_cie2012_xyz_2degree_cmfs(interval_nm: float = 1) -> SpectralDict:
    """Return CIE 2012 2-degree XYZ colour matching functions."""
    return get_standard_observer("cmfs", _cie2012_xyz_cmfs_stem(2, interval_nm))


def get_cie2012_xyz_10degree_cmfs(interval_nm: float = 1) -> SpectralDict:
    """Return CIE 2012 10-degree XYZ colour matching functions."""
    return get_standard_observer("cmfs", _cie2012_xyz_cmfs_stem(10, interval_nm))


def get_cie2006_lms_2degree_fundamentals(
    interval_nm: float = 1,
    energy: str = "linE",
) -> SpectralDict:
    """Return CIE 2006 2-degree LMS cone fundamentals."""
    return get_standard_observer(
        "cone_fundamentals",
        _cie2006_lms_fundamentals_stem(2, interval_nm, energy),
    )


def get_cie2006_lms_10degree_fundamentals(
    interval_nm: float = 1,
    energy: str = "linE",
) -> SpectralDict:
    """Return CIE 2006 10-degree LMS cone fundamentals."""
    return get_standard_observer(
        "cone_fundamentals",
        _cie2006_lms_fundamentals_stem(10, interval_nm, energy),
    )


def list_standard_observers(category: str) -> List[str]:
    """List all registered dataset names in a sub-category."""
    from ._registry import list_datasets
    return list_datasets(f"standard_observers.{_resolve_category(category)}")


def list_standard_observer_categories() -> List[str]:
    """Return the six standard observer sub-category keys."""
    return list(_CATEGORY_NAMES.keys())


def describe_standard_observer(category: str) -> str:
    """Return a human-readable description of a sub-category."""
    return _CATEGORY_NAMES.get(_resolve_category(category), category)
