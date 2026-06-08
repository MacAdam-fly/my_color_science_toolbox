"""Spectral distribution file readers and writers."""

from __future__ import annotations

import json
from os import PathLike
from pathlib import Path
from typing import Any, Mapping, Sequence, Union

import numpy as np

from color.spectra import MultiSpectralDistribution, SpectralDistribution


SpectralObject = Union[SpectralDistribution, MultiSpectralDistribution]


def _path_or_file(path: str | PathLike[str] | Any) -> tuple[Path | None, Any]:
    if isinstance(path, (str, PathLike)):
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        return output, output
    return None, path


def _json_default(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"object of type {type(value).__name__!r} is not JSON serializable")


def _numeric_frame(frame: Any) -> Any:
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - depends on environment.
        raise ImportError("pandas is required for spectral table IO") from exc

    result = frame.copy()
    if result.empty:
        raise ValueError("spectral table is empty")
    for column in result.columns:
        result[column] = pd.to_numeric(result[column], errors="raise")
    if not np.all(np.isfinite(result.to_numpy(dtype=float))):
        raise ValueError("spectral table contains non-finite values")
    return result


def spectral_to_dataframe(spectral: SpectralObject):
    """Return a pandas DataFrame representation of a spectral object."""
    if not isinstance(spectral, (SpectralDistribution, MultiSpectralDistribution)):
        raise TypeError(
            "spectral must be a SpectralDistribution or MultiSpectralDistribution"
        )
    return spectral.to_pandas()


def spectral_from_dataframe(
    frame: Any,
    *,
    x: str = "wavelength",
    y: str | None = None,
    ys: Sequence[str] | None = None,
    name: str = "",
    metadata: Mapping[str, Any] | None = None,
    fill_nan: float | None = None,
) -> SpectralObject:
    """Build a spectral object from a column-oriented pandas DataFrame."""
    frame = _numeric_frame(frame)
    if x not in frame.columns:
        raise ValueError(f"missing wavelength column {x!r}")

    if y is not None and ys is not None:
        raise ValueError("provide either y or ys, not both")

    value_columns = [column for column in frame.columns if column != x]
    if y is not None:
        if y not in frame.columns:
            raise ValueError(f"missing value column {y!r}")
        return SpectralDistribution(
            frame[x].to_numpy(dtype=float),
            frame[y].to_numpy(dtype=float),
            name=name,
            metadata=metadata,
            fill_nan=fill_nan,
        )

    if ys is not None:
        labels = tuple(ys)
        missing = [label for label in labels if label not in frame.columns]
        if missing:
            raise ValueError(f"missing value columns: {missing}")
        return MultiSpectralDistribution(
            frame[x].to_numpy(dtype=float),
            frame.loc[:, list(labels)].to_numpy(dtype=float),
            labels,
            name=name,
            metadata=metadata,
            fill_nan=fill_nan,
        )

    if len(value_columns) == 1:
        column = value_columns[0]
        return SpectralDistribution(
            frame[x].to_numpy(dtype=float),
            frame[column].to_numpy(dtype=float),
            name=name,
            metadata=metadata,
            fill_nan=fill_nan,
        )
    if len(value_columns) > 1:
        labels = tuple(str(column) for column in value_columns)
        return MultiSpectralDistribution(
            frame[x].to_numpy(dtype=float),
            frame.loc[:, value_columns].to_numpy(dtype=float),
            labels,
            name=name,
            metadata=metadata,
            fill_nan=fill_nan,
        )
    raise ValueError("spectral table must contain at least one value column")


def read_spectral_csv(
    path: str | PathLike[str] | Any,
    *,
    x: str = "wavelength",
    y: str | None = None,
    ys: Sequence[str] | None = None,
    name: str = "",
    metadata: Mapping[str, Any] | None = None,
    fill_nan: float | None = None,
    **read_csv_kwargs: Any,
) -> SpectralObject:
    """Read a spectral distribution from a column-oriented CSV file."""
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - depends on environment.
        raise ImportError("pandas is required for read_spectral_csv()") from exc

    frame = pd.read_csv(path, **read_csv_kwargs)
    return spectral_from_dataframe(
        frame,
        x=x,
        y=y,
        ys=ys,
        name=name,
        metadata=metadata,
        fill_nan=fill_nan,
    )


def write_spectral_csv(
    path: str | PathLike[str] | Any,
    spectral: SpectralObject,
    *,
    index: bool = False,
    **to_csv_kwargs: Any,
) -> Path | Any:
    """Write a spectral distribution to a column-oriented CSV file."""
    output, target = _path_or_file(path)
    frame = spectral_to_dataframe(spectral)
    frame.to_csv(target, index=index, **to_csv_kwargs)
    return output if output is not None else path


