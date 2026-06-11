"""Colorimetric computations from spectral object wrappers."""

from __future__ import annotations

from .chromaticity import (
    XYZ_to_upvp1976,
    XYZ_to_uv1960,
    XYZ_to_xy,
    XYZ_to_xyY,
    upvp1976_to_xy,
    uv1960_to_xy,
    xyY_to_XYZ,
    xy_to_upvp1976,
    xy_to_uv1960,
)
from .cone_responses import (
    emission_to_LMS,
)
from .cone_responses import reflectance_to_LMS
from .dominant import (
    ChromaticityAnalysis,
    analyze_chromaticity,
    colorimetric_purity,
    complementary_wavelength,
    dominant_wavelength,
    excitation_purity,
    is_inside_chromaticity_locus,
    xy_from_dominant_wavelength_pc,
    xy_from_dominant_wavelength_pe,
)
from .lightness import Lstar_to_Y, Y_to_Lstar
from .photometry import (
    luminous_efficacy,
    luminous_efficiency,
    luminous_flux,
    photopic_luminous_efficacy,
    photopic_luminous_efficiency,
    photopic_luminous_efficiency_function,
    photopic_luminous_flux,
    scotopic_luminous_efficacy,
    scotopic_luminous_efficiency,
    scotopic_luminous_efficiency_function,
    scotopic_luminous_flux,
)
from .temperature import (
    CCT_Duv_to_xy,
    CCT_to_mired,
    CCT_to_uv,
    CCT_to_xy,
    CCT_to_xy_CIE_D,
    TemperatureAnalysis,
    analyze_temperature,
    mired_to_CCT,
    uv_to_CCT,
    xy_to_CCT,
    xy_to_CCT_Duv,
)
from .tristimulus import emission_to_XYZ, reflectance_to_XYZ
from .transformations import LMS_to_XYZ, XYZ_to_LMS

# Chromaticity conversions.
__all__ = [
    "XYZ_to_xyY",  # convert tristimulus values to xyY coordinates
    "xyY_to_XYZ",  # convert xyY coordinates to tristimulus values
    "XYZ_to_xy",  # convert tristimulus values to xy chromaticity coordinates
    "xy_to_uv1960",  # convert xy chromaticity coordinates to CIE 1960 uv
    "XYZ_to_uv1960",  # convert tristimulus values to CIE 1960 uv
    "uv1960_to_xy",  # convert CIE 1960 uv coordinates to xy
    "xy_to_upvp1976",  # convert xy chromaticity coordinates to CIE 1976 u'v'
    "XYZ_to_upvp1976",  # convert tristimulus values to CIE 1976 u'v'
    "upvp1976_to_xy",  # convert CIE 1976 u'v' coordinates to xy
]

# Correlated colour temperature conversions.
__all__ += [
    "CCT_to_mired",  # convert CCT in kelvins to mired
    "mired_to_CCT",  # convert mired to CCT in kelvins
    "TemperatureAnalysis",  # result object for full CCT and Duv analysis
    "analyze_temperature",  # full CCT and Duv analysis from xy coordinates

    "CCT_to_xy_CIE_D",  # compute CIE D-series daylight xy from CCT

    "xy_to_CCT",  # estimate CCT from xy using a named method
    "CCT_to_xy",  # compute xy from CCT using a named method

    "uv_to_CCT",  # compute CCT and Duv from uv using a named method
    "CCT_to_uv",  # compute uv from CCT and Duv using a named method
    "xy_to_CCT_Duv",  # compute CCT and Duv from xy using a named method
    "CCT_Duv_to_xy",  # compute xy from CCT and Duv using a named method
]

# CIE 1976 lightness conversions.
__all__ += [
    "Y_to_Lstar",  # convert relative luminance Y to CIE L*
    "Lstar_to_Y",  # convert CIE L* to relative luminance Y
]

# Direct colour-response transformations.
__all__ += [
    "LMS_to_XYZ",  # transform CIE 2006 LMS responses to XYZ
    "XYZ_to_LMS",  # transform XYZ values to CIE 2006 LMS responses
]

# Dominant wavelength and purity.
__all__ += [
    "ChromaticityAnalysis",  # result object for full chromaticity analysis
    "analyze_chromaticity",  # full analysis of chromaticity coordinates
    "is_inside_chromaticity_locus",  # check if coordinates are inside the chromaticity locus
    "dominant_wavelength",  # compute dominant wavelength and boundary coordinate
    "complementary_wavelength",  # compute complementary wavelength and boundary coordinate
    "excitation_purity",  # compute excitation purity in CIE xy
    "colorimetric_purity",  # compute colorimetric purity in CIE xy
    "xy_from_dominant_wavelength_pe",  # reconstruct xy from dominant wavelength and excitation purity
    "xy_from_dominant_wavelength_pc",  # reconstruct xy from dominant wavelength and colorimetric purity
]

# Spectral to colorimetric-response conversions.
__all__ += [
    "emission_to_XYZ",  # integrate self-luminous spectra to XYZ
    "reflectance_to_XYZ",  # integrate reflectance spectra under an illuminant to XYZ
    "emission_to_LMS",  # integrate self-luminous spectra to LMS
    "reflectance_to_LMS",  # integrate reflectance spectra under an illuminant to LMS
]

# Luminous efficiency functions.
__all__ += [
    "photopic_luminous_efficiency_function",  # load photopic luminous efficiency function
    "scotopic_luminous_efficiency_function",  # load scotopic luminous efficiency function
]

# Generic photometric quantities.
__all__ += [
    "luminous_flux",  # compute luminous flux from a spectrum and LEF
    "luminous_efficiency",  # compute normalized luminous efficiency
    "luminous_efficacy",  # compute luminous efficacy in lm/W
]

# Safe photopic and scotopic photometric wrappers.
__all__ += [
    "photopic_luminous_flux",  # compute photopic luminous flux
    "scotopic_luminous_flux",  # compute scotopic luminous flux
    "photopic_luminous_efficiency",  # compute photopic luminous efficiency
    "scotopic_luminous_efficiency",  # compute scotopic luminous efficiency
    "photopic_luminous_efficacy",  # compute photopic luminous efficacy
    "scotopic_luminous_efficacy",  # compute scotopic luminous efficacy
]
