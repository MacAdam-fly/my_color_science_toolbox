"""Generic colour-space conversion entry points."""

from __future__ import annotations

import inspect
import warnings
from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np

from color.constants.illuminants_XYZ import D65_XYZ
from color.utils.methods import filter_kwargs

from .registry import ColorSpaceNode, get_colourspace_node
from .rgb import (
    RGBColorSpace,
    RGB_to_RGB,
    RGB_to_XYZ,
    XYZ_to_RGB,
    get_RGB_colourspace,
)
from .spec import SpaceSpec, as_space_spec


_D65_XYZ = np.asarray(D65_XYZ, dtype=np.float64)
_D65_XY = _D65_XYZ[:2] / np.sum(_D65_XYZ)
_D65_XYZ_ATOL = 5e-2
_D65_XY_ATOL = 5e-4


@dataclass(frozen=True)
class ConversionPathNode:
    """A node in a described colour-space conversion path."""

    name: str
    kind: str


@dataclass(frozen=True)
class ConversionPathEdge:
    """A directed edge in a described colour-space conversion path."""

    source: str
    target: str
    operation: str
    description: str


@dataclass(frozen=True)
class ConversionPath:
    """A structural description of a colour-space conversion route.

    The path records nodes and directed operations that ``convert_color(...)``
    would use, but it does not evaluate any colour values. It is intended for
    diagnostics, documentation, and plotting of conversion routes.

    Parameters
    ----------
    source
        Resolved source colour-space name.
    target
        Resolved target colour-space name.
    nodes
        Ordered route nodes.
    edges
        Directed operations between adjacent nodes.

    Returns
    -------
    ConversionPath
        Immutable route description.

    Notes
    -----
    ``ConversionPath`` is descriptive only; it does not validate colour value
    shapes and does not execute conversion math.

    Examples
    --------
    >>> from color.spaces import describe_conversion_path
    >>> path = describe_conversion_path("JzCzhz", "Lab")
    >>> [node.name for node in path.nodes]
    ['JzCzhz', 'Jzazbz', 'XYZ', 'Lab']
    """

    source: str
    target: str
    nodes: tuple[ConversionPathNode, ...]
    edges: tuple[ConversionPathEdge, ...]


def _call_conversion(function, value, options: dict[str, object]) -> np.ndarray:
    """Call *function* with the supported subset of *options*."""
    signature = inspect.signature(function)
    accepts_var_kwargs = any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in signature.parameters.values()
    )
    if accepts_var_kwargs:
        return function(value, **options)

    supported = filter_kwargs(function, options)
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


def _validate_reference_whitepoint_XYZ(value: object, *, name: str) -> np.ndarray:
    """Return *value* as a valid reference whitepoint XYZ triplet."""
    whitepoint = np.asarray(value, dtype=np.float64)
    if whitepoint.shape != (3,):
        raise ValueError(f"{name} must have shape (3,), got {whitepoint.shape}")
    if not np.all(np.isfinite(whitepoint)):
        raise ValueError(f"{name} must be finite")
    if np.any(whitepoint <= 0):
        raise ValueError(f"{name} values must be positive")
    return whitepoint


def _validate_reference_whitepoint_xy(value: object, *, name: str) -> np.ndarray:
    """Return *value* as a valid reference whitepoint xy pair."""
    whitepoint = np.asarray(value, dtype=np.float64)
    if whitepoint.shape != (2,):
        raise ValueError(f"{name} must have shape (2,), got {whitepoint.shape}")
    if not np.all(np.isfinite(whitepoint)):
        raise ValueError(f"{name} must be finite")
    if np.any(whitepoint <= 0):
        raise ValueError(f"{name} values must be positive")
    return whitepoint


def _is_D65_XYZ(value: object) -> bool:
    """Return whether *value* is the project D65 reference whitepoint."""
    whitepoint = _validate_reference_whitepoint_XYZ(value, name="whitepoint_XYZ")
    return bool(np.allclose(whitepoint, _D65_XYZ, rtol=1e-7, atol=_D65_XYZ_ATOL))


