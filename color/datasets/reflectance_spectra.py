"""Spectral reflectance datasets.

UEF reflectance spectra are stored as runtime CSV files in
``color/data/reflectance_spectra/uef_csv``.  The corresponding source
workbooks remain in ``uef_sources_data`` for audit and inspection.
"""

from __future__ import annotations

from typing import Any, List

from ._registry import DatasetEntry, SpectralDict, register
from ._utils import data_dir


_REFLECTANCE_DIR = str(data_dir("reflectance_spectra"))
_UEF_CSV_DIR = f"{_REFLECTANCE_DIR}/uef_csv"


_UEF_DATASETS = {
    "munsell_matt": {
        "description": "UEF Munsell matt spectral reflectance data",
        "sample_count": 1269,
        "wavelength_range_nm": (380, 800),
        "sampling_interval_nm": 1,
        "source_sheet": "reflectance_0_1",
        "notes": "Labels are Munsell notations parsed from the UEF README.",
    },
    "munsell_glossy_all": {
        "description": "UEF Munsell glossy spectral reflectance data, specular excluded",
        "sample_count": 1600,
        "wavelength_range_nm": (380, 780),
        "sampling_interval_nm": 1,
        "source_sheet": "reflectance_0_1",
        "notes": "Labels are parsed from UEF names.xls; .DX suffix removed.",
    },
    "agfa_it872": {
        "description": "UEF Agfa IT8.7/2 spectral reflectance patches",
        "sample_count": 288,
        "wavelength_range_nm": (400, 700),
        "sampling_interval_nm": 10,
        "source_sheet": "reflectance_0_1",
        "notes": "Minolta white calibration sample excluded from the runtime dataset.",
    },
    "paper_cardboardsce": {
        "description": "UEF cardboard paper spectral reflectance, SCE geometry",
        "sample_count": 140,
        "wavelength_range_nm": (400, 700),
        "sampling_interval_nm": 10,
        "source_sheet": "reflectance_0_1",
        "notes": "Percent reflectance source divided by 100.",
    },
    "paper_cardboardsci": {
        "description": "UEF cardboard paper spectral reflectance, SCI geometry",
        "sample_count": 210,
        "wavelength_range_nm": (400, 700),
        "sampling_interval_nm": 10,
        "source_sheet": "reflectance_0_1",
        "notes": "Percent reflectance source divided by 100.",
    },
    "paper_newsprintsce": {
        "description": "UEF newsprint spectral reflectance, SCE geometry",
        "sample_count": 36,
        "wavelength_range_nm": (400, 700),
        "sampling_interval_nm": 10,
        "source_sheet": "reflectance_0_1",
        "notes": "Percent reflectance source divided by 100.",
    },
    "paper_newsprintsci": {
        "description": "UEF newsprint spectral reflectance, SCI geometry",
        "sample_count": 54,
        "wavelength_range_nm": (400, 700),
        "sampling_interval_nm": 10,
        "source_sheet": "reflectance_0_1",
        "notes": "Percent reflectance source divided by 100.",
    },
    "paper_papersce": {
        "description": "UEF paper spectral reflectance, SCE geometry",
        "sample_count": 144,
        "wavelength_range_nm": (400, 700),
        "sampling_interval_nm": 10,
        "source_sheet": "reflectance_0_1",
        "notes": "Percent reflectance source divided by 100.",
    },
    "paper_papersci": {
        "description": "UEF paper spectral reflectance, SCI geometry",
        "sample_count": 216,
        "wavelength_range_nm": (400, 700),
        "sampling_interval_nm": 10,
        "source_sheet": "reflectance_0_1",
        "notes": "Percent reflectance source divided by 100.",
    },
    "forest_spruce": {
        "description": "UEF spruce forest spectral reflectance with reviewed scale correction",
        "sample_count": 349,
        "wavelength_range_nm": (390, 850),
        "sampling_interval_nm": 5,
        "source_sheet": "corrected_reflectance_0_1",
        "notes": "Runtime CSV uses corrected_reflectance_0_1; raw_relative remains in the audit workbook.",
        "corrections": {"spruce_0016": "scaled by 0.1"},
    },
    "forest_birch": {
        "description": "UEF birch forest spectral reflectance with reviewed scale correction",
        "sample_count": 337,
        "wavelength_range_nm": (390, 850),
        "sampling_interval_nm": 5,
        "source_sheet": "corrected_reflectance_0_1",
        "notes": "Runtime CSV uses corrected_reflectance_0_1; raw_relative remains in the audit workbook.",
        "corrections": {"birch_0262": "scaled by 1 / 1.4"},
    },
    "forest_pine": {
        "description": "UEF pine forest spectral reflectance with reviewed scale correction",
        "sample_count": 370,
        "wavelength_range_nm": (390, 850),
        "sampling_interval_nm": 5,
        "source_sheet": "corrected_reflectance_0_1",
        "notes": "Runtime CSV uses corrected_reflectance_0_1; raw_relative remains in the audit workbook.",
        "corrections": {"pine_0206": "scaled by 0.1"},
    },
}


for _name, _meta in _UEF_DATASETS.items():
    register(DatasetEntry(
        category="reflectance_spectra.uef",
        name=_name,
        description=_meta["description"],
        source="University of Eastern Finland (UEF) spectral databases",
        file_path=f"{_UEF_CSV_DIR}/{_name}.csv",
        read_options={"header": True, "coerce_numeric": True},
        metadata={
            "quantity": "spectral_reflectance",
            "source_collection": "UEF",
            "wavelength_unit": "nm",
            "value_unit": "reflectance_factor",
            "runtime_source": f"uef_csv/{_name}.csv",
            "audit_source": f"uef_sources_data/{_name}.xlsx",
            **{key: value for key, value in _meta.items() if key != "description"},
        },
    ))


def get_reflectance_spectrum(name: str, **kwargs: Any) -> SpectralDict:
    """Load a UEF spectral reflectance dataset.

    Parameters
    ----------
    name
        Registered UEF dataset name, for example ``"munsell_matt"`` or
        ``"agfa_it872"``.
    **kwargs
        Forwarded to the dataset registry.

    Returns
    -------
    dict[str, ndarray]
        Raw read-only mapping with ``"wavelength"`` and one column per
        reflectance sample.

    Notes
    -----
    Runtime data is read from audited CSV files in ``uef_csv``. Source
    workbooks are kept separately for inspection; Natural colors are not
    registered because the available AOTF values are not calibrated
    reflectance factors.
    """
    from ._registry import get

    return get("reflectance_spectra.uef", name, **kwargs)


def list_reflectance_spectra() -> List[str]:
    """List registered UEF spectral reflectance dataset names."""
    from ._registry import list_datasets

    return list_datasets("reflectance_spectra.uef")
