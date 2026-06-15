# generators - 详细指南

## AI Usage Notes

- Use this module when creating formula- or model-generated data such as illuminants, ideal spectra, Gaussian/multi-Gaussian SPDs, LEDs, or registered generator outputs.
- Do not use this module to read static standard files, recover spectra from color values, or wrap spectra as long-lived objects; route those to `datasets`, `recovery`, or `spectra`.
- Key assumptions: generator outputs are lightweight dictionaries/arrays by design; generated data is not automatically registered as static data.
- Common mistakes: confusing generated SPDs with measured datasets; using generators for inverse recovery; expecting generator names to be identical to dataset names.
- Related modules: use `spectra` to wrap generated columns, `colorimetry` to integrate them, and `plot` for visualization.

`color.generators` 是“基于公式或过程模型生成数据”的模块。它和 `color.datasets` 的边界很重要：

```text
color.datasets    读取已经存在的静态标准数据文件
color.generators  根据公式/模型即时生成数据
```

逐项顶层 API 的最小用法见 [`API_GUIDE.md`](API_GUIDE.md)。本文件保留模块边界、
注册表设计、各类生成器语义、缓存规则和使用注意。

两者返回的数据形式保持一致，都是原始列字典：

```python
dict[str, numpy.ndarray]
```

例如：

```python
{
    "wavelength": array([...]),
    "spd": array([...]),
}
```

如果需要插值、对齐、采样或进一步交给 `colorimetry` 做积分，应先用 `color.spectra.from_columns(...)` 包装成光谱对象：

```python
from color.generators.leds import single_led_spd
from color.spectra import from_columns

raw = single_led_spd(peak_wavelength=630, half_spectral_width=20)
sd = from_columns(raw, y="spd", name="single LED 630 nm")
```

## 模块定位

当前分层关系：

```text
color.generators  生成原始列字典
color.spectra     包装成 SpectralDistribution / MultiSpectralDistribution
color.colorimetry 使用光谱对象做 XYZ/LMS/光度学积分
```

`generators` 不负责：

- 文件读取。
- 光谱对象封装。
- XYZ / LMS 积分。
- 色度坐标或颜色空间转换。

它只负责按照公式生成数值列。

## 生成器注册表

生成器支持两种调用方式：

### 1. 直接调用函数

```python
from color.generators.blackbody import blackbody_spd

raw = blackbody_spd(temperature=6500)
```

### 2. 通过注册表 generate(...)

```python
from color.generators import generate

raw = generate("blackbody", "blackbody_spd", temperature=6500)
raw = generate("illuminants", "cie_d_daylight", cct=6500)
raw = generate("ideal", "gaussian", peak_wavelength=555, width=25)
raw = generate("leds", "single", peak_wavelength=630, half_spectral_width=20)
```

注册表相关 API：

| API | 说明 |
| --- | --- |
| `GeneratorEntry` | 生成器注册信息 |
| `register(entry)` | 注册一个生成器 |
| `generate(category, name, **kwargs)` | 调用注册生成器 |
| `describe(category, name)` | 查看生成器描述 |
| `list_categories()` | 列出生成器类别 |
| `list_generators(category=None)` | 列出生成器 |
| `clear_cache(category=None, name=None)` | 清理生成结果缓存 |

类别和名称使用 `canonicalize_resource_name(...)` 做宽松匹配，因此大小写、空格、连字符、下划线等轻微差异通常不会影响查找。

## 缓存与只读结果

`generate(...)` 会按：

```text
category + name + kwargs
```

缓存生成结果。再次使用相同参数时会复用缓存。

返回结果会被复制为只读数组，避免调用方意外修改缓存内部状态：

```python
raw = generate("ideal", "gaussian")
raw["spd"].flags.writeable  # False
```

如果确实需要修改，先复制：

```python
spd = raw["spd"].copy()
```

清理缓存：

```python
from color.generators import clear_cache

clear_cache()
clear_cache(category="ideal")
clear_cache(category="ideal", name="gaussian")
```

