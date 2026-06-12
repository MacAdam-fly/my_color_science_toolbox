# color.io

`color.io` contains lightweight file readers and writers for objects already
used by the toolbox. It does not register datasets, perform colour management,
or change scientific computation semantics.

## Public API

Figure export:

- `save_figure`

Spectral object IO:

- `spectral_to_dataframe`
- `spectral_from_dataframe`
- `read_spectral_csv`
- `write_spectral_csv`
- `read_spectral_excel`
- `write_spectral_excel`
- `read_spectral_json`
- `write_spectral_json`

Image IO:

- `read_image`
- `write_image`
- `read_sRGB_image`
- `write_sRGB_image`

## Quick Start

```python
from color.io import read_spectral_json, write_spectral_json
from color.spectra import SpectralDistribution

sd = SpectralDistribution([400, 500, 600], [0.1, 0.8, 0.2], name="sample")

write_spectral_json("sample.json", sd)
sd2 = read_spectral_json("sample.json")
```

```python
from color.io import read_image, read_sRGB_image, write_sRGB_image

raw_codes = read_image("input.png", as_float=False)
image = read_sRGB_image("input.jpg")
write_sRGB_image("preview.png", image)
```

For detailed design notes, see `README_DETAILS.md`. For per-API examples, see
`API_GUIDE.md`.
