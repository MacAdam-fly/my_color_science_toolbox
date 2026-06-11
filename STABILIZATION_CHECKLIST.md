# Stabilization Checklist

This project has moved past exploratory API growth. Use this checklist when
preparing modules for a stable release or when reviewing broad refactors.

## Public API Boundaries

- Keep package-level `__all__` focused on regular user workflows.
- Keep registries, solver internals, matrix builders, low-level constants, and
  implementation helpers in their submodules unless they are core user entry
  points.
- When top-level APIs change, update the module `README.md`,
  `README_DETAILS.md`, and `API_GUIDE.md` in the same change.
- Every top-level API name in `__all__` should appear in the corresponding
  `API_GUIDE.md`.

## Runtime Validation

- Do not use `assert` for production runtime validation. Use explicit
  `ValueError`, `TypeError`, or a narrower domain-specific exception.
- Test code can continue to use `assert`.
- Validation should protect public inputs and important internal invariants
  that would otherwise fail with unclear NumPy or SciPy errors.

## Python File Baseline

- Every Python file under `color/` should include:

  ```python
  from __future__ import annotations
  ```

- Use explicit `__all__` in public modules and package aggregators.
- Prefer dataclasses for structured result/config objects when they make the
  interface clearer; avoid adding dataclasses for simple temporary tuples.

## Documentation Baseline

- `README.md`: concise English quick start and current public API overview.
- `README_DETAILS.md`: Chinese design notes, constraints, and important
  technical caveats. Do not remove useful explanations merely because examples
  moved elsewhere.
- `API_GUIDE.md`: Chinese usage guide for top-level public APIs, with multiple
  minimal examples when an API supports multiple input forms or workflows.
- Public API docstrings should be compact reference text, not a duplicate of
  `API_GUIDE.md`. Prioritize docstrings when an API has non-obvious units,
  shape rules, whitepoint/reference-domain semantics, method dispatch, or
  important failure modes.
- Chinese documentation should be written and read as UTF-8.

## Dependencies

- Treat NumPy as the numerical base layer.
- Document feature-level dependencies clearly when a module relies on SciPy,
  Matplotlib, image IO, or Excel/JSON tooling.
- Do not add optional-dependency fallback logic unless the project has a clear
  degraded mode and tests for it.

## Testing Workflow

- Run the local module tests first.
- Run dependency-aware tests when changing shared registries, conversion
  routes, datasets, or utility layers.
- Run `pytest -m "not examples"` before considering a broad feature stable.
- Run `pytest -m examples` when public examples, plotting behavior, or
  demonstrated APIs change.
