# color.utils

`color.utils` is the shared foundation layer for small, dependency-light
helpers used across the package. It should stay below the scientific modules:

```text
color.utils
  -> arrays, names, method dispatch, numeric scale helpers

color.datasets / generators / spectra / colorimetry / spaces / appearance / difference
  -> domain logic and colour-science algorithms
```

The rule of thumb is:

```text
utils handles mechanics, not colour-science meaning.
```

Do not put spectral, colorimetric, colour-space, appearance, whitepoint, or
physical-parameter formulae here.

Chinese API usage examples are available in [`API_GUIDE.md`](API_GUIDE.md).
Chinese design notes are available in [`README_DETAILS.md`](README_DETAILS.md).

## Modules

| Module | Responsibility |
| --- | --- |
| `arrays.py` | NumPy float conversion, fixed-size last-axis validation, broadcasting, channel splitting |
| `names.py` | General, method, and resource-name canonicalisation |
| `methods.py` | Method alias indexes, dispatch resolution, and keyword filtering |
| `scale.py` | Explicit numeric scale conversion between domain/range conventions |

## arrays.py

Use these helpers at function boundaries when a public API accepts scalar,
single-point, or batch NumPy-like inputs.

```python
from color.utils.arrays import as_last_axis_triplets, broadcast_triplets

XYZ = as_last_axis_triplets(XYZ, name="XYZ")
Lab_1, Lab_2 = broadcast_triplets(Lab_1, Lab_2, name_1="Lab_1", name_2="Lab_2")
```

Public helpers:

```python
as_float_array(value, name="value", finite=True)
as_float_result(value)
as_last_axis(value, size, name="value", finite=True)
as_last_axis_triplets(value, name="value", finite=True)
as_last_axis_pairs(value, name="value", finite=True)
broadcast_last_axis(value_1, value_2, size, name_1="value_1", name_2="value_2", finite=True)
broadcast_triplets(value_1, value_2, ...)
broadcast_pairs(value_1, value_2, ...)
split_last_axis(value)
```

These helpers validate array mechanics only. Domain-specific checks such as
positive whitepoints, increasing wavelengths, valid CCT ranges, or valid
observer conditions belong in the calling module.

## names.py

All string canonicalisation lives in `names.py`.

```python
from color.utils.names import (
    canonical_method_name,
    canonicalize_name,
    canonicalize_resource_name,
)

canonicalize_name("CAM16-UCS")          # "cam16ucs"
canonical_method_name("CIE 2000")       # "cie2000"
canonicalize_resource_name("0.1 nm")    # "0p1nm"
canonicalize_resource_name("V(\u03bb)")      # "vlambda"
canonicalize_resource_name("10\u00b0 observer")  # "10degreeobserver"
```

Use `canonicalize_name(...)` or `canonical_method_name(...)` for methods,
options, transforms, and colour-space aliases.

Use `canonicalize_resource_name(...)` for dataset/generator resource names,
because resources may need to preserve decimal sampling intervals and symbols
such as `λ` and `°`.

## methods.py

Use `methods.py` when a public function accepts `method="..."`.

```python
from color.utils.methods import build_method_index, filter_kwargs, resolve_method

METHODS = {"CIE 2000": delta_E_CIE2000}
ALIASES = {"CIE 2000": ("cie2000", "CIEDE2000")}
METHOD_INDEX = build_method_index(ALIASES)

name, function = resolve_method("CIEDE2000", METHOD_INDEX, METHODS)
result = function(a, b, **filter_kwargs(function, kwargs))
```

`methods.py` re-exports `canonical_method_name(...)` for compatibility, but the
canonicalisation rule itself is defined in `names.py`.

## scale.py

Use `scale.py` when a module needs to make numeric scale changes explicit. This
package does not use a global scale state.

```python
from color.utils.scale import to_domain_1, to_domain_100

XYZ_relative = to_domain_1(XYZ_Y100, source_scale="100")
XYZ_Y100 = to_domain_100(XYZ_relative, source_scale="1")
```

Public helpers:

```python
to_domain_1(value, source_scale="100", scale_factor=100.0)
to_domain_100(value, source_scale="1", scale_factor=100.0)
from_range_1(value, target_scale="100", scale_factor=100.0)
from_range_100(value, target_scale="1", scale_factor=100.0)
to_domain_degrees(value, source_scale="1", scale_factor=360.0)
from_range_degrees(value, target_scale="1", scale_factor=360.0)
```

`scale.py` only expresses numeric scaling. It does not perform chromatic
adaptation, choose whitepoints, normalise spectral integrations, or interpret
appearance viewing conditions.

## Boundary Rules

Good candidates for `utils`:

- array shape and finite-value checks reused by multiple modules
- method alias/dispatch mechanics
- reusable string canonicalisation
- explicit numeric scale conversion

Poor candidates for `utils`:

- colour-space conversion formulae
- colour-difference formulae
- spectral interpolation or integration
- CCT, whitepoint, wavelength, or viewing-condition validation
- dataset registry behaviour beyond generic name canonicalisation

When in doubt, keep domain-specific behaviour local to the module that owns the
scientific meaning.
