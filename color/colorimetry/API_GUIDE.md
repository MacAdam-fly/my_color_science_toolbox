# color.colorimetry API 使用指南

本文档按 `color.colorimetry.__all__` 覆盖顶层 API。这里写最小使用案例；
积分规则、轨迹差异、算法解释和完整示例索引见 [`README_DETAILS.md`](README_DETAILS.md)。

色温算法的底层实现函数，例如 Robertson、Ohno 和 McCamy 的直接入口，
保留在 `color.colorimetry.temperature` 子包中。`color.colorimetry` 顶层只保留
推荐的通用分发入口和常用计算入口。

## 顶层 API 总览

### 默认常量

| API | 功能 |
| --- | --- |
| `DEFAULT_CMFS` | 默认 XYZ CMFs 数据集名 |
| `DEFAULT_FUNDAMENTALS` | 默认 LMS fundamentals 数据集名 |
| `DEFAULT_ILLUMINANT` | 默认反射率积分照明体 |
| `DEFAULT_PHOTOPIC_LEF` | 默认明视觉光视效率函数 |
| `DEFAULT_SCOTOPIC_LEF` | 默认暗视觉光视效率函数 |
| `DEFAULT_PHOTOPIC_K_M` | 默认明视觉最大光效 |
| `DEFAULT_SCOTOPIC_K_M` | 默认暗视觉最大光效 |

### 主要计算入口

| API | 功能 |
| --- | --- |
| `emission_to_XYZ`, `reflectance_to_XYZ` | 光谱到 XYZ |
| `emission_to_LMS`, `reflectance_to_LMS` | 光谱到 LMS |
| `XYZ_to_xyY`, `xyY_to_XYZ`, `XYZ_to_xy` | XYZ / xyY / xy |
| `xy_to_uv1960`, `XYZ_to_uv1960`, `uv1960_to_xy` | CIE 1960 UCS uv |
| `xy_to_upvp1976`, `XYZ_to_upvp1976`, `upvp1976_to_xy` | CIE 1976 UCS u'v' |
| `LMS_to_XYZ`, `XYZ_to_LMS` | CIE 2006 LMS / XYZ 矩阵转换 |
| `Y_to_Lstar`, `Lstar_to_Y` | CIE 1976 lightness |
| `photopic_*`, `scotopic_*`, `luminous_*` | 光度学 |
| `analyze_chromaticity`, `dominant_wavelength`, `complementary_wavelength`, `*_purity` | 主波长、互补波长和纯度 |
| `xy_from_dominant_wavelength_pe`, `xy_from_dominant_wavelength_pc` | 主波长 + 纯度反向构造 xy |
| `analyze_temperature`, `xy_to_CCT_Duv`, `CCT_Duv_to_xy`, `uv_to_CCT`, `CCT_to_uv` | 色温和 Duv |

## 默认常量

用途：查看高层函数默认使用的数据集和光度常数。

```python
from color.colorimetry import (
    DEFAULT_CMFS,
    DEFAULT_FUNDAMENTALS,
    DEFAULT_ILLUMINANT,
    DEFAULT_PHOTOPIC_LEF,
    DEFAULT_SCOTOPIC_LEF,
    DEFAULT_PHOTOPIC_K_M,
    DEFAULT_SCOTOPIC_K_M,
)

print(DEFAULT_CMFS)
print(DEFAULT_FUNDAMENTALS)
print(DEFAULT_ILLUMINANT)
print(DEFAULT_PHOTOPIC_LEF, DEFAULT_PHOTOPIC_K_M)
print(DEFAULT_SCOTOPIC_LEF, DEFAULT_SCOTOPIC_K_M)
```

注意：常量用于理解默认条件。科研复现代码中建议显式传入 CMFs、illuminant 或 fundamentals。

## 光谱到 XYZ / LMS

### `emission_to_XYZ(emission, *, cmfs=..., shape=None, k=None)`

用途：自发光光谱积分到 XYZ。

输入：`SpectralDistribution` 或 `MultiSpectralDistribution`，CMFs 可传字符串或对象。  
返回：XYZ 数组。

显式响应函数：

```python
from color.generators.leds import multi_led_spd
from color.spectra import from_columns, from_cie1931_xyz_cmfs
from color.colorimetry import emission_to_XYZ

raw = multi_led_spd(
    peak_wavelengths=(460, 530, 620),
    half_spectral_widths=(18, 28, 22),
    peak_power_ratios=(0.4, 0.7, 0.9),
)
led = from_columns(raw, y="spd", name="three-peak LED")
cmfs = from_cie1931_xyz_cmfs(interval_nm=1)

XYZ = emission_to_XYZ(led, cmfs=cmfs)
```

