# color.math API 使用指南

本文档对应 `color.math` 顶层公开 API。该模块提供光谱对象和其他模块复用的一维插值、外推底层数学工具。

英文快速入口见 [`README.md`](README.md)，中文设计说明见 [`README_DETAILS.md`](README_DETAILS.md)。

## API 总览

| API | 用途 |
| --- | --- |
| `Interpolator` | 插值方法类型标注 |
| `interpolate_1d` | 对一维采样信号插值 |
| `is_uniform` | 判断采样点是否等间隔 |
| `resolve_interpolator` | 根据 `method="auto"` 和采样结构选择实际插值器 |
| `Extrapolator` | 外推方法类型标注 |
| `extrapolate_1d` | 对一维采样信号插值并外推 |
| `gaussian_values` | 计算一条高斯曲线的数值 |
| `gaussian_values_from_fwhm` | 使用 FWHM 宽度计算高斯曲线 |
| `sigma_from_fwhm` | 将 FWHM 转成高斯标准差 `sigma` |

## 基本约定

- `x`、`y`、`target` 都必须是一维数组。
- `x` 必须严格递增。
- `target` 也必须严格递增。
- `x` 和 `y` 长度必须一致。
- 所有输入必须是 finite 数值。
- 返回值是 `np.ndarray`，shape 与 `target` 一致。

该模块只处理一维数值信号，不负责 `SpectralDistribution` 对象、通道标签、metadata 或科学单位。

## `Interpolator`

插值方法类型标注。当前支持：

```text
"auto"
"nearest"
"linear"
"cubic"
"pchip"
"sprague"
```

通常不需要直接使用这个类型；它主要用于函数签名和开发时提示。

```python
from color.math import Interpolator

method: Interpolator = "linear"
```

## `interpolate_1d(x, y, target, *, method="auto", bounds_error=True, fill_value=np.nan)`

对一维采样信号插值。

### 线性插值

```python
import numpy as np
from color.math import interpolate_1d

x = np.array([400.0, 500.0, 600.0])
y = np.array([0.1, 0.8, 0.2])
target = np.array([450.0, 550.0])

values = interpolate_1d(x, y, target, method="linear")
```

### 最近邻插值

```python
values = interpolate_1d(x, y, target, method="nearest")
```

### PCHIP 插值

```python
values = interpolate_1d(x, y, target, method="pchip")
```

PCHIP 使用 SciPy 的 monotonicity-preserving piecewise cubic interpolator，适合希望曲线更平滑但又避免普通三次插值过冲的场景。

### Sprague 插值

```python
x = np.array([400, 410, 420, 430, 440, 450], dtype=float)
y = np.array([0.1, 0.2, 0.5, 0.7, 0.6, 0.4])
target = np.array([405, 415, 425], dtype=float)

values = interpolate_1d(x, y, target, method="sprague")
```

Sprague 要求：

- `x` 等间隔。
- 至少 6 个样本。

当前实现调用本地 `colour.algebra.SpragueInterpolator`，用于保持和 colour-science 行为接近。

### 超出范围处理

默认 `bounds_error=True`，目标采样点超出原始范围会抛 `ValueError`：

```python
target = np.array([390.0, 450.0])
values = interpolate_1d(x, y, target, method="linear")
```

允许超范围并填充值：

```python
values = interpolate_1d(
    x,
    y,
    target,
    method="linear",
    bounds_error=False,
    fill_value=0.0,
)
```

如果需要真正外推，应使用 `extrapolate_1d(...)`。

## `is_uniform(x, *, rtol=1e-7, atol=1e-12)`

判断采样点是否等间隔。

```python
import numpy as np
from color.math import is_uniform

print(is_uniform(np.array([400.0, 410.0, 420.0])))  # True
print(is_uniform(np.array([400.0, 410.0, 425.0])))  # False
```

单点或两个点会返回 `True`，因为没有足够间隔差异可以比较。

## `resolve_interpolator(x, method="auto")`

将用户传入的插值方法解析为实际方法。

```python
import numpy as np
from color.math import resolve_interpolator

x = np.array([400, 410, 420, 430, 440, 450], dtype=float)
print(resolve_interpolator(x, method="auto"))  # "sprague"
```

`auto` 策略：

```text
等间隔且样本数 >= 6 -> sprague
非等间隔且样本数 >= 4 -> cubic
其他情况 -> linear
```

显式方法会直接返回：

```python
print(resolve_interpolator(x, method="pchip"))  # "pchip"
```

未知方法会抛 `ValueError`。

