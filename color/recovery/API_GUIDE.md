# color.recovery API 使用指南

本文档覆盖 `color.recovery.__all__` 中的顶层 API。设计语义和方法选择理由见
[`README_DETAILS.md`](README_DETAILS.md)。

## 快速选择

```text
effective spectrum from responses -> recover_spectrum_from_responses
effective spectrum from XYZ       -> recover_spectrum_from_XYZ
effective spectrum from xyY       -> recover_spectrum_from_xyY
effective spectrum from LMS       -> recover_spectrum_from_LMS

reflectance from XYZ              -> recover_reflectance_from_XYZ
reflectance from xyY              -> recover_reflectance_from_xyY

database prior                    -> load_reflectance_library + PCA/Dictionary options
```

## 基本约定

- `XYZ` 使用项目统一 `Y=100` 标度。
- 单点输入 shape 为 `(3,)`，返回 `SpectralDistribution`。
- 批量输入 shape 为 `(n, 3)`，返回 `MultiSpectralDistribution`。
- `labels` 只用于批量输出；数量必须等于样本数。
- 结果不是唯一真实光谱，而是在当前 method 先验和约束下的一条可行解。

## Recovery 入口

### `recover_spectrum_from_responses(target, responses, ...)`

从任意三通道响应函数恢复 effective spectrum。

```python
from color.recovery import BoundedLeastSquaresOptions, recover_spectrum_from_responses
from color.spectra import from_cie1931_xyz_cmfs

responses = from_cie1931_xyz_cmfs()
spectrum = recover_spectrum_from_responses(
    [24.0, 20.0, 18.0],
    responses,
    method=BoundedLeastSquaresOptions(bounds=(0.0, float("inf"))),
)
```

批量：

```python
spectra = recover_spectrum_from_responses(
    [[24.0, 20.0, 18.0], [12.0, 10.0, 9.0]],
    responses,
    labels=("sample_a", "sample_b"),
)
```

### `recover_spectrum_from_XYZ(XYZ, ...)`

从 `XYZ(Y=100)` 恢复 effective spectrum。自发光场景下可以把结果解释为 SPD。

```python
from color.recovery import BoundedLeastSquaresOptions, recover_spectrum_from_XYZ

spectrum = recover_spectrum_from_XYZ(
    [24.0, 20.0, 18.0],
    method=BoundedLeastSquaresOptions(bounds=(0.0, float("inf"))),
)
```

参数化高斯：

```python
from color.recovery import GaussianRecoveryOptions, recover_spectrum_from_XYZ

spectrum = recover_spectrum_from_XYZ(
    [24.0, 20.0, 18.0],
    method=GaussianRecoveryOptions(sigma_bounds=(2.0, 120.0)),
)
```

自动高斯策略：

```python
from color.recovery import AutoGaussianRecoveryOptions, recover_spectrum_from_XYZ

spectrum = recover_spectrum_from_XYZ(
    [24.0, 20.0, 18.0],
    method=AutoGaussianRecoveryOptions(n_components=2),
)
```

### `recover_spectrum_from_xyY(xyY, ...)`

从 `xyY` 恢复 effective spectrum。内部先转为 XYZ。

```python
from color.recovery import BoundedLeastSquaresOptions, recover_spectrum_from_xyY

spectrum = recover_spectrum_from_xyY(
    [0.32, 0.31, 20.0],
    method=BoundedLeastSquaresOptions(bounds=(0.0, float("inf"))),
)
```

### `recover_spectrum_from_LMS(LMS, ...)`

从 LMS cone responses 恢复 effective spectrum。

```python
from color.recovery import recover_spectrum_from_LMS

spectrum = recover_spectrum_from_LMS(
    [12.0, 14.0, 3.0],
    fundamentals="cie2006_lms2_linE_1nm",
    fill_nan=0.0,
)
```

`fill_nan=0.0` 用于 CVRL LMS 表中 S 通道长波端空白作为零响应的计算语义。

### `recover_reflectance_from_XYZ(XYZ, ...)`

在指定 illuminant 和 CMFs 下，从 `XYZ(Y=100)` 恢复 bounded reflectance。

```python
from color.recovery import BoundedLeastSquaresOptions, recover_reflectance_from_XYZ

reflectance = recover_reflectance_from_XYZ(
    [24.0, 20.0, 18.0],
    illuminant="D65",
    cmfs="cie1931_xyz_1nm",
    method=BoundedLeastSquaresOptions(bounds=(0.0, 1.0), smoothness=1e-3),
)
```

Burns 2019：

```python
from color.recovery import Burns2019RecoveryOptions, recover_reflectance_from_XYZ

reflectance = recover_reflectance_from_XYZ(
    [24.0, 20.0, 18.0],
    illuminant="D65",
    method=Burns2019RecoveryOptions(),
)
```

