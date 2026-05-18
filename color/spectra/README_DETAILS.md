# spectra - 详细指南

`color.spectra` 是离散光谱信号的对象封装层。它把原始的波长和值数组包装成不可变对象，并提供采样、插值、reshape、对齐、导出和基础算术操作。

它不负责数据读取，也不负责色度积分：

```text
color.datasets     静态数据文件 -> dict[str, ndarray]
color.generators   公式/过程生成数据 -> dict[str, ndarray]
color.spectra      光谱对象与信号域操作
color.colorimetry  XYZ/LMS 积分和色度计算结果
```

## 核心对象

| 对象 | 含义 |
| --- | --- |
| `SpectralShape` | 规则波长域：start、end、interval |
| `SpectralDistribution` | 单通道光谱信号 |
| `MultiSpectralDistribution` | 多个通道共享同一个波长域的光谱信号 |

单通道对象可以表示一个照明体 SPD、一条反射率曲线，或者一个发光效率函数。多通道对象可以表示 CMFs（`X/Y/Z`），也可以表示色卡数据，其中每个色块是一个通道。

对象构造时会复制输入数组，并把内部数组设为只读。这意味着使用者无法通过 `values` 或 `wavelengths` 意外修改对象内部状态。所有操作都会返回新对象，而不是原地修改原对象。

## 创建对象

### 1. 从已注册的静态数据集创建

当数据来源已经注册在 `color.datasets` 中时，使用 `from_dataset(...)`：

```python
from color.spectra import from_dataset

d65 = from_dataset("illuminants", "D65")
cmfs = from_dataset("standard_observers.cmfs", "cie1931_xyz_1nm")
pmc = from_dataset("color_cards", "pmc")
```

`from_dataset(...)` 内部会调用 `datasets.get(...)` 和 `datasets.describe(...)`，然后根据返回列判断对象类型：

```text
wavelength + 一个非 wavelength 列  -> SpectralDistribution
wavelength + 多个非 wavelength 列 -> MultiSpectralDistribution
没有 wavelength 列                -> ValueError
```

这个入口适合标准静态数据，但它仍然只是一个包装入口。`color.datasets.get(...)` 本身依然返回原始字典。

默认情况下，包装层会保留 `NaN`。如果某些数据源用空白单元格表示明确的零响应，可以在包装时显式填充：

```python
lms = from_dataset(
    "standard_observers.cone_fundamentals",
    "cie2006_lms2_linE_1nm",
    fill_nan=0.0,
)
```

这样生成对象的 `metadata` 会记录：

```python
{"nan_policy": "fill", "nan_fill_value": 0.0}
```

这个策略只属于计算准备阶段，不改变 `datasets` 对原始文件的忠实读取行为。

### 2. 从列字典创建

当数据已经在内存中时，使用 `from_columns(...)`：

```python
from color.spectra import from_columns

raw = {
    "wavelength": wavelength,
    "spd": values,
}

sd = from_columns(raw, x="wavelength", y="spd")
```

`x` 指定波长列，`y` 指定单通道值列。

对于多通道数据，使用 `ys`：

```python
cmfs = from_columns(raw, x="wavelength", ys=("X", "Y", "Z"))
```

这也是色卡示例可以直接传入色块名称的原因：

```python
raw = get_color_card("pmc")
patch_names = ("Caucasian", "Carrot", "Blue Sky")
pmc = from_columns(raw, x="wavelength", ys=patch_names)
```

因为 `raw` 已经是列映射：

```python
{
    "wavelength": ...,
    "Caucasian": ...,
    "Carrot": ...,
    "Blue Sky": ...,
    ...
}
```

`from_columns(..., ys=patch_names)` 会在内部提取这些列，并把它们堆叠成多通道对象。只有在需要重命名、筛选、归一化或提前变换列数据时，才需要手动把列取出来再包装。

`from_columns(...)` 同样支持显式 NaN 填充：

```python
sd = from_columns(raw, x="wavelength", y="spd", fill_nan=0.0)
```

### 3. 直接使用构造函数

当你已经有数组时，可以直接使用构造函数：

```python
from color.spectra import SpectralDistribution, MultiSpectralDistribution

sd = SpectralDistribution(wavelengths, values, name="sample")
msd = MultiSpectralDistribution(wavelengths, values_2d, labels=("X", "Y", "Z"))
```

直接构造函数是最低层的入口。它们会做 shape 和长度校验，复制数组，并把内部数组设为只读。

