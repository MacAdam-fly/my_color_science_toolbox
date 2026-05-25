"""Tests for shared name canonicalisation utilities."""

from __future__ import annotations

from color.utils.names import (
    canonical_method_name,
    canonicalize_name,
    canonicalize_resource_name,
)


def test_canonicalize_name_removes_delimiters_and_case():
    assert canonicalize_name(" CIE 1931 XYZ 1 nm ") == "cie1931xyz1nm"
    assert canonicalize_name("cie_1931-xyz/1nm") == "cie1931xyz1nm"
    assert canonicalize_name("CAM16-UCS") == "cam16ucs"


def test_canonicalize_name_is_basic_and_drops_decimal_punctuation():
    assert canonicalize_name("0.1 nm") == "01nm"
    assert canonicalize_name("2.5-degree") == "25degree"


def test_canonical_method_name_is_semantic_alias_for_basic_names():
    assert canonical_method_name("CIE 2000") == "cie2000"
    assert canonical_method_name("0.1 nm") == "01nm"


def test_canonicalize_resource_name_preserves_resource_semantics():
    assert canonicalize_resource_name("0.1 nm") == "0p1nm"
    assert canonicalize_resource_name("2.5-degree") == "2p5degree"
    assert canonicalize_resource_name("V(\u03bb)") == "vlambda"
    assert canonicalize_resource_name("10\u00b0 observer") == "10degreeobserver"