## 波长参数

大多数生成器使用参数名：

```python
wavelength_nm
```

它表示输出波长采样点，单位 nm。

如果不传入，生成器会使用自己的默认采样域。常见默认：

| 模块 | 默认波长 |
| --- | --- |
| `ideal` / `leds` | `360-780 nm, 1 nm` |
| `blackbody` | `300-830 nm, 1 nm` |
| `illuminant_a_spd` | `300-830 nm, 1 nm` |
| `daylight_spd` | `300-830 nm, 10 nm` |

如果要和标准观察者或其它光谱严格对齐，可以显式传入波长：

```python
import numpy as np

wavelengths = np.arange(360, 831, 1.0)
raw = single_led_spd(wavelength_nm=wavelengths)
```

或者先生成，再在 `spectra` 层使用 `reshape(...)` / `align(...)`。

## Blackbody

黑体模块提供 Planck 黑体辐射：

```python
from color.generators.blackbody import blackbody_spd

raw = blackbody_spd(temperature=6500)
```

返回列：

```python
{
    "wavelength": ...,
    "radiance": ...,
}
```

参数：

| 参数 | 含义 |
| --- | --- |
| `temperature` | 黑体温度，单位 K，必须为正 |
| `wavelength_nm` | 波长采样点，单位 nm |

注册表入口：

```python
from color.generators import generate

raw = generate("blackbody", "blackbody_spd", temperature=6500)
```

注意：这里返回的是光谱辐亮度数值，不会自动归一化到某个峰值或 `Y=100`。如果后续用于色度积分，结果尺度由原始辐亮度决定。

## Illuminants

照明体模块提供公式生成的标准照明体。

### CIE Illuminant A

```python
from color.generators.illuminants import illuminant_a_spd

raw = illuminant_a_spd()
```

返回列：

```python
{
    "wavelength": ...,
    "spd": ...,
}
```

它按 CIE A 光源公式生成相对 SPD。当前默认 560 nm 处归一到约 `100`。

注册表入口：

```python
raw = generate("illuminants", "A")
```

### CIE D-series daylight

```python
from color.generators.illuminants import daylight_spd

raw = daylight_spd(cct=6500)
```

参数：

| 参数 | 含义 |
| --- | --- |
| `cct` | D 系列日光相关色温，范围 `4000-25000 K` |
| `wavelength_nm` | 波长采样点 |

注册表入口：

```python
raw = generate("illuminants", "cie_d_daylight", cct=6500)
```

注意：`daylight_spd(...)` 生成完整 D 系列日光 SPD；`color.colorimetry.CCT_to_xy_CIE_D(...)` 只计算 D 系列日光的 `xy` 色坐标。二者使用同一条 D 系列日光色度公式，但职责不同。

## Ideal Spectra

`ideal` 模块提供理想化光谱，适合测试、示例和构造简单信号。

### constant / zero / equal_energy

```python
from color.generators.ideal import constant_spd, zero_spd, equal_energy_spd

raw = constant_spd(value=0.5)
raw = zero_spd()
raw = equal_energy_spd()
```

返回列默认是：

```python
{
    "wavelength": ...,
    "spd": ...,
}
```

可以改列名：

```python
raw = constant_spd(value=1.0, column="reflectance")
```

### gaussian

```python
from color.generators.ideal import gaussian_spd

raw = gaussian_spd(
    peak_wavelength=555,
    width=25,
    method="normal",
    amplitude=1.0,
)
```

参数：

| 参数 | 含义 |
| --- | --- |
| `peak_wavelength` | 峰值波长，单位 nm |
| `width` | 宽度 |
| `method="normal"` | `width` 解释为标准差 |
| `method="fwhm"` | `width` 解释为半高全宽 |
| `amplitude` | 峰值幅度 |
| `column` | 输出值列名，默认 `"spd"` |

注册表入口：

```python
raw = generate("ideal", "gaussian", peak_wavelength=555, width=25)
```

