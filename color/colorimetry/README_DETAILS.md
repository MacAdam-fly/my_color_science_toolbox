# colorimetry - 色度学计算模块详细说明

`color.colorimetry` 是项目中负责颜色科学计算的核心层。它位于
`datasets`、`generators` 和 `spectra` 之上，主要完成：

- 光谱数据到 XYZ / LMS 的数值积分。
- XYZ、xy、xyY 等基础色度坐标转换。
- 明视觉 / 暗视觉光视效率和光度量计算。
- CIE 1976 明度 `L*` 与相对亮度 `Y` 的转换。
- 主波长、互补波长、兴奋纯度和色度纯度计算。
- 相关色温 CCT、mired、Duv、CIE D 日光轨迹和普朗克轨迹计算。
- CIE 2006 LMS 与 XYZ 的直接矩阵转换。

这个模块不直接负责静态文件读取，也不直接负责光谱对象封装：

```text
color.datasets     静态标准数据读取
color.generators   公式生成数据，例如黑体辐射、D 系列日光 SPD
color.spectra      光谱对象封装、插值、外推、reshape
color.colorimetry  色度学计算
```

## 快速上手

### 自发光光谱到 XYZ / LMS

```python
from color.generators.blackbody import blackbody_spd
from color.spectra import from_columns
from color.colorimetry import emission_to_XYZ, emission_to_LMS

raw = blackbody_spd(temperature=6500)
sd = from_columns(raw, y="radiance", name="blackbody 6500 K")

XYZ = emission_to_XYZ(sd)
LMS = emission_to_LMS(sd)
```

`emission_to_*` 用于自发光光谱，例如黑体、LED、显示器光谱、发射光源 SPD。

### 反射率光谱到 XYZ / LMS

```python
from color.datasets import get_color_card
from color.spectra import from_columns
from color.colorimetry import reflectance_to_XYZ, reflectance_to_LMS

raw = get_color_card("pmc")
patch = from_columns(raw, y="Blue Sky", name="PMC Blue Sky")

XYZ = reflectance_to_XYZ(patch, illuminant="D65")
LMS = reflectance_to_LMS(patch, illuminant="D65")
```

`reflectance_to_*` 用于物体表面反射率，需要指定照明体。默认照明体为
`D65`。

### XYZ 与 xyY / xy

```python
from color.colorimetry import XYZ_to_xy, XYZ_to_xyY, xyY_to_XYZ

xy = XYZ_to_xy(XYZ)
xyY = XYZ_to_xyY(XYZ)
XYZ_again = xyY_to_XYZ(xyY)
```

`XYZ_to_xy(...)` 只返回二维色坐标，丢失亮度信息，因此不是可逆转换。
若需要可逆表达，请使用 `XYZ_to_xyY(...)`。

## 模块结构

```text
color/colorimetry/
├── __init__.py              # 统一导出公共 API
├── integration.py           # 光谱响应积分核心
├── tristimulus.py           # XYZ 积分入口
├── cone_responses.py        # LMS 积分入口
├── chromaticity.py          # XYZ / xy / xyY 转换
├── photometry.py            # 光视效率和光度量
├── lightness.py             # CIE 1976 Y <-> L*
├── transformations.py       # CIE 2006 LMS <-> XYZ 矩阵转换
├── dominant.py              # 主波长、互补波长和纯度
└── temperature/             # CCT、Duv、日光轨迹和普朗克轨迹
```

其中 `temperature` 已经是子包：

```text
temperature/
├── conversions.py           # CCT/mired、xy/XYZ/uv1960 转换
├── daylight.py              # CIE D-series daylight xy
├── mccamy1992.py            # McCamy 1992 CCT 近似
├── robertson1968.py         # Robertson 1968 CCT + Duv
├── ohno2013.py              # Ohno 2013 CCT + Duv
└── dispatch.py              # method 分发入口
```

## 光谱积分

