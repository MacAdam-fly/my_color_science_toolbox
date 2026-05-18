# Standard Illuminant Spectral Data

**Folder:** `color/data/illuminants/`

This folder stores static CIE illuminant reference files. Public loading APIs
live in `color.datasets.illuminants`.

## Files

### CIE Standard Illuminants

| File | Description | Loader |
| --- | --- | --- |
| `illuminant_A.csv` | CIE Illuminant A | `get_illuminant("A")` |
| `illuminant_D65.csv` | CIE Illuminant D65 | `get_illuminant("D65")` |
| `Fluorescents.xls` | CIE F1-F12 fluorescent lamp SPDs | `get_illuminant("fluorescents")` |

### Reference Data

| File | Description | Use |
| --- | --- | --- |
| `reference/DaylightSeries.xlsx` | CIE D-series daylight table | Reference/validation |
| `reference/blackbody.xlsx` | Planck blackbody table | Reference/validation |

Formula-generated blackbody radiation and CIE illuminants are provided by
`color.generators.blackbody` and `color.generators.illuminants`:

```python
from color.generators.blackbody import blackbody_spd
from color.generators.illuminants import daylight_spd, illuminant_a_spd

bb = blackbody_spd(temperature=6500)
a = illuminant_a_spd()
d50 = daylight_spd(cct=5000)
```

## References

- CIE (2004). Colorimetry, 3rd edition. CIE 15:2004.
- Wyszecki, G. & Stiles, W.S. Color Science: Concepts and Methods. Wiley.
- CVRL. http://www.cvrl.org/
- RIT Munsell Color Science Lab. https://www.rit.edu/science/munsell-color-science-lab-educational-resources
