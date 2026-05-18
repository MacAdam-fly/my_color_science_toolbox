# color_agent

This package is a clean landing zone for color-related agent tools and models.

New layout blueprint:

```
color_agent/
	constants/   # matrices, white points, primaries
	core/        # shared types and small abstractions
	data/        # static datasets (CMF, spectra tables)
	icc/         # ICC profile parsing and transforms
	io/          # file readers/writers for spectra, CMF, ICC
	math/        # solvers, interpolation, fitting, simulation
	models/      # appearance/opponent/observer models
	plot/        # 2D/3D visualization helpers
	spectra/     # spectral object wrappers, interpolation, alignment
	spaces/      # color space definitions and conversions (XYZ centered)
	tools/       # high-level workflow toolkits
	utils/       # legacy helpers used during refactor
```

Entry points and naming:

- High-level workflows: `color_agent.tools.<module>`
- Common toolkit exports: `color_agent.tools` (e.g. `DeltaEToolkit`)
- Legacy underscore modules should add a thin alias module (e.g. `deltae` -> `delta_e`).
- Classes use CapWords; functions use snake_case; module names are lowercase ASCII.

Directory docs:

Each top-level directory has a README with purpose and naming rules. Keep new features out of `utils/` and migrate into `spaces`, `models`, `math`, or `tools` instead.
