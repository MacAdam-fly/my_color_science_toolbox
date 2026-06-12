"""Low-level color-science toolkit.

The package root exposes a small lazy convenience facade for frequent
workflows. Complete APIs remain available from their dedicated submodules.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any


__version__ = "1.0.0"
__project_name__ = "color_science_toolbox"
__distribution_name__ = "color-science-toolbox"


_LAZY_EXPORTS: dict[str, str] = {
    # Spectral objects.
    "SpectralShape": "color.spectra",
    "SpectralDistribution": "color.spectra",
    "MultiSpectralDistribution": "color.spectra",
    "from_columns": "color.spectra",
    "from_D65_illuminant": "color.spectra",
    "from_cie1931_xyz_cmfs": "color.spectra",
    "from_cie1964_xyz_cmfs": "color.spectra",
    "from_cie2012_xyz_2degree_cmfs": "color.spectra",
    "from_cie2012_xyz_10degree_cmfs": "color.spectra",
    "from_cie2006_lms_2degree_fundamentals": "color.spectra",
    "from_cie2006_lms_10degree_fundamentals": "color.spectra",
    "from_iprgc_melanopic": "color.spectra",
    "from_alpha_opic_action_spectra": "color.spectra",
    # Colorimetry.
    "reflectance_to_XYZ": "color.colorimetry",
    "emission_to_XYZ": "color.colorimetry",
    "reflectance_to_LMS": "color.colorimetry",
    "emission_to_LMS": "color.colorimetry",
    "XYZ_to_xy": "color.colorimetry",
    "XYZ_to_xyY": "color.colorimetry",
    "xyY_to_XYZ": "color.colorimetry",
    "analyze_temperature": "color.colorimetry",
    "analyze_chromaticity": "color.colorimetry",
    # Spaces.
    "SpaceSpec": "color.spaces",
    "convert_color": "color.spaces",
    "RGB_to_XYZ": "color.spaces",
    "XYZ_to_RGB": "color.spaces",
    "sRGB_to_XYZ": "color.spaces",
    "XYZ_to_sRGB": "color.spaces",
    # Adaptation.
    "adapt_to_D65": "color.adaptation",
    "adapt_from_D65": "color.adaptation",
    # Appearance.
    "XYZ_to_CIECAM02": "color.appearance",
    "XYZ_to_CIECAM16": "color.appearance",
    # Difference.
    "delta_E_CIE2000": "color.difference",
    # Gamut.
    "DisplayPrimaries": "color.gamut",
    "compute_LCH_gamut_boundary": "color.gamut",
    "analyze_gamut": "color.gamut",
    # Device.
    "PrimaryResponseDisplay": "color.device",
    "melanopic_silent_range": "color.device",
}


__all__ = [
    "__version__",
    "__project_name__",
    "__distribution_name__",
    *_LAZY_EXPORTS,
]


def __getattr__(name: str) -> Any:
    """Lazily resolve selected root-level convenience API objects."""
    if name in _LAZY_EXPORTS:
        module = import_module(_LAZY_EXPORTS[name])
        value = getattr(module, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module 'color' has no attribute {name!r}")


def __dir__() -> list[str]:
    """Return public package attributes for interactive completion."""
    return sorted(__all__)
