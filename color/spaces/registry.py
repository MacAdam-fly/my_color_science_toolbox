"""Colour-space conversion node registry."""

from __future__ import annotations

from types import MappingProxyType
from typing import Iterable, Mapping

import numpy as np

from color.utils.names import canonical_method_name

from .appearance import SPACE_NODES as APPEARANCE_SPACE_NODES
from .basic import SPACE_NODES as BASIC_SPACE_NODES
from .node import ColorSpaceNode


def _identity(value, **_kwargs) -> np.ndarray:
    """Return a numeric copy of *value*."""
    return np.array(value, dtype=np.float64, copy=True)


CORE_SPACE_NODES = (
    ColorSpaceNode(
        name="XYZ",
        aliases=("ciexyz", "cie xyz"),
        to_XYZ=_identity,
        from_XYZ=_identity,
        family="XYZ",
    ),
)


def _build_registry(
    node_groups: Iterable[Iterable[ColorSpaceNode]],
) -> tuple[dict[str, ColorSpaceNode], dict[str, str]]:
    """Build node and alias mappings from grouped node declarations."""
    nodes: dict[str, ColorSpaceNode] = {}
    aliases: dict[str, str] = {}

    for group in node_groups:
        for node in group:
            if node.name in nodes:
                raise ValueError(f"duplicate colour-space node {node.name!r}")
            nodes[node.name] = node

            for alias in (node.name, *node.aliases):
                key = canonical_method_name(alias)
                if key in aliases:
                    other = aliases[key]
                    if other == node.name:
                        continue
                    raise ValueError(
                        f"duplicate colour-space node alias {alias!r} "
                        f"for {node.name!r} and {other!r}"
                    )
                aliases[key] = node.name

    return nodes, aliases


_NODES, _ALIASES = _build_registry(
    (
        CORE_SPACE_NODES,
        BASIC_SPACE_NODES,
        APPEARANCE_SPACE_NODES,
    )
)

SPACE_REGISTRY: Mapping[str, ColorSpaceNode] = MappingProxyType(_NODES)


def get_colourspace_node(name: str | ColorSpaceNode) -> ColorSpaceNode:
    """Resolve a registered generic colour-space node by name or alias.

    RGB colour spaces are managed by the separate RGB registry and should be
    resolved with ``get_RGB_colourspace``. Passing an existing ``ColorSpaceNode``
    returns it unchanged.
    """
    if isinstance(name, ColorSpaceNode):
        return name
    if not isinstance(name, str):
        raise TypeError("colour-space node name must be a string or ColorSpaceNode")
    key = canonical_method_name(name)
    if key not in _ALIASES:
        raise ValueError(f"unknown colour-space node {name!r}")
    return SPACE_REGISTRY[_ALIASES[key]]


def list_colourspace_nodes() -> tuple[str, ...]:
    """Return registered generic colour-space node names.

    The result excludes RGB colour-space names; use ``list_RGB_colourspaces`` for
    the RGB registry.
    """
    return tuple(SPACE_REGISTRY)


__all__ = [
    "ColorSpaceNode",
    "SPACE_REGISTRY",
    "get_colourspace_node",
    "list_colourspace_nodes",
]
