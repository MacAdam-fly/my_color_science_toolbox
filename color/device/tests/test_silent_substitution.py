"""Tests for XYZ/LMS-silent melanopic substitution."""

from __future__ import annotations

import numpy as np
import pytest

import color.device as device
import color.device.silent_substitution as silent_substitution_module
from color.colorimetry.integration import integrate_response_products
from color.device import PrimaryResponseDisplay, melanopic_silent_range
from color.device.silent_substitution import (
    SilentSubstitutionResult,
    _solve_silent_substitution_endpoint,
)
from color.spectra import MultiSpectralDistribution, SpectralDistribution


def _lms_display() -> PrimaryResponseDisplay:
    return PrimaryResponseDisplay(
        [
            [0.70, 0.30, 0.02, 0.10],
            [0.25, 0.80, 0.10, 0.20],
            [0.05, 0.15, 0.70, 0.65],
            [0.20, 0.55, 0.45, 0.95],
        ],
        response_names=("L", "M", "S", "mel"),
        primary_names=("R", "G", "B", "C"),
    )


def _lms_display_five() -> PrimaryResponseDisplay:
    return PrimaryResponseDisplay(
        [
            [0.70, 0.30, 0.02, 0.10],
            [0.25, 0.80, 0.10, 0.20],
            [0.05, 0.15, 0.70, 0.65],
            [0.20, 0.55, 0.45, 0.95],
            [0.40, 0.25, 0.35, 0.55],
        ],
        response_names=("L", "M", "S", "mel"),
        primary_names=("R", "G", "B", "C", "W"),
    )


def _xyz_display() -> PrimaryResponseDisplay:
    return PrimaryResponseDisplay(
        [
            [0.65, 0.31, 0.04, 0.10],
            [0.30, 0.72, 0.08, 0.20],
            [0.08, 0.12, 0.68, 0.65],
            [0.28, 0.50, 0.35, 0.95],
        ],
        response_names=("X", "Y", "Z", "mel"),
        primary_names=("R", "G", "B", "C"),
    )


def _full_display() -> PrimaryResponseDisplay:
    return PrimaryResponseDisplay(
        [
            [0.70, 0.30, 0.02, 0.65, 0.31, 0.04, 0.10],
            [0.25, 0.80, 0.10, 0.30, 0.72, 0.08, 0.20],
            [0.05, 0.15, 0.70, 0.08, 0.12, 0.68, 0.65],
            [0.20, 0.55, 0.45, 0.28, 0.50, 0.35, 0.95],
        ],
        response_names=("l", "m", "s", "x", "y", "z", "mel"),
        primary_names=("R", "G", "B", "C"),
    )


def test_device_top_level_api_is_contracted():
    assert device.__all__ == ["PrimaryResponseDisplay", "melanopic_silent_range"]
    assert not hasattr(device, "solve_silent_substitution")
    assert not hasattr(device, "SilentSubstitutionResult")
    assert SilentSubstitutionResult.__name__ == "SilentSubstitutionResult"

    namespace: dict[str, object] = {}
    with pytest.raises(ImportError):
        exec("from color.device import solve_silent_substitution", namespace)
    with pytest.raises(ImportError):
        exec("from color.device import SilentSubstitutionResult", namespace)


def test_primary_response_display_canonicalizes_response_names():
    display = _lms_display()

    assert display.response_names == ("l", "m", "s", "mel")
    assert display.primary_names == ("R", "G", "B", "C")
    assert display.primary_responses.flags.writeable is False


def test_primary_response_display_computes_lms_xyz_and_mel():
    display = _full_display()
    weights = np.array([0.35, 0.45, 0.30, 0.20])

    responses = display.responses_from_weights(weights)

    assert responses.shape == (7,)
    np.testing.assert_allclose(display.LMS_from_weights(weights), responses[:3])
    np.testing.assert_allclose(display.XYZ_from_weights(weights), responses[3:6])
    assert display.melanopic_from_weights(weights) == pytest.approx(responses[6])


def test_xyz_from_weights_requires_xyz_columns():
    display = _lms_display()

    with pytest.raises(ValueError, match="required responses"):
        display.XYZ_from_weights([0.1, 0.2, 0.3, 0.4])


def test_lms_from_weights_requires_lms_columns():
    display = _xyz_display()

    with pytest.raises(ValueError, match="required responses"):
        display.LMS_from_weights([0.1, 0.2, 0.3, 0.4])


@pytest.mark.parametrize(
    "kwargs",
    [
        {"primary_responses": [[1.0, 2.0, 3.0, np.nan]], "response_names": ("l", "m", "s", "mel")},
        {"primary_responses": [1.0, 2.0, 3.0, 4.0], "response_names": ("l", "m", "s", "mel")},
        {"primary_responses": [[1.0, 2.0, 3.0, 4.0]], "response_names": ("X", "x", "Y", "mel")},
        {"primary_responses": [[1.0, 2.0, 3.0]], "response_names": ("l", "m", "s")},
        {"primary_responses": [[1.0, 2.0, 3.0]], "response_names": ("l", "m", "mel")},
        {"primary_responses": [[1.0, 2.0, 3.0]], "response_names": ("x", "y", "mel")},
        {"primary_responses": [[1.0, 2.0, 3.0, 4.0]], "response_names": ("l", "m", "s", "rh")},
    ],
)
def test_invalid_display_inputs_raise_value_error(kwargs):
    with pytest.raises(ValueError):
        PrimaryResponseDisplay(**kwargs)


