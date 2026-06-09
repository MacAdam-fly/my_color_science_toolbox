# color.individual_cone_fundamentals API 使用指南

本文档对应 `color.individual_cone_fundamentals` 顶层公开 API。模块设计和
两种模型的计算语义见 [`README_DETAILS.md`](README_DETAILS.md)。

## 顶层 API 总览

| API | 用途 |
| --- | --- |
| `STOCKMAN_RIDER_REFERENCE` | Stockman/Rider 2023 参考文献字符串 |
| `ASANO2016_REFERENCE` | Asano et al. 2016 参考文献字符串 |
| `generate_stockman_rider_2023_individual_cone_fundamentals` | 生成 Stockman/Rider 2023 LMS fundamentals |
| `stockman_rider_2023_model_components` | 返回 Stockman/Rider 当前参数下的中间产物 |
| `generate_asano2016_individual_cone_fundamentals` | 生成 Asano 2016 LMS fundamentals |
| `asano2016_model_components` | 返回 Asano 当前参数下的中间产物 |

## 参考文献字符串

```python
from color.individual_cone_fundamentals import (
    ASANO2016_REFERENCE,
    STOCKMAN_RIDER_REFERENCE,
)

print(STOCKMAN_RIDER_REFERENCE)
print(ASANO2016_REFERENCE)
```

这些字符串适合写入 metadata、图注或报告。

## `generate_stockman_rider_2023_individual_cone_fundamentals(...)`

用途：生成 Stockman/Rider 2023 corneal energy LMS fundamentals。

标准 2 度观察者：

```python
from color.individual_cone_fundamentals import (
    generate_stockman_rider_2023_individual_cone_fundamentals,
)

lms_2 = generate_stockman_rider_2023_individual_cone_fundamentals(
    observer_degree=2
)
```

标准 10 度观察者：

```python
lms_10 = generate_stockman_rider_2023_individual_cone_fundamentals(
    observer_degree=10
)
```

改变个体参数：

```python
individual = generate_stockman_rider_2023_individual_cone_fundamentals(
    observer_degree=2,
    photopigment_od=(0.45, 0.52, 0.38),
    macular_density_460=0.50,
    lens_density_400=1.50,
    l_shift_nm=2.0,
    m_shift_nm=-1.0,
)
```

返回值是原始列字典：

```python
{
    "wavelength": ...,
    "l": ...,
    "m": ...,
    "s": ...,
}
```

## `stockman_rider_2023_model_components(...)`

用途：返回 Stockman/Rider 当前观察者参数下的完整中间产物。

```python
from color.individual_cone_fundamentals import (
    stockman_rider_2023_model_components,
)

components = stockman_rider_2023_model_components(
    observer_degree=2,
    l_shift_nm=2.0,
    macular_density_460=0.50,
    lens_density_400=1.50,
)

lens = components["lens_density"]
macular = components["macular_density"]
absorbance = components["photopigment_absorbance"]
final_lms = components["corneal_energy"]
```

返回字段统一为：

```python
{
    "wavelength": ...,
    "photopigment_absorbance": ...,
    "photopigment_od": ...,
    "retinal_absorptance": ...,
    "macular_density": ...,
    "lens_density": ...,
    "prereceptoral_density": ...,
    "corneal_quantal": ...,
    "corneal_energy": ...,
}
```

注意：这里的 `macular_density` 和 `lens_density` 已经应用当前个体参数，不是未缩放标准模板。

## `generate_asano2016_individual_cone_fundamentals(...)`

用途：生成 Asano et al. 2016 individual colorimetric observer LMS fundamentals。

默认观察者：

```python
from color.individual_cone_fundamentals import (
    generate_asano2016_individual_cone_fundamentals,
)

default = generate_asano2016_individual_cone_fundamentals()
```

改变 age 和 field size：

```python
older = generate_asano2016_individual_cone_fundamentals(
    age=70,
    field_size_degree=2,
)

wide_field = generate_asano2016_individual_cone_fundamentals(
    age=32,
    field_size_degree=10,
)
```

改变个体化参数：

```python
individual = generate_asano2016_individual_cone_fundamentals(
    lens_density_deviation=20.0,
    macular_density_deviation=30.0,
    photopigment_od_deviation=(5.0, -3.0, 0.0),
    photopigment_shift_nm=(4.0, -2.0, 0.0),
)
```

注意：Asano 的 deviation 参数是相对平均值的百分比偏差；shift 参数单位是 nm。

## `asano2016_model_components(...)`

用途：返回 Asano 当前观察者参数下的完整中间产物。

```python
from color.individual_cone_fundamentals import asano2016_model_components

components = asano2016_model_components(
    age=60,
    field_size_degree=4,
    lens_density_deviation=10.0,
    macular_density_deviation=-5.0,
    photopigment_shift_nm=(2.0, -1.0, 0.0),
)

lens = components["lens_density"]
macular = components["macular_density"]
absorbance = components["photopigment_absorbance"]
final_lms = components["corneal_energy"]
```

Asano 的 `lens_density` 已经应用 age 和 lens deviation；`macular_density` 已经应用
field size 和 macular deviation；`photopigment_absorbance` 已经应用 L/M/S shift。

## 与 generators / spectra 配合

通过 generators 注册表：

```python
from color.generators import generate_individual_cone_fundamental

stockman = generate_individual_cone_fundamental("stockman_rider_2023")
asano = generate_individual_cone_fundamental("asano2016", age=45)
```

包装成 `MultiSpectralDistribution`：

```python
from color.spectra import from_asano2016_individual_cone_fundamentals

lms = from_asano2016_individual_cone_fundamentals(age=45)
print(lms.keys())       # wavelength, l, m, s
print(lms["l"].values)  # L channel values
```

Stockman/Rider 的 spectra 包装入口为：

```python
from color.spectra import from_stockman_rider_2023_individual_cone_fundamentals

lms = from_stockman_rider_2023_individual_cone_fundamentals(observer_degree=2)
```

## 用于光谱积分

```python
from color.colorimetry import emission_to_LMS
from color.generators import gaussian_spd
from color.spectra import (
    from_asano2016_individual_cone_fundamentals,
    from_columns,
)

led_raw = gaussian_spd(peak_wavelength=530, width=18)
led = from_columns(led_raw, x="wavelength", y="spd")
lms_fundamentals = from_asano2016_individual_cone_fundamentals(age=45)
LMS = emission_to_LMS(led, fundamentals=lms_fundamentals)
```