### 公共入口

| 函数 | 用途 | 默认条件 |
| --- | --- | --- |
| `emission_to_XYZ(emission, *, cmfs="cie1931_xyz_1nm")` | 自发光光谱积分到 XYZ | CIE 1931 2° XYZ CMFs |
| `reflectance_to_XYZ(reflectance, *, illuminant="D65", cmfs="cie1931_xyz_1nm")` | 反射率在照明体下积分到 XYZ | D65 + CIE 1931 2° |
| `emission_to_LMS(emission, *, fundamentals="cie2006_lms2_linE_1nm", fill_nan=0.0)` | 自发光光谱积分到 LMS | CIE 2006 2° LMS |
| `reflectance_to_LMS(reflectance, *, illuminant="D65", fundamentals="cie2006_lms2_linE_1nm", fill_nan=0.0)` | 反射率在照明体下积分到 LMS | D65 + CIE 2006 2° LMS |

这里的 `emission` 和 `reflectance` 应该是 `color.spectra` 中的
`SpectralDistribution` 或 `MultiSpectralDistribution`，而不是原始
`dict[str, np.ndarray]`。

### 自发光与反射率的区别

自发光模式：

```text
XYZ = k * ∫ SPD(λ) * CMF(λ) dλ
```

反射率模式：

```text
XYZ = k * ∫ R(λ) * Illuminant(λ) * CMF(λ) dλ
```

反射率模式默认会根据照明体和响应函数做归一化，使理想白反射体得到
接近 `Y=100` 的结果。

### NaN 策略

部分 CVRL LMS 数据在长波端的 S 通道存在空白值。`datasets` 会保留这些
空白为 `NaN`，而 `colorimetry` 的 LMS 高层入口默认使用 `fill_nan=0.0`，
把这些位置当作零响应用于积分。

如果手动加载响应函数，也可以显式写出：

```python
from color.spectra import from_dataset

fundamentals = from_dataset(
    "standard_observers.cone_fundamentals",
    "cie2006_lms2_linE_1nm",
    fill_nan=0.0,
)
```

## 色度坐标转换

### API

| 函数 | 说明 |
| --- | --- |
| `XYZ_to_xyY(XYZ)` | XYZ 转 xyY，保留亮度 Y |
| `xyY_to_XYZ(xyY)` | xyY 转 XYZ |
| `XYZ_to_xy(XYZ)` | XYZ 转二维 xy 色坐标 |

这些函数支持单个三元组，也支持最后一维为 3 的批量数组，例如
`(n, 3)` 或 `(h, w, 3)`。

### 使用建议

- 只做色坐标分析时使用 `XYZ_to_xy(...)`。
- 需要后续还原 XYZ 时使用 `XYZ_to_xyY(...)`。
- 不要把 `xy` 当作完整颜色值；它没有亮度信息。

## LMS 与 XYZ 直接矩阵转换

### API

| 函数 | 说明 |
| --- | --- |
| `LMS_to_XYZ(LMS, observer=2)` | CIE 2006 LMS 转 XYZ |
| `XYZ_to_LMS(XYZ, observer=2)` | XYZ 转 CIE 2006 LMS |

`observer` 支持 `2` 和 `10`，分别对应 CIE 2006 2° 和 10° 观察者。

这组函数不是光谱积分，而是在已经得到 LMS / XYZ 数值之后做矩阵变换：

```python
from color.colorimetry import LMS_to_XYZ, XYZ_to_LMS

XYZ = LMS_to_XYZ(LMS, observer=2)
LMS = XYZ_to_LMS(XYZ, observer=2)
```

## 光度学与光视效率

### 数据访问

| 函数 | 说明 |
| --- | --- |
| `photopic_luminous_efficiency_function()` | 返回明视觉 V(λ) 光视效率函数 |
| `scotopic_luminous_efficiency_function()` | 返回暗视觉 V'(λ) 光视效率函数 |

