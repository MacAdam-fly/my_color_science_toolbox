# color.utils

`color.utils` contains small, dependency-light helpers shared by multiple
modules. It is a foundation layer and should not depend on higher-level colour
science modules such as `spaces`, `colorimetry`, `appearance`, or `difference`.

## Current Entry Points

- `color.utils.arrays`: NumPy input validation, fixed-size last-axis arrays,
  broadcasting helpers, scalar/array result handling.
- `color.utils.methods`: method-name canonicalisation, alias indexes, dispatch
  resolution, and keyword filtering.
- `color.utils.scale`: explicit numeric scale conversion between `[0, 1]`,
  `[0, 100]`, and degree-style angle domains.

## Array Helpers

Use `arrays.py` when a function needs consistent NumPy input handling.

```python
from color.utils.arrays import as_last_axis_triplets, broadcast_triplets

XYZ = as_last_axis_triplets(XYZ, name="XYZ")
Lab_1, Lab_2 = broadcast_triplets(Lab_1, Lab_2, name_1="Lab_1", name_2="Lab_2")
```

Available helpers:

```python
as_float_array(value, name="value", finite=True)
as_float_result(value)
as_last_axis(value, size, name="value", finite=True)
as_last_axis_triplets(value, name="value", finite=True)
as_last_axis_pairs(value, name="value", finite=True)
broadcast_last_axis(value_1, value_2, size, name_1="value_1", name_2="value_2", finite=True)
broadcast_triplets(...)
broadcast_pairs(...)
split_last_axis(value)
```

## Method Helpers

Use `methods.py` when a public function accepts a `method=...` style option.

```python
from color.utils.methods import build_method_index, filter_kwargs, resolve_method

METHODS = {"CIE 2000": delta_E_CIE2000}
ALIASES = {"CIE 2000": ("cie2000", "CIEDE2000")}
INDEX = build_method_index(ALIASES)

_, function = resolve_method("CIEDE2000", INDEX, METHODS)
result = function(a, b, **filter_kwargs(function, kwargs))
```

Available helpers:

```python
canonical_method_name(name)
build_method_index(method_aliases)
resolve_method(method, method_index, methods)
filter_kwargs(function, kwargs)
```

## Scale Helpers

Use `scale.py` when a module needs to make numeric scale changes explicit.
Unlike `colour-science`, this package does not use a global domain/range scale
state: callers declare the source or target scale directly.

```python
from color.utils.scale import to_domain_1, to_domain_100

XYZ_relative = to_domain_1(XYZ_Y100)
XYZ_Y100 = to_domain_100(XYZ_relative)
```

Available helpers:

```python
to_domain_1(value, source_scale="100", scale_factor=100.0)
to_domain_100(value, source_scale="1", scale_factor=100.0)
from_range_1(value, target_scale="100", scale_factor=100.0)
from_range_100(value, target_scale="1", scale_factor=100.0)
to_domain_degrees(value, source_scale="1", scale_factor=360.0)
from_range_degrees(value, target_scale="1", scale_factor=360.0)
```

`source_scale="reference"` and `target_scale="reference"` are no-op copy
paths. They are useful when a function wants to accept a scale option without
performing hidden conversion.

## Boundary Rules

Keep this package narrow.

- Do add helpers used by more than one module.
- Do keep helpers NumPy-only or standard-library-only.
- Do not add colour-science formulae here.
- Do not add high-level colour-space conversion logic here.
- Do not add objects that belong to `spaces`, `spectra`, `appearance`, or
  `difference`.

`color.difference` is currently the first migrated user of these helpers. Other
modules can migrate gradually when they are next touched.