def _is_D65_xy(value: object) -> bool:
    """Return whether *value* is the project D65 chromaticity."""
    whitepoint = _validate_reference_whitepoint_xy(value, name="whitepoint_xy")
    return bool(np.allclose(whitepoint, _D65_XY, rtol=1e-7, atol=_D65_XY_ATOL))


def _XYZ_whitepoint_to_xy(whitepoint: np.ndarray) -> np.ndarray:
    """Return xy chromaticity for a validated whitepoint XYZ triplet."""
    return whitepoint[:2] / np.sum(whitepoint)


def _validate_XYZ_metadata_options(options: Mapping[str, object]) -> None:
    """Validate metadata-only options accepted by the XYZ hub node."""
    allowed = {"whitepoint_XYZ"}
    unsupported = set(options) - allowed
    if unsupported:
        names = ", ".join(sorted(unsupported))
        raise ValueError(f"unsupported conversion option(s): {names}")
    if "whitepoint_XYZ" in options:
        _validate_reference_whitepoint_XYZ(
            options["whitepoint_XYZ"],
            name="whitepoint_XYZ",
        )


def _node_requires_D65_referred_XYZ(node: ColorSpaceNode) -> bool:
    """Return whether *node* or one of its parents requires D65-referred XYZ."""
    current = node
    while True:
        if current.requires_D65_referred_XYZ:
            return True
        if current.parent is None:
            return False
        current = get_colourspace_node(current.parent)


def _spec_D65_reference_issue(endpoint_spec: SpaceSpec) -> str | None:
    """Return a human-readable D65 reference-domain issue, if any."""
    parameters = endpoint_spec.parameters
    if "whitepoint_XYZ" in parameters:
        whitepoint = _validate_reference_whitepoint_XYZ(
            parameters["whitepoint_XYZ"],
            name="whitepoint_XYZ",
        )
        if np.allclose(whitepoint, _D65_XYZ, rtol=1e-7, atol=_D65_XYZ_ATOL):
            return None
        if np.allclose(
            _XYZ_whitepoint_to_xy(whitepoint),
            _D65_XY,
            rtol=1e-7,
            atol=_D65_XY_ATOL,
        ):
            return (
                "declares D65 chromaticity but not the project D65_XYZ "
                "reference domain on the Y=100 scale"
            )
        return "declares a non-D65 reference whitepoint chromaticity"
    if "XYZ_w" in parameters:
        whitepoint = _validate_reference_whitepoint_XYZ(
            parameters["XYZ_w"],
            name="XYZ_w",
        )
        if np.allclose(whitepoint, _D65_XYZ, rtol=1e-7, atol=_D65_XYZ_ATOL):
            return None
        if np.allclose(
            _XYZ_whitepoint_to_xy(whitepoint),
            _D65_XY,
            rtol=1e-7,
            atol=_D65_XY_ATOL,
        ):
            return (
                "declares D65 chromaticity but not the project D65_XYZ "
                "reference domain on the Y=100 scale"
            )
        return "declares a non-D65 reference whitepoint chromaticity"
    if "whitepoint_xy" in parameters:
        if _is_D65_xy(parameters["whitepoint_xy"]):
            return None
        return "declares a non-D65 reference whitepoint chromaticity"
    return None


def _spec_has_unknown_XYZ_reference(endpoint_spec: SpaceSpec, node: ColorSpaceNode) -> bool:
    """Return whether *endpoint_spec* leaves an XYZ-like reference unstated."""
    if endpoint_spec.parameters:
        return False
    return node.name in {"XYZ", "xyY"}


def _warn_D65_reference_risk(message: str) -> None:
    """Emit a warning for routes crossing a D65-referred space boundary."""
    warnings.warn(message, UserWarning, stacklevel=3)


