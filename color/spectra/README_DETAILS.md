# spectra - 详细指南

`color.spectra` 是离散光谱信号的对象封装层。它不读取文件，也不直接做
XYZ/LMS 积分，而是把已经得到的波长列和值列包装成可采样、可插值、可对齐的对象。

逐项 API 的最小用法见 [`API_GUIDE.md`](API_GUIDE.md)。本文件保留更完整的设计说明、工作流、插值策略和使用注意。

当前分层关系是：

```text
color.datasets     静态标准数据读取 -> dict[str, ndarray]
color.generators   公式/过程生成数据 -> dict[str, ndarray]
color.spectra      光谱对象封装、采样、插值、对齐、导出、算术
color.colorimetry  XYZ/LMS 积分、色度、色温、主波长等计算
```

也就是说，`datasets` 和 `generators` 负责给出原始列字典，`spectra` 负责把这些列变成信号对象，`colorimetry` 再使用这些对象进行积分和色度计算。

## 核心对象

| 对象 | 含义 |
| --- | --- |
| `SpectralShape` | 规则波长域：`start`、`end`、`interval` |
| `SpectralDistribution` | 单通道光谱信号 |
| `MultiSpectralDistribution` | 多个通道共享同一个波长域的光谱信号 |

单通道对象可以表示一个照明体 SPD、一条反射率曲线、一个发光效率函数，或者任意只有一个值列的光谱信号。

多通道对象可以表示：

```text
CMFs：X、Y、Z
LMS fundamentals：l、m、s
色卡：每个色块一个通道
相机灵敏度：R、G、B
```

对象构造时会复制输入数组，并把内部数组设为只读。所有重采样、对齐和算术操作都会返回新对象，不会原地修改源对象。

## 创建对象的入口

### 1. 从列字典创建：from_columns

当数据已经在内存中，且形式类似：

```python
raw = {
    "wavelength": wavelength,
    "spd": values,
}
```

使用：

```python
from color.spectra import from_columns

sd = from_columns(raw, x="wavelength", y="spd")
```

其中：

```text
x  -> 波长列名
y  -> 单通道值列名
ys -> 多通道值列名
```

多通道示例：

```python
cmfs = from_columns(raw, x="wavelength", ys=("X", "Y", "Z"))
```

色卡数据也是同样逻辑：

```python
from color.datasets.color_cards import get_color_card
from color.spectra import from_columns

raw = get_color_card("macbeth")
card = from_columns(raw, ys=("Dark Skin", "Blue Sky", "White"))
```

因为 `raw` 本身就是列映射：

```python
{
    "wavelength": ...,
    "Dark Skin": ...,
    "Blue Sky": ...,
    "White": ...,
}
```

所以不需要先手动把每一列取出来再包装。

### 2. 从注册数据集创建：from_dataset

当数据已经注册在 `color.datasets` 里时，可以使用：

```python
from color.spectra import from_dataset

d65 = from_dataset("illuminants", "D65")
cmfs = from_dataset("standard_observers.cmfs", "cie1931_xyz_1nm")
pmc = from_dataset("color_cards", "pmc")
```

`from_dataset(...)` 内部会调用：

```text
color.datasets.get(...)
color.datasets.describe(...)
```

然后根据列结构自动判断对象类型：

```text
wavelength + 一个值列   -> SpectralDistribution
wavelength + 多个值列   -> MultiSpectralDistribution
没有 wavelength 列      -> ValueError
没有光谱值列            -> ValueError
```

注意：`from_dataset(...)` 只是包装入口。`color.datasets.get(...)` 本身仍然返回原始字典。

### 3. 常用标准数据快捷入口

为了避免常用标准观察者和 D65 需要记文件名，`spectra` 提供了一组语义化入口：

```python
from color.spectra import (
    from_D65_illuminant,
    from_cie1931_xyz_cmfs,
    from_cie1964_xyz_cmfs,
    from_cie2012_xyz_2degree_cmfs,
    from_cie2012_xyz_10degree_cmfs,
    from_cie2006_lms_2degree_fundamentals,
    from_cie2006_lms_10degree_fundamentals,
    from_iprgc_melanopic,
    from_alpha_opic_action_spectra,
)
```

对应含义：