### multi_gaussian

```python
from color.generators.ideal import multi_gaussian_spd

raw = multi_gaussian_spd(
    peak_wavelengths=(450, 540, 630),
    widths=(18, 35, 24),
    amplitudes=(0.8, 0.55, 1.0),
)
```

`multi_gaussian_spd(...)` 会把多个标准高斯分量相加。它和 `multi_led_spd(...)`
不是同一个模型：

- `multi_gaussian_spd(...)` 使用标准高斯公式，属于理想数学曲线。
- `multi_led_spd(...)` 使用 Ohno 2005 LED 模型，属于 LED 经验谱形。

参数规则也更严格：

- `widths` 和 `amplitudes` 可以是标量，表示所有分量共用同一个值。
- 如果传入数组，长度必须和 `peak_wavelengths` 一致。
- 不会像 `np.resize` 那样循环填充短数组，避免隐藏输入错误。

注册表入口：

```python
raw = generate(
    "ideal",
    "multi_gaussian",
    peak_wavelengths=(450, 540, 630),
    widths=(18, 35, 24),
    amplitudes=(0.8, 0.55, 1.0),
)
```

## LED

LED 模块使用 Ohno 2005 LED 模型。

### single_led_spd

```python
from color.generators.leds import single_led_spd

raw = single_led_spd(
    peak_wavelength=630,
    half_spectral_width=20,
    amplitude=1.0,
)
```

参数：

| 参数 | 含义 |
| --- | --- |
| `peak_wavelength` | 峰值波长，单位 nm |
| `half_spectral_width` | 半谱宽，必须为正 |
| `amplitude` | 幅度 |
| `column` | 输出值列名 |

注册表入口：

```python
raw = generate("leds", "single", peak_wavelength=630, half_spectral_width=20)
```

### multi_led_spd

```python
from color.generators.leds import multi_led_spd

raw = multi_led_spd(
    peak_wavelengths=(460, 530, 620),
    half_spectral_widths=(18, 28, 22),
    peak_power_ratios=(0.4, 0.7, 0.9),
)
```

多 LED 生成器会把多个单 LED 分量相加。`half_spectral_widths` 和 `peak_power_ratios` 会按 `peak_wavelengths` 的形状调整。

注册表入口：

```python
raw = generate(
    "leds",
    "multi",
    peak_wavelengths=(460, 530, 620),
    half_spectral_widths=(18, 28, 22),
    peak_power_ratios=(0.4, 0.7, 0.9),
)
```

## Individual Cone Fundamentals

`individual_cone_fundamentals` 类别用于生成个体化 LMS cone fundamentals。
当前注册了两个模型：

- `stockman_rider_2023`：Stockman/Rider 2023 公式，参数包括 2/10 度、OD、
  macular/lens density 和 L/M/S 峰值偏移。
- `asano2016`：Asano et al. 2016 individual colorimetric observer model，
  参数包括年龄、视场大小、lens/macular density deviation、photopigment OD
  deviation 和 L/M/S lambda-max shift。

二者都返回最终的 corneal energy LMS：

```python
from color.generators import generate

raw = generate(
    "individual_cone_fundamentals",
    "stockman_rider_2023",
    observer_degree=2,
    l_shift_nm=2.0,
    m_shift_nm=-1.0,
)
```

Asano 2016：

```python
from color.generators import generate

raw = generate(
    "individual_cone_fundamentals",
    "asano2016",
    age=45,
    field_size_degree=4,
    lens_density_deviation=10.0,
)
```

返回列为：

```python
{
    "wavelength": ...,
    "l": ...,
    "m": ...,
    "s": ...,
}
```

也可以使用直接入口：

```python
from color.generators import (
    generate_asano2016_individual_cone_fundamentals,
    generate_stockman_rider_2023_individual_cone_fundamentals,
)

stockman = generate_stockman_rider_2023_individual_cone_fundamentals(
    observer_degree=10
)
asano = generate_asano2016_individual_cone_fundamentals(
    age=32,
    field_size_degree=10,
)
```

