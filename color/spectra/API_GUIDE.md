# color.spectra API 使用指南

本文档按 `color.spectra.__all__` 覆盖顶层 API。这里写最小使用案例；
模块设计、插值策略、NaN 策略和完整工作流说明见 [`README_DETAILS.md`](README_DETAILS.md)。

## 顶层 API 总览

| API | 功能 | 推荐场景 |
| --- | --- | --- |
| `SpectralShape` | 规则波长采样域 | reshape、align、固定网格 |
| `SpectralDistribution` | 单通道光谱对象 | SPD、反射率、V(lambda) |
| `MultiSpectralDistribution` | 多通道光谱对象 | CMFs、LMS、色卡、多通道响应 |
| `from_columns` | 从列字典包装对象 | datasets/generators/raw dict |
| `from_dataset` | 从注册静态数据集包装对象 | 已知 datasets category/name |
| `from_D65_illuminant` | CIE D65 光源对象 | 常用积分照明体 |
| `from_cie1931_xyz_cmfs` | CIE 1931 XYZ CMFs | 默认 XYZ 积分响应 |
| `from_cie1964_xyz_cmfs` | CIE 1964 XYZ CMFs | 10 度 XYZ 观察者 |
| `from_cie2012_xyz_2degree_cmfs` | CIE 2012 2 度 XYZ CMFs | CIE 2012 2 度响应 |
| `from_cie2012_xyz_10degree_cmfs` | CIE 2012 10 度 XYZ CMFs | CIE 2012 10 度响应 |
| `from_cie2006_lms_2degree_fundamentals` | CIE 2006 2 度 LMS fundamentals | LMS 积分响应 |
| `from_cie2006_lms_10degree_fundamentals` | CIE 2006 10 度 LMS fundamentals | 10 度 LMS 积分响应 |
| `from_iprgc_melanopic` | CIE S 026 melanopic / ipRGC 曲线 | melanopic / ipRGC 响应 |
| `from_alpha_opic_action_spectra` | CIE S 026 五通道 alpha-opic 曲线组合 | alpha-opic 分析 |
| `from_stockman_rider_2023_individual_cone_fundamentals` | Stockman/Rider 个体化 LMS | 个体参数化 cone fundamentals |
| `from_asano2016_individual_cone_fundamentals` | Asano 2016 个体化 LMS | Asano individual colorimetric observer |

## 核心对象

### `SpectralShape`

用途：表示规则波长采样域。

输入：`start`、`end`、`interval`。  
返回：不可变 shape 对象。

```python
from color.spectra import SpectralShape

shape = SpectralShape(400, 700, 5)
print(shape.wavelengths)
print(len(shape))
print(500 in shape)
```

注意：`end` 会尽量包含在 `wavelengths` 中；`start >= end` 或 `interval <= 0` 会报错。

### `SpectralDistribution`

用途：单通道光谱对象。

输入：一维 `wavelengths`、一维 `values`。  
返回：只读单通道对象。

直接构造：

```python
from color.spectra import SpectralDistribution

sd = SpectralDistribution(
    [400, 500, 600],
    [0.1, 1.0, 0.2],
    name="example SPD",
)
```

基础访问：

```python
print(sd.wavelengths)
print(sd.values)
print(sd.domain)  # wavelengths alias
print(sd.range)   # values alias
print(sd.keys())  # ("wavelength", "value")
print(sd["value"])
```

采样和重采样：

```python
from color.spectra import SpectralShape

value_550 = sd.sample([550], method="linear")
same = sd([550], method="linear")
reshaped = sd.reshape(SpectralShape(400, 600, 50))
```

导出：

```python
raw = sd.to_dict()
array = sd.to_numpy()
frame = sd.to_pandas()
```

注意：`to_dict()` 返回可写副本；对象内部数组仍然只读。

### `MultiSpectralDistribution`

用途：共享同一波长轴的多通道光谱对象。

输入：一维 `wavelengths`、二维 `values`、通道 `labels`。  
返回：只读多通道对象。

直接构造：

```python
from color.spectra import MultiSpectralDistribution

msd = MultiSpectralDistribution(
    [400, 500, 600],
    [[0.1, 0.0], [0.8, 0.4], [0.2, 0.9]],
    labels=("A", "B"),
    name="two channels",
)
```

这里的 `A`、`B` 是通道标签；实际使用中通常是 `X/Y/Z`、`l/m/s`、色卡 patch 名或传感器通道名。

通道访问：

```python
print(msd.labels)
print(msd.keys())       # ("wavelength", "A", "B")
print(msd["wavelength"])
a_channel = msd["A"]    # SpectralDistribution
same = msd.channel("A")
```

多通道采样：

```python
values = msd.sample([450, 550], method="linear")
reshaped = msd.reshape(msd.shape)
```