便捷字符串：

```python
XYZ = emission_to_XYZ(led, cmfs="cie1931_xyz_1nm")
```

注意：自发光积分默认不归一化；`k=None` 时按 `k=1` 处理。

### `reflectance_to_XYZ(reflectance, *, illuminant=..., cmfs=..., shape=None, k=None)`

用途：反射率在照明体下积分到 XYZ。

输入：反射率对象、照明体、CMFs。  
返回：XYZ 数组。

显式对象：

```python
from color.datasets import get_color_card
from color.spectra import from_columns, from_D65_illuminant, from_cie1931_xyz_cmfs
from color.colorimetry import reflectance_to_XYZ

raw = get_color_card("pmc")
patch = from_columns(raw, y="Blue Sky", name="PMC Blue Sky")
d65 = from_D65_illuminant()
cmfs = from_cie1931_xyz_cmfs(interval_nm=1)

XYZ = reflectance_to_XYZ(patch, illuminant=d65, cmfs=cmfs)
```

便捷字符串：

```python
XYZ = reflectance_to_XYZ(patch, illuminant="D65", cmfs="cie1931_xyz_1nm")
```

注意：反射率积分默认归一化，使理想完全反射体在所选照明体下得到 `Y=100`。

### `emission_to_LMS(...)` / `reflectance_to_LMS(...)`

用途：自发光或反射率积分到 LMS。

输入：光谱对象，LMS fundamentals 可传字符串或对象。  
返回：LMS 数组。

```python
from color.spectra import from_cie2006_lms_2degree_fundamentals
from color.colorimetry import emission_to_LMS, reflectance_to_LMS

lms2 = from_cie2006_lms_2degree_fundamentals(interval_nm=1)

LMS_emission = emission_to_LMS(led, fundamentals=lms2)
LMS_reflectance = reflectance_to_LMS(
    patch,
    illuminant=d65,
    fundamentals=lms2,
    normalisation_channel="m",
)
```

注意：LMS 高层入口默认 `fill_nan=0.0`，适合 CVRL S 通道长波端空白作为零响应的积分语义。

## XYZ、xyY、xy 与 UCS 色度坐标

### `XYZ_to_xyY(XYZ)` / `xyY_to_XYZ(xyY)` / `XYZ_to_xy(XYZ)`

用途：XYZ 与基础色度坐标转换。

```python
from color.colorimetry import XYZ_to_xy, XYZ_to_xyY, xyY_to_XYZ

XYZ = [19.01, 20.00, 21.78]

xyY = XYZ_to_xyY(XYZ)
XYZ_back = xyY_to_XYZ(xyY)
xy = XYZ_to_xy(XYZ)
```

批量输入：

```python
import numpy as np
from color.colorimetry import XYZ_to_xyY

XYZ_grid = np.ones((2, 3, 3)) * [19.01, 20.0, 21.78]
xyY_grid = XYZ_to_xyY(XYZ_grid)
```

注意：`xy` 丢失亮度；需要可逆表达时使用 `xyY`。

### `xy_to_uv1960(...)` / `XYZ_to_uv1960(...)` / `uv1960_to_xy(...)`

用途：CIE 1960 UCS `uv` 转换，主要服务 CCT + Duv。

```python
from color.colorimetry import XYZ_to_uv1960, xy_to_uv1960, uv1960_to_xy

uv = xy_to_uv1960([0.3127, 0.3290])
uv_from_XYZ = XYZ_to_uv1960([95.047, 100.0, 108.883])
xy = uv1960_to_xy(uv)
```

### `xy_to_upvp1976(...)` / `XYZ_to_upvp1976(...)` / `upvp1976_to_xy(...)`

用途：CIE 1976 UCS `u'v'` 转换，常用于 Luv 相关色度图。

```python
from color.colorimetry import XYZ_to_upvp1976, xy_to_upvp1976, upvp1976_to_xy

upvp = xy_to_upvp1976([0.3127, 0.3290])
upvp_from_XYZ = XYZ_to_upvp1976([95.047, 100.0, 108.883])
xy = upvp1976_to_xy(upvp)
```

注意：`uv1960` 和 `u'v'1976` 都是二维色度坐标，不是完整三维颜色空间。

## CIE 2006 LMS / XYZ 矩阵转换

### `LMS_to_XYZ(LMS, observer=2)` / `XYZ_to_LMS(XYZ, observer=2)`

