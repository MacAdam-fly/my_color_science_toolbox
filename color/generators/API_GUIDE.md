# color.generators API 使用指南

本文档按 `color.generators.__all__` 覆盖顶层 API。这里写最小使用案例；
模块定位、缓存语义、公式说明和注意事项见 [`README_DETAILS.md`](README_DETAILS.md)。

`generators` 返回原始列字典：

```python
dict[str, numpy.ndarray]
```

如果后续需要插值、reshape、align 或色度积分，请用 `color.spectra.from_columns(...)`
包装成光谱对象。

## 顶层 API 总览

### 注册表

| API | 功能 |
| --- | --- |
| `GeneratorEntry` | 生成器注册描述对象 |
| `register` | 注册生成器 |
| `generate` | 按 category/name 调用生成器 |
| `describe` | 查看生成器描述 |
| `clear_cache` | 清理生成缓存 |
| `list_categories` | 列出生成器类别 |
| `list_generators` | 列出生成器名称 |

### 公式生成器

| API | 功能 |
| --- | --- |
| `blackbody_spd`, `generate_blackbody`, `list_blackbody_generators` | 黑体光谱 |
| `illuminant_a_spd`, `daylight_spd`, `generate_illuminant`, `list_illuminant_generators` | CIE A / D 系列照明体 |
| `constant_spd`, `zero_spd`, `equal_energy_spd`, `gaussian_spd`, `generate_ideal`, `list_ideal_generators` | 理想光谱 |
| `single_led_spd`, `multi_led_spd`, `generate_led`, `list_led_generators` | LED 光谱 |
| `macular_density_spectrum`, `lens_density_spectrum`, `cone_absorbance_spectra`, `generate_individual_cone_fundamentals`, `generate_individual_cone_fundamental`, `list_individual_cone_fundamental_generators` | Stockman/Rider 个体锥体模型 |

## 注册表 API

### `GeneratorEntry`

用途：描述一个可注册生成器。

输入：`category`、`name`、`description`、`generate_fn`、可选 `parameters` 和 `metadata`。  
返回：不可变 dataclass 实例。

```python
import numpy as np
from color.generators import GeneratorEntry

def demo_generator(value=1.0):
    wavelength = np.arange(400, 701, 100, dtype=float)
    return {"wavelength": wavelength, "spd": np.full_like(wavelength, value)}

entry = GeneratorEntry(
    category="demo",
    name="constant",
    description="Small demo generator",
    generate_fn=demo_generator,
    parameters=("value",),
    metadata={"quantity": "relative_spd"},
)
```

注意：`GeneratorEntry` 只是描述对象；需要 `register(entry)` 后才能被 `generate(...)` 调用。

### `register(entry)`

用途：把自定义生成器加入全局注册表。

```python
from color.generators import generate, register

register(entry)
raw = generate("demo", "constant", value=0.5)
```

注意：category/name 会做资源名 canonical 匹配；如果和已有 canonical 名称冲突会抛错。

### `generate(category, name, **kwargs)`

用途：按注册表生成数据。结果会缓存，并以只读数组形式返回。

普通调用：

```python
from color.generators import generate

raw = generate("ideal", "gaussian", peak_wavelength=555, width=25)
```

类别/名称宽松匹配：

```python
raw = generate("Illuminants", "cie d daylight", cct=6500)
```

和 `spectra` 串联：

```python
from color.generators import generate
from color.spectra import from_columns

raw = generate("leds", "single", peak_wavelength=630, half_spectral_width=20)
sd = from_columns(raw, y="spd", name="single LED 630 nm")
```

注意：生成器返回字典，不是 `SpectralDistribution`。

### `describe(category, name)`

用途：查看注册项说明、参数和 metadata。

```python
from color.generators import describe

entry = describe("illuminants", "cie_d_daylight")
print(entry.description)
print(entry.parameters)
print(entry.metadata)
```

### `list_categories()` / `list_generators(category=None)`

