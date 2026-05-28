"""Tests for Stockman/Rider individual cone fundamentals."""

from __future__ import annotations

import numpy as np
import pytest

from color.datasets.standard_observers import (
    get_cie2006_lms_2degree_fundamentals,
    get_cie2006_lms_10degree_fundamentals,
)
from color.individual_cone_fundamentals import (
    cone_absorbance_spectra,
    generate_individual_cone_fundamentals,
    lens_density_spectrum,
    macular_density_spectrum,
)


def _stack(raw):
    return np.column_stack((raw["l"], raw["m"], raw["s"]))


def test_macular_and_lens_templates_are_standard_scaled():
    macular = macular_density_spectrum(np.array([460.0]))
    lens = lens_density_spectrum(np.array([400.0]))
    np.testing.assert_allclose(macular["optical_density"], [0.350], atol=5e-5)
    np.testing.assert_allclose(lens["optical_density"], [1.7649], atol=5e-5)


def test_cone_absorbance_templates_peak_at_one():
    raw = cone_absorbance_spectra()
    values = _stack(raw)
    np.testing.assert_allclose(values.max(axis=0), [1.0, 1.0, 1.0], atol=1e-12)
    assert set(raw) == {"wavelength", "l", "m", "s"}


def test_generate_standard_observers_shape_and_normalisation():
    for observer_degree in (2, 10):
        raw = generate_individual_cone_fundamentals(observer_degree=observer_degree)
        values = _stack(raw)
        assert raw["wavelength"].shape == (491,)
        assert values.shape == (491, 3)
        assert np.isfinite(values).all()
        np.testing.assert_allclose(values.max(axis=0), [1.0, 1.0, 1.0])


def test_generated_2degree_matches_cie2006_linear_energy():
    generated = generate_individual_cone_fundamentals(observer_degree=2)
    reference = get_cie2006_lms_2degree_fundamentals(interval_nm=1, energy="linE")
    mask = (generated["wavelength"] >= 400) & (generated["wavelength"] <= 830)
    values = _stack({key: value[mask] for key, value in generated.items()})
    ref_mask = (reference["wavelength"] >= 400) & (reference["wavelength"] <= 830)
    ref_values = _stack({key: value[ref_mask] for key, value in reference.items()})
    finite = np.isfinite(ref_values)
    np.testing.assert_allclose(values[finite], ref_values[finite], atol=2.0e-2)
    assert np.mean(np.abs(values[finite] - ref_values[finite])) < 2.5e-3


def test_generated_10degree_matches_cie2006_linear_energy():
    generated = generate_individual_cone_fundamentals(observer_degree=10)
    reference = get_cie2006_lms_10degree_fundamentals(interval_nm=1, energy="linE")
    mask = (generated["wavelength"] >= 400) & (generated["wavelength"] <= 830)
    values = _stack({key: value[mask] for key, value in generated.items()})
    ref_mask = (reference["wavelength"] >= 400) & (reference["wavelength"] <= 830)
    ref_values = _stack({key: value[ref_mask] for key, value in reference.items()})
    finite = np.isfinite(ref_values)
    np.testing.assert_allclose(values[finite], ref_values[finite], atol=2.0e-2)
    assert np.mean(np.abs(values[finite] - ref_values[finite])) < 2.5e-3


def test_individual_parameters_change_result():
    standard = generate_individual_cone_fundamentals()
    shifted = generate_individual_cone_fundamentals(
        l_shift_nm=2.0,
        m_shift_nm=-1.0,
        photopigment_od=(0.45, 0.52, 0.38),
        macular_density_460=0.5,
        lens_density_400=1.5,
    )
    assert not np.allclose(_stack(standard), _stack(shifted))


def test_l_template_options_are_available():
    ser = generate_individual_cone_fundamentals(l_template="ser180")
    ala = generate_individual_cone_fundamentals(l_template="ala180")
    mean = generate_individual_cone_fundamentals(l_template="mean")
    assert not np.allclose(ser["l"], ala["l"])
    assert not np.allclose(mean["l"], ser["l"])


@pytest.mark.parametrize(
    "kwargs, match",
    [
        ({"observer_degree": 5}, "observer_degree"),
        ({"photopigment_od": (0.5, 0.5)}, "photopigment_od"),
        ({"photopigment_od": (0.5, -0.1, 0.4)}, "photopigment_od"),
        ({"macular_density_460": -0.1}, "macular_density_460"),
        ({"lens_density_400": -0.1}, "lens_density_400"),
        ({"l_template": "unknown"}, "l_template"),
        ({"wavelength_nm": [500, 400]}, "strictly increasing"),
        ({"wavelength_nm": [350, 400]}, "360-850"),
    ],
)
def test_invalid_inputs_raise(kwargs, match):
    with pytest.raises(ValueError, match=match):
        generate_individual_cone_fundamentals(**kwargs)