## 命名：wavelengths/values 与 domain/range

面向光谱语义的命名是：

```python
sd.wavelengths
sd.values
```

面向数学直觉的别名是：

```python
sd.domain  # 等同于 sd.wavelengths
sd.range   # 等同于 sd.values
```

这两组属性暴露的都是只读数组。

## sample、__call__ 与 interpolate

当你只想得到数值结果时，使用 `sample(...)`：

```python
values = sd.sample([450, 550], method="linear")
values = sd([450, 550], method="linear")
```

`__call__(...)` 只是 `sample(...)` 的快捷写法。

当你想得到一个新的光谱对象时，使用 `interpolate(...)`：

```python
sd_450_550 = sd.interpolate([450, 550], method="linear")
```

三者区别是：

```text
sample(...)      -> numpy.ndarray
__call__(...)    -> numpy.ndarray
interpolate(...) -> SpectralDistribution 或 MultiSpectralDistribution
```

默认情况下，插值会拒绝超出原始波长范围的目标波长：

```python
sd.interpolate([350, 450])  # 如果 sd 从 400 nm 开始，这里会抛错
```

如果明确希望对范围外的值进行填充：

```python
sd.interpolate([350, 450], bounds_error=False, fill_value=0.0)
```

如果需要真正的外推行为，优先使用 `align(...)` 或 `extrapolate(...)`。

## reshape、trim、extrapolate 与 align

### reshape

`reshape(shape)` 会在 `shape.wavelengths` 上重新采样，并返回新对象：

```python
from color.spectra import SpectralShape

d65_5nm = d65.reshape(SpectralShape(400, 700, 5))
```

`reshape(...)` 适合原始数据范围内部的重采样。如果目标 shape 超出了原始波长范围，应该使用 `align(...)`。

### trim

`trim(shape)` 会保留落在 shape 范围内的原始采样点：

```python
visible = sd.trim(SpectralShape(400, 700, 10))
```

它不会创建新的边界采样点。它是裁剪/过滤操作，不是插值操作。

### extrapolate

`extrapolate(shape)` 会在目标 shape 上采样，并对原始范围外的部分进行填充或外推：

```python
filled = sd.extrapolate(shape, method="fill", fill_value=0.0)
linear = sd.extrapolate(shape, method="linear")
```

默认行为是：

```python
sd.extrapolate(shape)
# method="fill", fill_value=np.nan
```

### align

当多个光谱需要统一到同一个波长域时，`align(shape)` 是主要的便捷入口：

```python
aligned = sd.align(SpectralShape(360, 830, 5))
```

默认行为是：

```python
sd.align(shape)
# interpolator="auto", extrapolator="constant"
```

也就是说，`align(...)` 会在原始范围内插值，在原始范围外使用边界值常数外推。

## 插值方法

当前支持的插值方法：

| 方法 | 适用场景 |
| --- | --- |
| `auto` | 默认通用选择 |
| `linear` | 保守、可预测 |
| `pchip` | 平滑且保形，常适合反射率/SPD 曲线 |
| `sprague` | CIE 风格的规则采样光谱插值 |
| `cubic` | 样本足够时的平滑三次插值 |
| `nearest` | 离散最近邻采样行为 |

`method="auto"` 的选择规则是：

```text
波长均匀且至少 6 个采样点 -> sprague
否则如果至少 4 个采样点   -> cubic
否则                       -> linear
```

Sprague 插值当前委托给 `colour.algebra.SpragueInterpolator`，这样可以尽量贴近参考库的行为。

对于颜色科学中的常见光谱曲线，比较实用的选择是：

```text
标准规则表格   -> auto 或 sprague
反射率曲线     -> pchip 或 linear
小规模数据     -> linear
调试/对比      -> nearest
```

## 外推方法

当前支持的外推方法：

| 方法 | 行为 |
| --- | --- |
| `constant` | 范围外使用第一个/最后一个边界值 |
| `linear` | 沿边界斜率线性延伸 |
| `fill` | 范围外写入 `fill_value` |

也可以显式覆盖左右两侧：

```python
aligned = sd.align(shape, left=0.0, right=0.0)
```

实用建议：

```text
constant -> 对齐时最安全的默认选择
linear   -> 对平滑物理趋势有用，但可能过冲
fill     -> 当范围外的值应该明确无效或置零时使用
```

## 多通道对象

`MultiSpectralDistribution` 的值数组形状是：

```text
(n_wavelengths, n_channels)
```

