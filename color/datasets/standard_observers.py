"""CVRL standard observer data — auto-discovered from 112 CSV files.

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

from ._registry import DatasetEntry, register, SpectralDict
from ._utils import data_dir

# ---------------------------------------------------------------------------
# Column-name inference
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Custom registration — add new categories / files here (one dict per entry)
# ---------------------------------------------------------------------------
#
# Supported fields:
#   category    — folder name under standard_observer_data/ (required)
#   stem        — CSV filename without .csv (required)
#   columns     — column name tuple, e.g. ("wavelength", "l", "m", "s") (optional)
#                 Controls column names.
#   description — human-readable description (optional, falls back to filename pattern)
#   aliases     — list of category aliases (optional)
#   metadata    — dict of read_csv options (optional), e.g.:
#                 {"skiprows": 3, "header": 3}
#                 Supported keys: header, skiprows, usecols.
#                 "names" is ignored — use "columns" instead.
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
#      "metadata": {"header": 3}},

_CUSTOM_ENTRIES: list[dict[str, Any]] = [
    # Add your custom entries here
    {'category': 'test_data', 'stem': 'just_for_test_with_header',
     'columns': ('wavelength', 'l', 'm', 's'), # 这个字段覆盖率文件自带头
     "metadata": { "header": 'auto'} },
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

# Multiple aliases → canonical category name
_CATEGORY_ALIASES: dict[str, str] = {
    # cmfs
    "cmf": "cmfs",
    "cmfs": "cmfs",
    "xyz": "cmfs",
    # cone_fundamentals
    "cone": "cone_fundamentals",
    "cones": "cone_fundamentals",
    "cone_fundamentals": "cone_fundamentals",
    "lms": "cone_fundamentals",
    "fundamentals": "cone_fundamentals",
    # luminous_efficiency
    "luminous": "luminous_efficiency",
    "luminous_efficiency": "luminous_efficiency",
    "v_lambda": "luminous_efficiency",
    "vl": "luminous_efficiency",
    "efficiency": "luminous_efficiency",
    # prereceptoral_filters
    "filter": "prereceptoral_filters",
    "filters": "prereceptoral_filters",
    "prereceptoral": "prereceptoral_filters",
    "prereceptoral_filters": "prereceptoral_filters",
    "macular": "prereceptoral_filters",
    "lens": "prereceptoral_filters",
    # chromaticity_coordinates
    "chromaticity": "chromaticity_coordinates",
    "chromaticity_coordinates": "chromaticity_coordinates",
    "chroma": "chromaticity_coordinates",
    "chro": "chromaticity_coordinates",
    "xy": "chromaticity_coordinates",
    # photopigments
    "photopigment": "photopigments",
    "photopigments": "photopigments",
    "pigment": "photopigments",
    "pigments": "photopigments",
}


def _resolve_category(category: str) -> str:
    """Resolve a category alias to its canonical name."""
    cat = category.lower().strip()
    canonical = _CATEGORY_ALIASES.get(cat)
    if canonical is not None:
        return canonical
    # Zero-config: accept any folder that was auto-discovered
    candidate = _OBSERVER_ROOT / cat
    if candidate.is_dir():
        return cat
    raise KeyError(
        f"Unknown standard observer category: {category!r}. "
        f"Valid categories: {list(_CATEGORY_NAMES.keys())}"
    )


# ---------------------------------------------------------------------------
# Auto-discovery & registration
# ---------------------------------------------------------------------------

_OBSERVER_ROOT = data_dir("standard_observer_data")

# Built from _CUSTOM_ENTRIES at module load time
_CUSTOM_COL_OVERRIDES: dict[tuple[str, str], Tuple[str, ...]] = {}
_CUSTOM_META_OVERRIDES: dict[tuple[str, str], dict[str, Any]] = {}


def _process_custom_entries() -> None:
    """Inject custom entries into aliases, descriptions, and column overrides."""
    for entry in _CUSTOM_ENTRIES:
        cat = entry["category"]
        stem = entry["stem"]

        # Column override
        if "columns" in entry:
            _CUSTOM_COL_OVERRIDES[(cat, stem)] = tuple(entry["columns"])

        # Metadata override (header, skiprows, etc.)
        if "metadata" in entry:
            _CUSTOM_META_OVERRIDES[(cat, stem)] = entry["metadata"]

        # Description override
        if "description" in entry:
            _DESCRIPTION_OVERRIDES[f"{cat}/{stem}"] = entry["description"]

        # Category aliases — always register the canonical name itself
        _CATEGORY_ALIASES[cat.lower()] = cat
        for alias in entry.get("aliases", []):
            _CATEGORY_ALIASES[alias.lower()] = cat


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

            # Metadata: auto-detect header, merge custom overrides
            meta: dict[str, Any] = {"header": True}
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
                metadata=meta,
            ))


# Run discovery at import time
_scan_and_register()


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
