# Testing Guide

This project now has many unit tests and example smoke tests. Running the full
suite after every small change is unnecessary. Use this guide to choose the
smallest useful test set.

## 1. Local Module Tests

Run the tests for the module you changed first.

```powershell
.\venv\Scripts\python.exe -m pytest color\recovery\tests -q --basetemp .pytest_tmp
.\venv\Scripts\python.exe -m pytest color\spaces\tests -q --basetemp .pytest_tmp
.\venv\Scripts\python.exe -m pytest color\gamut\tests -q --basetemp .pytest_tmp
```

Use this for ordinary implementation changes.

## 2. Dependency-Aware Tests

If a module depends on several lower layers, run the dependent modules together.

Examples:

```powershell
# Recovery depends on datasets, spectra, and colorimetry.
.\venv\Scripts\python.exe -m pytest color\recovery\tests color\datasets\tests color\spectra\tests color\colorimetry\tests -q --basetemp .pytest_tmp

# Spaces changes often affect gamut, difference, and examples using conversion.
.\venv\Scripts\python.exe -m pytest color\spaces\tests color\gamut\tests color\difference\tests -q --basetemp .pytest_tmp

# Plot changes should include plot tests and selected example smoke tests.
.\venv\Scripts\python.exe -m pytest color\plot\tests -q --basetemp .pytest_tmp
```

Use this when changing shared APIs, conversion routes, dataset registration, or
plot primitives.

## 3. Example Smoke Tests

Example tests execute scripts under `examples/`. They are useful, but slower
than focused unit tests because they generate figures and run long pipelines.

All example smoke tests are marked with:

```python
@pytest.mark.examples
```

Example tests are parameterized by script, so the examples-only run reports one
pytest case per `examples/**/example_*.py` file.

Run only examples:

```powershell
.\venv\Scripts\python.exe -m pytest -m examples -q --basetemp .pytest_tmp
```

Skip examples:

```powershell
.\venv\Scripts\python.exe -m pytest -m "not examples" -q --basetemp .pytest_tmp
```

Run one module's examples:

```powershell
.\venv\Scripts\python.exe -m pytest color\recovery\tests\test_recovery_examples.py -q --basetemp .pytest_tmp
.\venv\Scripts\python.exe -m pytest color\gamut\tests\test_gamut_examples.py -q --basetemp .pytest_tmp
.\venv\Scripts\python.exe -m pytest color\plot\tests\test_plot_examples.py -q --basetemp .pytest_tmp
```

Use example tests after changing example scripts, plot output logic, or public
APIs demonstrated by examples.

## 4. Full Regression

Run the full suite when a feature is complete, when shared infrastructure
changes, or before committing.

```powershell
.\venv\Scripts\python.exe -m pytest -q --basetemp .pytest_tmp
```

Typical cases that justify a full run:

- changes to `color.datasets` registry or static data;
- changes to `color.spaces.convert_color`;
- changes to `color.plot` primitives or style behavior;
- changes to common utilities used across modules;
- major feature completion.

## Practical Default

For day-to-day work:

```powershell
# 1. local module
.\venv\Scripts\python.exe -m pytest color\<module>\tests -q --basetemp .pytest_tmp

# 2. skip examples when you only need unit confidence
.\venv\Scripts\python.exe -m pytest color\<module>\tests -m "not examples" -q --basetemp .pytest_tmp

# 3. full regression only at feature boundaries
.\venv\Scripts\python.exe -m pytest -q --basetemp .pytest_tmp
```
