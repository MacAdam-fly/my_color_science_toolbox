"""Tests for individual cone fundamental generators."""

from __future__ import annotations

import numpy as np

from color.generators import (
    generate,
    generate_individual_cone_fundamental,
    generate_individual_cone_fundamentals,
    list_individual_cone_fundamental_generators,
)


def test_generate_individual_cone_fundamentals_entrypoint():
    raw = generate_individual_cone_fundamentals(observer_degree=2)
    assert set(raw) == {"wavelength", "l", "m", "s"}
    assert raw["wavelength"].flags.writeable is False
    np.testing.assert_allclose(
        [raw["l"].max(), raw["m"].max(), raw["s"].max()],
        [1.0, 1.0, 1.0],
    )


def test_registered_generator_paths_match():
    direct = generate_individual_cone_fundamental("stockman_rider_2023")
    registry = generate("individual_cone_fundamentals", "stockman rider 2023")
    np.testing.assert_allclose(direct["wavelength"], registry["wavelength"])
    np.testing.assert_allclose(direct["l"], registry["l"])
    assert "stockman_rider_2023" in list_individual_cone_fundamental_generators()
