"""Generic colour-space conversion entry points."""

from __future__ import annotations

import inspect
from collections.abc import Mapping

import numpy as np

from .registry import ColorSpaceNode, get_colourspace_node
from .rgb import (
    RGBColorSpace,
    RGB_to_RGB,
    RGB_to_XYZ,
    XYZ_to_RGB,
    get_RGB_colourspace,
)
from .spec import SpaceSpec, as_space_spec


def _call_conversion(function, value, options: dict[str, object]) -> np.ndarray:
    """Call *function* with the supported subset of *options*."""
    signature = inspect.signature(function)
    accepts_var_kwargs = any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in signature.parameters.values()
    )
    if accepts_var_kwargs:
        return function(value, **options)

    supported = {
        key: option
        for key, option in options.items()
        if key in signature.parameters
    }
    unused = set(options) - set(supported)
    if unused:
        names = ", ".join(sorted(unused))
        raise ValueError(f"unsupported conversion option(s): {names}")
    return function(value, **supported)


def _try_get_RGB_colourspace(value: str | ColorSpaceNode | RGBColorSpace) -> RGBColorSpace | None:
    """Resolve *value* as an RGB colour space when possible."""
    if isinstance(value, ColorSpaceNode):
        return None
    try:
        return get_RGB_colourspace(value)
    except ValueError:
        return None


def _get_generic_node(value: str | ColorSpaceNode) -> ColorSpaceNode:
    """Resolve *value* as a generic colour-space node."""
    return get_colourspace_node(value)


def _pop_rgb_option(
    options: dict[str, object],
    name: str,
    default: bool,
) -> bool:
    """Pop a boolean RGB transfer option from *options*."""
    value = options.pop(name, default)
    return bool(value)


def _reject_chromatic_adaptation(options: Mapping[str, object], *, source: str) -> None:
    """Reject hidden chromatic adaptation options in *options*."""
    if "chromatic_adaptation" in options:
        raise ValueError(
            "convert_color(...) does not support chromatic_adaptation; "
            f"remove it from {source} and use RGB_to_RGB(...) or color.adaptation explicitly"
        )


def _merge_options(
    common_options: Mapping[str, object],
    endpoint_spec: SpaceSpec,
) -> dict[str, object]:
    """Merge common conversion options with endpoint-specific parameters."""
    options = dict(common_options)
    options.update(endpoint_spec.parameters)
    return options


def _rgb_source_options(
    common_options: dict[str, object],
    endpoint_spec: SpaceSpec,
) -> dict[str, object]:
    """Return source RGB options without leaking target-only options."""
    options = dict(endpoint_spec.parameters)
    if "apply_decoding" in common_options:
        options.setdefault("apply_decoding", common_options.pop("apply_decoding"))
    return options


def _rgb_target_options(
    common_options: dict[str, object],
    endpoint_spec: SpaceSpec,
) -> dict[str, object]:
    """Return target RGB options without leaking source-only options."""
    options = dict(endpoint_spec.parameters)
    if "apply_encoding" in common_options:
        options.setdefault("apply_encoding", common_options.pop("apply_encoding"))
    return options


def _require_no_options(options: Mapping[str, object]) -> None:
    """Raise if *options* still contains unsupported conversion options."""
    if options:
        names = ", ".join(sorted(options))
        raise ValueError(f"unsupported conversion option(s): {names}")


def _parameters_equal(
    left: Mapping[str, object],
    right: Mapping[str, object],
) -> bool:
    """Return whether two endpoint parameter mappings are numerically equal."""
    if set(left) != set(right):
        return False
    for key in left:
        left_value = left[key]
        right_value = right[key]
        if isinstance(left_value, np.ndarray) or isinstance(right_value, np.ndarray):
            if not np.array_equal(np.asarray(left_value), np.asarray(right_value)):
                return False
            continue
        try:
            if left_value != right_value:
                return False
        except ValueError:
            if not np.array_equal(np.asarray(left_value), np.asarray(right_value)):
                return False
    return True


def _raise_path_error_or_original_option_error(
    exc: ValueError,
    source_name: str,
    target_name: str,
) -> None:
    """Preserve option validation errors, otherwise raise a path error."""
    if "unsupported conversion option" in str(exc):
        raise exc
    raise ValueError(
        "unsupported colour-space conversion path "
        f"{source_name!r} -> {target_name!r}"
    ) from exc


