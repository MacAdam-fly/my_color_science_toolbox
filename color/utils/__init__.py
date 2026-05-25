"""General-purpose utilities used across the color package."""

from __future__ import annotations

from .arrays import (
    as_float_array,
    as_float_result,
    as_last_axis,
    as_last_axis_pairs,
    as_last_axis_triplets,
    broadcast_last_axis,
    broadcast_pairs,
    broadcast_triplets,
    split_last_axis,
)
from .methods import (
    build_method_index,
    filter_kwargs,
    resolve_method,
)
from .names import canonical_method_name, canonicalize_name, canonicalize_resource_name
from .scale import (
    from_range_1,
    from_range_100,
    from_range_degrees,
    to_domain_1,
    to_domain_100,
    to_domain_degrees,
)

__all__ = [
    "as_float_array",  # convert input to float ndarray with optional finite check
    "as_float_result",  # return scalar for scalar-like outputs, array otherwise
    "as_last_axis",  # validate fixed-size last-axis arrays
    "as_last_axis_triplets",  # validate arrays with three values on the last axis
    "as_last_axis_pairs",  # validate arrays with two values on the last axis
    "broadcast_last_axis",  # broadcast fixed-size last-axis arrays
    "broadcast_triplets",  # broadcast triplet arrays
    "broadcast_pairs",  # broadcast pair arrays
    "split_last_axis",  # split array channels along the last axis
    "canonicalize_name",  # normalize general names and aliases
    "canonicalize_resource_name",  # normalize dataset/generator registry names
    "canonical_method_name",  # semantic wrapper for method names and aliases
    "build_method_index",  # build canonical method alias lookup
    "resolve_method",  # resolve a method name to a registered function
    "filter_kwargs",  # keep kwargs accepted by a function signature
    "to_domain_1",  # convert values to a [0, 1] numeric domain
    "to_domain_100",  # convert values to a [0, 100] numeric domain
    "from_range_1",  # convert values from a [0, 1] numeric range
    "from_range_100",  # convert values from a [0, 100] numeric range
    "to_domain_degrees",  # convert normalized angle-like values to degrees
    "from_range_degrees",  # convert degree values to a target numeric range
]
