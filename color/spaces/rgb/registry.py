"""RGB colour-space registry."""

from __future__ import annotations

from types import MappingProxyType

from color.utils.names import canonical_method_name

from .colourspace import RGBColorSpace
from .display_standards import RGB_COLOURSPACE_DEFINITIONS


_spaces = {
    name: RGBColorSpace.from_definition(definition)
    for name, definition in RGB_COLOURSPACE_DEFINITIONS.items()
}
RGB_COLORSPACES = MappingProxyType(_spaces)

_ALIASES: dict[str, str] = {}
for _name, _space in RGB_COLORSPACES.items():
    for _alias in (_space.name, *_space.aliases):
        _key = canonical_method_name(_alias)
        if _key in _ALIASES and _ALIASES[_key] != _name:
            raise ValueError(f"duplicate RGB colour-space alias {_alias!r}")
        _ALIASES[_key] = _name


def get_RGB_colourspace(name: str | RGBColorSpace) -> RGBColorSpace:
    """Resolve an RGB colour space by name or alias."""
    if isinstance(name, RGBColorSpace):
        return name
    key = canonical_method_name(name)
    try:
        return RGB_COLORSPACES[_ALIASES[key]]
    except KeyError as exc:
        raise ValueError(f"unknown RGB colour space {name!r}") from exc


def list_RGB_colourspaces() -> tuple[str, ...]:
    """Return registered RGB colour-space names."""
    return tuple(sorted(RGB_COLORSPACES))


__all__ = [
    "RGB_COLORSPACES",
    "get_RGB_colourspace",
    "list_RGB_colourspaces",
]
