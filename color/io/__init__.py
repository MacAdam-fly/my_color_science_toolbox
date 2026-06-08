"""Readers and writers for spectral objects, images, and figures."""

from __future__ import annotations

from .figure import save_figure
from .image import read_sRGB_image, write_sRGB_image
from .spectral import (
    read_spectral_csv,
    read_spectral_excel,
    read_spectral_json,
    spectral_from_dataframe,
    spectral_to_dataframe,
    write_spectral_csv,
    write_spectral_excel,
    write_spectral_json,
)

__all__ = [
    "save_figure",  # save a Matplotlib figure
]

__all__ += [
    "spectral_to_dataframe",  # convert spectral objects to pandas DataFrame
    "spectral_from_dataframe",  # build spectral objects from DataFrame columns
    "read_spectral_csv",  # read spectral objects from CSV tables
    "write_spectral_csv",  # write spectral objects to CSV tables
    "read_spectral_excel",  # read spectral objects from Excel sheets
    "write_spectral_excel",  # write spectral objects to Excel workbooks
    "read_spectral_json",  # read spectral objects from JSON files
    "write_spectral_json",  # write spectral objects to JSON files
]

__all__ += [
    "read_sRGB_image",  # read encoded sRGB image as float array in [0, 1]
    "write_sRGB_image",  # write encoded sRGB float array as 8-bit image
]