PCA：

```python
from color.recovery import (
    PCAReflectanceOptions,
    load_reflectance_library,
    recover_reflectance_from_XYZ,
)

library = load_reflectance_library("munsell_matt")
reflectance = recover_reflectance_from_XYZ(
    [24.0, 20.0, 18.0],
    illuminant="D65",
    method=PCAReflectanceOptions(library=library, n_components=12),
)
```

Dictionary：

```python
from color.recovery import DictionaryReflectanceOptions, recover_reflectance_from_XYZ

reflectance = recover_reflectance_from_XYZ(
    [24.0, 20.0, 18.0],
    illuminant="D65",
    method=DictionaryReflectanceOptions(
        library=library,
        top_k=120,
        regularization=1e-6,
    ),
)
```

字符串 method 兼容写法仍可用，但 PCA / dictionary 仍必须显式传入 `library`：

```python
reflectance = recover_reflectance_from_XYZ(
    [24.0, 20.0, 18.0],
    method="dictionary",
    library=library,
    dictionary_top_k=120,
)
```

### `recover_reflectance_from_xyY(xyY, ...)`

从 `xyY` 恢复 reflectance。内部先转为 XYZ。

```python
from color.recovery import recover_reflectance_from_xyY

reflectance = recover_reflectance_from_xyY(
    [0.32, 0.31, 20.0],
    illuminant="D65",
)
```

批量：

```python
reflectances = recover_reflectance_from_xyY(
    [[0.32, 0.31, 20.0], [0.40, 0.32, 35.0]],
    labels=("sample_a", "sample_b"),
)
```

## Method Options

Options 对象是推荐写法。不要把 options 对象和同一 method 的额外关键字混用。

### `BoundedLeastSquaresOptions`

用于 spectrum 和 reflectance 的平滑有界最小二乘。

```python
from color.recovery import BoundedLeastSquaresOptions

spectrum_options = BoundedLeastSquaresOptions(bounds=(0.0, float("inf")), smoothness=1e-3)
reflectance_options = BoundedLeastSquaresOptions(bounds=(0.0, 1.0), smoothness=1e-3)
```

`bounds=None` 时，入口会使用默认域：spectrum 为 `(0, inf)`，reflectance 为 `(0, 1)`。

### `GaussianRecoveryOptions`

单高斯 effective spectrum。

```python
from color.recovery import GaussianRecoveryOptions

options = GaussianRecoveryOptions(
    sigma_bounds=(2.0, 120.0),
    use_dominant_wavelength_initial=True,
)
```

### `MultiGaussianRecoveryOptions`

多高斯 effective spectrum，当前支持 `n_components=2` 或 `3`。

```python
from color.recovery import MultiGaussianRecoveryOptions

options = MultiGaussianRecoveryOptions(n_components=2)
```

### `AutoGaussianRecoveryOptions`

自动选择 single / multi Gaussian 的策略。

```python
from color.recovery import AutoGaussianRecoveryOptions

options = AutoGaussianRecoveryOptions(n_components=3)
```

### `Burns2019RecoveryOptions`

Burns 2019 Method 3 reflectance recovery。

```python
from color.recovery import Burns2019RecoveryOptions

options = Burns2019RecoveryOptions(max_iterations=50, tolerance=1e-8)
```

当前只支持 `bounds=(0, 1)`。

### `Meng2015RecoveryOptions`

Meng 2015 reflectance recovery。

```python
from color.recovery import Meng2015RecoveryOptions

options = Meng2015RecoveryOptions(bounds=(0.0, 1.0))
```

### `PCAReflectanceOptions`

PCA reflectance recovery。必须显式传入 `ReflectanceLibrary`。

```python
from color.recovery import PCAReflectanceOptions, load_reflectance_library

library = load_reflectance_library("munsell_matt")
options = PCAReflectanceOptions(
    library=library,
    n_components=12,
    coefficient_regularization=1e-3,
)
```

### `DictionaryReflectanceOptions`

Convex dictionary reflectance recovery。必须显式传入 `ReflectanceLibrary`。

```python
from color.recovery import DictionaryReflectanceOptions

options = DictionaryReflectanceOptions(
    library=library,
    top_k=120,
    regularization=1e-6,
)
```

`top_k=None` 表示使用完整 library；计算量会更大。

## Reflectance Library

### `ReflectanceLibrary`

保存统一 shape 下的反射谱矩阵：

```text
wavelengths
reflectances
labels
sources
shape
metadata
```

数组是只读的。

### `load_reflectance_library(datasets=("munsell_matt",), shape=None)`

默认库：

```python
from color.recovery import load_reflectance_library

library = load_reflectance_library()
print(library.metadata["datasets"])
print(library.reflectances.shape)
```

