"""Tests for Academy Spectral Similarity Index."""

from __future__ import annotations

import numpy as np
import pytest

from color.generators.blackbody import blackbody_spd
from color.generators.ideal import gaussian_spd
from color.quality import SPECTRAL_SHAPE_SSI, spectral_similarity_index
from color.spectra import SpectralDistribution, from_D65_illuminant, from_columns


def _to_colour_sd(sd: SpectralDistribution):
    from colour.colorimetry import SpectralDistribution as ColourSpectralDistribution

    return ColourSpectralDistribution(dict(zip(sd.wavelengths, sd.values)))


def test_spectral_shape_ssi() -> None:
    assert SPECTRAL_SHAPE_SSI.start == 375.0
    assert SPECTRAL_SHAPE_SSI.end == 675.0
    assert SPECTRAL_SHAPE_SSI.interval == 1.0
    assert len(SPECTRAL_SHAPE_SSI) == 301


def test_d65_against_itself_is_100() -> None:
    d65 = from_D65_illuminant()
    assert spectral_similarity_index(d65, d65) == 100
    assert spectral_similarity_index(d65, d65, round_result=False) == pytest.approx(100.0)


def test_round_result_controls_rounding() -> None:
    d65 = from_D65_illuminant()
    gaussian = from_columns(
        gaussian_spd(peak_wavelength=555, width=45, method="fwhm"),
        y="spd",
    )

    rounded = spectral_similarity_index(gaussian, d65)
    unrounded = spectral_similarity_index(gaussian, d65, round_result=False)

    assert rounded == np.around(unrounded)
    assert rounded != unrounded


@pytest.mark.parametrize(
    "test_sd",
    [
        from_columns(
            blackbody_spd(temperature=2856),
            y="radiance",
            name="Blackbody 2856 K",
        ),
        from_columns(
            blackbody_spd(temperature=6500),
            y="radiance",
            name="Blackbody 6500 K",
        ),
        from_columns(
            gaussian_spd(peak_wavelength=555, width=45, method="fwhm"),
            y="spd",
            name="Gaussian 555 nm",
        ),
    ],
)
def test_matches_colour_reference(test_sd: SpectralDistribution) -> None:
    from colour.quality import spectral_similarity_index as colour_ssi

    reference = from_D65_illuminant()

    expected = colour_ssi(_to_colour_sd(test_sd), _to_colour_sd(reference))
    result = spectral_similarity_index(test_sd, reference)
    assert result == pytest.approx(expected)

    expected_float = colour_ssi(
        _to_colour_sd(test_sd),
        _to_colour_sd(reference),
        round_result=False,
    )
    result_float = spectral_similarity_index(test_sd, reference, round_result=False)
    assert result_float == pytest.approx(expected_float)


def test_rejects_non_spectral_distribution() -> None:
    d65 = from_D65_illuminant()
    with pytest.raises(TypeError):
        spectral_similarity_index({"wavelength": [400, 500]}, d65)  # type: ignore[arg-type]


def test_rejects_non_finite_values() -> None:
    bad = SpectralDistribution([400, 500], [1.0, np.inf])
    d65 = from_D65_illuminant()
    with pytest.raises(ValueError, match="values must be finite"):
        spectral_similarity_index(bad, d65)