def _warn_if_source_may_not_be_D65_referred(
    source_spec: SpaceSpec,
    source_node: ColorSpaceNode,
    target_node: ColorSpaceNode,
) -> None:
    """Warn if a route feeds a possibly non-D65 source into a D65-only target."""
    if not _node_requires_D65_referred_XYZ(target_node):
        return
    if _node_requires_D65_referred_XYZ(source_node):
        return

    issue = _spec_D65_reference_issue(source_spec)
    if issue is not None:
        _warn_D65_reference_risk(
            f"{target_node.name} requires D65-referred XYZ, but the source "
            f"{source_node.name} SpaceSpec {issue}. "
            "convert_color(...) does not adapt automatically; use "
            "color.adaptation.adapt_to_D65(...) and keep the spaces XYZ reference "
            "domain on the Y=100 scale when colour appearance must be preserved."
        )
        return

    if _spec_has_unknown_XYZ_reference(source_spec, source_node):
        _warn_D65_reference_risk(
            f"{target_node.name} requires D65-referred XYZ, but the source "
            f"{source_node.name} route does not declare a reference whitepoint. "
            "convert_color(...) assumes the XYZ values are already D65-referred; "
            "use SpaceSpec('XYZ', whitepoint_XYZ=...) or adapt_to_D65(...) when needed."
        )


def _warn_if_target_may_not_be_D65_referred(
    source_node: ColorSpaceNode,
    target_spec: SpaceSpec,
    target_node: ColorSpaceNode,
) -> None:
    """Warn if a D65-only source is routed into an explicitly non-D65 target."""
    if not _node_requires_D65_referred_XYZ(source_node):
        return
    if _node_requires_D65_referred_XYZ(target_node):
        return

    issue = _spec_D65_reference_issue(target_spec)
    if issue is not None:
        _warn_D65_reference_risk(
            f"{source_node.name} converts back to D65-referred XYZ, but the target "
            f"{target_node.name} SpaceSpec {issue}. "
            "convert_color(...) does not adapt automatically; convert to XYZ, call "
            "color.adaptation.adapt_from_D65(...), and use a target reference domain "
            "consistent with the spaces Y=100 scale when colour appearance must be preserved."
        )


def _warn_if_rgb_source_may_not_be_D65_referred(
    source_rgb: RGBColorSpace,
    target_node: ColorSpaceNode,
) -> None:
    """Warn if a non-D65 RGB source feeds a D65-only target."""
    if not _node_requires_D65_referred_XYZ(target_node):
        return
    if np.allclose(source_rgb.white_xy, _D65_XY, rtol=1e-7, atol=_D65_XY_ATOL):
        return
    _warn_D65_reference_risk(
        f"{target_node.name} requires D65-referred XYZ, but {source_rgb.name} has "
        f"a {source_rgb.white_name} whitepoint. convert_color(...) does not adapt "
        "automatically; use RGB_to_RGB(..., chromatic_adaptation=...) or "
        "color.adaptation.adapt_to_D65(...) when colour appearance must be preserved."
    )


def _warn_if_rgb_target_may_not_be_D65_referred(
    source_node: ColorSpaceNode,
    target_rgb: RGBColorSpace,
) -> None:
    """Warn if a D65-only source feeds a non-D65 RGB target."""
    if not _node_requires_D65_referred_XYZ(source_node):
        return
    if np.allclose(target_rgb.white_xy, _D65_XY, rtol=1e-7, atol=_D65_XY_ATOL):
        return
    _warn_D65_reference_risk(
        f"{source_node.name} converts back to D65-referred XYZ, but {target_rgb.name} "
        f"has a {target_rgb.white_name} whitepoint. convert_color(...) does not adapt "
        "automatically; use color.adaptation.adapt_from_D65(...) or RGB_to_RGB(..., "
        "chromatic_adaptation=...) when colour appearance must be preserved."
    )


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


def _validate_conversion_options(function, options: Mapping[str, object]) -> None:
    """Validate that *function* accepts the given conversion *options*."""
    signature = inspect.signature(function)
    accepts_var_kwargs = any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in signature.parameters.values()
    )
    if accepts_var_kwargs:
        return

    unused = set(options) - set(filter_kwargs(function, options))
    if unused:
        names = ", ".join(sorted(unused))
        raise ValueError(f"unsupported conversion option(s): {names}")


