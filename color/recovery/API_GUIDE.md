# color.recovery API 使用指南

本文档按 `color.recovery.__all__` 覆盖当前顶层 API。这里写最小使用案例；
反问题语义、通用 spectrum recovery 与 reflectance recovery 的区别见
[`README_DETAILS.md`](README_DETAILS.md)。

`color.recovery` 当前只实现 bounded smooth least-squares。PCA、basis/dictionary、
Meng、Smits 等方法尚未实现；方法注册表只是为后续扩展预留。

## 顶层 API 总览

### 普通恢复入口

| API | 功能 |
| --- | --- |
| `recover_spectrum_from_responses` | 从任意三通道响应恢复 effective spectrum |
| `recover_spectrum_from_XYZ` | 从 XYZ 恢复 effective spectrum |
| `recover_spectrum_from_LMS` | 从 LMS 恢复 effective spectrum |
| `recover_reflectance_from_XYZ` | 从 XYZ 恢复 bounded smooth reflectance |
| `recover_reflectance_from_xyY` | 从 xyY 恢复 bounded smooth reflectance |

### 高级/开发入口

| API | 功能 |
| --- | --- |
| `response_recovery_matrix` | 构造 `target = A @ spectrum` 的线性矩阵 |
| `reflectance_recovery_matrix` | 构造 `XYZ = A @ reflectance` 的线性矩阵 |
| `second_difference_matrix` | 构造二阶差分平滑矩阵 |
| `solve_bounded_least_squares` | 有界平滑最小二乘 solver |
| `SPECTRUM_RECOVERY_METHODS`, `REFLECTANCE_RECOVERY_METHODS` | recovery method 注册表 |
| `resolve_spectrum_recovery_method`, `resolve_reflectance_recovery_method` | 解析 method 名称 |

## 基本约定

- `XYZ` 使用项目统一 `Y=100` 标度。
- 单点输入 shape 为 `(3,)`，返回 `SpectralDistribution`。
- 批量输入 shape 为 `(n, 3)`，返回 `MultiSpectralDistribution`。
- 结果不是唯一真实光谱，而是在 bounds 和 smoothness 约束下的一条可行光谱。
- 当前 `method` 只支持 `"bounded_least_squares"` 及其别名。

## 通用 effective spectrum recovery

### `recover_spectrum_from_responses(target, responses, ...)`

用途：从任意三通道响应函数和目标三通道响应恢复 effective spectrum。

```python
from color.recovery import recover_spectrum_from_responses
from color.spectra import from_cie1931_xyz_cmfs

cmfs = from_cie1931_xyz_cmfs(interval_nm=1)

spectrum = recover_spectrum_from_responses(
    [24.0, 20.0, 18.0],
    cmfs,
    bounds=(0.0, float("inf")),
    smoothness=1e-3,
)
```

批量恢复：

```python
spectra = recover_spectrum_from_responses(
    [[24.0, 20.0, 18.0], [40.0, 35.0, 30.0]],
    cmfs,
    labels=("sample_a", "sample_b"),
)
```

注意：`responses` 必须是三通道 `MultiSpectralDistribution`。

### `recover_spectrum_from_XYZ(XYZ, cmfs="cie1931_xyz_1nm", ...)`

用途：从 XYZ 恢复 effective spectrum。自发光场景下可以把它解释为一条可行 SPD。

```python
from color.colorimetry import emission_to_XYZ
from color.recovery import recover_spectrum_from_XYZ

target_XYZ = [24.0, 20.0, 18.0]
spectrum = recover_spectrum_from_XYZ(
    target_XYZ,
    cmfs="cie1931_xyz_1nm",
    bounds=(0.0, float("inf")),
    smoothness=1e-3,
)

closed_XYZ = emission_to_XYZ(spectrum, cmfs="cie1931_xyz_1nm")
```

自定义 shape：

```python
from color.spectra import SpectralShape

spectrum = recover_spectrum_from_XYZ(
    target_XYZ,
    shape=SpectralShape(400, 700, 5),
)
```

### `recover_spectrum_from_LMS(LMS, fundamentals="cie2006_lms2_linE_1nm", fill_nan=0.0, ...)`

用途：从 LMS 响应恢复 effective spectrum。

```python
from color.colorimetry import emission_to_LMS
from color.recovery import recover_spectrum_from_LMS

target_LMS = [12.0, 14.0, 3.0]
spectrum = recover_spectrum_from_LMS(
    target_LMS,
    fundamentals="cie2006_lms2_linE_1nm",
    fill_nan=0.0,
)

closed_LMS = emission_to_LMS(
    spectrum,
    fundamentals="cie2006_lms2_linE_1nm",
    fill_nan=0.0,
)
```

注意：`fill_nan=0.0` 用于 CVRL LMS 表中 S 通道长波端空白作为零响应的计算语义。

