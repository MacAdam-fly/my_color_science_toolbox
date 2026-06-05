# color.individual_cone_fundamentals API 使用指南

本文档对应 `color.individual_cone_fundamentals` 顶层公开 API。该模块基于 Stockman & Rider 2023 公式生成标准或个体化 LMS cone fundamentals。

英文快速入口见 [`README.md`](README.md)，中文设计说明见 [`README_DETAILS.md`](README_DETAILS.md)。

## API 总览

| API | 用途 |
| --- | --- |
| `STOCKMAN_RIDER_REFERENCE` | Stockman/Rider 2023 模型参考文献说明字符串 |
| `macular_density_spectrum` | 生成 macular pigment density 谱模板 |
| `lens_density_spectrum` | 生成 lens density 谱模板 |
| `cone_absorbance_spectra` | 生成 L/M/S photopigment absorbance 谱模板 |
| `generate_individual_cone_fundamentals` | 生成最终 corneal energy LMS cone fundamentals |

## 基本约定

- 默认波长为 `360-850 nm / 1 nm`。
- 所有函数返回原始列字典，至少包含 `wavelength`。
- `generate_individual_cone_fundamentals(...)` 的输出包含 `wavelength, l, m, s`。
- 最终 `l/m/s` 是 corneal energy LMS fundamentals，并且每个通道独立峰值归一化到 1。
- 该模块只负责公式生成；插值、重采样和通道访问建议交给 `color.spectra` 包装层。

## `STOCKMAN_RIDER_REFERENCE`

模型参考文献说明。

```python
from color.individual_cone_fundamentals import STOCKMAN_RIDER_REFERENCE

print(STOCKMAN_RIDER_REFERENCE)
```

适合写入 metadata 或生成报告时标注模型来源。

## `macular_density_spectrum(wavelength_nm=None)`

生成 macular pigment density 谱模板。

### 默认波长

```python
from color.individual_cone_fundamentals import macular_density_spectrum

raw = macular_density_spectrum()
print(raw.keys())          # wavelength, macular_density
print(raw["wavelength"])   # 默认 360-850 nm
```

### 自定义波长

```python
import numpy as np
from color.individual_cone_fundamentals import macular_density_spectrum

wavelengths = np.arange(400.0, 701.0, 5.0)
raw = macular_density_spectrum(wavelengths)
```

注意：这个函数只生成密度模板，不乘以个体化的 `macular_density_460`。完整 cone fundamentals 生成时才使用该密度参数。

## `lens_density_spectrum(wavelength_nm=None)`

生成 lens density 谱模板。

### 默认波长

```python
from color.individual_cone_fundamentals import lens_density_spectrum

raw = lens_density_spectrum()
print(raw.keys())  # wavelength, lens_density
```

### 自定义波长

```python
import numpy as np
from color.individual_cone_fundamentals import lens_density_spectrum

raw = lens_density_spectrum(np.arange(380.0, 781.0, 2.0))
```

注意：这个函数只生成 lens density 模板，不等同于最终 LMS fundamentals。

## `cone_absorbance_spectra(wavelength_nm=None, *, l_shift_nm=0.0, m_shift_nm=0.0, s_shift_nm=0.0, l_template="mean")`

生成 L/M/S photopigment absorbance 谱。

### 默认平均模板

```python
from color.individual_cone_fundamentals import cone_absorbance_spectra

raw = cone_absorbance_spectra()
print(raw.keys())  # wavelength, l, m, s
```

### 模拟 cone 峰值偏移

```python
from color.individual_cone_fundamentals import cone_absorbance_spectra

raw = cone_absorbance_spectra(
    l_shift_nm=2.0,
    m_shift_nm=-1.0,
    s_shift_nm=0.0,
)
```

### 指定 L cone 多态模板

```python
from color.individual_cone_fundamentals import cone_absorbance_spectra

ser = cone_absorbance_spectra(l_template="ser180")
ala = cone_absorbance_spectra(l_template="ala180")
mean = cone_absorbance_spectra(l_template="mean")
```

`l_template="mean"` 使用项目实现的群体平均 L 模板。`ser180` 和 `ala180` 用于显式比较 L cone polymorphism。

## `generate_individual_cone_fundamentals(...)`

生成最终 corneal energy LMS cone fundamentals，是该模块最主要的入口。

签名核心参数：

