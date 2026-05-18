# spectra examples

These examples show how `color.spectra` wraps raw `color.datasets` arrays as
spectral objects for interpolation, extrapolation, reshaping, export, and
arithmetic.

Run from the project root:

```powershell
.\.venv\Scripts\python.exe examples\spectra\example_single_distribution.py
.\.venv\Scripts\python.exe examples\spectra\example_multi_distribution.py
.\.venv\Scripts\python.exe examples\spectra\example_from_columns.py
.\.venv\Scripts\python.exe examples\spectra\example_interpolation_bounds.py
.\.venv\Scripts\python.exe examples\spectra\example_align_and_arithmetic.py
.\.venv\Scripts\python.exe examples\spectra\example_sample_and_aliases.py
.\.venv\Scripts\python.exe examples\spectra\example_interpolation_methods.py
.\.venv\Scripts\python.exe examples\spectra\example_extrapolation_strategies.py
.\.venv\Scripts\python.exe examples\spectra\example_multi_channel_workflow.py
.\.venv\Scripts\python.exe examples\spectra\example_export_formats.py
.\.venv\Scripts\python.exe examples\spectra\example_arithmetic_alignment.py
.\.venv\Scripts\python.exe examples\spectra\example_plot_single_distribution.py
.\.venv\Scripts\python.exe examples\spectra\example_plot_cmfs.py
.\.venv\Scripts\python.exe examples\spectra\example_plot_pmc_color_card.py
```

The examples intentionally focus on the spectral object layer. Use
`examples/colorimetry/` for XYZ/LMS spectral integration workflows.

Plot examples save PNG files under `examples/spectra/output/`.

Coverage
- `example_single_distribution.py`: registered single-channel dataset.
- `example_multi_distribution.py`: registered multi-channel CMFs.
- `example_from_columns.py`: user-provided raw column dictionaries.
- `example_sample_and_aliases.py`: `sample()`, `__call__()`, `domain`, `range`.
- `example_interpolation_methods.py`: `nearest`, `linear`, `pchip`, `sprague`.
- `example_interpolation_bounds.py`: bounds handling and fill values.
- `example_extrapolation_strategies.py`: `constant`, `linear`, `fill`, left/right.
- `example_align_and_arithmetic.py`: align, export shape, scalar arithmetic.
- `example_arithmetic_alignment.py`: align two signals before object arithmetic.
- `example_export_formats.py`: dict, NumPy, and pandas export.
- `example_plot_single_distribution.py`: visualize interpolation/extrapolation.
- `example_plot_cmfs.py`: visualize multi-channel CMFs.
- `example_plot_pmc_color_card.py`: wrap three PMC color-card patches and plot 0.5 nm interpolation.
