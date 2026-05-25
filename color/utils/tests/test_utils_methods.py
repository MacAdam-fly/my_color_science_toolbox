"""Tests for shared method utilities."""

from __future__ import annotations

import pytest

from color.utils.methods import (
    build_method_index,
    canonical_method_name,
    filter_kwargs,
    resolve_method,
)


def sample_method(a, b, scale=1):
    return scale * (a + b)


def other_method(a, b):
    return a - b


METHOD_ALIASES = {
    "CIE 2000": ("cie2000", "CIEDE2000"),
    "Oklab": ("OKLab", "OKLAB"),
}
METHODS = {
    "CIE 2000": sample_method,
    "Oklab": other_method,
}


def test_canonical_method_name():
    assert canonical_method_name("CIE 2000") == "cie2000"
    assert canonical_method_name("CAM16-UCS") == "cam16ucs"
    assert canonical_method_name("Jz Az Bz") == "jzazbz"
    assert canonical_method_name("0.1 nm") == "01nm"


def test_build_method_index():
    index = build_method_index(METHOD_ALIASES)

    assert index["cie2000"] == "CIE 2000"
    assert index["ciede2000"] == "CIE 2000"
    assert index["oklab"] == "Oklab"


def test_resolve_method_with_name_and_alias():
    index = build_method_index(METHOD_ALIASES)

    canonical, function = resolve_method("CIEDE2000", index, METHODS)
    assert canonical == "CIE 2000"
    assert function is sample_method

    canonical, function = resolve_method("OKLAB", index, METHODS)
    assert canonical == "Oklab"
    assert function is other_method


def test_resolve_method_unknown_raises():
    index = build_method_index(METHOD_ALIASES)

    with pytest.raises(ValueError, match="unknown method"):
        resolve_method("DIN99", index, METHODS)


def test_filter_kwargs():
    kwargs = filter_kwargs(sample_method, {"scale": 2, "unused": 10})

    assert kwargs == {"scale": 2}
