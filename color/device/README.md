# color.device

`color.device` contains display-device helpers that operate on primary drive
weights and response matrices.

The current scope is multi-primary melanopic silent substitution: keep either
LMS or XYZ responses unchanged while finding the minimum and maximum
melanopic / ipRGC activation. It does not implement ICC, LUT calibration,
RGB colour-space conversion, temporal modulation, or display-management
workflows.

## Public API

- `PrimaryResponseDisplay`
- `melanopic_silent_range`

`melanopic_silent_range(...)` returns internal result objects with fields such
as `weights`, `responses`, `target_responses`, `melanopic`, `held`, `objective`,
`residual`, and `success`. The result class is available from the
`color.device.silent_substitution` submodule for advanced inspection, but it is
not part of the top-level public API.

## Quick Start

```python
import numpy as np

from color.device import PrimaryResponseDisplay, melanopic_silent_range

display = PrimaryResponseDisplay(
    [
        [0.70, 0.30, 0.02, 0.10],  # R: l, m, s, mel
        [0.25, 0.80, 0.10, 0.20],  # G
        [0.05, 0.15, 0.70, 0.65],  # B
        [0.20, 0.55, 0.45, 0.95],  # C
    ],
    response_names=("l", "m", "s", "mel"),
    primary_names=("R", "G", "B", "C"),
)

baseline = np.array([0.35, 0.45, 0.30, 0.20])
target_LMS = display.LMS_from_weights(baseline)

low, high = melanopic_silent_range(display, target_LMS, held="LMS")
print(low.weights, high.weights)
print(low.melanopic, high.melanopic)
```

## Documentation

- Chinese design notes: [`README_DETAILS.md`](README_DETAILS.md)
- API guide: [`API_GUIDE.md`](API_GUIDE.md)
