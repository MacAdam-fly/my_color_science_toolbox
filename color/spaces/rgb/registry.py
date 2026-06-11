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
_STANDARD_NAMES = frozenset(_spaces)
_CUSTOM_NAMES: set[str] = set()

_ALIASES: dict[str, str] = {}
for _name, _space in _spaces.items():
    for _alias in (_space.name, *_space.aliases):
        _key = canonical_method_name(_alias)
        if _key in _ALIASES and _ALIASES[_key] != _name:
            raise ValueError(f"duplicate RGB colour-space alias {_alias!r}")
        _ALIASES[_key] = _name
_STANDARD_ALIAS_KEYS = frozenset(_ALIASES)


def _alias_keys(space: RGBColorSpace) -> tuple[str, ...]:
    keys = tuple(dict.fromkeys(canonical_method_name(alias) for alias in (space.name, *space.aliases)))
    if any(key == "" for key in keys):
        raise ValueError("RGB colour-space name and aliases must contain letters or digits")
    return keys


def get_RGB_colourspace(name: str | RGBColorSpace) -> RGBColorSpace:
    """Resolve an RGB colour space by name or alias.

    Passing an existing ``RGBColorSpace`` returns it unchanged. Custom RGB spaces
    are resolvable here only after explicit ``register_RGB_colourspace``.
    """
    if isinstance(name, RGBColorSpace):
        return name
    key = canonical_method_name(name)
    try:
        return RGB_COLORSPACES[_ALIASES[key]]
    except KeyError as exc:
        raise ValueError(f"unknown RGB colour space {name!r}") from exc


def list_RGB_colourspaces() -> tuple[str, ...]:
    """Return registered RGB colour-space names.

    The result includes built-in standards and any custom spaces registered in
    the current Python process.
    """
    return tuple(sorted(RGB_COLORSPACES))


def register_RGB_colourspace(space: RGBColorSpace, *, overwrite: bool = False) -> RGBColorSpace:
    """Register a custom RGB colour space.

    Standard RGB colour spaces cannot be overwritten. ``overwrite=True`` only
    replaces a previously registered custom colour space with the same name.
    """
    if not isinstance(space, RGBColorSpace):
        raise TypeError("space must be an RGBColorSpace")

    name = space.name
    keys = _alias_keys(space)
    name_key = canonical_method_name(name)
    if name in _STANDARD_NAMES or name_key in _STANDARD_ALIAS_KEYS:
        raise ValueError(f"cannot overwrite standard RGB colour space {name!r}")

    existing = _spaces.get(name)
    if existing is not None:
        if name not in _CUSTOM_NAMES:
            raise ValueError(f"cannot overwrite standard RGB colour space {name!r}")
        if not overwrite:
            raise ValueError(f"RGB colour space {name!r} is already registered")
        for key in _alias_keys(existing):
            if _ALIASES.get(key) == name:
                del _ALIASES[key]

    for key in keys:
        if key in _STANDARD_ALIAS_KEYS:
            raise ValueError(f"RGB colour-space alias {key!r} conflicts with a standard colour space")
        if key in _ALIASES and _ALIASES[key] != name:
            raise ValueError(f"RGB colour-space alias {key!r} is already registered")

    _spaces[name] = space
    _CUSTOM_NAMES.add(name)
    for key in keys:
        _ALIASES[key] = name
    return space


__all__ = [
    "RGB_COLORSPACES",
    "get_RGB_colourspace",
    "list_RGB_colourspaces",
    "register_RGB_colourspace",
]
