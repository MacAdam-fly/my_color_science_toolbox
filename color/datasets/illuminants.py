"""Static standard illuminant spectral power distributions.

Provides file-based access to CIE A, D65, and fluorescent F1-F12 data.
Formula-generated source models live in :mod:`color.generators.blackbody`
and :mod:`color.generators.illuminants`.
"""

from __future__ import annotations

from typing import Any, List

from ._registry import DatasetEntry, SpectralDict, register
from ._utils import data_dir


_ILLUM_DIR = str(data_dir("illuminants"))


register(DatasetEntry(
    category="illuminants",
    name="A",
    description="CIE Illuminant A, typical incandescent/tungsten light",
    source="CVRL / CIE 15:2004",
    file_path=f"{_ILLUM_DIR}/illuminant_A.csv",
    columns=("wavelength", "spd"),
    metadata={
        "quantity": "relative_spd",
        "wavelength_unit": "nm",
    },
))

register(DatasetEntry(
    category="illuminants",
    name="D65",
    description="CIE Illuminant D65, average daylight",
    source="CVRL / CIE 15:2004",
    file_path=f"{_ILLUM_DIR}/illuminant_D65.csv",
    columns=("wavelength", "spd"),
    metadata={
        "quantity": "relative_spd",
        "wavelength_unit": "nm",
    },
))

register(DatasetEntry(
    category="illuminants",
    name="fluorescents",
    description="CIE F1-F12 fluorescent lamp spectral power distributions",
    source="RIT Munsell Color Science Lab",
    file_path=f"{_ILLUM_DIR}/Fluorescents.xls",
    columns=(
        "wavelength",
        "F1",
        "F2",
        "F3",
        "F4",
        "F5",
        "F6",
        "F7",
        "F8",
        "F9",
        "F10",
        "F11",
        "F12",
    ),
    read_options={"header": 1},
    metadata={
        "quantity": "relative_spd",
        "wavelength_unit": "nm",
    },
))


def get_illuminant(name: str, **kwargs: Any) -> SpectralDict:
    """Load a static illuminant spectral distribution."""
    from ._registry import get

    return get("illuminants", name, **kwargs)


def list_illuminants() -> List[str]:
    """List all registered static illuminant names."""
    from ._registry import list_datasets

    return list_datasets("illuminants")