def read_spectral_excel(
    path: str | PathLike[str] | Any,
    *,
    sheet_name: str | int = 0,
    x: str = "wavelength",
    y: str | None = None,
    ys: Sequence[str] | None = None,
    name: str = "",
    metadata: Mapping[str, Any] | None = None,
    fill_nan: float | None = None,
    **read_excel_kwargs: Any,
) -> SpectralObject:
    """Read a spectral distribution from one Excel worksheet."""
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - depends on environment.
        raise ImportError("pandas is required for read_spectral_excel()") from exc

    frame = pd.read_excel(path, sheet_name=sheet_name, **read_excel_kwargs)
    return spectral_from_dataframe(
        frame,
        x=x,
        y=y,
        ys=ys,
        name=name,
        metadata=metadata,
        fill_nan=fill_nan,
    )


def write_spectral_excel(
    path: str | PathLike[str] | Any,
    spectral: SpectralObject,
    *,
    sheet_name: str = "spectra",
    metadata_sheet: str | None = "metadata",
) -> Path | Any:
    """Write a spectral distribution to an Excel workbook."""
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - depends on environment.
        raise ImportError("pandas is required for write_spectral_excel()") from exc

    output, target = _path_or_file(path)
    frame = spectral_to_dataframe(spectral)
    with pd.ExcelWriter(target) as writer:
        frame.to_excel(writer, sheet_name=sheet_name, index=False)
        if metadata_sheet is not None:
            rows: list[dict[str, str]] = [
                {"key": "kind", "value": type(spectral).__name__},
                {"key": "name", "value": spectral.name},
            ]
            for key, value in spectral.metadata.items():
                rows.append(
                    {
                        "key": str(key),
                        "value": json.dumps(value, ensure_ascii=False, default=_json_default),
                    }
                )
            pd.DataFrame(rows).to_excel(writer, sheet_name=metadata_sheet, index=False)
    return output if output is not None else path


def write_spectral_json(
    path: str | PathLike[str] | Any,
    spectral: SpectralObject,
    *,
    indent: int | None = 2,
    ensure_ascii: bool = False,
) -> Path | Any:
    """Write a spectral distribution to a JSON object file."""
    if isinstance(spectral, SpectralDistribution):
        payload: dict[str, Any] = {
            "kind": "SpectralDistribution",
            "name": spectral.name,
            "metadata": dict(spectral.metadata),
            "wavelength": spectral.wavelengths,
            "value": spectral.values,
        }
    elif isinstance(spectral, MultiSpectralDistribution):
        payload = {
            "kind": "MultiSpectralDistribution",
            "name": spectral.name,
            "metadata": dict(spectral.metadata),
            "wavelength": spectral.wavelengths,
            "labels": spectral.labels,
            "values": spectral.values,
        }
    else:
        raise TypeError(
            "spectral must be a SpectralDistribution or MultiSpectralDistribution"
        )

    output, target = _path_or_file(path)
    if output is None:
        json.dump(
            payload,
            target,
            indent=indent,
            ensure_ascii=ensure_ascii,
            default=_json_default,
        )
        return path

    with open(target, "w", encoding="utf-8") as handle:
        json.dump(
            payload,
            handle,
            indent=indent,
            ensure_ascii=ensure_ascii,
            default=_json_default,
        )
    return output if output is not None else path


def read_spectral_json(
    path: str | PathLike[str] | Any,
    *,
    name: str | None = None,
    fill_nan: float | None = None,
) -> SpectralObject:
    """Read a spectral distribution from a JSON object file."""
    if isinstance(path, (str, PathLike)):
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    else:
        payload = json.load(path)

    if not isinstance(payload, dict):
        raise ValueError("spectral JSON must contain an object")
    if "wavelength" not in payload:
        raise ValueError("spectral JSON is missing 'wavelength'")

    object_name = payload.get("name", "") if name is None else name
    metadata = payload.get("metadata", {})
    kind = payload.get("kind", "")

    if "labels" in payload or kind == "MultiSpectralDistribution":
        if "labels" not in payload or "values" not in payload:
            raise ValueError("multi-channel spectral JSON needs 'labels' and 'values'")
        return MultiSpectralDistribution(
            payload["wavelength"],
            payload["values"],
            tuple(payload["labels"]),
            name=object_name,
            metadata=metadata,
            fill_nan=fill_nan,
        )

    if "value" not in payload:
        raise ValueError("single-channel spectral JSON is missing 'value'")
    return SpectralDistribution(
        payload["wavelength"],
        payload["value"],
        name=object_name,
        metadata=metadata,
        fill_nan=fill_nan,
    )


__all__ = [
    "SpectralObject",
    "spectral_to_dataframe",
    "spectral_from_dataframe",
    "read_spectral_csv",
    "write_spectral_csv",
    "read_spectral_excel",
    "write_spectral_excel",
    "read_spectral_json",
    "write_spectral_json",
]
