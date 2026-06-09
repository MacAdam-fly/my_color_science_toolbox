# IO Examples

Examples for `color.io` file readers and writers.

Generated files are written to `examples/io/output/`. The output directory is
ignored by Git except for `.gitkeep`.

## Examples

- `example_01_figure_export.py` - Build a simple spectral line plot and save it with `save_figure(...)`.
- `example_02_spectral_data_io.py` - Read real CSV variants, plot spectra and CIE 1931 xy, then write/read spectral CSV, Excel and JSON files.
- `example_03_image_io.py` - Read an image, boost Lab(D65) lightness, write edited sRGB and save a comparison figure.

## Inputs

- `input_csv/single_spd_standard_header_trailing_blank.csv` - single-channel spectral CSV with a standard header and an extra trailing blank row.
- `input_csv/single_spd_vendor_header.csv` - single-channel spectral CSV with a vendor header row.
- `input_csv/multi_spd_vendor_header.csv` - two-channel spectral CSV with a vendor header row.
- `input_csv/single_spd_chinese_header_gbk.csv` - single-channel spectral CSV with GBK Chinese column names.
- `input_image/test_img1.jpg` - RGB image used by the image IO example.

## Outputs

- `01_figure_export.png`
- `02_input_spectra_panels.png`
- `02_input_spectra_cie1931_xy.png`
- `02_roundtrip_single_spectral.csv`
- `02_roundtrip_single_spectral.xlsx`
- `02_roundtrip_single_spectral.json`
- `02_roundtrip_multi_spectral.csv`
- `02_roundtrip_multi_spectral.xlsx`
- `02_roundtrip_multi_spectral.json`
- `03_image_lab_lightness_x1p2.jpg`
- `03_image_lab_lightness_comparison.png`

Run one example:

```bash
python examples/io/example_02_spectral_data_io.py
```