def _conversion_path_node(name: str, kind: str = "generic") -> ConversionPathNode:
    """Return a conversion path node, marking XYZ as the central hub."""
    if name == "XYZ":
        return ConversionPathNode(name="XYZ", kind="hub")
    return ConversionPathNode(name=name, kind=kind)


def _node_sequence_from_edges(
    first: ConversionPathNode,
    edges: list[ConversionPathEdge],
    kind_lookup: Mapping[str, str] | None = None,
) -> tuple[ConversionPathNode, ...]:
    """Build an ordered node sequence from *first* and *edges*."""
    kind_lookup = kind_lookup or {}
    nodes = [first]
    for edge in edges:
        kind = kind_lookup.get(edge.target, "generic")
        nodes.append(_conversion_path_node(edge.target, kind=kind))
    return tuple(nodes)


def _describe_to_XYZ(
    node: ColorSpaceNode,
    endpoint_spec: SpaceSpec,
    common_options: Mapping[str, object],
) -> list[ConversionPathEdge]:
    """Describe conversion from *node* to XYZ, following parent links."""
    if node.name == "XYZ":
        _validate_XYZ_metadata_options(endpoint_spec.parameters)
        return []

    if node.to_XYZ is not None:
        options = _merge_options(common_options, endpoint_spec)
        _validate_conversion_options(node.to_XYZ, options)
        return [
            ConversionPathEdge(
                source=node.name,
                target="XYZ",
                operation="to_XYZ",
                description=f"{node.name} to XYZ",
            )
        ]

    if node.parent is not None and node.to_parent is not None:
        parent_node = get_colourspace_node(node.parent)
        return [
            ConversionPathEdge(
                source=node.name,
                target=parent_node.name,
                operation="to_parent",
                description=f"{node.name} to parent {parent_node.name}",
            ),
            *_describe_to_XYZ(parent_node, endpoint_spec, common_options),
        ]

    raise ValueError(f"colour-space node {node.name!r} cannot convert to XYZ")


def _describe_from_XYZ(
    node: ColorSpaceNode,
    endpoint_spec: SpaceSpec,
    common_options: Mapping[str, object],
) -> list[ConversionPathEdge]:
    """Describe conversion from XYZ to *node*, following parent links."""
    if node.name == "XYZ":
        _validate_XYZ_metadata_options(endpoint_spec.parameters)
        return []

    if node.from_XYZ is not None:
        options = _merge_options(common_options, endpoint_spec)
        _validate_conversion_options(node.from_XYZ, options)
        return [
            ConversionPathEdge(
                source="XYZ",
                target=node.name,
                operation="from_XYZ",
                description=f"XYZ to {node.name}",
            )
        ]

    if node.parent is not None and node.from_parent is not None:
        parent_node = get_colourspace_node(node.parent)
        return [
            *_describe_from_XYZ(parent_node, endpoint_spec, common_options),
            ConversionPathEdge(
                source=parent_node.name,
                target=node.name,
                operation="from_parent",
                description=f"Parent {parent_node.name} to {node.name}",
            ),
        ]

    raise ValueError(f"colour-space node {node.name!r} cannot convert from XYZ")