| 函数 | 含义 |
| --- | --- |
| `from_D65_illuminant()` | CIE 标准照明体 D65 |
| `from_cie1931_xyz_cmfs(interval_nm=1)` | CIE 1931 2 度 XYZ CMFs |
| `from_cie1964_xyz_cmfs(interval_nm=1)` | CIE 1964 10 度 XYZ CMFs |
| `from_cie2012_xyz_2degree_cmfs(interval_nm=1)` | CIE 2012 2 度 XYZ CMFs |
| `from_cie2012_xyz_10degree_cmfs(interval_nm=1)` | CIE 2012 10 度 XYZ CMFs |
| `from_cie2006_lms_2degree_fundamentals(interval_nm=1, energy="linE")` | CIE 2006 2 度 LMS fundamentals |
| `from_cie2006_lms_10degree_fundamentals(interval_nm=1, energy="linE")` | CIE 2006 10 度 LMS fundamentals |
| `from_iprgc_melanopic()` | CIE S 026 melanopic / ipRGC action spectrum |
| `from_alpha_opic_action_spectra()` | CIE S 026 五通道 alpha-opic action spectra |
| `from_stockman_rider_2023_individual_cone_fundamentals(...)` | Stockman/Rider 2023 个体化 LMS fundamentals |
| `from_asano2016_individual_cone_fundamentals(...)` | Asano 2016 个体化 LMS fundamentals |

`interval_nm` 的含义是“选择已有原始数据文件的采样间隔”，不是插值间隔。例如：

```python
cmfs_1nm = from_cie1931_xyz_cmfs(interval_nm=1)
cmfs_5nm = from_cie1931_xyz_cmfs(interval_nm=5)
```

如果需要新的采样间隔，应在对象创建后使用：

```python
cmfs_2nm = cmfs_1nm.reshape(SpectralShape(360, 830, 2))
```

CIE 2006 LMS fundamentals 额外有 `energy` 参数：

```python
lms = from_cie2006_lms_2degree_fundamentals(
    interval_nm=1,
    energy="linE",
)
```

当前支持的 `energy` 取值来自已有数据文件，例如：

```text
linE
logE
logQ
```

### 4. CIE S 026 alpha-opic 入口

`from_iprgc_melanopic()` 包装的是 CIE S 026 Toolbox 中的 melanopic / ipRGC
radiometric action spectrum：

```python
from color.spectra import from_iprgc_melanopic

mel = from_iprgc_melanopic()
```

该曲线不提供 2 度 / 10 度区分。ipRGC 主要分布在外周，因此本项目按外周
ipRGC 激活语义记录该数据。

`from_alpha_opic_action_spectra()` 返回五通道组合对象：

```python
from color.spectra import from_alpha_opic_action_spectra

alpha = from_alpha_opic_action_spectra()
print(alpha.labels)  # ("sc", "mc", "lc", "rh", "mel")
```

这个函数不是读取一个独立五列表 dataset，而是组合已有标准数据：

- `sc/mc/lc` 来自 CIE 2006 10 度 LMS linear-energy fundamentals；
- `rh` 来自 scotopic `V_prime`；
- `mel` 来自 CIE S 026 melanopic / ipRGC action spectrum。

输出统一到 `380-780 nm / 1 nm`。由于 CIE 2006 LMS 表从 390 nm 开始，组合入口
在 `380-389 nm` 对 cone channels 补 0，匹配 CIE S 026 Toolbox 的 action spectra
表格语义，不做外推。

### 5. 直接构造

当你已经有数组时，也可以直接使用构造函数：

```python
from color.spectra import SpectralDistribution, MultiSpectralDistribution

sd = SpectralDistribution(wavelengths, values, name="sample")
msd = MultiSpectralDistribution(
    wavelengths,
    values_2d,
    labels=("X", "Y", "Z"),
)
```

直接构造函数是最低层入口，会做长度、维度、波长递增和标签数量校验。

## NaN 与 fill_nan

默认情况下，`spectra` 会保留原始数据中的 `NaN`。这和 `datasets` 的忠实读取原则一致。

如果某些数据源中的空白值在计算语境下明确表示零响应，可以在包装时显式声明：

```python
lms = from_dataset(
    "standard_observers.cone_fundamentals",
    "cie2006_lms2_linE_1nm",
    fill_nan=0.0,
)
```

对象 metadata 会记录：

```python
{
    "nan_policy": "fill",
    "nan_fill_value": 0.0,
}
```

常用 CIE 2006 LMS 快捷入口默认 `fill_nan=0.0`，因为它们通常作为响应函数用于数值积分，空白长波端更自然地按零响应处理：

```python
lms = from_cie2006_lms_2degree_fundamentals()
```

如果你想保留 NaN，可以显式传入：

```python
lms = from_cie2006_lms_2degree_fundamentals(fill_nan=None)
```

## 个体化 LMS 入口