```python
generate_individual_cone_fundamentals(
    wavelength_nm=None,
    *,
    observer_degree=2,
    photopigment_od=None,
    macular_density_460=None,
    lens_density_400=1.7649,
    l_shift_nm=0.0,
    m_shift_nm=0.0,
    s_shift_nm=0.0,
    l_template="mean",
)
```

### 标准 2° 模型

```python
from color.individual_cone_fundamentals import generate_individual_cone_fundamentals

lms_2 = generate_individual_cone_fundamentals(observer_degree=2)
print(lms_2.keys())  # wavelength, l, m, s
```

默认参数：

```text
photopigment_od=(0.50, 0.50, 0.40)
macular_density_460=0.350
lens_density_400=1.7649
```

### 标准 10° 模型

```python
from color.individual_cone_fundamentals import generate_individual_cone_fundamentals

lms_10 = generate_individual_cone_fundamentals(observer_degree=10)
```

默认参数：

```text
photopigment_od=(0.38, 0.38, 0.30)
macular_density_460=0.095
lens_density_400=1.7649
```

### 自定义个体参数

```python
from color.individual_cone_fundamentals import generate_individual_cone_fundamentals

individual = generate_individual_cone_fundamentals(
    observer_degree=2,
    photopigment_od=(0.45, 0.52, 0.38),
    macular_density_460=0.50,
    lens_density_400=1.60,
    l_shift_nm=2.0,
    m_shift_nm=-1.0,
    s_shift_nm=0.0,
)
```

这些参数用于直接建模个体差异。当前版本不从 codon 或 genotype 自动推导这些偏移。

### 自定义波长采样

```python
import numpy as np
from color.individual_cone_fundamentals import generate_individual_cone_fundamentals

wavelengths = np.arange(400.0, 831.0, 1.0)
lms = generate_individual_cone_fundamentals(wavelengths, observer_degree=2)
```

如果后续要和其他光谱数据积分，通常建议先包装为 `MultiSpectralDistribution`，再用 spectra 的 `align(...)` 或 `reshape(...)` 对齐采样。

## 与 `color.generators` 的关系

该模型也注册在 `color.generators` 中。需要统一生成器入口时可以这样用：

```python
from color.generators import generate

raw = generate(
    "individual_cone_fundamentals",
    "stockman_rider_2023",
    observer_degree=2,
)
```

这和直接调用核心函数的结果语义一致，仍然返回原始列字典。

## 与 `color.spectra` 的关系

需要插值、重采样、通道访问或后续光谱积分时，优先使用 `spectra` 为该模型专门设计的包装入口，而不是手工调用 `from_columns(...)`。

```python
from color.spectra import from_individual_cone_fundamentals

lms = from_individual_cone_fundamentals(observer_degree=2)
print(lms.keys())       # wavelength, l, m, s
print(lms["l"].values)  # L channel as SpectralDistribution values
```

这个专用入口内部会调用 `color.generators.generate_individual_cone_fundamentals(...)`，
再包装成 `MultiSpectralDistribution`，并在 metadata 中保留 generator 类别、名称和传入参数。`individual_cone_fundamentals` 本身只负责公式生成和返回原始列字典。

## 常见工作流

### 比较标准 2° 与个体化模型

```python
from color.individual_cone_fundamentals import generate_individual_cone_fundamentals

standard = generate_individual_cone_fundamentals(observer_degree=2)
shifted = generate_individual_cone_fundamentals(
    observer_degree=2,
    l_shift_nm=2.0,
    m_shift_nm=-1.0,
)

delta_l = shifted["l"] - standard["l"]
```

### 生成 LMS fundamentals 后用于 LMS 响应计算

```python
from color.colorimetry import emission_to_LMS
from color.generators import generate_ideal_spectrum
from color.spectra import from_columns, from_individual_cone_fundamentals

led_raw = generate_ideal_spectrum(kind="gaussian", peak_wavelength=530, fwhm=20)
led = from_columns(led_raw, y="spd")

lms_fundamentals = from_individual_cone_fundamentals(observer_degree=2)
LMS = emission_to_LMS(led, fundamentals=lms_fundamentals)
```

## 使用边界

- 当前版本不做 codon/hybrid genotype 推断。
- 当前版本不输出中间层级的完整对象；模板函数可用于检查中间谱。
- 默认输出是 energy-based corneal LMS fundamentals。
- 若需要复现 CIE 2006 标准观察者，严格比较应主要关注 `400-830 nm` 区间。
