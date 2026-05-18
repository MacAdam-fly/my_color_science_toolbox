"""Tests for color.generators._registry."""

from __future__ import annotations

import numpy as np
import pytest

from color.generators._registry import (
    GeneratorEntry,
    _CACHE,
    _REGISTRY,
    clear_cache,
    describe,
    generate,
    list_categories,
    list_generators,
    register,
)


def test_register_and_generate():
    def _gen(scale=1.0):
        return {"wavelength": np.array([400.0]), "value": np.array([scale])}

    register(GeneratorEntry(
        category="test_generators",
        name="constant",
        description="constant",
        generate_fn=_gen,
        parameters=("scale",),
    ))

    data = generate("test_generators", "constant", scale=2.0)
    np.testing.assert_array_equal(data["value"], [2.0])


def test_generate_with_canonical_names():
    def _gen():
        return {"wavelength": np.array([400.0]), "value": np.array([1.0])}

    register(GeneratorEntry(
        category="canonical_generators",
        name="my_generator",
        description="",
        generate_fn=_gen,
    ))

    data = generate("Canonical Generators", "My Generator")
    np.testing.assert_array_equal(data["value"], [1.0])


def test_generated_result_is_readonly_copy():
    calls = 0

    def _gen():
        nonlocal calls
        calls += 1
        return {"wavelength": np.array([400.0]), "value": np.array([1.0])}

    register(GeneratorEntry(
        category="readonly_generators",
        name="one",
        description="",
        generate_fn=_gen,
    ))

    first = generate("readonly_generators", "one")
    with pytest.raises(ValueError):
        first["value"][0] = 2.0

    second = generate("readonly_generators", "one")
    assert calls == 1
    assert first is not second
    assert second["value"].flags.writeable is False
    np.testing.assert_array_equal(second["value"], [1.0])


def test_cache_key_includes_parameters():
    calls = 0

    def _gen(scale=1.0):
        nonlocal calls
        calls += 1
        return {"wavelength": np.array([400.0]), "value": np.array([scale])}

    register(GeneratorEntry(
        category="cache_generators",
        name="scale",
        description="",
        generate_fn=_gen,
    ))

    generate("cache_generators", "scale", scale=1.0)
    generate("cache_generators", "scale", scale=1.0)
    generate("cache_generators", "scale", scale=2.0)
    assert calls == 2


def test_describe_and_list():
    entry = describe("illuminants", "blackbody")
    assert entry.name == "blackbody"
    assert "illuminants" in list_categories()
    assert "blackbody" in list_generators("illuminants")


def test_missing_generator_raises():
    with pytest.raises(KeyError, match="No generator"):
        generate("missing", "missing")


def test_clear_cache():
    _CACHE.clear()

    def _gen():
        return {"wavelength": np.array([400.0]), "value": np.array([1.0])}

    register(GeneratorEntry(
        category="clear_generators",
        name="one",
        description="",
        generate_fn=_gen,
    ))
    generate("clear_generators", "one")
    assert clear_cache("clear_generators", "one") == 1
    assert all(key[0] != "clear_generators" for key in _CACHE)


def test_register_rejects_canonical_collision():
    register(GeneratorEntry(
        category="generator_collision",
        name="my-generator",
        description="",
        generate_fn=lambda: {"value": np.array([1.0])},
    ))
    with pytest.raises(ValueError, match="Canonical generator name collision"):
        register(GeneratorEntry(
            category="generator_collision",
            name="my generator",
            description="",
            generate_fn=lambda: {"value": np.array([1.0])},
        ))


def test_registry_contains_expected_builtin():
    assert ("illuminants", "blackbody") in _REGISTRY