def _to_XYZ(
    value,
    node: ColorSpaceNode,
    endpoint_spec: SpaceSpec,
    common_options: Mapping[str, object],
) -> np.ndarray:
    """Convert *value* from *node* to XYZ, following parent links if needed."""
    if node.name == "XYZ":
        _validate_XYZ_metadata_options(endpoint_spec.parameters)
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
        _validate_XYZ_metadata_options(endpoint_spec.parameters)
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
    """Convert *value* between registered colour-space nodes.

    ``source`` and ``target`` can be names, ``SpaceSpec`` objects, registered
    generic nodes, or RGB colour spaces. Generic spaces are routed through XYZ,
    derived spaces follow their parent chain, and RGB spaces apply transfer
    decoding/encoding as requested. The function does not perform implicit
    chromatic adaptation; use ``color.adaptation`` or ``RGB_to_RGB`` with an
    explicit adaptation method when a reference whitepoint must change.

    Parameters
    ----------
    value
        Colour values. The final axis must match the source space.
    source
        Source colour space, optionally wrapped in ``SpaceSpec``.
    target
        Target colour space, optionally wrapped in ``SpaceSpec``.
    **kwargs
        Options shared with the source and target endpoint conversion
        functions, such as RGB transfer flags.

    Returns
    -------
    numpy.ndarray
        Converted colour values with the final axis of the target space.

    Notes
    -----
    XYZ is the conversion hub and public XYZ values use the project Y=100
    scale. Oklab, IPT and Jzazbz require D65-referred XYZ; this function warns
    on known risky routes but does not adapt automatically.

    Examples
    --------
    >>> Lab = convert_color([19.01, 20.0, 21.78], "XYZ", "Lab")
    >>> Lab.shape
    (3,)
    """
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
        _warn_if_rgb_source_may_not_be_D65_referred(source_rgb, target_node)
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
        _warn_if_rgb_target_may_not_be_D65_referred(source_node, target_rgb)
        try:
            XYZ = _to_XYZ(value, source_node, source_spec, options)
        except ValueError as exc:
            _raise_path_error_or_original_option_error(exc, source_node.name, target_rgb.name)
        return XYZ_to_RGB(XYZ, colourspace=target_rgb, apply_encoding=apply_encoding)

    source_node = get_colourspace_node(source_spec.name)
    target_node = get_colourspace_node(target_spec.name)

    _warn_if_source_may_not_be_D65_referred(source_spec, source_node, target_node)
    _warn_if_target_may_not_be_D65_referred(source_node, target_spec, target_node)

    if source_node.name == target_node.name:
        if _parameters_equal(source_spec.parameters, target_spec.parameters):
            return np.array(value, dtype=np.float64, copy=True)
    try:
        XYZ = _to_XYZ(value, source_node, source_spec, kwargs)
        return _from_XYZ(XYZ, target_node, target_spec, kwargs)
    except ValueError as exc:
        _raise_path_error_or_original_option_error(exc, source_node.name, target_node.name)