## Reflectance recovery

### `recover_reflectance_from_XYZ(XYZ, illuminant="D65", cmfs="cie1931_xyz_1nm", ...)`

用途：在指定照明体和 CMFs 下，从 XYZ 恢复 bounded smooth reflectance。

```python
from color.colorimetry import reflectance_to_XYZ
from color.recovery import recover_reflectance_from_XYZ

target_XYZ = [24.0, 20.0, 18.0]
reflectance = recover_reflectance_from_XYZ(
    target_XYZ,
    illuminant="D65",
    cmfs="cie1931_xyz_1nm",
    bounds=(0.0, 1.0),
    smoothness=1e-3,
)

closed_XYZ = reflectance_to_XYZ(
    reflectance,
    illuminant="D65",
    cmfs="cie1931_xyz_1nm",
)
```

批量恢复：

```python
reflectances = recover_reflectance_from_XYZ(
    [[24.0, 20.0, 18.0], [40.0, 35.0, 30.0]],
    illuminant="D65",
    labels=("patch_a", "patch_b"),
)
```

注意：反射率默认 `bounds=(0, 1)`。不要先恢复 effective spectrum 再除以 illuminant；
那样约束没有施加在 reflectance 上。

### `recover_reflectance_from_xyY(xyY, **kwargs)`

用途：从 xyY 恢复 reflectance，内部先转 XYZ。

```python
from color.recovery import recover_reflectance_from_xyY

reflectance = recover_reflectance_from_xyY(
    [0.3127, 0.3290, 20.0],
    illuminant="D65",
    cmfs="cie1931_xyz_1nm",
)
```

批量：

```python
reflectances = recover_reflectance_from_xyY(
    [[0.3127, 0.3290, 20.0], [0.40, 0.32, 35.0]],
    labels=("sample_a", "sample_b"),
)
```

## 矩阵构造

### `response_recovery_matrix(responses, shape=None, k=1.0)`

用途：构造通用 response recovery 的线性矩阵。

```python
from color.recovery import response_recovery_matrix
from color.spectra import from_cie1931_xyz_cmfs

cmfs = from_cie1931_xyz_cmfs(interval_nm=1)
A, wavelengths, shape = response_recovery_matrix(cmfs)
```

数学语义：

```text
target = A @ spectrum
A = k * interval * responses.T
```

### `reflectance_recovery_matrix(cmfs="cie1931_xyz_1nm", illuminant="D65", shape=None)`

用途：构造与 `reflectance_to_XYZ(...)` 一致的反射率积分矩阵。

```python
from color.recovery import reflectance_recovery_matrix

A, wavelengths, shape = reflectance_recovery_matrix(
    cmfs="cie1931_xyz_1nm",
    illuminant="D65",
)
```

数学语义：

```text
XYZ = A @ reflectance
A = k * interval * (illuminant * CMFs).T
k = 100 / sum(illuminant * ybar * interval)
```

## Solver

### `second_difference_matrix(size)`

用途：构造二阶差分平滑矩阵。

```python
from color.recovery import second_difference_matrix

D = second_difference_matrix(10)
```

用于平滑项：

```text
smoothness * ||D r||²
```

### `solve_bounded_least_squares(targets, matrix, bounds, smoothness)`

用途：求解共享的有界平滑最小二乘问题。

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

注意：普通用户不需要直接调用 solver；它主要服务后续 recovery methods。

## Method Registry

### `SPECTRUM_RECOVERY_METHODS` / `REFLECTANCE_RECOVERY_METHODS`

用途：查看当前注册的 spectrum / reflectance recovery 方法。

```python
from color.recovery import SPECTRUM_RECOVERY_METHODS, REFLECTANCE_RECOVERY_METHODS

print(SPECTRUM_RECOVERY_METHODS.keys())
print(REFLECTANCE_RECOVERY_METHODS.keys())
```

当前只有：

```text
bounded_least_squares
```

### `resolve_spectrum_recovery_method(method)` / `resolve_reflectance_recovery_method(method)`

用途：解析 method 名称到规范名和 solver。

```python
from color.recovery import (
    resolve_reflectance_recovery_method,
    resolve_spectrum_recovery_method,
)

name, solver = resolve_spectrum_recovery_method("bounded least squares")
name_reflectance, solver_reflectance = resolve_reflectance_recovery_method(
    "BoundedLeastSquares"
)
```

注意：这些是开发入口。未来新增 PCA、basis/dictionary、Meng、Smits 等方法时，
会通过这里的注册表分发。

## 与其它模块串联

RGB 或 Lab 输入必须先显式转为 XYZ：

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

恢复结果可以继续作为光谱对象进入 `color.colorimetry`：

```python
from color.colorimetry import reflectance_to_XYZ

closed_XYZ = reflectance_to_XYZ(reflectance, illuminant="D65")
```