注意：`msd["A"]` 返回单通道对象，不是裸数组；需要裸数组副本时使用 `msd.to_dict()["A"]`。

## 从数据创建对象

### `from_columns(raw, x="wavelength", y=None, ys=None, ...)`

用途：从原始列字典创建单通道或多通道对象。

输入：列映射、波长列名、单通道 `y` 或多通道 `ys`。  
返回：`SpectralDistribution` 或 `MultiSpectralDistribution`。

单通道 SPD：

```python
from color.spectra import from_columns

raw = {
    "wavelength": [400, 500, 600],
    "spd": [0.1, 1.0, 0.2],
}

sd = from_columns(raw, x="wavelength", y="spd", name="example SPD")
```

多通道 CMFs：

```python
from color.spectra import from_columns

raw = {
    "wavelength": [400, 500, 600],
    "X": [0.1, 0.5, 0.2],
    "Y": [0.0, 0.8, 0.3],
    "Z": [0.6, 0.2, 0.0],
}

cmfs = from_columns(raw, ys=("X", "Y", "Z"), name="example CMFs")
```

色卡 patch：

```python
from color.datasets import get_color_card
from color.spectra import from_columns

raw = get_color_card("pmc")
patch = from_columns(raw, y="Blue Sky", name="PMC Blue Sky")
card = from_columns(raw, ys=("Caucasian", "Carrot", "Blue Sky"), name="PMC subset")
```

显式填充 NaN：

```python
from color.spectra import from_columns

sd = from_columns(raw, y="spd", fill_nan=0.0)
```

注意：`y` 和 `ys` 不能同时提供；`fill_nan=None` 会保留原始 NaN。

### `from_dataset(category, name, **kwargs)`

用途：读取注册静态数据集并包装为光谱对象。

输入：datasets category/name，可附加 datasets 参数。  
返回：按列数自动判断的单通道或多通道对象。

照明体：

```python
from color.spectra import from_dataset

d65 = from_dataset("illuminants", "D65")
```

标准观察者：

```python
from color.spectra import from_dataset

cmfs = from_dataset("standard_observers.cmfs", "cie1931_xyz_1nm")
```

色卡：

```python
from color.spectra import from_dataset

pmc = from_dataset("color_cards", "pmc")
blue_sky = pmc["Blue Sky"]
```

带读取参数的数据：

```python
from color.spectra import from_dataset

pointer = from_dataset("gamut_data", "pointer", L=50)
```

注意：没有 `wavelength` 列的数据不能包装为 spectral object，会抛 `ValueError`。

## 常用标准入口

### `from_D65_illuminant()`

用途：返回 CIE standard illuminant D65。

输入：无。  
返回：`SpectralDistribution`。

```python
from color.spectra import from_D65_illuminant

d65 = from_D65_illuminant()
```

### `from_cie1931_xyz_cmfs(interval_nm=1)`

用途：返回 CIE 1931 2 度 XYZ CMFs。

输入：已有数据文件采样间隔。  
返回：`MultiSpectralDistribution`，labels 为 `("X", "Y", "Z")`。

```python
from color.spectra import from_cie1931_xyz_cmfs

cmfs_1nm = from_cie1931_xyz_cmfs(interval_nm=1)
cmfs_5nm = from_cie1931_xyz_cmfs(interval_nm=5)
```

注意：`interval_nm` 选择已有源文件，不是插值。需要新网格时使用 `reshape(...)`。

### `from_cie1964_xyz_cmfs(interval_nm=1)`

用途：返回 CIE 1964 10 度 XYZ CMFs。

输入：已有数据文件采样间隔。  
返回：`MultiSpectralDistribution`。

```python
from color.spectra import from_cie1964_xyz_cmfs

cmfs = from_cie1964_xyz_cmfs(interval_nm=1)
```

### `from_cie2012_xyz_2degree_cmfs(interval_nm=1)` / `from_cie2012_xyz_10degree_cmfs(interval_nm=1)`

用途：返回 CIE 2012 2 度或 10 度 XYZ CMFs。

输入：已有数据文件采样间隔。  
返回：`MultiSpectralDistribution`。

```python
from color.spectra import (
    from_cie2012_xyz_2degree_cmfs,
    from_cie2012_xyz_10degree_cmfs,
)

cmfs_2 = from_cie2012_xyz_2degree_cmfs(interval_nm=1)
cmfs_10 = from_cie2012_xyz_10degree_cmfs(interval_nm=1)
```

### `from_cie2006_lms_2degree_fundamentals(...)` / `from_cie2006_lms_10degree_fundamentals(...)`

用途：返回 CIE 2006 LMS cone fundamentals。

输入：`interval_nm`、`energy`、`fill_nan`。  
返回：`MultiSpectralDistribution`，labels 为 `("l", "m", "s")`。