def _to_XYZ(
    value,
    node: ColorSpaceNode,
    endpoint_spec: SpaceSpec,
    common_options: Mapping[str, object],
) -> np.ndarray:
    """Convert *value* from *node* to XYZ, following parent links if needed."""
    if node.name == "XYZ":
        _require_no_options(endpoint_spec.parameters)
        return np.array(value, dtype=np.float64, copy=True)

    if node.to_XYZ is not None:
        return _call_conversion(
            node.to_XYZ,
            value,
            _merge_options(common_options, endpoint_spec),
        )

    if node.parent is not None and node.to_parent is not None:
        parent_value = _call_conversion(node.to_parent, value, {})
        parent_node = get_colourspace_node(node.parent)
        return _to_XYZ(parent_value, parent_node, endpoint_spec, common_options)

    raise ValueError(f"colour-space node {node.name!r} cannot convert to XYZ")


def _from_XYZ(
    XYZ,
    node: ColorSpaceNode,
    endpoint_spec: SpaceSpec,
    common_options: Mapping[str, object],
) -> np.ndarray:
    """Convert *XYZ* to *node*, following parent links if needed."""
    if node.name == "XYZ":
        _require_no_options(endpoint_spec.parameters)
        return np.array(XYZ, dtype=np.float64, copy=True)

    if node.from_XYZ is not None:
        return _call_conversion(
            node.from_XYZ,
            XYZ,
            _merge_options(common_options, endpoint_spec),
        )

    if node.parent is not None and node.from_parent is not None:
        parent_node = get_colourspace_node(node.parent)
        parent_value = _from_XYZ(XYZ, parent_node, endpoint_spec, common_options)
        return _call_conversion(node.from_parent, parent_value, {})

    raise ValueError(f"colour-space node {node.name!r} cannot convert from XYZ")


def convert_color(
    value,
    source: str | ColorSpaceNode | RGBColorSpace | SpaceSpec,
    target: str | ColorSpaceNode | RGBColorSpace | SpaceSpec,
    **kwargs,
) -> np.ndarray:
    """Convert *value* between registered colour-space nodes."""
    source_spec = as_space_spec(source)
    target_spec = as_space_spec(target)

    _reject_chromatic_adaptation(kwargs, source="convert_color keyword arguments")
    _reject_chromatic_adaptation(source_spec.parameters, source="source SpaceSpec")
    _reject_chromatic_adaptation(target_spec.parameters, source="target SpaceSpec")

    source_rgb = _try_get_RGB_colourspace(source_spec.name)
    target_rgb = _try_get_RGB_colourspace(target_spec.name)

    if source_rgb is not None and target_rgb is not None:
        options = dict(kwargs)
        source_options = _rgb_source_options(options, source_spec)
        target_options = _rgb_target_options(options, target_spec)
        apply_decoding = _pop_rgb_option(source_options, "apply_decoding", True)
        apply_encoding = _pop_rgb_option(target_options, "apply_encoding", True)
        _require_no_options(options)
        _require_no_options(source_options)
        _require_no_options(target_options)
        return RGB_to_RGB(
            value,
            source_rgb,
            target_rgb,
            apply_decoding=apply_decoding,
            apply_encoding=apply_encoding,
            chromatic_adaptation=None,
        )

    if source_rgb is not None:
        target_node = _get_generic_node(target_spec.name)  # type: ignore[arg-type]
        options = dict(kwargs)
        source_options = _rgb_source_options(options, source_spec)
        apply_decoding = _pop_rgb_option(source_options, "apply_decoding", True)
        _require_no_options(source_options)
        XYZ = RGB_to_XYZ(value, colourspace=source_rgb, apply_decoding=apply_decoding)
        try:
            return _from_XYZ(XYZ, target_node, target_spec, options)
        except ValueError as exc:
            _raise_path_error_or_original_option_error(exc, source_rgb.name, target_node.name)

    if target_rgb is not None:
        source_node = _get_generic_node(source_spec.name)  # type: ignore[arg-type]
        options = dict(kwargs)
        target_options = _rgb_target_options(options, target_spec)
        apply_encoding = _pop_rgb_option(target_options, "apply_encoding", True)
        _require_no_options(target_options)
        try:
            XYZ = _to_XYZ(value, source_node, source_spec, options)
        except ValueError as exc:
            _raise_path_error_or_original_option_error(exc, source_node.name, target_rgb.name)
        return XYZ_to_RGB(XYZ, colourspace=target_rgb, apply_encoding=apply_encoding)

    source_node = get_colourspace_node(source_spec.name)
    target_node = get_colourspace_node(target_spec.name)

    if source_node.name == target_node.name:
        if _parameters_equal(source_spec.parameters, target_spec.parameters):
            return np.array(value, dtype=np.float64, copy=True)
    try:
        XYZ = _to_XYZ(value, source_node, source_spec, kwargs)
        return _from_XYZ(XYZ, target_node, target_spec, kwargs)
    except ValueError as exc:
        _raise_path_error_or_original_option_error(exc, source_node.name, target_node.name)


__all__ = [
    "convert_color",
]