def describe_conversion_path(
    source: str | ColorSpaceNode | RGBColorSpace | SpaceSpec,
    target: str | ColorSpaceNode | RGBColorSpace | SpaceSpec,
    **kwargs,
) -> ConversionPath:
    """Describe the structural route used for a colour-space conversion.

    The returned ``ConversionPath`` mirrors the routing rules of
    ``convert_color(...)`` without inspecting or transforming numeric input.
    Unsupported options and hidden chromatic-adaptation requests are rejected
    in the same style as the real conversion entry point.

    Parameters
    ----------
    source
        Source colour space, optionally wrapped in ``SpaceSpec``.
    target
        Target colour space, optionally wrapped in ``SpaceSpec``.
    **kwargs
        Conversion options used only to validate route compatibility.

    Returns
    -------
    ConversionPath
        Structural route description.

    Notes
    -----
    Use ``color.spaces.plotting.plot_conversion_path`` to draw the returned
    path. The plotting helper is intentionally not part of the top-level
    ``color.spaces`` API.

    Examples
    --------
    >>> path = describe_conversion_path("Oklch", "Lab")
    >>> [edge.operation for edge in path.edges]
    ['to_parent', 'to_XYZ', 'from_XYZ']
    """
    source_spec = as_space_spec(source)
    target_spec = as_space_spec(target)

    _reject_chromatic_adaptation(kwargs, source="describe_conversion_path keyword arguments")
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
        edges = (
            ConversionPathEdge(
                source=source_rgb.name,
                target="XYZ",
                operation="decode",
                description=(
                    f"{source_rgb.name} to XYZ; apply_decoding={apply_decoding}; "
                    "chromatic_adaptation=None"
                ),
            ),
            ConversionPathEdge(
                source="XYZ",
                target=target_rgb.name,
                operation="encode",
                description=f"XYZ to {target_rgb.name}; apply_encoding={apply_encoding}",
            ),
        )
        return ConversionPath(
            source=source_rgb.name,
            target=target_rgb.name,
            nodes=(
                ConversionPathNode(source_rgb.name, "rgb"),
                ConversionPathNode("XYZ", "hub"),
                ConversionPathNode(target_rgb.name, "rgb"),
            ),
            edges=edges,
        )

    if source_rgb is not None:
        target_node = _get_generic_node(target_spec.name)  # type: ignore[arg-type]
        options = dict(kwargs)
        source_options = _rgb_source_options(options, source_spec)
        apply_decoding = _pop_rgb_option(source_options, "apply_decoding", True)
        _require_no_options(source_options)
        _warn_if_rgb_source_may_not_be_D65_referred(source_rgb, target_node)
        edges = [
            ConversionPathEdge(
                source=source_rgb.name,
                target="XYZ",
                operation="decode",
                description=f"{source_rgb.name} to XYZ; apply_decoding={apply_decoding}",
            ),
            *_describe_from_XYZ(target_node, target_spec, options),
        ]
        return ConversionPath(
            source=source_rgb.name,
            target=target_node.name,
            nodes=_node_sequence_from_edges(
                ConversionPathNode(source_rgb.name, "rgb"),
                edges,
                kind_lookup={source_rgb.name: "rgb"},
            ),
            edges=tuple(edges),
        )

    if target_rgb is not None:
        source_node = _get_generic_node(source_spec.name)  # type: ignore[arg-type]
        options = dict(kwargs)
        target_options = _rgb_target_options(options, target_spec)
        apply_encoding = _pop_rgb_option(target_options, "apply_encoding", True)
        _require_no_options(target_options)
        _warn_if_rgb_target_may_not_be_D65_referred(source_node, target_rgb)
        edges = [
            *_describe_to_XYZ(source_node, source_spec, options),
            ConversionPathEdge(
                source="XYZ",
                target=target_rgb.name,
                operation="encode",
                description=f"XYZ to {target_rgb.name}; apply_encoding={apply_encoding}",
            ),
        ]
        return ConversionPath(
            source=source_node.name,
            target=target_rgb.name,
            nodes=_node_sequence_from_edges(
                _conversion_path_node(source_node.name),
                edges,
                kind_lookup={target_rgb.name: "rgb"},
            ),
            edges=tuple(edges),
        )

    source_node = get_colourspace_node(source_spec.name)
    target_node = get_colourspace_node(target_spec.name)

    _warn_if_source_may_not_be_D65_referred(source_spec, source_node, target_node)
    _warn_if_target_may_not_be_D65_referred(source_node, target_spec, target_node)

    if source_node.name == target_node.name:
        if _parameters_equal(source_spec.parameters, target_spec.parameters):
            return ConversionPath(
                source=source_node.name,
                target=target_node.name,
                nodes=(_conversion_path_node(source_node.name),),
                edges=(
                    ConversionPathEdge(
                        source=source_node.name,
                        target=target_node.name,
                        operation="identity",
                        description=f"{source_node.name} to {target_node.name}; identity copy",
                    ),
                ),
            )

    try:
        edges = [
            *_describe_to_XYZ(source_node, source_spec, kwargs),
            *_describe_from_XYZ(target_node, target_spec, kwargs),
        ]
    except ValueError as exc:
        _raise_path_error_or_original_option_error(exc, source_node.name, target_node.name)

    return ConversionPath(
        source=source_node.name,
        target=target_node.name,
        nodes=_node_sequence_from_edges(_conversion_path_node(source_node.name), edges),
        edges=tuple(edges),
    )


__all__ = [
    "ConversionPath",
    "ConversionPathEdge",
    "ConversionPathNode",
    "convert_color",
    "describe_conversion_path",
]
