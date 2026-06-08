# color.recovery API 使用指南

本文档按 `color.recovery.__all__` 覆盖当前顶层 API。这里写最小使用案例；
反问题语义、通用 spectrum recovery 与 reflectance recovery 的区别见
[`README_DETAILS.md`](README_DETAILS.md)。

`color.recovery` 当前实现 bounded smooth least-squares、Gaussian parametric
spectrum recovery、Meng 2015、reflectance PCA 和 convex dictionary recovery。
Smits、basis 等方法尚未实现；方法注册表会继续作为扩展入口。

## 顶层 API 总览

### 普通恢复入口

| API | 功能 |
| --- | --- |
| `recover_spectrum_from_responses` | 从任意三通道响应恢复 effective spectrum |
| `recover_spectrum_from_XYZ` | 从 XYZ 恢复 effective spectrum |
| `recover_spectrum_from_LMS` | 从 LMS 恢复 effective spectrum |
| `recover_reflectance_from_XYZ` | 从 XYZ 恢复 bounded smooth reflectance |
| `recover_reflectance_from_xyY` | 从 xyY 恢复 bounded smooth reflectance |
| `ReflectanceLibrary` | 对齐后的反射谱样本矩阵对象 |
| `load_reflectance_library` | 加载 UEF 反射谱库，供后续 basis / dictionary recovery 使用 |

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
- Spectrum recovery 支持 `"bounded_least_squares"`、`"gaussian"`、`"multi_gaussian"` 和 `"auto_gaussian"`。
- Reflectance recovery 支持 `"bounded_least_squares"`、`"meng2015"`、`"pca"` 和 `"dictionary"`。

## Method 选择说明

Recovery 是反问题，同一个 `XYZ` 或 `xyY` 可以对应无数条光谱。`method`
不是数值细节，而是在选择不同的先验约束。

| method | 适用入口 | 是否依赖反射谱库 | 主要参数 | 适合场景 |
| --- | --- | --- | --- | --- |
| `"bounded_least_squares"` | spectrum / reflectance | 否 | `bounds`, `smoothness` | 基线方法；只要求闭合目标响应和光谱平滑 |
| `"gaussian"` | spectrum only | 否 | `amplitude_bounds`, `center_bounds`, `sigma_bounds`, `error` | 单峰 LED / 窄带光源的参数化 effective spectrum |
| `"multi_gaussian"` | spectrum only | 否 | `n_components`, `amplitude_bounds`, `center_bounds`, `sigma_bounds`, `error` | 双峰/多峰 LED，尤其是 purple/complementary 方向 |
| `"auto_gaussian"` | spectrum only | 否 | 同 multi Gaussian | XYZ 入口下按主波长分析自动选择 single / multi Gaussian |
| `"meng2015"` | reflectance only | 否 | `bounds` | 强制 XYZ 闭合，并在可行解中寻找相邻变化最小的反射谱 |
| `"pca"` | reflectance only | 是 | `library`, `library_datasets`, `n_components`, `coefficient_regularization` | 希望结果落在常见物体反射谱的低维变化模式附近 |
| `"dictionary"` | reflectance only | 是 | `library`, `library_datasets`, `dictionary_regularization` | 希望结果可解释为真实样本反射谱的凸组合 |

### 推荐使用顺序

先用 bounded least-squares 建立闭合基线：

```python
from color.recovery import recover_reflectance_from_XYZ

reflectance = recover_reflectance_from_XYZ(
    XYZ,
    method="bounded_least_squares",
    illuminant="D65",
    bounds=(0.0, 1.0),
    smoothness=1e-3,
)
```

如果希望反射谱形状更接近已有物体数据，使用 PCA：

```python
from color.recovery import load_reflectance_library, recover_reflectance_from_XYZ

library = load_reflectance_library("munsell_matt")
reflectance = recover_reflectance_from_XYZ(
    XYZ,
    method="pca",
    library=library,
    n_components=12,
    coefficient_regularization=1e-3,
)
```

如果希望不使用数据库、但强制目标 `XYZ` 等式闭合，使用 Meng 2015：

```python
reflectance = recover_reflectance_from_XYZ(
    XYZ,
    method="meng2015",
    illuminant="D65",
    bounds=(0.0, 1.0),
)
```

如果希望恢复结果能解释为库中真实样本的非负加权平均，使用 dictionary：

```python
reflectance = recover_reflectance_from_XYZ(
    XYZ,
    method="dictionary",
    library=library,
    dictionary_regularization=1e-6,
)
```

### 参数边界

- `smoothness` 只作用于 `"bounded_least_squares"`，控制二阶差分平滑项。
- `amplitude_bounds`、`center_bounds`、`sigma_bounds`、`center_initials`、`error`
  只作用于 `"gaussian"`、`"multi_gaussian"` 和 `"auto_gaussian"`。
- `n_components` 只作用于 `"multi_gaussian"` 和 `"auto_gaussian"`。
- `"meng2015"` 不使用 `smoothness`，它直接最小化一阶相邻差分能量，并用等式约束闭合 `XYZ`。
- `library` / `library_datasets` 只作用于 `"pca"` 和 `"dictionary"`。
- `n_components` / `coefficient_regularization` 只作用于 `"pca"`。
- `dictionary_regularization` 只作用于 `"dictionary"`。
- `bounds` 对 bounded least-squares 和 PCA 是显式反射率约束；dictionary
  使用库样本凸组合，结果范围由库样本本身决定。

### shape 与 library 对齐

PCA 和 dictionary 都要求 recovery 积分矩阵与 `ReflectanceLibrary` 使用同一
`SpectralShape`。

