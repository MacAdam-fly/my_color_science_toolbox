# spectra examples

These examples show how `color.spectra` wraps raw arrays as immutable spectral
objects for sampling, interpolation, extrapolation, alignment, export and basic
arithmetic.

The directory is intentionally small. Read the numbered files in order:

```text
datasets / raw columns -> spectra -> sampling / alignment / export / plots
```

Use `examples/colorimetry/` for XYZ/LMS spectral integration workflows.

## Run

Run individual examples from the project root:

```powershell
.\.venv\Scripts\python.exe examples\spectra\example_01_create_spectral_objects.py
.\.venv\Scripts\python.exe examples\spectra\example_02_sampling_interpolation_alignment.py
.\.venv\Scripts\python.exe examples\spectra\example_03_multi_channel_workflow.py
.\.venv\Scripts\python.exe examples\spectra\example_04_export_and_arithmetic.py
.\.venv\Scripts\python.exe examples\spectra\example_05_visualization_cases.py
```

Plot outputs are written to `examples/spectra/output/`.

## Guide

`example_01_create_spectral_objects.py` shows the object creation paths:
registered datasets with `from_dataset(...)`, in-memory column mappings with
`from_columns(...)`, semantic shortcuts such as `from_D65_illuminant()` /
`from_cie1931_xyz_cmfs(...)`, and direct `SpectralDistribution` /
`MultiSpectralDistribution` construction. It also clarifies that `y` selects one
value column while `ys` selects multiple value columns.

`example_02_sampling_interpolation_alignment.py` covers the main domain
operations: `sample()`, `__call__()`, `domain`, `range`, `interpolate()`,
`reshape()`, `trim()`, `extrapolate()` and `align()`. It compares `nearest`,
`linear`, `pchip` and `sprague` interpolation and shows explicit out-of-domain
handling.

`example_03_multi_channel_workflow.py` focuses on multi-channel objects such as
XYZ CMFs and PMC colour-card patches. It demonstrates labels, `keys()`,
dictionary-like `obj["channel"]` access, `channel(label)`, multi-channel
reshape and a shared wavelength domain.

`example_04_export_and_arithmetic.py` shows `to_dict()`, `to_numpy()`,
`to_pandas()`, scalar arithmetic and object arithmetic. It intentionally shows
that object arithmetic requires matching wavelength domains, so callers should
align explicitly before multiplying two spectral objects.

`example_05_visualization_cases.py` generates three focused plots:

- single-channel interpolation and extrapolation strategies
- CIE 1931 XYZ CMFs before and after reshape
- three PMC colour-card patches with source samples and PCHIP interpolation

The examples only demonstrate the spectral object layer. They do not compute
XYZ, LMS or photometric responses; those integrations live in
`color.colorimetry` and `examples/colorimetry/`.