并且带有通道标签：

```python
cmfs.labels  # ("X", "Y", "Z")
```

使用 `channel(label)` 可以提取单个通道：

```python
y_bar = cmfs.channel("Y")
```

它会返回一个共享相同波长域的 `SpectralDistribution`。

当多个通道必须保持对齐时，应使用多通道对象，例如：

```text
CMFs：X、Y、Z
色卡：每个色块作为一个通道
相机灵敏度：R、G、B
```

## 导出

可以使用：

```python
sd.to_dict()
sd.to_numpy()
sd.to_pandas()
```

对于 `SpectralDistribution`，`to_numpy()` 返回：

```text
(n, 2) -> wavelength, value
```

对于 `MultiSpectralDistribution`，`to_numpy()` 返回：

```text
(n, 1 + channels) -> wavelength, channel_1, channel_2, ...
```

`to_dict()` 返回的是可写副本，因此下游代码可以安全修改。

## 算术操作

光谱对象支持标量算术：

```python
scaled = sd * 0.5
offset = sd + 1.0
```

也支持同类型对象之间的算术：

```python
combined = sd1 + sd2
product = illuminant * reflectance
```

对象之间做算术时，要求波长采样完全一致：

```text
相同波长采样 -> 允许
不同波长采样 -> ValueError
```

对于多通道算术，通道标签也必须完全一致。

算术操作不会自动执行对齐。应该先显式对齐：

```python
shape = SpectralShape(400, 700, 5)
left = left.align(shape)
right = right.align(shape)
result = left * right
```

这样可以让插值和外推选择保持可见，而不是被隐藏在算术运算符内部。

## 常见工作流

### 静态照明体转对象

```python
from color.spectra import from_dataset, SpectralShape

d65 = from_dataset("illuminants", "D65")
d65_5nm = d65.reshape(SpectralShape(400, 700, 5))
```

### 生成黑体光谱后转对象

```python
from color.generators.blackbody import blackbody_spd
from color.spectra import from_columns

raw = blackbody_spd(temperature=6500)
bb = from_columns(raw, y="radiance", name="blackbody 6500 K")
```

### 色卡色块转多通道对象

```python
from color.datasets import get_color_card
from color.spectra import from_columns, SpectralShape

raw = get_color_card("pmc")
patches = ("Caucasian", "Carrot", "Blue Sky")
pmc = from_columns(raw, ys=patches, name="PMC selected patches")
pmc_05nm = pmc.reshape(SpectralShape(400, 700, 0.5), method="pchip")
```

### 为色度计算准备信号

```python
shape = SpectralShape(400, 700, 5)
spd = spd.align(shape)
reflectance = reflectance.align(shape)
weighted = spd * reflectance
```

XYZ/LMS 转换由 `color.colorimetry` 提供；本模块只负责光谱对象准备、重采样和对齐。

## 示例

可执行示例位于 `examples/spectra/`：

| 示例 | 重点 |
| --- | --- |
| `example_single_distribution.py` | 已注册的单通道数据集 |
| `example_multi_distribution.py` | 已注册的多通道 CMFs |
| `example_from_columns.py` | 原始列字典 |
| `example_interpolation_bounds.py` | 越界插值、`bounds_error` 和 `fill_value` |
| `example_align_and_arithmetic.py` | 对齐、shape 导出和标量算术 |
| `example_sample_and_aliases.py` | `sample`、`__call__`、`domain`、`range` |
| `example_interpolation_methods.py` | 插值器对比 |
| `example_extrapolation_strategies.py` | 外推策略对比 |
| `example_multi_channel_workflow.py` | 多通道对象的通道提取、reshape 和导出 |
| `example_export_formats.py` | `to_dict()`、`to_numpy()`、`to_pandas()` |
| `example_arithmetic_alignment.py` | 算术前显式对齐 |
| `example_plot_single_distribution.py` | 单通道光谱的插值/外推可视化 |
| `example_plot_cmfs.py` | CIE 1931 XYZ CMFs 原始/reshape 可视化 |
| `example_plot_pmc_color_card.py` | PMC 色卡包装与 0.5 nm 插值 |

## 模块边界

`color.spectra` 不直接实现：

- 光谱积分
- `area()`
- SPD x 响应函数到 XYZ/LMS
- 反射率 x 照明体 x 响应函数到 XYZ/LMS

其中 XYZ/LMS 响应积分已经由 `color.colorimetry` 承接
