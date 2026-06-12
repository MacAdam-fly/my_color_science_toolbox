# color_science_toolbox

`color_science_toolbox` is a low-level color-science toolkit. It organizes
standard datasets, spectral objects, colorimetric calculations, color-space
conversion, appearance models, color differences, gamut analysis, spectral
recovery, display-device response optimisation, plotting, and IO into a
coherent computation framework.

Chinese documentation: [`readme_cn.md`](readme_cn.md)

## Installation

This is a pure Python toolkit. The current dependency set has been validated in
the project `.venv` with `Python 3.9.0`; use `Python >= 3.9`.

For normal use in another project, install the release wheel:

```powershell
py -3.9 -m venv .venv
.\.venv\Scripts\python.exe -m pip install "https://github.com/MacAdam-fly/my_color_science_toolbox/releases/download/v1.0.0/color_science_toolbox-1.0.0-py3-none-any.whl"
.\.venv\Scripts\python.exe -c "import color; print(color.__version__)"
```

The installable package declares its runtime dependencies in `setup.py`;

## Development Setup

Use this path only when you want to modify the toolbox source, run tests, or
build a new wheel.

```powershell
git clone git@github.com:MacAdam-fly/my_color_science_toolbox.git
cd my_color_science_toolbox
py -3.9 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m pytest -m "not examples" --import-mode=importlib -q --basetemp .pytest_tmp
```

`requirements.txt` is the pinned development dependency entrypoint. The
editable install keeps imports linked to the local source tree:

```powershell
.\.venv\Scripts\python.exe -c "import color; print(color.__version__)"
```

For day-to-day development, run the tests for the modules you changed first.
See [`TESTING_GUIDE.md`](TESTING_GUIDE.md) for the shorter testing workflow.

## Architecture

The project has one primary representation pipeline: data sources become
spectral objects, spectral objects become colorimetric quantities, and those
quantities become `XYZ / LMS / xyY / uv / CCT / Duv` values. The other modules
operate around these representations: converting, adapting, comparing,
recovering, optimising device primary weights, plotting, and reading/writing
data.

![color_science_toolbox architecture](docs/architecture.svg)

Core principles:

- `datasets`, `generators`, and `individual_cone_fundamentals` are the main data
  sources.
- `spectra -> colorimetry` is the base forward pipeline.
- `adaptation` is an `XYZ -> XYZ` operation; `appearance` maps between `XYZ` and
  appearance correlates; `spaces` uses `XYZ` as the central conversion hub.
- `difference` compares coordinates already in the same space. `gamut` combines
  `XYZ / xy / Lab / LCH / primaries / standard gamut data`. `recovery` solves
  inverse problems from `XYZ / xyY / LMS` back to spectra or reflectances.
  `device` solves primary-weight optimisation problems such as melanopic silent
  substitution from response matrices.
- `io` is a foundation module for file IO. `plot` is a presentation layer and
  does not change scientific computation semantics.

## Root Convenience API

The package root provides a small lazy facade for common workflows:

```python
from color import from_cie1931_xyz_cmfs, reflectance_to_XYZ, convert_color
```

This facade is intentionally selective. It is useful for quick scripts and for
verifying that the toolbox is installed, but it does not replace module-level
APIs such as `color.recovery`, `color.gamut`, `color.device`, or `color.plot`.
Use `color/docs/<module>/README.md`, `README_DETAILS.md`, and `API_GUIDE.md` for
complete API coverage. These files are included in the wheel so they are
available in pip-installed environments.

## Module Overview

### Foundation

`constants / data / math / utils` provide standard constants, built-in data
files, pure numerical utilities, and shared validation/dispatch helpers.

```python
from color.constants import D65_XYZ
from color.math import gaussian_values
from color.utils import as_last_axis_triplets
```

### Data Sources

Static datasets:

```python
from color.datasets import get_color_card, get_reflectance_spectrum

macbeth = get_color_card("macbeth")
munsell = get_reflectance_spectrum("munsell_matt")
```

Generated spectra and model data:

```python
from color.generators import daylight_spd, multi_gaussian_spd

d65_like = daylight_spd(cct=6500)
led_like = multi_gaussian_spd(peak_wavelengths=(450, 540, 620))
```

Individualized LMS cone fundamentals:

```python
from color.individual_cone_fundamentals import (
    generate_asano2016_individual_cone_fundamentals,
)

lms = generate_asano2016_individual_cone_fundamentals(
    age=40,
    field_size_degree=10,
)
```

### Spectral Objects

Wrap raw column data into spectral objects:

```python
from color.datasets import get_color_card
from color.spectra import from_columns

raw = get_color_card("macbeth")
patch = from_columns(raw, y="Blue Sky", name="Macbeth Blue Sky")
aligned = patch.align(patch.shape)
```

### Colorimetry

Compute core colorimetric quantities from spectra:

```python
from color.colorimetry import XYZ_to_xy, analyze_temperature, reflectance_to_XYZ

XYZ = reflectance_to_XYZ(patch, illuminant="D65")
xy = XYZ_to_xy(XYZ)
temperature = analyze_temperature(xy)
```

### Color Models And Spaces

Explicit chromatic adaptation:

```python
from color.adaptation import adapt_to_D65
from color.constants import D50_XYZ

XYZ_D65 = adapt_to_D65(XYZ, source_white_XYZ=D50_XYZ)
```