用途：查看可用生成器。

```python
from color.generators import list_categories, list_generators

categories = list_categories()
all_names = list_generators()
led_names = list_generators("leds")
```

### `clear_cache(category=None, name=None)`

用途：清理 `generate(...)` 缓存，返回删除数量。

清空全部：

```python
from color.generators import clear_cache

removed = clear_cache()
```

按 category：

```python
removed = clear_cache(category="ideal")
```

按 category + name：

```python
removed = clear_cache(category="ideal", name="gaussian")
```

注意：`name` 必须和 `category` 一起传入。

## Blackbody

### `blackbody_spd(wavelength_nm=None, temperature=6500.0)`

用途：按 Planck 定律生成黑体光谱辐亮度。

```python
from color.generators import blackbody_spd

raw = blackbody_spd(temperature=6500)
print(raw["wavelength"])
print(raw["radiance"])
```

自定义波长：

```python
import numpy as np
from color.generators import blackbody_spd

wavelength = np.arange(380, 781, 5)
raw = blackbody_spd(wavelength_nm=wavelength, temperature=3000)
```

注意：返回列名是 `radiance`，不是 `spd`。

### `generate_blackbody(name="blackbody_spd", **kwargs)` / `list_blackbody_generators()`

```python
from color.generators import generate_blackbody, list_blackbody_generators

print(list_blackbody_generators())
raw = generate_blackbody(temperature=6500)
```

## Illuminants

### `illuminant_a_spd(wavelength_nm=None)`

用途：生成 CIE Standard Illuminant A 相对 SPD。

```python
from color.generators import illuminant_a_spd

a = illuminant_a_spd()
```

### `daylight_spd(wavelength_nm=None, cct=6500.0)`

用途：生成 CIE D-series daylight SPD。

```python
from color.generators import daylight_spd

d65 = daylight_spd(cct=6500)
d50 = daylight_spd(cct=5000)
```

注意：`cct` 必须在 `4000-25000 K`。这是完整 SPD；只需要 D 系列 xy 时用
`color.colorimetry.CCT_to_xy_CIE_D(...)`。

### `generate_illuminant(name, **kwargs)` / `list_illuminant_generators()`

```python
from color.generators import generate_illuminant, list_illuminant_generators

print(list_illuminant_generators())
a = generate_illuminant("A")
d65 = generate_illuminant("cie_d_daylight", cct=6500)
```

## Ideal Spectra

### `constant_spd(...)` / `zero_spd(...)` / `equal_energy_spd(...)`

用途：生成常数、零值和等能量理想光谱。

```python
from color.generators import constant_spd, equal_energy_spd, zero_spd

constant = constant_spd(value=0.5)
zero = zero_spd()
ee = equal_energy_spd()
```

自定义列名：

```python
from color.generators import constant_spd

reflectance = constant_spd(value=1.0, column="reflectance")
```

### `gaussian_spd(wavelength_nm=None, peak_wavelength=555.0, width=25.0, method="normal", amplitude=1.0, column="spd")`

用途：生成高斯理想光谱。

标准差宽度：

```python
from color.generators import gaussian_spd

raw = gaussian_spd(peak_wavelength=555, width=25, method="normal")
```

FWHM 宽度：

```python
raw = gaussian_spd(peak_wavelength=555, width=50, method="fwhm")
```

### `generate_ideal(name, **kwargs)` / `list_ideal_generators()`

```python
from color.generators import generate_ideal, list_ideal_generators

print(list_ideal_generators())
raw = generate_ideal("gaussian", peak_wavelength=555, width=25)
```

## LED

### `single_led_spd(wavelength_nm=None, peak_wavelength=555.0, half_spectral_width=25.0, amplitude=1.0, column="spd")`

用途：生成单 LED SPD。

```python
from color.generators import single_led_spd

red = single_led_spd(peak_wavelength=630, half_spectral_width=20)
```