Stockman/Rider 常用参数：

| 参数 | 含义 |
| --- | --- |
| `observer_degree` | `2` 或 `10`，选择默认 OD 和 macular density |
| `photopigment_od` | L/M/S photopigment optical density |
| `macular_density_460` | 460 nm 处 macular pigment density |
| `lens_density_400` | 400 nm 处 lens density |
| `l_shift_nm`, `m_shift_nm`, `s_shift_nm` | L/M/S 峰值波长偏移 |
| `l_template` | `"mean"`、`"ser180"` 或 `"ala180"` |

第一版不做 codon/hybrid 到 shift 的自动推导；如果需要个体观察者差异，
请直接传入 shift 和密度参数。

Asano 2016 的参数以 deviation 形式表达相对平均观察者的变化，例如
`lens_density_deviation=10` 表示 lens density 增加约 10%。如果只需要 CIE 2006
平均 2 度或 10 度 LMS fundamentals，优先使用 `color.spectra` 的 CIE 2006
静态数据入口；Asano 入口适合需要年龄、视场和个体差异模型时使用。

## 从 generators 到 spectra

生成器返回的是原始字典。如果后续要做插值、对齐、积分，推荐立即包装：

```python
from color.generators.leds import multi_led_spd
from color.spectra import from_columns

raw = multi_led_spd(
    peak_wavelengths=(460, 530, 620),
    half_spectral_widths=(18, 28, 22),
    peak_power_ratios=(0.4, 0.7, 0.9),
)

led = from_columns(raw, y="spd", name="RGB LED mixture")
```

然后可以进入 `color.colorimetry`：

```python
from color.colorimetry import emission_to_XYZ
from color.spectra import from_cie1931_xyz_cmfs

cmfs = from_cie1931_xyz_cmfs(interval_nm=1)
XYZ = emission_to_XYZ(led, cmfs=cmfs)
```

## 常见误区

### generators 不是 datasets

`datasets` 读取固定文件；`generators` 根据参数生成数据。即使某些公式对应标准数据，例如 Illuminant A 或 D 系列日光，也仍属于生成器，因为结果由公式和参数决定。

### 生成结果不是光谱对象

生成器返回字典：

```python
raw["wavelength"]
raw["spd"]
```

如果需要：

```python
sd.sample(...)
sd.reshape(...)
sd.align(...)
```

必须先用 `from_columns(...)` 包装。

### 不要把所有实验数据都放进 generators

`generators` 适合可复现公式和过程模型。未来频繁编辑的实验数据、测量数据、用户本地数据，更适合走单独的 IO 路线，而不是注册成标准生成器。

### 生成器不自动做色度归一化

多数生成器只生成相对 SPD 或物理辐射量。是否归一化到 `Y=100`、是否乘响应函数积分，属于 `color.colorimetry` 的职责。

## API 总览

### 注册表

```python
GeneratorEntry
register
generate
describe
clear_cache
list_categories
list_generators
```

### Blackbody

```python
blackbody_spd
generate_blackbody
list_blackbody_generators
```

### Illuminants

```python
illuminant_a_spd
daylight_spd
generate_illuminant
list_illuminant_generators
```

### Ideal

```python
constant_spd
zero_spd
equal_energy_spd
gaussian_spd
multi_gaussian_spd
generate_ideal
list_ideal_generators
```

### LEDs

```python
single_led_spd
multi_led_spd
generate_led
list_led_generators
```

### Individual Cone Fundamentals

```python
generate_stockman_rider_2023_individual_cone_fundamentals
generate_asano2016_individual_cone_fundamentals
generate_individual_cone_fundamental
list_individual_cone_fundamental_generators
```

## 测试

运行生成器测试：

```powershell
.\.venv\Scripts\python.exe -m pytest color\generators\tests -q --basetemp .pytest_tmp
```

运行全量测试：

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .pytest_tmp
```