```python
from color.spectra import (
    from_cie2006_lms_2degree_fundamentals,
    from_cie2006_lms_10degree_fundamentals,
)

lms_2 = from_cie2006_lms_2degree_fundamentals(interval_nm=1, energy="linE")
lms_10 = from_cie2006_lms_10degree_fundamentals(interval_nm=1, energy="linE")
```

保留原始 NaN：

```python
from color.spectra import from_cie2006_lms_2degree_fundamentals

lms = from_cie2006_lms_2degree_fundamentals(fill_nan=None)
```

注意：这些 LMS 入口默认 `fill_nan=0.0`，适合积分中的零响应语义。

### `from_iprgc_melanopic()`

用途：返回 CIE S 026 melanopic / ipRGC radiometric action spectrum。

输入：无。  
返回：`SpectralDistribution`。

```python
from color.spectra import from_iprgc_melanopic

mel = from_iprgc_melanopic()
print(mel.wavelengths[0], mel.wavelengths[-1])
print(mel.values.max())
```

注意：该曲线不区分 2 度 / 10 度视角。ipRGC 主要分布在外周，通常按外周 ipRGC 激活语义使用。

### `from_alpha_opic_action_spectra()`

用途：返回 CIE S 026 五通道 alpha-opic action spectra。

输入：无。  
返回：`MultiSpectralDistribution`，labels 为 `("sc", "mc", "lc", "rh", "mel")`。

```python
from color.spectra import from_alpha_opic_action_spectra

alpha = from_alpha_opic_action_spectra()
print(alpha.labels)
mel = alpha["mel"]
```

注意：这是组合入口，不是读取一个官方五列表 dataset。`sc/mc/lc` 来自 CIE 2006 10 度 LMS linear-energy fundamentals，`rh` 来自 scotopic `V_prime`，`mel` 来自 CIE S 026 melanopic / ipRGC action spectrum。输出统一为 `380-780 nm / 1 nm`，cone channels 在 `380-389 nm` 补 0。

### `from_stockman_rider_2023_individual_cone_fundamentals(**kwargs)`

用途：生成并包装 Stockman/Rider 2023 个体化 LMS fundamentals。

输入：个体化参数，例如 observer degree、macular/lens density、OD、L/M/S shift。  
返回：`MultiSpectralDistribution`，labels 为 `("l", "m", "s")`。

标准 2 度：

```python
from color.spectra import from_stockman_rider_2023_individual_cone_fundamentals

lms = from_stockman_rider_2023_individual_cone_fundamentals(observer_degree=2)
```

带个体参数：

```python
from color.spectra import from_stockman_rider_2023_individual_cone_fundamentals

individual = from_stockman_rider_2023_individual_cone_fundamentals(
    observer_degree=2,
    l_shift_nm=2.0,
    m_shift_nm=-1.0,
    macular_density_460=0.30,
)
```

注意：该入口包装的是生成数据，不是静态 dataset 文件。

### `from_asano2016_individual_cone_fundamentals(**kwargs)`

用途：生成并包装 Asano et al. 2016 个体化 LMS fundamentals。

输入：`age`、`field_size_degree`、density deviation、OD deviation、L/M/S shift。  
返回：`MultiSpectralDistribution`，labels 为 `("l", "m", "s")`。

平均 2 度语义：

```python
from color.spectra import from_asano2016_individual_cone_fundamentals

lms = from_asano2016_individual_cone_fundamentals(
    age=32,
    field_size_degree=2,
)
```

带个体参数：

```python
individual = from_asano2016_individual_cone_fundamentals(
    age=45,
    field_size_degree=4,
    lens_density_deviation=10.0,
    macular_density_deviation=-5.0,
    photopigment_shift_nm=(2.0, -1.0, 0.0),
)
```

注意：该入口适合需要 Asano 年龄/视场/个体 deviation 模型的场景；只需要
CIE 2006 平均观察者时，优先使用 `from_cie2006_lms_2degree_fundamentals(...)`
或 `from_cie2006_lms_10degree_fundamentals(...)`。

## 常见操作组合

### 对齐后算术

```python
from color.spectra import SpectralShape, from_D65_illuminant, from_columns

shape = SpectralShape(400, 700, 5)
illuminant = from_D65_illuminant().align(shape)
reflectance = from_columns(raw, y="Blue Sky").align(shape)

effective = illuminant * reflectance
```

算术不会自动对齐。对象之间做运算前，应显式指定 `align(...)` 策略。

### 进入 colorimetry

```python
from color.colorimetry import reflectance_to_XYZ
from color.datasets import get_color_card
from color.spectra import from_columns

raw = get_color_card("pmc")
patch = from_columns(raw, y="Blue Sky", name="PMC Blue Sky")
XYZ = reflectance_to_XYZ(patch, illuminant="D65")
```

`spectra` 负责光谱对象准备；XYZ/LMS 积分属于 `color.colorimetry`。
