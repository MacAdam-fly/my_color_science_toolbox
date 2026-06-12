"""Shared file-reading utilities for the datasets package.

All readers return a ``dict[str, np.ndarray]`` keyed by column name.
The first column is always ``'wavelength'`` unless overridden via *names*.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Union

import numpy as np


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def attest(condition: bool, message: str = "") -> None:
    """Like ``assert`` but cannot be disabled by ``python -O``."""
    if not condition:
        raise AssertionError(message)


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

_DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
"""Absolute path to the ``color/data/`` directory."""


def data_dir(*parts: str) -> Path:
    """Build a path relative to the data root."""
    return _DATA_ROOT.joinpath(*parts)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _import_pandas() -> Any:
    """Import pandas only when a dataset reader actually needs it."""
    import pandas as pd

    return pd


def _default_names(ncols: int) -> tuple[str, ...]:
    """Generate default column names for a given column count."""
    if ncols == 1:
        return ("wavelength",)
    if ncols == 2:
        return ("wavelength", "value")
    return ("wavelength",) + tuple(f"col{i}" for i in range(1, ncols))


def _auto_detect_header(df: Any) -> tuple[Any, bool]:
    """If the first row is all-numeric, treat it as data (assign default header).

    If the first row has text, use it as the column names and drop it from data.

    Returns
    -------
    tuple[DataFrame, bool]
        The processed DataFrame and ``True`` if a header row was detected.
    """
    first = df.iloc[0]
    for v in first:
        if isinstance(v, str):
            try:
                float(v)
            except ValueError:
                # Text found → use first row as header
                df.columns = [str(v).strip() if v is not None else "" for v in first]
                return df.iloc[1:].reset_index(drop=True), True
        elif not isinstance(v, (int, float, np.integer, np.floating)):
            return df, False
    # All numeric → first row is data, not a header
    df.columns = list(_default_names(len(df.columns)))
    return df, False


def _df_to_dict(
    df: Any,
    names: Optional[Sequence[str]] = None,
    usecols: Optional[Sequence[int]] = None,
    coerce_numeric: bool = False,
) -> Dict[str, np.ndarray]:
    """Convert a DataFrame to ``Dict[str, np.ndarray]``.

    Applies *names* override, *usecols* filtering, and default name fallback.
    If *coerce_numeric* is true, non-numeric cells are converted to NaN.
    """
    # usecols filtering (by index)
    if usecols is not None:
        cols = [df.columns[i] for i in usecols if i < len(df.columns)]
        df = df[cols]

    # names override
    if names is not None:
        df.columns = list(names)
    else:
        # Replace integer or NaN column names with defaults
        needs_default = any(
            isinstance(c, (int, np.integer)) or (isinstance(c, float) and np.isnan(c))
            for c in df.columns
        )
        if needs_default:
            df.columns = list(_default_names(len(df.columns)))

    # Convert to dict of numpy arrays
    result: Dict[str, np.ndarray] = {}
    pd = _import_pandas() if coerce_numeric else None
    for col in df.columns:
        series = df[col]
        if coerce_numeric:
            result[str(col)] = pd.to_numeric(series, errors="coerce").to_numpy(
                dtype=float,
                na_value=float("nan"),
            )
        else:
            result[str(col)] = series.to_numpy(dtype=float, na_value=float("nan"))
    return result


def _header_params(
    header: Union[bool, int, str],
    skiprows: int = 0,
) -> dict[str, Any]:
    """Translate our *header* parameter to pandas ``read_csv`` / ``read_excel`` kwargs.

    Parameters
    ----------
    header : bool, int, or ``"auto"``
        See ``read_csv`` / ``read_xlsx`` / ``read_xls`` for semantics.
    skiprows : int
        Additional rows to skip before reading.  Combined with *header*.

    Returns
    -------
    dict
        Kwargs to pass to the pandas reader.
    """
    if header is False:
        kw: dict[str, Any] = {"header": None}
        if skiprows:
            kw["skiprows"] = skiprows
        return kw
    if header is True or header == "auto":
        kw = {"header": 0}
        if skiprows:
            kw["skiprows"] = skiprows
        return kw
    if isinstance(header, int):
        # Skip that many rows, then use the next row as header.
        total_skip = header + skiprows
        return {"skiprows": total_skip, "header": 0}
    raise ValueError(f"header must be bool, int, or 'auto', got {header!r}")


# ---------------------------------------------------------------------------
# CSV reader
# ---------------------------------------------------------------------------

def read_csv(
    path: Union[str, Path],
    *,
    header: Union[bool, int, str] = False,
    skiprows: int = 0,
    usecols: Optional[Sequence[int]] = None,
    names: Optional[Sequence[str]] = None,
    coerce_numeric: bool = False,
) -> Dict[str, np.ndarray]:
    """Read a CSV file into a dict of numpy arrays.

    Parameters
    ----------
    path : path-like
        Absolute path to the CSV file.
    header : bool, int, or ``"auto"``
        ``False`` — no header (default).
        ``True`` / ``"auto"`` — auto-detect the first row as header.
        ``int`` — skip that many rows, then use the next row as header.
    skiprows : int
        Rows to skip before reading.  Only used when *header* is ``False``.
    usecols : sequence of int, optional
        Column indices to read.  ``None`` reads all columns.
    names : sequence of str, optional
        Column names.  Overrides header-detected names.
    coerce_numeric : bool
        If ``True``, convert non-numeric cells to NaN instead of raising.
    """
    pd = _import_pandas()

    if header is True or header == "auto":
        # Read without header to inspect first row
        df = pd.read_csv(str(path), header=None, skiprows=skiprows,
                         skipinitialspace=True)
        df, found_header = _auto_detect_header(df)
        # names (from DatasetEntry.columns) always overrides detected header
        return _df_to_dict(
            df, names=names, usecols=usecols, coerce_numeric=coerce_numeric
        )
    else:
        kwargs = _header_params(header, skiprows=skiprows)
        kwargs["skipinitialspace"] = True
        if names is not None:
            kwargs["names"] = names
        df = pd.read_csv(str(path), **kwargs)
    return _df_to_dict(df, names=names, usecols=usecols, coerce_numeric=coerce_numeric)


# ---------------------------------------------------------------------------
# XLSX reader
# ---------------------------------------------------------------------------

def read_xlsx(
    path: Union[str, Path],
    *,
    sheet: Union[int, str] = 0,
    header: Union[bool, int, str] = False,
    skiprows: int = 0,
    usecols: Optional[Sequence[int]] = None,
    names: Optional[Sequence[str]] = None,
    coerce_numeric: bool = False,
) -> Dict[str, np.ndarray]:
    """Read an XLSX file into a dict of numpy arrays.

    Parameters
    ----------
    path : path-like
        Absolute path to the ``.xlsx`` file.
    sheet : int or str
        Sheet index (0-based) or sheet name.
    header : bool, int, or ``"auto"``
        ``False`` — no header (default).
        ``True`` / ``"auto"`` — first row is header.
        ``int`` — skip that many rows, then use the next row as header.
    skiprows : int
        Rows to skip before reading.  Only used when *header* is ``False``.
    usecols : sequence of int, optional
        Column indices to read.  ``None`` reads all columns.
    names : sequence of str, optional
        Column names.  Overrides header-detected names.
    coerce_numeric : bool
        If ``True``, convert non-numeric cells to NaN instead of raising.
    """
    pd = _import_pandas()

    kwargs = _header_params(header, skiprows=skiprows)
    df = pd.read_excel(str(path), sheet_name=sheet, engine="openpyxl", **kwargs)
    return _df_to_dict(df, names=names, usecols=usecols, coerce_numeric=coerce_numeric)


# ---------------------------------------------------------------------------
# XLS reader
# ---------------------------------------------------------------------------

def read_xls(
    path: Union[str, Path],
    *,
    sheet: Union[int, str] = 0,
    header: Union[bool, int, str] = False,
    skiprows: int = 0,
    usecols: Optional[Sequence[int]] = None,
    names: Optional[Sequence[str]] = None,
    coerce_numeric: bool = False,
) -> Dict[str, np.ndarray]:
    """Read an XLS file into a dict of numpy arrays.

    Parameters
    ----------
    path : path-like
        Absolute path to the ``.xls`` file.
    sheet : int or str
        Sheet index (0-based) or sheet name.
    header : bool, int, or ``"auto"``
        ``False`` — no header (default).
        ``True`` / ``"auto"`` — first row is header.
        ``int`` — skip that many rows, then use the next row as header.
    skiprows : int
        Rows to skip before reading.  Only used when *header* is ``False``.
    usecols : sequence of int, optional
        Column indices to read.  ``None`` reads all columns.
    names : sequence of str, optional
        Column names.  Overrides header-detected names.
    coerce_numeric : bool
        If ``True``, convert non-numeric cells to NaN instead of raising.
    """
    pd = _import_pandas()

    kwargs = _header_params(header, skiprows=skiprows)
    df = pd.read_excel(str(path), sheet_name=sheet, engine="xlrd", **kwargs)
    return _df_to_dict(df, names=names, usecols=usecols, coerce_numeric=coerce_numeric)