`color.spectra` 现在也提供公式生成数据的包装入口：

```python
from color.spectra import (
    from_asano2016_individual_cone_fundamentals,
    from_stockman_rider_2023_individual_cone_fundamentals,
)

stockman = from_stockman_rider_2023_individual_cone_fundamentals(
    observer_degree=2,
    l_shift_nm=2.0,
    m_shift_nm=-1.0,
)

asano = from_asano2016_individual_cone_fundamentals(
    age=32,
    field_size_degree=2,
)
```

这些入口内部调用 `color.generators` 中注册的个体化 cone fundamental 生成器，然后包装成
`MultiSpectralDistribution`。返回通道为：

```python
("l", "m", "s")
```

它们和 `from_cie2006_lms_2degree_fundamentals(...)` 的区别是：

- `from_cie2006_lms_...` 读取 CVRL 静态标准数据；
- `from_stockman_rider_2023_individual_cone_fundamentals(...)` 根据 Stockman/Rider 2023 公式即时生成，
  可以改变 photopigment OD、macular density、lens density 和 L/M/S 峰值偏移。
- `from_asano2016_individual_cone_fundamentals(...)` 根据 Asano 2016 / CIEPO06
  individual observer 语义即时生成，可以改变 age、field size、lens/macular
  density deviation、photopigment OD deviation 和 L/M/S lambda-max shift。

第一版不做 codon/hybrid 到 shift 的自动推导；如果需要个体化，直接传入
`l_shift_nm`、`m_shift_nm`、`s_shift_nm` 等数值参数。

## 属性、keys 与字典式访问

光谱对象不是字典，但提供了和原始列字典接近的访问方式。

### 基本属性

```python
sd.wavelengths
sd.values
sd.domain  # wavelengths 的只读别名
sd.range   # values 的只读别名
```

多通道对象还有：

```python
msd.labels
```

### keys()

`keys()` 返回和 `to_dict()` 对齐的列名：

```python
sd.keys()
# ("wavelength", "value")

cmfs.keys()
# ("wavelength", "X", "Y", "Z")
```

这样从 `datasets` 的原始字典迁移到 `spectra` 对象时，查看列名的方式保持一致。

### [] 访问

单通道对象：

```python
sd["wavelength"]  # 波长数组
sd["value"]       # 数值数组
```

多通道对象：

```python
cmfs["wavelength"]  # 波长数组
cmfs["Y"]           # Y 通道 SpectralDistribution
```

注意，多通道对象中 `cmfs["Y"]` 返回的是单通道 `SpectralDistribution`，不是裸数组。这样可以保留波长域、名称和 metadata，并继续支持：

```python
cmfs["Y"].sample([450, 550])
cmfs["Y"].reshape(shape)
cmfs["Y"].align(shape)
```

如果只想要裸数组副本，可以导出字典：

```python
y_values = cmfs.to_dict()["Y"]
```

`channel(label)` 与 `obj[label]` 等价，语义更显式：

```python
y_bar = cmfs.channel("Y")
```

## sample、__call__ 与 interpolate

当只需要数值时，使用 `sample(...)`：

```python
values = sd.sample([450, 550], method="linear")
```

`__call__(...)` 是 `sample(...)` 的快捷写法：

```python
values = sd([450, 550], method="linear")
```

当需要新的光谱对象时，使用 `interpolate(...)`：

```python
sampled = sd.interpolate([450, 550], method="linear")
```

区别是：

```text
sample(...)      -> numpy.ndarray
__call__(...)    -> numpy.ndarray
interpolate(...) -> SpectralDistribution 或 MultiSpectralDistribution
```

默认情况下，插值拒绝超出原始波长范围：

```python
sd.interpolate([350, 450])
```

如果确实需要范围外填充值：

```python
sd.interpolate([350, 450], bounds_error=False, fill_value=0.0)
```

## reshape、trim、extrapolate、align

### reshape

`reshape(shape)` 会在 `shape.wavelengths` 上重采样：

```python
d65_5nm = d65.reshape(SpectralShape(400, 700, 5))
```

它适合目标波长域仍在原始范围内的情况。

### trim

`trim(shape)` 保留落在范围内的原始采样点：

```python
visible = sd.trim(SpectralShape(400, 700, 10))
```

它不会创建新的边界点，因此是裁剪/过滤，不是插值。

### extrapolate

`extrapolate(shape)` 会采样目标 shape，并处理原始范围外的值：

```python
filled = sd.extrapolate(shape, method="fill", fill_value=0.0)
linear = sd.extrapolate(shape, method="linear")
```