def test_melanopic_silent_range_returns_two_lms_feasible_endpoints():
    display = _lms_display()
    baseline = np.array([0.35, 0.45, 0.30, 0.20])
    target = display.LMS_from_weights(baseline)

    low, high = melanopic_silent_range(display, target, held="LMS")

    np.testing.assert_allclose(display.LMS_from_weights(low.weights), target, atol=1e-9)
    np.testing.assert_allclose(display.LMS_from_weights(high.weights), target, atol=1e-9)
    assert low.melanopic < high.melanopic
    assert low.held == "LMS"
    assert high.held == "LMS"


def test_four_primary_fast_path_matches_endpoint_lp_lms():
    display = _lms_display()
    baseline = np.array([0.35, 0.45, 0.30, 0.20])
    target = display.LMS_from_weights(baseline)

    low, high = melanopic_silent_range(display, target, held="LMS")
    low_lp = _solve_silent_substitution_endpoint(
        display,
        target,
        held_indices=display.lms_indices,
        objective="minimize_mel",
        held="LMS",
        bounds=(0.0, 1.0),
        tolerance=1e-9,
    )
    high_lp = _solve_silent_substitution_endpoint(
        display,
        target,
        held_indices=display.lms_indices,
        objective="maximize_mel",
        held="LMS",
        bounds=(0.0, 1.0),
        tolerance=1e-9,
    )

    np.testing.assert_allclose(low.melanopic, low_lp.melanopic, atol=1e-9)
    np.testing.assert_allclose(high.melanopic, high_lp.melanopic, atol=1e-9)
    np.testing.assert_allclose(low.weights, low_lp.weights, atol=1e-9)
    np.testing.assert_allclose(high.weights, high_lp.weights, atol=1e-9)


def test_melanopic_silent_range_returns_two_xyz_feasible_endpoints():
    display = _xyz_display()
    baseline = np.array([0.35, 0.45, 0.30, 0.20])
    target = display.XYZ_from_weights(baseline)

    low, high = melanopic_silent_range(display, target, held="XYZ")

    np.testing.assert_allclose(display.XYZ_from_weights(low.weights), target, atol=1e-9)
    np.testing.assert_allclose(display.XYZ_from_weights(high.weights), target, atol=1e-9)
    assert low.melanopic < high.melanopic
    assert low.held == "XYZ"
    assert high.held == "XYZ"


def test_four_primary_fast_path_matches_endpoint_lp_xyz():
    display = _xyz_display()
    baseline = np.array([0.35, 0.45, 0.30, 0.20])
    target = display.XYZ_from_weights(baseline)

    low, high = melanopic_silent_range(display, target, held="XYZ")
    low_lp = _solve_silent_substitution_endpoint(
        display,
        target,
        held_indices=display.xyz_indices,
        objective="minimize_mel",
        held="XYZ",
        bounds=(0.0, 1.0),
        tolerance=1e-9,
    )
    high_lp = _solve_silent_substitution_endpoint(
        display,
        target,
        held_indices=display.xyz_indices,
        objective="maximize_mel",
        held="XYZ",
        bounds=(0.0, 1.0),
        tolerance=1e-9,
    )

    np.testing.assert_allclose(low.melanopic, low_lp.melanopic, atol=1e-9)
    np.testing.assert_allclose(high.melanopic, high_lp.melanopic, atol=1e-9)


def test_batch_melanopic_silent_range_preserves_leading_shape():
    display = _lms_display()
    baselines = np.array([
        [0.35, 0.45, 0.30, 0.20],
        [0.25, 0.50, 0.25, 0.25],
    ])
    targets = display.LMS_from_weights(baselines)

    low, high = melanopic_silent_range(display, targets, held="LMS")

    assert low.weights.shape == (2, 4)
    assert high.responses.shape == (2, 4)
    assert low.melanopic.shape == (2,)
    assert low.residual.shape == (2, 3)
    np.testing.assert_allclose(display.LMS_from_weights(low.weights), targets, atol=1e-9)
    np.testing.assert_allclose(display.LMS_from_weights(high.weights), targets, atol=1e-9)
    assert np.all(low.melanopic < high.melanopic)


def test_four_primary_batch_fast_path_does_not_call_lp(monkeypatch):
    display = _lms_display()
    baselines = np.array([
        [0.35, 0.45, 0.30, 0.20],
        [0.25, 0.50, 0.25, 0.25],
        [0.45, 0.30, 0.20, 0.35],
    ])
    targets = display.LMS_from_weights(baselines)

    def fail_endpoint(*args, **kwargs):
        raise AssertionError("four-primary batch path should not call LP")

    monkeypatch.setattr(
        silent_substitution_module,
        "_solve_silent_substitution_endpoint",
        fail_endpoint,
    )

    low, high = melanopic_silent_range(display, targets, held="LMS")

    np.testing.assert_allclose(display.LMS_from_weights(low.weights), targets, atol=1e-9)
    np.testing.assert_allclose(display.LMS_from_weights(high.weights), targets, atol=1e-9)
    assert np.all(low.melanopic < high.melanopic)