## `Extrapolator`

外推方法类型标注。当前支持：

```text
"constant"
"linear"
"fill"
```

通常不需要直接使用这个类型；它主要用于函数签名和开发时提示。

```python
from color.math import Extrapolator

method: Extrapolator = "constant"
```

## `extrapolate_1d(x, y, target, *, interpolator="auto", method="constant", fill_value=np.nan, left=None, right=None)`

先对范围内目标点插值，再对范围外目标点外推。

### 常数外推

```python
import numpy as np
from color.math import extrapolate_1d

x = np.array([400.0, 500.0, 600.0])
y = np.array([0.1, 0.8, 0.2])
target = np.array([350.0, 450.0, 650.0])

values = extrapolate_1d(x, y, target, method="constant", interpolator="linear")
```

范围外结果使用两端端点值：

```text
350 nm -> y[0]
650 nm -> y[-1]
```

### 线性外推

```python
values = extrapolate_1d(x, y, target, method="linear", interpolator="linear")
```

线性外推使用首尾两个样本估计左右斜率。需要至少 2 个样本。

### 填充值外推

```python
values = extrapolate_1d(
    x,
    y,
    target,
    method="fill",
    fill_value=0.0,
)
```

范围外结果全部为 `fill_value`。

### 单独覆盖左侧和右侧

```python
values = extrapolate_1d(
    x,
    y,
    target,
    method="constant",
    left=0.0,
    right=1.0,
)
```

`left` 和 `right` 优先级高于 `method` 的默认外推结果。

## `gaussian_values(x, *, amplitude=1.0, center=0.0, sigma=1.0)`

计算一条高斯曲线：

```text
y = amplitude * exp(-0.5 * ((x - center) / sigma)^2)
```

```python
import numpy as np
from color.math import gaussian_values

x = np.linspace(400.0, 700.0, 301)
y = gaussian_values(x, amplitude=1.0, center=555.0, sigma=25.0)
```

注意：这里的 `x` 只是数值坐标。它可以是波长，也可以是其他一维坐标；`color.math` 不保存单位和 metadata。

## `sigma_from_fwhm(fwhm)`

把高斯曲线的 full width at half maximum 转换成标准差：

```python
from color.math import sigma_from_fwhm

sigma = sigma_from_fwhm(50.0)
```

公式为：

```text
sigma = fwhm / (2 * sqrt(2 * ln(2)))
```

`fwhm` 必须是有限正数。

## `gaussian_values_from_fwhm(x, *, amplitude=1.0, center=0.0, fwhm=1.0)`

使用 FWHM 宽度直接计算高斯曲线。

```python
import numpy as np
from color.math import gaussian_values_from_fwhm

wavelengths = np.array([530.0, 555.0, 580.0])
values = gaussian_values_from_fwhm(
    wavelengths,
    amplitude=1.0,
    center=555.0,
    fwhm=50.0,
)
```

这个函数等价于：

```python
from color.math import gaussian_values, sigma_from_fwhm

values = gaussian_values(
    wavelengths,
    amplitude=1.0,
    center=555.0,
    sigma=sigma_from_fwhm(50.0),
)
```

## 与 generators / recovery 的关系

`color.math` 只提供高斯公式本身。若你需要生成一个带 `wavelength` / `spd` 列的字典，应使用：

```python
from color.generators import gaussian_spd

data = gaussian_spd(peak_wavelength=555.0, width=25.0)
```

若你需要从 `XYZ` 优化恢复一条参数化高斯 effective spectrum，应使用：

```python
from color.recovery import recover_spectrum_from_XYZ

sd = recover_spectrum_from_XYZ(XYZ, method="gaussian")
```

## 与 `color.spectra` 的关系

`color.math` 是底层数值工具；`color.spectra` 是面向光谱对象的封装层。普通使用者通常通过 spectra 对象调用：

```python
from color.spectra import SpectralDistribution

sd = SpectralDistribution([400, 500, 600], [0.1, 0.8, 0.2])
resampled = sd.interpolate([450, 550], method="linear")
```

内部再由 spectra 调用 `color.math.interpolate_1d(...)` 或 `extrapolate_1d(...)`。

如果你只是处理裸的一维数组，可以直接使用 `color.math`。

## 使用边界

`color.math` 不负责：

- 多通道光谱对象包装。
- 波长单位解释。
- 反射率、SPD、CMFs 等科学语义。
- 光谱积分。
- 色度学转换。
- 数据集读取。

这些逻辑应留在 `spectra`、`colorimetry`、`datasets` 等模块中。