用途：已经得到 LMS 或 XYZ 数值之后做 CIE 2006 矩阵转换。

```python
from color.colorimetry import LMS_to_XYZ, XYZ_to_LMS

XYZ = LMS_to_XYZ([20.0, 21.0, 5.0], observer=2)
LMS = XYZ_to_LMS(XYZ, observer=2)
```

注意：这不是光谱积分函数。光谱到 LMS 用 `emission_to_LMS(...)` 或 `reflectance_to_LMS(...)`。

## Lightness

### `Y_to_Lstar(Y, Y_n=100.0)` / `Lstar_to_Y(Lstar, Y_n=100.0)`

用途：CIE 1976 相对亮度 `Y` 与明度 `L*` 往返。

```python
from color.colorimetry import Lstar_to_Y, Y_to_Lstar

Lstar = Y_to_Lstar(18.0, Y_n=100.0)
Y = Lstar_to_Y(Lstar, Y_n=100.0)
```

注意：这里的 `Y` 是相对亮度标度，不是 `cd/m^2` 绝对亮度。

## 光度学

### `photopic_luminous_efficiency_function()` / `scotopic_luminous_efficiency_function()`

用途：获取明视觉或暗视觉光视效率函数。

```python
from color.colorimetry import (
    photopic_luminous_efficiency_function,
    scotopic_luminous_efficiency_function,
)

V = photopic_luminous_efficiency_function()
Vp = scotopic_luminous_efficiency_function()
```

### `luminous_flux(...)` / `luminous_efficiency(...)` / `luminous_efficacy(...)`

用途：使用指定 LEF 计算通用光度量。

```python
from color.colorimetry import (
    luminous_efficacy,
    luminous_efficiency,
    luminous_flux,
    photopic_luminous_efficiency_function,
)

lef = photopic_luminous_efficiency_function()
flux = luminous_flux(led, lef, K_m=683.0)
efficiency = luminous_efficiency(led, lef)
efficacy = luminous_efficacy(led, lef, K_m=683.0)
```

注意：通用入口适合自定义 LEF；普通工作流优先使用 photopic/scotopic 包装。

### `photopic_luminous_flux(...)` / `scotopic_luminous_flux(...)`

```python
from color.colorimetry import photopic_luminous_flux, scotopic_luminous_flux

phi_v = photopic_luminous_flux(led)
phi_vp = scotopic_luminous_flux(led)
```

### `photopic_luminous_efficiency(...)` / `scotopic_luminous_efficiency(...)`

```python
from color.colorimetry import photopic_luminous_efficiency, scotopic_luminous_efficiency

eta_v = photopic_luminous_efficiency(led)
eta_vp = scotopic_luminous_efficiency(led)
```

### `photopic_luminous_efficacy(...)` / `scotopic_luminous_efficacy(...)`

```python
from color.colorimetry import photopic_luminous_efficacy, scotopic_luminous_efficacy

K_v = photopic_luminous_efficacy(led)
K_vp = scotopic_luminous_efficacy(led)
```

注意：photopic/scotopic 包装会保持 LEF 和 `K_m` 常数匹配，能减少误用。

## 主波长、互补波长和纯度

### `ChromaticityAnalysis` / `analyze_chromaticity(xy, ...)`

用途：一次性计算主波长、互补波长、边界坐标、区域标签和两类纯度。

```python
from color.colorimetry import ChromaticityAnalysis, analyze_chromaticity

analysis: ChromaticityAnalysis = analyze_chromaticity([0.54369557, 0.32107944])

print(analysis.wavelength)
print(analysis.dominant_xy)
print(analysis.complementary_wavelength)
print(analysis.complementary_xy)
print(analysis.excitation_purity)
print(analysis.colorimetric_purity)
```

注意：`wavelength < 0` 表示非光谱紫色区域，绝对值是互补光谱波长。

### `dominant_wavelength(...)` / `complementary_wavelength(...)`

用途：分别返回主波长或互补波长及对应边界点。

```python
from color.colorimetry import complementary_wavelength, dominant_wavelength

wl, xy_wl = dominant_wavelength([0.54369557, 0.32107944])
cwl, xy_cwl = complementary_wavelength([0.54369557, 0.32107944])
```

注意：如果需要两边信息和纯度，优先用 `analyze_chromaticity(...)`。

### `excitation_purity(...)` / `colorimetric_purity(...)`

```python
from color.colorimetry import colorimetric_purity, excitation_purity

Pe = excitation_purity([0.54369557, 0.32107944])
Pc = colorimetric_purity([0.54369557, 0.32107944])
```