def test_five_primary_display_uses_lp_path_and_returns_feasible_range():
    display = _lms_display_five()
    baseline = np.array([0.35, 0.45, 0.30, 0.20, 0.15])
    target = display.LMS_from_weights(baseline)

    low, high = melanopic_silent_range(display, target, held="LMS")

    assert low.success is True
    assert high.success is True
    np.testing.assert_allclose(display.LMS_from_weights(low.weights), target, atol=1e-9)
    np.testing.assert_allclose(display.LMS_from_weights(high.weights), target, atol=1e-9)
    assert low.melanopic <= high.melanopic
    assert np.all((low.weights >= 0.0) & (low.weights <= 1.0))
    assert np.all((high.weights >= 0.0) & (high.weights <= 1.0))


def test_display_missing_held_responses_raises_value_error():
    display = _lms_display()

    with pytest.raises(ValueError, match="required responses"):
        melanopic_silent_range(display, [0.2, 0.3, 0.1], held="XYZ")


def test_unknown_held_mode_raises_value_error():
    display = _lms_display()

    with pytest.raises(ValueError, match="held"):
        melanopic_silent_range(display, [0.2, 0.3, 0.1], held="uv")


def test_infeasible_batch_target_reports_flat_index():
    display = _lms_display()
    baseline = display.LMS_from_weights([0.35, 0.45, 0.30, 0.20])
    targets = np.vstack([baseline, [10.0, 10.0, 10.0]])

    with pytest.raises(ValueError, match="flat index 1"):
        melanopic_silent_range(display, targets, held="LMS")


def test_less_than_four_primaries_raises_value_error():
    display = PrimaryResponseDisplay(
        [
            [0.70, 0.30, 0.02, 0.10],
            [0.25, 0.80, 0.10, 0.20],
            [0.05, 0.15, 0.70, 0.65],
        ],
        response_names=("l", "m", "s", "mel"),
        primary_names=("R", "G", "B"),
    )

    with pytest.raises(ValueError, match="at least four primaries"):
        melanopic_silent_range(display, [0.2, 0.3, 0.1], held="LMS")


def _primary_spds() -> MultiSpectralDistribution:
    wavelengths = np.arange(380.0, 781.0, 5.0)
    values = np.column_stack(
        [
            np.exp(-0.5 * ((wavelengths - 630.0) / 25.0) ** 2),
            np.exp(-0.5 * ((wavelengths - 530.0) / 25.0) ** 2),
            np.exp(-0.5 * ((wavelengths - 450.0) / 20.0) ** 2),
            np.exp(-0.5 * ((wavelengths - 500.0) / 35.0) ** 2),
        ]
    )
    return MultiSpectralDistribution(
        wavelengths,
        values,
        labels=("R", "G", "B", "C"),
    )


def test_from_primary_spds_builds_full_response_matrix():
    display = PrimaryResponseDisplay.from_primary_spds(_primary_spds())

    assert display.primary_responses.shape == (4, 7)
    assert display.response_names == ("l", "m", "s", "x", "y", "z", "mel")
    assert display.primary_names == ("R", "G", "B", "C")
    assert "rh" not in display.response_names
    assert np.all(np.isfinite(display.primary_responses))


def test_from_primary_spds_matches_response_product_helper():
    wavelengths = np.array([400.0, 500.0, 600.0])
    fundamentals = MultiSpectralDistribution(
        wavelengths,
        np.identity(3),
        labels=("l", "m", "s"),
    )
    cmfs = MultiSpectralDistribution(
        wavelengths,
        np.identity(3),
        labels=("X", "Y", "Z"),
    )
    melanopic = SpectralDistribution(wavelengths, np.ones(3), name="mel")
    responses = MultiSpectralDistribution(
        wavelengths,
        np.column_stack([np.identity(3), np.identity(3), np.ones(3)]),
        labels=("l", "m", "s", "x", "y", "z", "mel"),
    )

    display = PrimaryResponseDisplay.from_primary_spds(
        _primary_spds(),
        fundamentals=fundamentals,
        cmfs=cmfs,
        melanopic=melanopic,
    )
    expected = integrate_response_products(_primary_spds(), responses)

    np.testing.assert_allclose(display.primary_responses, expected)


def test_from_primary_spds_lms_mel_builds_lms_mel_matrix():
    display = PrimaryResponseDisplay.from_primary_spds_lms_mel(_primary_spds())

    assert display.primary_responses.shape == (4, 4)
    assert display.response_names == ("l", "m", "s", "mel")


def test_from_primary_spds_xyz_mel_builds_xyz_mel_matrix():
    display = PrimaryResponseDisplay.from_primary_spds_xyz_mel(_primary_spds())

    assert display.primary_responses.shape == (4, 4)
    assert display.response_names == ("x", "y", "z", "mel")
