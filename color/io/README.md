# io

Purpose
- File readers and writers for spectra, figures, CMF, and ICC artifacts.

Naming
- Use `reader_*` / `writer_*` or `load_*` / `save_*` patterns.
- Figure export lives here, not in `color.plot`, because saving files is an IO
  operation rather than a plotting primitive.

Entry points
- Prefer `color.io.<module>` for IO utilities.
- `save_figure(...)` is exported from `color.io` for Matplotlib figure export.