支持的外推方式：

| 方法 | 行为 |
| --- | --- |
| `constant` | 范围外使用边界值 |
| `linear` | 沿边界斜率线性延伸 |
| `fill` | 范围外写入 `fill_value` |

### align

`align(shape)` 是最常用的对齐入口：

```python
aligned = sd.align(SpectralShape(360, 830, 5))
```

默认行为：

```python
sd.align(shape)
# interpolator="auto", extrapolator="constant"
```

也就是说，在原始范围内插值，在范围外使用边界值常数外推。

## 插值方法

当前支持：

| 方法 | 说明 |
| --- | --- |
| `auto` | 默认选择 |
| `linear` | 线性插值，保守稳定 |
| `nearest` | 最近邻 |
| `cubic` | 三次插值 |
| `pchip` | 保形插值，常适合反射率曲线 |
| `sprague` | CIE 风格规则采样光谱插值 |

`method="auto"` 的选择规则：

```text
波长均匀且至少 6 个采样点 -> sprague
否则如果至少 4 个采样点   -> cubic
否则                       -> linear
```

实用建议：

```text
标准规则表格 -> auto 或 sprague
反射率曲线   -> pchip 或 linear
少量点       -> linear
调试/离散值  -> nearest
```

## 导出

```python
raw = sd.to_dict()
array = sd.to_numpy()
frame = sd.to_pandas()
```

单通道 `to_numpy()`：

```text
(n, 2) -> wavelength, value
```

多通道 `to_numpy()`：

```text
(n, 1 + channels) -> wavelength, channel_1, channel_2, ...
```

`to_dict()` 返回的是可写副本，因此下游代码可以安全修改，不会影响光谱对象内部状态。

## 算术操作

支持标量算术：

```python
scaled = sd * 0.5
offset = sd + 1.0
```

也支持同类型对象之间的算术：

```python
product = illuminant * reflectance
combined = sd1 + sd2
```

要求：

```text
单通道对象之间：波长采样必须完全一致
多通道对象之间：波长采样和 labels 都必须完全一致
```

算术操作不会自动对齐。应该显式写出对齐策略：

```python
shape = SpectralShape(400, 700, 5)
left = left.align(shape)
right = right.align(shape)
result = left * right
```

这能避免插值和外推策略被隐藏在运算符内部。

## 常见工作流

### D65 与 CIE 1931 CMFs

```python
from color.spectra import from_D65_illuminant, from_cie1931_xyz_cmfs

d65 = from_D65_illuminant()
cmfs = from_cie1931_xyz_cmfs(interval_nm=1)
```

### 色卡反射谱

```python
from color.datasets.color_cards import get_color_card
from color.spectra import from_columns

raw = get_color_card("macbeth")
card = from_columns(raw, ys=("Blue Sky", "White", "Black"))

blue_sky = card["Blue Sky"]
reflectance_values = blue_sky.values
```

### 生成数据转对象

```python
from color.generators.blackbody import blackbody_spd
from color.spectra import from_columns

raw = blackbody_spd(temperature=6500)
bb = from_columns(raw, y="radiance", name="blackbody 6500 K")
```

### 为 colorimetry 积分准备

```python
from color.colorimetry import reflectance_to_XYZ

XYZ = reflectance_to_XYZ(
    blue_sky,
    illuminant=d65,
    cmfs=cmfs,
)
```

`spectra` 只负责对象准备；真正的 XYZ/LMS 积分由 `color.colorimetry` 完成。

## 示例

可执行示例位于 `examples/spectra/`：

| 示例 | 重点 |
| --- | --- |
| `example_01_create_spectral_objects.py` | `from_dataset`、`from_columns`、直接构造和常用入口 |
| `example_02_sampling_interpolation_alignment.py` | sample、`__call__`、插值、reshape、trim、外推、align |
| `example_03_multi_channel_workflow.py` | CMFs、色卡、多通道标签和通道提取 |
| `example_04_export_and_arithmetic.py` | `to_dict`、`to_numpy`、`to_pandas`、算术和显式对齐 |
| `example_05_visualization_cases.py` | 单通道、CMFs、色卡插值与可视化 |

## 模块边界

`color.spectra` 不直接实现：

- 光谱积分
- SPD 到 XYZ/LMS
- 反射率 x 照明体 x 响应函数到 XYZ/LMS
- 色度坐标、色温、主波长、色差

这些由 `color.colorimetry`、`color.spaces` 和 `color.difference` 承接。

这个边界的好处是：数据读取、光谱信号准备、色度计算和颜色空间转换各自保持干净。
