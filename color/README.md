# color

Core package for the colour-science toolbox.

The package is organised by domain modules. Users should import from the
specific module they need, for example:

```python
from color.spectra import from_cie1931_xyz_cmfs
from color.colorimetry import reflectance_to_XYZ
from color.spaces import convert_color
from color.gamut import compute_LCH_gamut_boundary
```

Main modules:

- `datasets`: static reference data loading from `color/data`.
- `generators`: formula/procedural spectrum generation.
- `spectra`: spectral object wrappers, interpolation, extrapolation and alignment.
- `colorimetry`: spectral integration, chromaticity, photometry, lightness, temperature, dominant wavelength and LMS/XYZ transforms.
- `adaptation`: explicit XYZ chromatic adaptation.
- `appearance`: CIECAM02 and CIECAM16 colour appearance models.
- `spaces`: colour-space definitions and conversion routing.
- `difference`: colour-difference metrics.
- `gamut`: display-primary gamuts, Pointer gamut and MacAdam limits.
- `quality`: spectral quality metrics such as SSI.
- `individual_cone_fundamentals`: Stockman/Rider individual LMS fundamentals.
- `plot`: low-level plotting components for colour-science visualisation.
- `math`: interpolation and extrapolation helpers.
- `constants`: shared scientific constants and matrices.
- `utils`: low-level shared utility functions.

`color.core` has been removed because it only contained unused type aliases and
an unused context object. Shared behaviour now lives in the concrete modules
above.