```python
from color.spectra import SpectralShape
from color.recovery import load_reflectance_library, recover_reflectance_from_XYZ

shape = SpectralShape(400, 700, 2)
library = load_reflectance_library("munsell_matt", shape=shape)

reflectance = recover_reflectance_from_XYZ(
    XYZ,
    method="pca",
    library=library,
    shape=shape,
)
```

如果显式传入 `library`，推荐省略 `shape`，或传入与 `library.shape` 完全一致的
shape。若不传 `library`，函数会按当前 `shape` 自动加载 `library_datasets`；如果
`shape=None`，数据库驱动方法使用默认 `400-700 nm / 5 nm`。

### 结果解释

- bounded least-squares 通常能给出稳定闭合结果，但曲线形状未必像真实物体反射谱。
- Meng 2015 不依赖数据库，闭合约束更硬；若目标 `XYZ` 在当前 `bounds` 下不可行，优化会失败。
- PCA 是低维数据库先验；`n_components` 太少会欠拟合，太多会更贴近目标但可能削弱先验约束。
- Dictionary 是真实样本凸组合；可解释性强，但对库覆盖不到的颜色可能更保守。
- 所有方法都不恢复“唯一真实光谱”。应同时检查恢复曲线、目标响应闭合误差和所选先验是否符合任务语义。

## Reflectance library 数据层

### `ReflectanceLibrary`

用途：保存统一 shape 下的反射谱样本矩阵。它不是 recovery 算法，而是后续
basis、PCA、dictionary recovery 的数据输入。

字段：

```text
wavelengths   # (n_wavelengths,)
reflectances  # (n_samples, n_wavelengths)
labels        # 每条样本唯一标签
sources       # 每条样本来源数据集名
shape         # SpectralShape
metadata      # 数据集与样本统计
```

### `load_reflectance_library(datasets=("munsell_matt",), shape=None)`

用途：从已注册 UEF 反射谱数据构建 `ReflectanceLibrary`。

默认 Munsell matt：

```python
from color.recovery import load_reflectance_library

library = load_reflectance_library()

print(library.metadata["datasets"])   # ("munsell_matt",)
print(library.reflectances.shape)     # (1269, 61), default 400-700 nm / 5 nm
print(library.labels[:3])
```

显式混用多个数据集：

```python
library = load_reflectance_library(("munsell_matt", "agfa_it872"))

print(library.metadata["sample_counts"])
print(library.sources[:5])
```

加载当前全部 UEF 反射谱：

```python
library = load_reflectance_library("all_uef")

print(library.metadata["datasets"])
print(library.metadata["sample_count"])
```

自定义 shape：

```python
from color.spectra import SpectralShape

library = load_reflectance_library(
    "munsell_matt",
    shape=SpectralShape(420, 680, 10),
)
```

注意：

- `datasets="all_uef"` 只展开当前 `reflectance_spectra.uef` 下的 UEF 数据。
- 不支持 `datasets="all"`，避免无意混用不同来源和清洗策略。
- 反射率保留原值，不裁剪到 `[0, 1]`。
- `wavelengths` 和 `reflectances` 是只读数组。

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

参数化单高斯恢复：

```python
spectrum = recover_spectrum_from_XYZ(
    target_XYZ,
    method="gaussian",
    shape=SpectralShape(400, 700, 10),
    sigma_bounds=(2.0, 120.0),
)

print(spectrum.metadata["gaussian_parameters"][0])
```

多高斯恢复：

```python
spectrum = recover_spectrum_from_XYZ(
    target_XYZ,
    method="multi_gaussian",
    n_components=2,
)
```

自动高斯策略：

```python
spectrum = recover_spectrum_from_XYZ(
    target_XYZ,
    method="auto_gaussian",
)

print(spectrum.metadata["selected_parametric_method"])
print(spectrum.metadata["selection_reason"])
```

注意：

- `method="gaussian"` 严格表示单峰高斯，不会自动切换成多高斯。
- `method="auto_gaussian"` 在 XYZ 入口会使用主波长分析：spectral 方向选择
  single Gaussian，purple/undefined/near-white 方向选择 multi Gaussian。
- `recover_spectrum_from_LMS(...)` 和 `recover_spectrum_from_responses(...)` 不自动做
  主波长分析；可以显式传入 `center_initials`。

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

PCA recovery：

```python
from color.recovery import recover_reflectance_from_XYZ

reflectance = recover_reflectance_from_XYZ(
    target_XYZ,
    method="pca",
    library_datasets=("munsell_matt",),
    n_components=8,
    coefficient_regularization=1e-3,
)
```

显式传入已加载的 library：

```python
from color.recovery import load_reflectance_library

library = load_reflectance_library("munsell_matt")
reflectance = recover_reflectance_from_XYZ(
    target_XYZ,
    method="pca",
    library=library,
)
```

注意：PCA 是数据库先验方法。`library_datasets` 改变时，恢复结果也会改变。

Dictionary recovery：

```python
reflectance = recover_reflectance_from_XYZ(
    target_XYZ,
    method="dictionary",
    library_datasets=("munsell_matt",),
    dictionary_regularization=1e-6,
)
```

显式传入已加载的 library：

```python
library = load_reflectance_library("munsell_matt")
reflectance = recover_reflectance_from_XYZ(
    target_XYZ,
    method="dictionary",
    library=library,
)
```

注意：dictionary recovery 使用真实样本反射谱的非负凸组合。它不是 PCA basis，
也不是 sparse dictionary；第一版不会强制只使用少数样本。

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
gaussian  # spectrum recovery only
multi_gaussian  # spectrum recovery only
auto_gaussian  # spectrum recovery only
meng2015  # reflectance recovery only
pca  # reflectance recovery only
dictionary  # reflectance recovery only
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

注意：这些是开发入口。未来新增 basis、Smits、sparse dictionary 等方法时，
会继续通过这里的注册表分发。

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