显式多数据集：

```python
library = load_reflectance_library(("munsell_matt", "agfa_it872"))
```

当前全部 UEF 反射谱：

```python
library = load_reflectance_library("all_uef")
```

自定义 shape：

```python
from color.spectra import SpectralShape

library = load_reflectance_library(
    "munsell_matt",
    shape=SpectralShape(400, 700, 2),
)
```

`"all_uef"` 只表示当前 UEF 来源，不代表未来所有反射谱来源。

### PCA / dictionary 与 shape 对齐

PCA 和 dictionary 要求 recovery 积分矩阵与 `ReflectanceLibrary` 使用同一
`SpectralShape`。

```python
from color.recovery import (
    PCAReflectanceOptions,
    load_reflectance_library,
    recover_reflectance_from_XYZ,
)
from color.spectra import SpectralShape

shape = SpectralShape(400, 700, 2)
library = load_reflectance_library("munsell_matt", shape=shape)
options = PCAReflectanceOptions(library=library)
```

调用 recovery 时推荐省略 `shape`，让入口使用 `library.shape`：

```python
reflectance = recover_reflectance_from_XYZ(
    [24.0, 20.0, 18.0],
    illuminant="D65",
    method=options,
)
```

如果显式传入 `shape`，必须与 library 的波长网格一致。

## 矩阵与 Solver

### `response_recovery_matrix(responses, shape=None, k=1.0)`

构造：

```text
target = A @ spectrum
A = k * interval * responses.T
```

```python
from color.recovery import response_recovery_matrix
from color.spectra import from_cie1931_xyz_cmfs

responses = from_cie1931_xyz_cmfs()
A, wavelengths, shape = response_recovery_matrix(responses)
```

### `reflectance_recovery_matrix(cmfs="cie1931_xyz_1nm", illuminant="D65", shape=None)`

构造：

```text
XYZ = A @ reflectance
A = k * interval * (illuminant * CMFs).T
k = 100 / sum(illuminant * ybar * interval)
```

```python
from color.recovery import reflectance_recovery_matrix

A, wavelengths, shape = reflectance_recovery_matrix(
    cmfs="cie1931_xyz_1nm",
    illuminant="D65",
)
```

### `second_difference_matrix(size)`

构造二阶差分平滑矩阵。

```python
from color.recovery import second_difference_matrix

D = second_difference_matrix(10)
```

### `solve_bounded_least_squares(targets, matrix, bounds, smoothness)`

共享底层 solver。普通用户通常不需要直接调用。

```python
import numpy as np
from color.recovery import solve_bounded_least_squares

A = np.array([[1.0, 0.5, 0.0], [0.0, 0.5, 1.0], [0.2, 0.2, 0.2]])
targets = np.array([[1.0, 1.0, 0.4]])
x = solve_bounded_least_squares(
    targets,
    A,
    bounds=(0.0, 1.0),
    smoothness=0.0,
)
```

## Method Registry

### `SPECTRUM_RECOVERY_METHODS` / `REFLECTANCE_RECOVERY_METHODS`

查看当前注册方法。

```python
from color.recovery import SPECTRUM_RECOVERY_METHODS, REFLECTANCE_RECOVERY_METHODS

print(SPECTRUM_RECOVERY_METHODS.keys())
print(REFLECTANCE_RECOVERY_METHODS.keys())
```

当前注册方法：

```text
SPECTRUM_RECOVERY_METHODS:
  bounded_least_squares
  gaussian
  multi_gaussian
  auto_gaussian

REFLECTANCE_RECOVERY_METHODS:
  bounded_least_squares
  burns2019
  meng2015
  pca
  dictionary
```

### `resolve_spectrum_recovery_method(method)` / `resolve_reflectance_recovery_method(method)`

解析 method 名称到规范名和 solver。

```python
from color.recovery import (
    resolve_reflectance_recovery_method,
    resolve_spectrum_recovery_method,
)

name, solver = resolve_spectrum_recovery_method("bounded least squares")
name_reflectance, solver_reflectance = resolve_reflectance_recovery_method("PCA")
```

## 与其它模块串联

从其它颜色空间进入 recovery：

```python
from color.constants import D65_XYZ
from color.recovery import recover_reflectance_from_XYZ
from color.spaces import SpaceSpec, convert_color

XYZ = convert_color(
    Lab,
    SpaceSpec("Lab", whitepoint_XYZ=D65_XYZ),
    "XYZ",
)
reflectance = recover_reflectance_from_XYZ(XYZ, illuminant="D65")
```

验证闭合：

```python
from color.colorimetry import reflectance_to_XYZ

closed_XYZ = reflectance_to_XYZ(reflectance, illuminant="D65")
```