Appearance model:

```python
from color.appearance import XYZ_to_CIECAM16
from color.constants import D65_XYZ

spec = XYZ_to_CIECAM16(XYZ, XYZ_w=D65_XYZ, L_A=64, Y_b=20)
```

Color-space conversion:

```python
from color.constants import D65_XYZ
from color.spaces import SpaceSpec, convert_color

XYZ_D65 = SpaceSpec("XYZ", whitepoint_XYZ=D65_XYZ)
Lab = convert_color(XYZ, "XYZ", "Lab")
Oklab = convert_color(XYZ, XYZ_D65, "Oklab")
sRGB = convert_color(XYZ, "XYZ", "sRGB")
```

### Analysis And Inverse Problems

Color difference:

```python
from color.difference import delta_E_CIE2000

delta_E = delta_E_CIE2000(Lab, Lab)
```

Gamut analysis:

```python
from color.gamut import analyze_gamut

analysis = analyze_gamut("Display P3")
print(analysis.xy_area, analysis.lab_volume)
```

Device response optimisation:

```python
from color.device import PrimaryResponseDisplay, melanopic_silent_range

display = PrimaryResponseDisplay(
    primary_responses,
    response_names=("l", "m", "s", "mel"),
)
target_LMS = display.LMS_from_weights([0.35, 0.45, 0.30, 0.20])
low, high = melanopic_silent_range(display, target_LMS, held="LMS")
```

Spectral or reflectance recovery:

```python
from color.recovery import recover_reflectance_from_XYZ

recovered = recover_reflectance_from_XYZ(
    XYZ,
    illuminant="D65",
    shape=patch.shape,
)
```

### Presentation And IO

Plot and save figures:

```python
from color.io import save_figure
from color.plot import plot_lines, plot_style

with plot_style("presentation"):
    fig, ax = plot_lines(
        (patch.wavelengths, patch.values),
        xlabel="Wavelength (nm)",
        ylabel="Reflectance",
    )
save_figure("patch_reflectance.png", fig=fig)
```

Read spectral tables or images:

```python
from color.io import read_image, read_spectral_csv

spectrum = read_spectral_csv("spectrum.csv", x="wavelength", y="spd")
image = read_image("image.png")
```

## End-To-End Example

The runnable companion script is:

[`examples/integration/example_01_long_colour_pipeline.py`](examples/integration/example_01_long_colour_pipeline.py)

Run it with:

```powershell
.\.venv\Scripts\python.exe examples\integration\example_01_long_colour_pipeline.py
```

It uses three input routes:

```text
1. generators -> spectra: generated three-peak LED emission spectrum.
2. spaces: encoded sRGB [0.4, 0.5, 0.6] converted to XYZ.
3. datasets -> spectra: Macbeth "Blue Sky" reflectance spectrum.
```

Main pipeline:

```text
datasets / generators
-> spectra
-> colorimetry: XYZ, LMS, xy, relative Y, CCT+Duv, dominant wavelength
-> spaces: Lab, Luv, Oklab, CAM16-UCS
-> adaptation: D65 -> D50 for CAM16 viewing
-> appearance: CIECAM16 correlates
-> difference: CIEDE2000 against Macbeth Foliage
-> gamut: coarse sRGB gamut analysis
-> recovery: Blue Sky XYZ back to reflectance
-> plot/io: save original-vs-recovered reflectance figure
```

Output figure:

```text
examples/integration/output/01_long_colour_pipeline_reflectance_recovery.png
```

`relative Y` is the luminance channel of `XYZ`. Applying `CCT / Duv` analysis to
an object-color `xy` is a chromaticity description, not a claim that the object
has a physical color temperature.

## Dependency Boundary

Main dependencies:

- `numpy`: arrays and numerical computation.
- `scipy`: optimization, interpolation, geometry, and numerical algorithms.
- `pandas`, `openpyxl`, `xlrd`: CSV / Excel data reading.
- `matplotlib`: plotting.
- `Pillow`, `imageio`: image IO.

Currently out of scope or not a focus:

- ICC/profile management.
- GUI or interactive applications.
- General multi-primary device color-space conversion or unique RGB/RGBC weight
  solving.
- Display calibration, LUT, temporal modulation, and full device-management
  workflows.
- Full CRI / TM-30 / CQS color-quality systems.

## Documentation

Installed module documentation lives under `color/docs/`. Most mature modules
have three documentation layers:

- `README.md`: English quick entrypoint.
- `README_DETAILS.md`: Chinese design notes, boundaries, and caveats.
- `API_GUIDE.md`: Chinese guide for top-level public APIs.

In a Python environment, locate the installed docs with:

```python
from pathlib import Path
import color

docs = Path(color.__file__).parent / "docs"
print(docs)
```

The source repository also provides `examples/` with runnable workflows. The
integration example is the best starting point for seeing how modules connect.

## Testing

Prefer focused tests during development, then run broader regression before
closing a larger change.

Common commands:

```powershell
.\.venv\Scripts\python.exe -m pytest color\<module>\tests -q --basetemp .pytest_tmp
.\.venv\Scripts\python.exe -m pytest -m "not examples" --import-mode=importlib -q --basetemp .pytest_tmp
.\.venv\Scripts\python.exe -m pytest -q --basetemp .pytest_tmp
```
