"""Tests for generic colour-space registry."""

from __future__ import annotations

import pytest

from color.spaces import (
    ColorSpaceNode,
    SPACE_REGISTRY,
    get_colourspace_node,
    list_colourspace_nodes,
)
from color.spaces.xyy import SPACE_NODES as XYY_SPACE_NODES


def test_registry_resolves_xyz_and_xyy():
    assert get_colourspace_node("XYZ").name == "XYZ"
    assert get_colourspace_node("xyY").name == "xyY"
    assert get_colourspace_node("Lab").name == "Lab"
    assert get_colourspace_node("LCHab").parent == "Lab"
    assert get_colourspace_node("Luv").name == "Luv"
    assert get_colourspace_node("LCHuv").parent == "Luv"
    assert get_colourspace_node("Oklab").name == "Oklab"
    assert get_colourspace_node("Oklch").parent == "Oklab"
    assert get_colourspace_node("CAM02-UCS").name == "CAM02-UCS"
    assert get_colourspace_node("CAM02-LCD").name == "CAM02-LCD"
    assert get_colourspace_node("CAM02-SCD").name == "CAM02-SCD"


def test_xyy_declares_its_own_space_node():
    assert len(XYY_SPACE_NODES) == 1
    assert XYY_SPACE_NODES[0].name == "xyY"
    assert SPACE_REGISTRY["xyY"] is XYY_SPACE_NODES[0]


def test_registry_resolves_aliases_case_insensitively():
    assert get_colourspace_node("xyy").name == "xyY"
    assert get_colourspace_node("CIE xyY").name == "xyY"
    assert get_colourspace_node("cie xyz").name == "XYZ"
    assert get_colourspace_node("CAM02UCS").name == "CAM02-UCS"
    assert get_colourspace_node("CAM02 LCD").name == "CAM02-LCD"


def test_list_colourspace_nodes():
    names = list_colourspace_nodes()

    assert "XYZ" in names
    assert "xyY" in names
    assert "Lab" in names
    assert "LCHab" in names
    assert "Luv" in names
    assert "LCHuv" in names
    assert "Oklab" in names
    assert "Oklch" in names
    assert "CAM02-UCS" in names
    assert "CAM02-LCD" in names
    assert "CAM02-SCD" in names


def test_registry_is_read_only_mapping():
    with pytest.raises(TypeError):
        SPACE_REGISTRY["custom"] = get_colourspace_node("XYZ")  # type: ignore[index]


def test_get_colourspace_node_accepts_node_instance():
    node = get_colourspace_node("XYZ")

    assert isinstance(node, ColorSpaceNode)
    assert get_colourspace_node(node) is node


def test_unknown_node_raises():
    with pytest.raises(ValueError, match="unknown colour-space node"):
        get_colourspace_node("unknown")