默认使用：

| 模式 | 默认函数 | 最大光效 |
| --- | --- | --- |
| 明视觉 photopic | `vl1924_1nm` | `683 lm/W` |
| 暗视觉 scotopic | `scotopic_v_1nm` | `1700 lm/W` |

### 推荐安全入口

| 函数 | 说明 |
| --- | --- |
| `photopic_luminous_flux(sd)` | 明视觉光通量 |
| `scotopic_luminous_flux(sd)` | 暗视觉光通量 |
| `photopic_luminous_efficiency(sd)` | 明视觉归一化光视效率 |
| `scotopic_luminous_efficiency(sd)` | 暗视觉归一化光视效率 |
| `photopic_luminous_efficacy(sd)` | 明视觉光效，单位 lm/W |
| `scotopic_luminous_efficacy(sd)` | 暗视觉光效，单位 lm/W |

推荐优先使用 `photopic_*` 和 `scotopic_*`，因为它们会自动保持
光视效率函数和 `K_m` 常数匹配。

### 通用入口

| 函数 | 说明 |
| --- | --- |
| `luminous_flux(sd, lef, K_m=...)` | 使用指定 LEF 和常数计算光通量 |
| `luminous_efficiency(sd, lef)` | 计算归一化光视效率 |
| `luminous_efficacy(sd, lef, K_m=...)` | 计算 lm/W 光效 |

通用入口适合研究自定义 LEF 或非标准条件；普通使用更建议走安全包装函数。

## 明度与相对亮度

### API

| 函数 | 说明 |
| --- | --- |
| `Y_to_Lstar(Y, Y_n=100.0)` | 相对亮度 Y 转 CIE 1976 明度 L* |
| `Lstar_to_Y(Lstar, Y_n=100.0)` | CIE 1976 明度 L* 转相对亮度 Y |

这里的 `Y` 是相对亮度，不是绝对亮度单位 `cd/m^2`。默认白点亮度
`Y_n=100.0`。

```python
from color.colorimetry import Y_to_Lstar, Lstar_to_Y

Lstar = Y_to_Lstar(18.0)
Y = Lstar_to_Y(Lstar)
```

## 主波长、互补波长和纯度

### API

| 函数 | 说明 |
| --- | --- |
| `dominant_wavelength(xy)` | 返回主波长和对应边界交点 |
| `complementary_wavelength(xy)` | 返回互补波长和对应边界交点 |
| `excitation_purity(xy)` | 计算兴奋纯度 |
| `colorimetric_purity(xy)` | 计算色度纯度 |
| `analyze_chromaticity(xy)` | 返回完整色度分析结果 |
| `is_inside_chromaticity_locus(xy)` | 判断 xy 是否在闭合色度边界内 |
| `xy_from_dominant_wavelength_pe(wavelength, excitation_purity)` | 由主波长和兴奋纯度反推 xy |
| `xy_from_dominant_wavelength_pc(wavelength, colorimetric_purity)` | 由主波长和色度纯度反推 xy |

默认白点为 D65：

```python
xy_n = (0.3127, 0.3290)
```

默认光谱轨迹为：

```text
standard_observers.chromaticity_coordinates / cie1931_chro_1nm
```

### 完整分析结果

```python
from color.colorimetry import analyze_chromaticity

result = analyze_chromaticity([0.54369557, 0.32107944])

print(result.wavelength)
print(result.xy)
print(result.complementary_wavelength)
print(result.complementary_xy)
print(result.excitation_purity)
print(result.colorimetric_purity)
print(result.dominant_region)
print(result.complementary_region)
```

`ChromaticityAnalysis` 中的区域字段通常为：

| 值 | 含义 |
| --- | --- |
| `"spectral"` | 交点在光谱轨迹上 |
| `"purple"` | 交点在紫线边界上 |
| `"undefined"` | 白点或无法定义主方向 |

