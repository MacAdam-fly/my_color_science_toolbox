# color.quality

`color.quality` contains colour-quality and light-quality metrics built on top
of the spectral, colorimetry and colour-space layers.

The first version implements the **Academy Spectral Similarity Index (SSI)**.
SSI compares the spectral shape of two light sources. It is useful when the
question is "how similar are these two SPDs?" rather than "how accurately does
this light render object colours?"

For the Chinese API guide, see [API_GUIDE.md](API_GUIDE.md). For Chinese
detailed notes, see [README_DETAILS.md](README_DETAILS.md).

## Current API

```python
from color.quality import spectral_similarity_index
```

## Quick Start

```python
from color.quality import spectral_similarity_index
from color.spectra import from_D65_illuminant, from_columns
from color.generators.leds import multi_led_spd

d65 = from_D65_illuminant()

raw_led = multi_led_spd(
    peak_wavelengths=(455, 535, 615),
    half_spectral_widths=(18, 28, 22),
    peak_power_ratios=(1.0, 0.8, 0.6),
)
led = from_columns(raw_led, y="spd", name="Example LED")

ssi = spectral_similarity_index(led, d65)
ssi_float = spectral_similarity_index(led, d65, round_result=False)
```

`round_result=True` follows the reference SSI presentation and returns the
rounded score. Use `round_result=False` for optimisation or diagnostics.

## What SSI Is Not

SSI is not CRI, TM-30 or CQS:

- SSI compares two spectral power distributions directly.
- CRI/TM-30/CQS evaluate colour rendering using standard reflectance samples.
- A high SSI to D65 means the light source spectrum resembles D65; it does not
  by itself guarantee good rendering under every object set.

CRI, TM-30 and CQS are planned as later `quality` additions because they require
standard colour sample datasets and more colourimetric processing.

## Examples

```powershell
.\.venv\Scripts\python.exe examples\quality\example_01_ssi.py
```

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest color\quality\tests -q --basetemp .pytest_tmp
```
