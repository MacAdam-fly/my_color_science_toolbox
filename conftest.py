"""Pytest configuration for the project."""

from __future__ import annotations

from pathlib import Path
import tempfile

import matplotlib
from matplotlib.figure import Figure

matplotlib.use("Agg", force=True)


_ORIGINAL_SAVEFIG = Figure.savefig


def _savefig_with_file_object(self, fname, *args, **kwargs):
    if isinstance(fname, (str, Path)):
        path = Path(fname)
        path.parent.mkdir(parents=True, exist_ok=True)
        format_name = kwargs.pop("format", None) or path.suffix.lstrip(".") or None
        temporary_name = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                suffix=path.suffix,
                dir=path.parent,
                delete=False,
            ) as file:
                temporary_name = file.name
                result = _ORIGINAL_SAVEFIG(self, file, *args, format=format_name, **kwargs)
            Path(temporary_name).replace(path)
            return result
        finally:
            if temporary_name is not None:
                temporary_path = Path(temporary_name)
                if temporary_path.exists():
                    temporary_path.unlink()
    return _ORIGINAL_SAVEFIG(self, fname, *args, **kwargs)


Figure.savefig = _savefig_with_file_object
