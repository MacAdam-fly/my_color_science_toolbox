# Testing Guide

Use the smallest test set that gives useful confidence. The full suite is
available, but it does not need to run after every small change.

## 1. Local Module Tests

Run the tests for the module you changed first.

```powershell
.\.venv\Scripts\python.exe -m pytest color\<module>\tests -q --basetemp .pytest_tmp
```

Examples:

```powershell
.\.venv\Scripts\python.exe -m pytest color\spaces\tests -q --basetemp .pytest_tmp
.\.venv\Scripts\python.exe -m pytest color\recovery\tests -q --basetemp .pytest_tmp
.\.venv\Scripts\python.exe -m pytest color\gamut\tests -q --basetemp .pytest_tmp
```

## 2. Dependency-Aware Tests

Run related layers together when changing shared data, conversion routes,
registries, utility functions, or public APIs.

```powershell
# Recovery depends on datasets, spectra, and colorimetry.
.\.venv\Scripts\python.exe -m pytest color\recovery\tests color\datasets\tests color\spectra\tests color\colorimetry\tests -q --basetemp .pytest_tmp

# Spaces changes often affect gamut and difference.
.\.venv\Scripts\python.exe -m pytest color\spaces\tests color\gamut\tests color\difference\tests -q --basetemp .pytest_tmp

# Plot changes should include plot tests.
.\.venv\Scripts\python.exe -m pytest color\plot\tests -q --basetemp .pytest_tmp
```

## 3. Example Smoke Tests

Examples are marked with `examples`. Run them when changing example scripts,
plot output behavior, IO workflows, or public APIs shown by examples.

```powershell
# Run all examples.
.\.venv\Scripts\python.exe -m pytest -m examples -q --basetemp .pytest_tmp

# Skip examples for faster unit confidence.
.\.venv\Scripts\python.exe -m pytest -m "not examples" --import-mode=importlib -q --basetemp .pytest_tmp

# Run one module's examples.
.\.venv\Scripts\python.exe -m pytest color\recovery\tests\test_recovery_examples.py -q --basetemp .pytest_tmp
.\.venv\Scripts\python.exe -m pytest color\gamut\tests\test_gamut_examples.py -q --basetemp .pytest_tmp
.\.venv\Scripts\python.exe -m pytest color\plot\tests\test_plot_examples.py -q --basetemp .pytest_tmp
```

## 4. Regression Runs

Before considering a broad feature stable, run non-example regression:

```powershell
.\.venv\Scripts\python.exe -m pytest -m "not examples" --import-mode=importlib -q --basetemp .pytest_tmp
```

Before release or after large shared changes, run the full suite:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .pytest_tmp
```

## Practical Default

1. Change one module -> run that module's tests.
2. Change shared infrastructure -> run dependency-aware tests.
3. Change examples, plotting, or IO demos -> run example smoke tests.
4. Finish a feature or cleanup -> run `pytest -m "not examples"`.
5. Before release or major merge -> run the full suite.
