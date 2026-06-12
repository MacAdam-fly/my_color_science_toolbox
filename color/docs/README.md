# color_science_toolbox Installed Documentation

This directory contains module-level documentation shipped with the installed
package. It is intended for users and AI assistants working from a pip-installed
environment where the full source repository, examples, and root documentation
may not be available.

Use this routing table before reading source code:

| Task | Documentation |
| --- | --- |
| Static datasets and registered data sources | `datasets/` |
| Spectral objects, resampling, and wrappers | `spectra/` |
| Spectrum to XYZ/LMS/xy/CCT/Duv/dominant wavelength | `colorimetry/` |
| Color-space conversion and custom RGB spaces | `spaces/` |
| Chromatic adaptation | `adaptation/` |
| CIECAM02/CIECAM16 appearance models | `appearance/` |
| Color-difference equations | `difference/` |
| Display/object gamut, coverage, Pointer, MacAdam | `gamut/` |
| Spectrum and reflectance recovery | `recovery/` |
| Device primary responses and melanopic silent substitution | `device/` |
| Low-level plotting components and styles | `plot/` |
| Spectral/image/figure IO | `io/` |
| Formula-based generators | `generators/` |
| Individual cone fundamentals | `individual_cone_fundamentals/` |
| Numeric helpers | `math/` |
| Shared array/name/scale utilities | `utils/` |
| Standard constants | `constants/` |

Each stable module usually provides:

- `README.md`: short English entry point.
- `README_DETAILS.md`: detailed Chinese design notes.
- `API_GUIDE.md`: Chinese per-API usage guide.

The root package exposes only a small convenience facade. For complete API
coverage, read the documentation for the relevant module and import from that
module directly.