### 正负波长约定

反向构造函数沿用 signed wavelength 约定：

- 正波长表示主方向落在光谱轨迹上。
- 负波长表示非光谱紫色区域，数值绝对值对应互补光谱波长。

这可以让一个标量波长同时表达“光谱色主波长”和“非光谱色互补主波长”。

### 兴奋纯度与色度纯度

兴奋纯度主要是几何比例：

```text
Pe = distance(xy_n, xy) / distance(xy_n, boundary_xy)
```

色度纯度在兴奋纯度基础上还考虑边界点和目标点的 `y` 坐标比例：

```text
Pc = Pe * boundary_y / xy_y
```

两者都依赖选择的白点和光谱轨迹。

## 相关色温、Duv 和两条轨迹

色温模块最容易误用的地方是把两条轨迹混在一起：

```text
CIE D-series daylight locus  = 标准日光色度轨迹
Planckian locus              = 理想黑体辐射色度轨迹
```

### CIE D 系列日光轨迹

| 函数 | 说明 |
| --- | --- |
| `CCT_to_xy_CIE_D(CCT)` | CIE D 系列 daylight locus 的 CCT -> xy |
| `CCT_to_xy(CCT, method="cie_d")` | 上述函数的分发入口 |

`CCT_to_xy_CIE_D(...)` 只返回 D 系列日光的色坐标，不生成完整 SPD。
完整 D 系列日光光谱由 `color.generators.illuminants.daylight_spd(...)`
负责。

例如 D65 接近：

```text
CCT ≈ 6504 K
xy  ≈ (0.3127, 0.3290)
```

这个点属于 CIE D 日光轨迹，不等同于 6504 K 黑体点。

### McCamy 1992

| 函数 | 说明 |
| --- | --- |
| `xy_to_CCT_McCamy1992(xy)` | 从 xy 快速估算 CCT |
| `xy_to_CCT(xy, method="mccamy1992")` | 上述函数的分发入口 |

McCamy 是经验近似，只做 `xy -> CCT`，不返回 `Duv`，也不提供可靠的
`CCT -> xy` 反向。原因是它把二维 `xy` 压缩成一个中间变量 `n`，会丢失
一维信息。

### CIE 1960 UCS uv

| 函数 | 说明 |
| --- | --- |
| `xy_to_uv1960(xy)` | xy 转 CIE 1960 uv |
| `XYZ_to_uv1960(XYZ)` | XYZ 转 CIE 1960 uv |
| `uv1960_to_xy(uv)` | CIE 1960 uv 转 xy |

Robertson 和 Ohno 都是在 CIE 1960 UCS `uv` 空间中相对普朗克轨迹计算
`CCT + Duv`。

### Robertson 1968

| 函数 | 说明 |
| --- | --- |
| `uv_to_CCT_Robertson1968(uv)` | uv -> `[CCT, Duv]` |
| `CCT_to_uv_Robertson1968([CCT, Duv])` | `[CCT, Duv]` -> uv |

Robertson 1968 是当前默认的 CCT+Duv 快速路径：

```python
from color.colorimetry import uv_to_CCT, CCT_to_uv

CCT_Duv = uv_to_CCT(uv, method="robertson1968")
uv = CCT_to_uv(CCT_Duv, method="robertson1968")
```

### Ohno 2013

| 函数 | 说明 |
| --- | --- |
| `planckian_table_Ohno2013(...)` | 生成 Ohno 使用的普朗克 uv 表 |
| `uv_to_CCT_Ohno2013(uv)` | uv -> `[CCT, Duv]` |
| `CCT_to_uv_Ohno2013([CCT, Duv])` | `[CCT, Duv]` -> uv |

Ohno 2013 使用更密的普朗克轨迹表和更精细的几何 / 抛物线修正，通常比
Robertson 更适合严肃色温分析。实现中不依赖 `colour-science`，而是使用
本工程自己的：