### `multi_led_spd(wavelength_nm=None, peak_wavelengths=..., half_spectral_widths=..., peak_power_ratios=None, column="spd")`

用途：把多个 Ohno 2005 LED 分量相加。

三峰 LED：

```python
from color.generators import multi_led_spd

rgb = multi_led_spd(
    peak_wavelengths=(460, 530, 620),
    half_spectral_widths=(18, 28, 22),
    peak_power_ratios=(0.4, 0.7, 0.9),
)
```

使用默认峰值但自定义功率：

```python
rgb = multi_led_spd(peak_power_ratios=(0.7, 1.0, 1.5))
```

注意：为避免把峰值误传成 `wavelength_nm`，建议始终使用关键字参数。

### `generate_led(name, **kwargs)` / `list_led_generators()`

```python
from color.generators import generate_led, list_led_generators

print(list_led_generators())
single = generate_led("single", peak_wavelength=630, half_spectral_width=20)
multi = generate_led("multi", peak_wavelengths=(460, 530, 620))
```

## Individual Cone Fundamentals

### `macular_density_spectrum(...)`

用途：生成 Stockman/Rider macular density 光谱。

```python
from color.generators import macular_density_spectrum

raw = macular_density_spectrum()
```

### `lens_density_spectrum(...)`

用途：生成 lens density 光谱。

```python
from color.generators import lens_density_spectrum

raw = lens_density_spectrum()
```

### `cone_absorbance_spectra(...)`

用途：生成 L/M/S photopigment absorbance 模板。

```python
from color.generators import cone_absorbance_spectra

raw = cone_absorbance_spectra(
    l_shift_nm=1.0,
    m_shift_nm=-1.0,
    s_shift_nm=0.0,
    l_template="mean",
)
```

注意：这些 density / absorbance 函数服务于个体锥体模型分析；一般积分工作流更常用
`generate_individual_cone_fundamentals(...)`。模板函数不接收个体 density 缩放；
`macular_density_460`、`lens_density_400` 和 `photopigment_od` 属于最终 LMS fundamentals
生成函数的参数。

### `generate_individual_cone_fundamentals(**kwargs)`

用途：生成 Stockman/Rider 2023 个体化 corneal energy LMS fundamentals。

默认 2 度观察者：

```python
from color.generators import generate_individual_cone_fundamentals

lms2 = generate_individual_cone_fundamentals(observer_degree=2)
```

10 度观察者：

```python
lms10 = generate_individual_cone_fundamentals(observer_degree=10)
```

改变个体参数：

```python
custom = generate_individual_cone_fundamentals(
    observer_degree=2,
    l_shift_nm=2.0,
    m_shift_nm=-1.0,
    macular_density_460=0.28,
)
```

### `generate_individual_cone_fundamental(name="stockman_rider_2023", **kwargs)` / `list_individual_cone_fundamental_generators()`

```python
from color.generators import (
    generate_individual_cone_fundamental,
    list_individual_cone_fundamental_generators,
)

print(list_individual_cone_fundamental_generators())
lms = generate_individual_cone_fundamental(observer_degree=2)
```

## 从 generators 到 spectra / colorimetry

生成器返回原始数据字典。需要计算 XYZ 时，先包装：

```python
from color.generators import multi_led_spd
from color.spectra import from_columns, from_cie1931_xyz_cmfs
from color.colorimetry import emission_to_XYZ

raw = multi_led_spd(
    peak_wavelengths=(460, 530, 620),
    half_spectral_widths=(18, 28, 22),
    peak_power_ratios=(0.4, 0.7, 0.9),
)
sd = from_columns(raw, y="spd", name="RGB LED")
cmfs = from_cie1931_xyz_cmfs(interval_nm=1)

XYZ = emission_to_XYZ(sd, cmfs=cmfs)
```

反射率场景不要直接把生成的照明体当作反射谱；照明体应传给
`reflectance_to_XYZ(..., illuminant=...)`。