### `is_inside_chromaticity_locus(xy, ...)`

```python
from color.colorimetry import is_inside_chromaticity_locus

inside = is_inside_chromaticity_locus([0.3127, 0.3290])
batch = is_inside_chromaticity_locus([[0.3127, 0.3290], [0.9, 0.9]])
```

### `xy_from_dominant_wavelength_pe(...)` / `xy_from_dominant_wavelength_pc(...)`

用途：由主波长和纯度反向构造 xy。

用兴奋纯度：

```python
from color.colorimetry import analyze_chromaticity, xy_from_dominant_wavelength_pe

analysis = analyze_chromaticity([0.54369557, 0.32107944])
xy = xy_from_dominant_wavelength_pe(
    analysis.wavelength,
    analysis.excitation_purity,
)
```

用色度纯度：

```python
from color.colorimetry import analyze_chromaticity, xy_from_dominant_wavelength_pc

analysis = analyze_chromaticity([0.54369557, 0.32107944])
xy = xy_from_dominant_wavelength_pc(
    analysis.wavelength,
    analysis.colorimetric_purity,
)
```

注意：两者的纯度定义不同；不要把 `Pe` 和 `Pc` 混用。

## 色温、mired 和 Duv

### `CCT_to_mired(CCT)` / `mired_to_CCT(mired)`

```python
from color.colorimetry import CCT_to_mired, mired_to_CCT

mired = CCT_to_mired(6500)
CCT = mired_to_CCT(mired)
```

### `CCT_to_xy_CIE_D(CCT)` / `CCT_to_xy(CCT, method="cie_d")`

用途：CIE D-series daylight locus 的 CCT -> xy。

```python
from color.colorimetry import CCT_to_xy, CCT_to_xy_CIE_D

xy_d65 = CCT_to_xy_CIE_D(6504.389)
xy_d = CCT_to_xy(6504.389, method="cie_d")
```

注意：这是 CIE D 日光轨迹，不是普朗克黑体轨迹。

### `xy_to_CCT(xy, method="mccamy1992")`

用途：从 xy 快速估算 CCT。

```python
from color.colorimetry import xy_to_CCT

CCT = xy_to_CCT([0.3127, 0.3290], method="mccamy1992")
```

注意：McCamy 是近似 `xy -> CCT`，不返回 Duv。

### `uv_to_CCT(...)` / `CCT_to_uv(...)`

用途：按 method 分发 Robertson 或 Ohno，在 CIE 1960 UCS 中做 `[CCT, Duv]` 往返。

```python
from color.colorimetry import CCT_to_uv, uv_to_CCT

CCT_Duv_fast = uv_to_CCT([0.1978, 0.3122], method="robertson1968")
CCT_Duv_fine = uv_to_CCT([0.1978, 0.3122], method="ohno2013")

uv = CCT_to_uv([6500, 0.003], method="ohno2013")
```

### `xy_to_CCT_Duv(...)` / `CCT_Duv_to_xy(...)`

用途：xy 与 `[CCT, Duv]` 往返。

```python
from color.colorimetry import CCT_Duv_to_xy, xy_to_CCT_Duv

CCT_Duv = xy_to_CCT_Duv([0.3127, 0.3290], method="ohno2013")
xy = CCT_Duv_to_xy(CCT_Duv, method="ohno2013")
```

注意：`Duv=0` 表示位于普朗克轨迹上，不表示位于 CIE D daylight locus 上。

### `TemperatureAnalysis` / `analyze_temperature(xy, method=...)`

用途：返回带语义字段的完整 CCT+Duv 分析对象。

```python
from color.colorimetry import TemperatureAnalysis, analyze_temperature

analysis: TemperatureAnalysis = analyze_temperature(
    [0.3127, 0.3290],
    method="ohno2013",
)

print(analysis.CCT)
print(analysis.Duv)
print(analysis.xy)
print(analysis.uv)
print(analysis.method)
print(analysis.locus)
```

注意：需要字段清楚时用 `analyze_temperature(...)`；需要轻量数组时用 `xy_to_CCT_Duv(...)`。

### 子包算法入口

如果需要精确测试某个算法实现，可从子包导入：

```python
from color.colorimetry.temperature import (
    xy_to_CCT_McCamy1992,
    uv_to_CCT_Robertson1968,
    uv_to_CCT_Ohno2013,
    planckian_table_Ohno2013,
)
```

这些不是 `color.colorimetry` 顶层推荐入口。
