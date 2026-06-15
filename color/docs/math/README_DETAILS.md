# color.math 详细说明

## AI Usage Notes

- Use this module for pure numerical helpers such as interpolation, extrapolation, and Gaussian curve values.
- Do not use this module as a color-science semantic layer, dataset loader, spectrum wrapper, or plotting layer.
- Key assumptions: functions operate on arrays and numeric values; they do not encode observer, illuminant, whitepoint, or color-space meaning.
- Common mistakes: calling math helpers when a higher-level `spectra`, `generators`, or `recovery` API should own the semantics; assuming interpolation choices imply a colorimetric standard.
- Related modules: use `spectra` for spectral resampling semantics, `generators` for generated SPDs, and `recovery` for inverse problems.

`color.math` 是项目里的底层数值方法层，目前主要服务于光谱插值、外推和少量可被多个模块复用的纯数值曲线。它只处理数组上的数值运算，不表达颜色科学对象本身。

逐项顶层 API 的最小使用案例见 [`API_GUIDE.md`](API_GUIDE.md)。本文档保留模块边界、插值/外推策略和与上层模块的关系说明。

## 模块定位

```text
color.math
  -> 一维插值、外推等底层数值方法

color.spectra
  -> 光谱对象、通道标签、metadata、reshape/align 工作流
```

也就是说：

- `color.math.interpolate_1d(...)` 只知道 `x/y/target`。
- `color.spectra.SpectralDistribution.interpolate(...)` 知道 wavelength、values、name、metadata，并调用 `color.math` 完成底层数值计算。

## 当前模块结构

| 文件 | 职责 |
| --- | --- |
| `interpolation.py` | 一维采样数据插值 |
| `extrapolation.py` | 一维采样数据外推 |
| `gaussian.py` | 高斯曲线底层数值公式 |

## 输入约定

所有当前公开函数都采用严格的一维输入：

```text
x       原始采样点，一维，严格递增
y       原始采样值，一维，长度必须等于 x
target  目标采样点，一维，严格递增
```

所有数值必须 finite。非法 shape、非有限数值、非递增采样都会抛 `ValueError`。

这种严格约束是有意设计：底层数学函数不猜测输入排列，也不自动排序。需要保留通道、标签、单位或对象上下文时，应使用 `color.spectra`。

## 插值方法

`interpolate_1d(...)` 支持：

```text
nearest
linear
cubic
pchip
sprague
auto
```

### auto 策略

`method="auto"` 的策略是：

```text
等间隔且样本数 >= 6 -> sprague
非等间隔且样本数 >= 4 -> cubic
其他情况 -> linear
```

这个策略的目的不是替用户判断所有科学场景，而是给 spectra 默认流程一个稳定、适合规则采样光谱数据的插值选择。

### Sprague

Sprague 插值要求等间隔采样且至少 6 个样本。当前实现为项目内本地实现，使用 CIE 风格的五次多项式公式，并在首尾按 Sprague 边界外推系数补充额外样本点。

### PCHIP

PCHIP 使用 SciPy 的 `PchipInterpolator`。它通常比普通三次插值更适合需要控制过冲的曲线，但具体是否适合某个光谱数据仍应由调用方判断。

## 外推方法

`extrapolate_1d(...)` 支持：

```text
constant
linear
fill
```

外推函数会先对范围内点调用 `interpolate_1d(...)`，然后处理范围外点：

- `constant`：使用左右端点值。
- `linear`：使用首尾两段斜率线性延伸。
- `fill`：使用 `fill_value`。

`left` 和 `right` 可以显式覆盖左右两端外推值。

## 与 spectra 的关系

普通光谱工作流建议优先使用 `color.spectra`：

```python
from color.spectra import SpectralDistribution, SpectralShape

sd = SpectralDistribution([400, 500, 600], [0.1, 0.8, 0.2])
reshaped = sd.reshape(SpectralShape(400, 600, 10), method="linear")
```

只有在你明确处理裸数组时，才直接使用 `color.math`：

```python
from color.math import interpolate_1d

values = interpolate_1d(x, y, target, method="linear")
```

## 高斯曲线工具的边界

`gaussian_values(...)`、`gaussian_values_from_fwhm(...)` 和
`sigma_from_fwhm(...)` 放在 `color.math`，原因是高斯公式同时被多个上层模块复用：

- `color.generators.ideal.gaussian_spd(...)` 需要用高斯公式生成理想 SPD 字典。
- `color.recovery.parametric` 需要在优化循环中反复计算单高斯和多高斯模型。

两者共享的只有数学公式，不共享对象语义。因此底层只保留：

```text
x + amplitude + center + sigma/fwhm -> np.ndarray
```

它不负责：

- 判断 `x` 是否是 wavelength。
- 创建 `{"wavelength": ..., "spd": ...}` 字典。
- 创建 `SpectralDistribution`。
- 记录 recovery 参数或优化误差。

对应地：

- 需要生成公式光谱数据时，用 `color.generators.gaussian_spd(...)`。
- 需要从 `XYZ/LMS` 恢复参数化光谱时，用 `color.recovery.recover_spectrum_from_XYZ(..., method="gaussian")` 或 `method="multi_gaussian"`。

## 不负责的内容

`color.math` 不负责：

- 光谱数据读取。
- 光谱对象构造。
- 多通道标签管理。
- 反射率或 SPD 的物理范围。
- CMFs / LMS / XYZ 积分。
- 色适应、颜色空间转换或色差计算。

这些属于上层模块。

## 后续扩展边界

如果未来加入拟合、优化或更复杂的数值方法，应优先满足两个条件：

1. 多个模块确实会复用。
2. 方法本身不绑定某个具体颜色科学语义。

如果某个算法只服务于 recovery、gamut、appearance 或 colorimetry 的强领域流程，应优先放在对应模块内部，而不是放进 `color.math`。