```text
blackbody_spd -> emission_to_XYZ -> XYZ_to_uv1960
```

默认 Ohno 表会缓存，避免重复生成。

### 便捷入口

| 函数 | 说明 |
| --- | --- |
| `uv_to_CCT(uv, method="robertson1968")` | uv -> `[CCT, Duv]` |
| `CCT_to_uv([CCT, Duv], method="robertson1968")` | `[CCT, Duv]` -> uv |
| `xy_to_CCT_Duv(xy, method="robertson1968")` | xy -> `[CCT, Duv]` |
| `CCT_Duv_to_xy([CCT, Duv], method="robertson1968")` | `[CCT, Duv]` -> xy |
| `analyze_temperature(xy, method="robertson1968")` | 返回完整 `TemperatureAnalysis` 结果对象 |

`method` 当前支持：

```text
robertson1968
ohno2013
```

使用建议：

```python
from color.colorimetry import xy_to_CCT_Duv, CCT_Duv_to_xy

# 常规快速分析
CCT_Duv = xy_to_CCT_Duv(xy, method="robertson1968")

# 更精细的分析
CCT_Duv = xy_to_CCT_Duv(xy, method="ohno2013")

# 从 CCT+Duv 反推 xy
xy = CCT_Duv_to_xy([6500, 0.003], method="ohno2013")
```

### 完整色温分析结果

`xy_to_CCT_Duv(...)` 返回的是轻量数组，适合数值计算。若希望字段含义更清楚，
可以使用 `analyze_temperature(...)`：

```python
from color.colorimetry import analyze_temperature

result = analyze_temperature(xy, method="ohno2013")

print(result.CCT)
print(result.Duv)
print(result.xy)
print(result.uv)
print(result.method)
print(result.locus)
```

`TemperatureAnalysis` 字段如下：

| 字段 | 说明 |
| --- | --- |
| `CCT` | 相关色温，单位 K |
| `Duv` | 相对普朗克轨迹的有符号距离，位于 CIE 1960 UCS |
| `xy` | 输入点对应的 CIE xy 坐标，经过同一方法闭环重建 |
| `uv` | 输入点对应的 CIE 1960 UCS uv 坐标 |
| `method` | 使用的方法，如 `"robertson1968"` 或 `"ohno2013"` |
| `locus` | 当前为 `"planckian"`，表示分析相对普朗克轨迹 |

这个对象与 `ChromaticityAnalysis` 的设计意图一致：底层函数保持数组返回，
高层分析入口提供更清晰的语义字段。

## 公共 API 总览

### 光谱到色度响应

| API | 说明 |
| --- | --- |
| `emission_to_XYZ` | 自发光光谱到 XYZ |
| `reflectance_to_XYZ` | 反射率光谱到 XYZ |
| `emission_to_LMS` | 自发光光谱到 LMS |
| `reflectance_to_LMS` | 反射率光谱到 LMS |

### 基础色度坐标

| API | 说明 |
| --- | --- |
| `XYZ_to_xyY` | XYZ 到 xyY |
| `xyY_to_XYZ` | xyY 到 XYZ |
| `XYZ_to_xy` | XYZ 到 xy |

### 光度学

| API | 说明 |
| --- | --- |
| `photopic_luminous_efficiency_function` | 明视觉 V(λ) |
| `scotopic_luminous_efficiency_function` | 暗视觉 V'(λ) |
| `photopic_luminous_flux` / `scotopic_luminous_flux` | 安全光通量入口 |
| `photopic_luminous_efficiency` / `scotopic_luminous_efficiency` | 安全归一化光视效率入口 |
| `photopic_luminous_efficacy` / `scotopic_luminous_efficacy` | 安全 lm/W 光效入口 |
| `luminous_flux` / `luminous_efficiency` / `luminous_efficacy` | 自定义 LEF 的通用入口 |

### 明度

