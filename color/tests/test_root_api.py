"""Tests for the root package lazy convenience API."""

from __future__ import annotations

import importlib
import sys

import pytest


EXPECTED_LAZY_EXPORTS = {
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
    "reflectance_to_XYZ": "color.colorimetry",
    "emission_to_XYZ": "color.colorimetry",
    "reflectance_to_LMS": "color.colorimetry",
    "emission_to_LMS": "color.colorimetry",
    "XYZ_to_xy": "color.colorimetry",
    "XYZ_to_xyY": "color.colorimetry",
    "xyY_to_XYZ": "color.colorimetry",
    "analyze_temperature": "color.colorimetry",
    "analyze_chromaticity": "color.colorimetry",
    "SpaceSpec": "color.spaces",
    "convert_color": "color.spaces",
    "RGB_to_XYZ": "color.spaces",
    "XYZ_to_RGB": "color.spaces",
    "sRGB_to_XYZ": "color.spaces",
    "XYZ_to_sRGB": "color.spaces",
    "adapt_to_D65": "color.adaptation",
    "adapt_from_D65": "color.adaptation",
    "XYZ_to_CIECAM02": "color.appearance",
    "XYZ_to_CIECAM16": "color.appearance",
    "delta_E_CIE2000": "color.difference",
    "DisplayPrimaries": "color.gamut",
    "compute_LCH_gamut_boundary": "color.gamut",
    "analyze_gamut": "color.gamut",
    "PrimaryResponseDisplay": "color.device",
    "melanopic_silent_range": "color.device",
}


def _fresh_color_module():
    """Import a fresh root package module without loaded submodule attributes."""
    for name in tuple(sys.modules):
        if name == "color" or name.startswith("color."):
            del sys.modules[name]
    return importlib.import_module("color")


def test_root_package_metadata_and_public_names():
    import color

    assert color.__version__ == "1.0.0"
    assert color.__project_name__ == "color_science_toolbox"
    assert color.__distribution_name__ == "color-science-toolbox"
    assert set(color.__all__) == {
        "__version__",
        "__project_name__",
        "__distribution_name__",
        *EXPECTED_LAZY_EXPORTS,
    }
    assert dir(color) == sorted(color.__all__)


def test_import_color_is_lightweight_until_lazy_access():
    color = _fresh_color_module()

    assert "color.spectra" not in sys.modules
    assert "color.colorimetry" not in sys.modules
    assert "color.spaces" not in sys.modules
    assert "color.device" not in sys.modules

    _ = color.convert_color

    assert "color.spaces" in sys.modules
    assert "color.device" not in sys.modules


@pytest.mark.parametrize("name,module_name", sorted(EXPECTED_LAZY_EXPORTS.items()))
def test_lazy_export_matches_submodule_object(name: str, module_name: str):
    import color

    value = getattr(color, name)
    module = importlib.import_module(module_name)

    assert value is getattr(module, name)


def test_from_color_import_common_api():
    from color import (
        convert_color,
        from_cie1931_xyz_cmfs,
        melanopic_silent_range,
        reflectance_to_XYZ,
    )
    from color.colorimetry import reflectance_to_XYZ as module_reflectance_to_XYZ
    from color.device import melanopic_silent_range as module_melanopic_silent_range
    from color.spectra import from_cie1931_xyz_cmfs as module_from_cie1931_xyz_cmfs
    from color.spaces import convert_color as module_convert_color

    assert convert_color is module_convert_color
    assert from_cie1931_xyz_cmfs is module_from_cie1931_xyz_cmfs
    assert reflectance_to_XYZ is module_reflectance_to_XYZ
    assert melanopic_silent_range is module_melanopic_silent_range


def test_unknown_root_attribute_raises_attribute_error():
    import color

    with pytest.raises(AttributeError, match="does_not_exist"):
        getattr(color, "does_not_exist")