| API | 说明 |
| --- | --- |
| `Y_to_Lstar` | Y 到 L* |
| `Lstar_to_Y` | L* 到 Y |

### 色温

| API | 说明 |
| --- | --- |
| `CCT_to_mired` / `mired_to_CCT` | K 与 mired 转换 |
| `TemperatureAnalysis` / `analyze_temperature` | 完整 CCT+Duv 分析结果 |
| `CCT_to_xy_CIE_D` / `CCT_to_xy` | CIE D 系列日光轨迹 |
| `xy_to_CCT_McCamy1992` / `xy_to_CCT` | McCamy CCT 近似 |
| `xy_to_uv1960` / `XYZ_to_uv1960` / `uv1960_to_xy` | CIE 1960 UCS 转换 |
| `uv_to_CCT_Robertson1968` / `CCT_to_uv_Robertson1968` | Robertson CCT+Duv |
| `uv_to_CCT_Ohno2013` / `CCT_to_uv_Ohno2013` | Ohno CCT+Duv |
| `xy_to_CCT_Duv` / `CCT_Duv_to_xy` | CCT+Duv 便捷入口 |

### 主波长与纯度

| API | 说明 |
| --- | --- |
| `ChromaticityAnalysis` | 完整色度分析结果对象 |
| `analyze_chromaticity` | 完整分析入口 |
| `is_inside_chromaticity_locus` | 判断 xy 是否在色度边界内 |
| `dominant_wavelength` | 主波长 |
| `complementary_wavelength` | 互补波长 |
| `excitation_purity` | 兴奋纯度 |
| `colorimetric_purity` | 色度纯度 |
| `xy_from_dominant_wavelength_pe` | 主波长 + 兴奋纯度反推 xy |
| `xy_from_dominant_wavelength_pc` | 主波长 + 色度纯度反推 xy |

## 示例脚本

`examples/colorimetry/` 中提供了当前模块的端到端示例：

| 示例 | 内容 |
| --- | --- |
| `example_end_to_end_smoke.py` | datasets / generators / spectra / colorimetry 综合烟测 |
| `example_emission_generators_xyz_lms.py` | 生成光谱到 XYZ/LMS |
| `example_reflectance_color_card_xyz_lms.py` | 色卡反射率到 XYZ/LMS |
| `example_illuminant_a_xyz_comparison.py` | 静态 A 光源与公式 A 光源比较 |
| `example_lms_xyz_transformations.py` | LMS 与 XYZ 矩阵转换 |
| `example_photometry.py` | 明视觉/暗视觉光视效率和光效 |
| `example_lightness.py` | Y 与 L* 往返 |
| `example_dominant_wavelength.py` | 主波长、互补波长和纯度可视化 |
| `example_temperature.py` | CCT、Duv、CIE D 轨迹和普朗克轨迹可视化 |

运行示例：

```powershell
.\.venv\Scripts\python.exe examples\colorimetry\example_temperature.py
```

图像输出位于：

```text
examples/colorimetry/output/
```

## 当前边界和后续方向

当前 `colorimetry` 已经覆盖基础色度学计算主干。`：

```text
color.colorimetry = CIE 色度学基础计算
color.spaces      = 颜色空间、RGB、Lab、Luv、色适应
```

后续可以考虑：

- 为色温添加 `TemperatureAnalysis` 结果对象。
- 为 Ohno 表缓存添加显式清理入口。
- 在 `color.spaces` 中实现 whitepoint、chromatic adaptation、sRGB、Lab、Luv。
- 将 example 中的可视化结果进一步整理为教程文档。

## 测试

运行 colorimetry 测试：

```powershell
.\.venv\Scripts\python.exe -m pytest color/colorimetry/tests -q --basetemp .pytest_tmp
```

运行全量测试：

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .pytest_tmp
```

当前测试会运行 example 脚本作为端到端检查，因此示例也是模块行为的一部分。
