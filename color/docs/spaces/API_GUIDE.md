# color.spaces API 使用指南

本文档按 `color.spaces.__all__` 覆盖顶层 API。这里写最小使用案例；
空间架构、XYZ 中枢、D65-referred 语义、色适应边界和设计说明见
[`README_DETAILS.md`](README_DETAILS.md)。

`color.spaces` 的核心约定：

- 公开 `XYZ` 使用 `Y=100` 标度。
- `XYZ` 是唯一全局转换中枢。
- `convert_color(...)` 做统一路由。
- `Oklab`、`IPT`、`Jzazbz` 要求输入为 D65-referred XYZ。
- RGB 标准空间和普通空间分别由 RGB 子模块注册表与 generic registry 管理。

## 顶层 API 总览

### 转换图和路由

| API | 功能 |
| --- | --- |
| `get_colourspace_node` | 解析普通颜色空间节点 |
| `list_colourspace_nodes` | 列出普通颜色空间节点 |
| `SpaceSpec` | 带参数的空间端点 |
| `convert_color` | 通过 XYZ 中枢转换颜色 |
| `ConversionPath` | 转换路径描述对象 |
| `describe_conversion_path` | 描述转换路径，不执行数值转换 |

### RGB

| API | 功能 |
| --- | --- |
| `RGBColorSpace` | RGB 空间对象 |
| `get_RGB_colourspace`, `list_RGB_colourspaces`, `register_RGB_colourspace` | RGB 注册表入口 |
| `RGB_colourspace_from_primaries_xy`, `RGB_colourspace_from_primaries_XYZ` | 自定义三基色 RGB 空间 |
| `RGB_to_XYZ`, `XYZ_to_RGB`, `RGB_to_RGB`, `sRGB_to_XYZ`, `XYZ_to_sRGB` | RGB / XYZ 转换 |

### Basic Spaces

| API | 功能 |
| --- | --- |
| `XYZ_to_xyY`, `xyY_to_XYZ`, `XYZ_to_xy`, `xyY_to_xy` | XYZ / xyY / xy |
| `xy_to_uv1960`, `XYZ_to_uv1960`, `uv1960_to_xy` | CIE 1960 UCS uv |
| `xy_to_upvp1976`, `XYZ_to_upvp1976`, `upvp1976_to_xy` | CIE 1976 UCS u'v' |
| `XYZ_to_Lab`, `Lab_to_XYZ`, `Lab_to_LCHab`, `LCHab_to_Lab` | CIE Lab / LCHab |
| `XYZ_to_Luv`, `Luv_to_XYZ`, `Luv_to_LCHuv`, `LCHuv_to_Luv`, `Luv_to_Lshuv`, `Lshuv_to_Luv` | CIE Luv 派生空间 |
| `XYZ_to_UVW`, `UVW_to_XYZ` | CIE 1964 UVW |
| `XYZ_to_Oklab`, `Oklab_to_XYZ`, `Oklab_to_Oklch`, `Oklch_to_Oklab` | Oklab / Oklch |
| `XYZ_to_IPT`, `IPT_to_XYZ`, `IPT_hue_angle` | IPT |
| `XYZ_to_Jzazbz`, `Jzazbz_to_XYZ`, `Jzazbz_to_JzCzhz`, `JzCzhz_to_Jzazbz` | Jzazbz / JzCzhz |

### Appearance Uniform Spaces

| API | 功能 |
| --- | --- |
| `JMh_CIECAM02_to_CAM02UCS`, `CAM02UCS_to_JMh_CIECAM02` | CIECAM02 JMh / CAM02-UCS |
| `JMh_CIECAM02_to_CAM02LCD`, `CAM02LCD_to_JMh_CIECAM02` | CIECAM02 JMh / CAM02-LCD |
| `JMh_CIECAM02_to_CAM02SCD`, `CAM02SCD_to_JMh_CIECAM02` | CIECAM02 JMh / CAM02-SCD |
| `XYZ_to_CAM02UCS`, `CAM02UCS_to_XYZ`, `XYZ_to_CAM02LCD`, `CAM02LCD_to_XYZ`, `XYZ_to_CAM02SCD`, `CAM02SCD_to_XYZ` | XYZ / CAM02 均匀空间 |
| `JMh_CIECAM16_to_CAM16UCS`, `CAM16UCS_to_JMh_CIECAM16` | CIECAM16 JMh / CAM16-UCS |
| `JMh_CIECAM16_to_CAM16LCD`, `CAM16LCD_to_JMh_CIECAM16` | CIECAM16 JMh / CAM16-LCD |
| `JMh_CIECAM16_to_CAM16SCD`, `CAM16SCD_to_JMh_CIECAM16` | CIECAM16 JMh / CAM16-SCD |
| `XYZ_to_CAM16UCS`, `CAM16UCS_to_XYZ`, `XYZ_to_CAM16LCD`, `CAM16LCD_to_XYZ`, `XYZ_to_CAM16SCD`, `CAM16SCD_to_XYZ` | XYZ / CAM16 均匀空间 |

## 转换图、注册表和 `SpaceSpec`

### `get_colourspace_node(...)` / `list_colourspace_nodes()`

用途：解析和列出普通颜色空间节点。

```python
from color.spaces import get_colourspace_node, list_colourspace_nodes

print(list_colourspace_nodes())
node = get_colourspace_node("Lab")
print(node.name, node.parent, node.family)
```

注意：底层 `ColorSpaceNode` 和 `SPACE_REGISTRY` 保留在 `color.spaces.node` 与
`color.spaces.registry`，不作为 `color.spaces` 顶层 API。

### `SpaceSpec(name, **parameters)`

用途：为 source 或 target 空间携带白点、观察条件等端点参数。

Lab 白点：

```python
from color.constants import D50_XYZ
from color.spaces import SpaceSpec, convert_color

Lab_D50 = convert_color(
    [19.01, 20.0, 21.78],
    "XYZ",
    SpaceSpec("Lab", whitepoint_XYZ=D50_XYZ),
)
```

CAM16 观察条件：

```python
from color.constants import D65_XYZ
from color.spaces import SpaceSpec, convert_color

cam16 = convert_color(
    [19.01, 20.0, 21.78],
    "XYZ",
    SpaceSpec("CAM16-UCS", XYZ_w=D65_XYZ, L_A=318.31, Y_b=20.0),
)
```

注意：`SpaceSpec` 参数只用于该端点的转换，不代表隐式色适应。

### `convert_color(value, source, target, **kwargs)`

用途：通过注册图和 XYZ 中枢转换颜色。

基础空间：

```python
from color.spaces import convert_color

Lab = convert_color([19.01, 20.0, 21.78], "XYZ", "Lab")
XYZ = convert_color(Lab, "Lab", "XYZ")
```

RGB 到普通空间：

```python
Lab = convert_color([0.4, 0.5, 0.6], "sRGB", "Lab")
rgb = convert_color(Lab, "Lab", "sRGB")
```

派生空间链路：

```python
Oklch = convert_color([0.4, 0.5, 0.6], "sRGB", "Oklch")
JzCzhz = convert_color(Oklch, "Oklch", "JzCzhz")
```

不同参数空间：

```python
from color.constants import D50_XYZ, D65_XYZ
from color.spaces import SpaceSpec, convert_color

Luv_D65 = convert_color(
    [50.0, 5.0, 10.0],
    SpaceSpec("Lab", whitepoint_XYZ=D50_XYZ),
    SpaceSpec("Luv", whitepoint_XYZ=D65_XYZ),
)
```

注意：这只是参数化空间转换；如果需要白点适应，请显式调用 `color.adaptation`。

### `ConversionPath`

用途：保存 `describe_conversion_path(...)` 的结构化结果。

```python
from color.spaces import ConversionPath, describe_conversion_path

path: ConversionPath = describe_conversion_path("JzCzhz", "Lab")
for edge in path.edges:
    print(edge.source, "->", edge.target, edge.operation)
```

### `describe_conversion_path(source, target)`

用途：解释 `convert_color(...)` 会走哪条路径，不执行数值转换。

```python
from color.spaces import describe_conversion_path

path = describe_conversion_path("sRGB", "CAM16-UCS")
print(path.nodes)
print(path.edges)
```

绘图函数属于 `color.spaces.plotting`：

```python
from color.spaces import describe_conversion_path
from color.spaces.plotting import plot_conversion_graph, plot_conversion_path

path = describe_conversion_path("sRGB", "CAM16-UCS")
fig_path, ax_path = plot_conversion_path(path)
fig_graph, ax_graph = plot_conversion_graph()
```

默认 D65 `Y=100` 白点保留在 `color.spaces.basic.DEFAULT_WHITEPOINT_XYZ`。

## RGB 空间

### `RGBColorSpace`

用途：保存 RGB primaries、whitepoint、transfer 和转换矩阵。

```python
from color.spaces import get_RGB_colourspace, RGBColorSpace

srgb: RGBColorSpace = get_RGB_colourspace("sRGB")
print(srgb.name)
print(srgb.white_xy)
print(srgb.matrix_RGB_to_XYZ)
```

### `get_RGB_colourspace(...)` / `list_RGB_colourspaces()`

```python
from color.spaces import get_RGB_colourspace, list_RGB_colourspaces

print(list_RGB_colourspaces())
p3 = get_RGB_colourspace("Display P3")
p3_alias = get_RGB_colourspace("P3-D65")
```

### `RGB_colourspace_from_primaries_xy(...)`

用途：由三基色 `xy` 和白点创建自定义 RGB 空间，白点传入XYZ，就按照XYZ配平，传入xy，默认按照Y=100配平。

```python
from color.spaces import RGB_colourspace_from_primaries_xy

custom = RGB_colourspace_from_primaries_xy(
    "Custom Display",
    primaries_xy=[
        [0.690, 0.310],
        [0.210, 0.720],
        [0.145, 0.055],
    ],
    whitepoint_xy=[0.3127, 0.3290],
    transfer=("gamma", (2.2, 2.3, 2.1)),
    aliases=("CustomDisplay",),
)
```

### `RGB_colourspace_from_primaries_XYZ(...)`

用途：由实测三基色 XYZ 创建 RGB 空间，不重新白点配平。

```python
from color.spaces import RGB_colourspace_from_primaries_XYZ

measured = RGB_colourspace_from_primaries_XYZ(
    "Measured Display",
    primaries_XYZ=[
        [41.0, 22.0, 2.0],
        [35.0, 70.0, 9.0],
        [18.0, 8.0, 97.0],
    ],
    transfer="linear",
)
```

注意：白点为三基色 XYZ 之和；如果 `Y` 不是约 `100`，会警告但保留原尺度。

### `register_RGB_colourspace(space, overwrite=False)`

用途：把自定义 RGB 空间注册进字符串路由。

```python
from color.spaces import register_RGB_colourspace, convert_color

register_RGB_colourspace(custom)
Lab = convert_color([0.4, 0.5, 0.6], "Custom Display", "Lab")
```

注意：创建自定义空间不会自动注册；标准空间不能被覆盖。

### `RGB_to_XYZ(...)` / `XYZ_to_RGB(...)`

用途：RGB 与 XYZ 转换。

encoded RGB：

```python
from color.spaces import RGB_to_XYZ, XYZ_to_RGB

XYZ = RGB_to_XYZ([0.4, 0.5, 0.6], "sRGB")
rgb = XYZ_to_RGB(XYZ, "sRGB")
```

linear RGB：

```python
XYZ = RGB_to_XYZ([0.4, 0.5, 0.6], "sRGB", apply_decoding=False)
linear = XYZ_to_RGB(XYZ, "sRGB", apply_encoding=False)
```

对象入口：

```python
srgb = get_RGB_colourspace("sRGB")
XYZ = RGB_to_XYZ([0.4, 0.5, 0.6], srgb)
```

注意：函数不自动 clip 到 `[0, 1]`。

### `RGB_to_RGB(...)`

用途：RGB 标准之间转换。

默认不做色适应：

```python
from color.spaces import RGB_to_RGB

p3 = RGB_to_RGB([0.4, 0.5, 0.6], "sRGB", "Display P3")
```

显式色适应：

```python
srgb = RGB_to_RGB(
    [1.0, 1.0, 1.0],
    "DCI-P3",
    "sRGB",
    chromatic_adaptation="Bradford",
)
```

注意：`convert_color(...)` 不暴露色适应参数；需要 RGB 间适应时用 `RGB_to_RGB(...)`。

### `sRGB_to_XYZ(...)` / `XYZ_to_sRGB(...)`

用途：高频 sRGB 便捷入口。

```python
from color.spaces import XYZ_to_sRGB, sRGB_to_XYZ

XYZ = sRGB_to_XYZ([0.4, 0.5, 0.6])
rgb = XYZ_to_sRGB(XYZ)
```

## xyY、xy、uv1960 和 u'v'1976

### `XYZ_to_xyY(...)` / `xyY_to_XYZ(...)`

```python
from color.spaces import XYZ_to_xyY, xyY_to_XYZ

xyY = XYZ_to_xyY([19.01, 20.0, 21.78])
XYZ = xyY_to_XYZ(xyY)
```

### `XYZ_to_xy(...)` / `xyY_to_xy(...)`

```python
from color.spaces import XYZ_to_xy, xyY_to_xy

xy = XYZ_to_xy([19.01, 20.0, 21.78])
xy2 = xyY_to_xy([0.3127, 0.3290, 20.0])
```

注意：`xy` 是二维投影，不注册为空间节点。

### `xy_to_uv1960(...)` / `XYZ_to_uv1960(...)` / `uv1960_to_xy(...)`

```python
from color.spaces import XYZ_to_uv1960, uv1960_to_xy, xy_to_uv1960

uv = xy_to_uv1960([0.3127, 0.3290])
uv_from_XYZ = XYZ_to_uv1960([95.047, 100.0, 108.883])
xy = uv1960_to_xy(uv)
```

### `xy_to_upvp1976(...)` / `XYZ_to_upvp1976(...)` / `upvp1976_to_xy(...)`

```python
from color.spaces import XYZ_to_upvp1976, upvp1976_to_xy, xy_to_upvp1976

upvp = xy_to_upvp1976([0.3127, 0.3290])
upvp_from_XYZ = XYZ_to_upvp1976([95.047, 100.0, 108.883])
xy = upvp1976_to_xy(upvp)
```

## Lab、Luv、UVW

### `XYZ_to_Lab(...)` / `Lab_to_XYZ(...)`

```python
from color.constants import D50_XYZ
from color.spaces import XYZ_to_Lab, Lab_to_XYZ

Lab = XYZ_to_Lab([19.01, 20.0, 21.78])
XYZ = Lab_to_XYZ(Lab)

Lab_D50 = XYZ_to_Lab([19.01, 20.0, 21.78], whitepoint_XYZ=D50_XYZ)
```

注意：`whitepoint_XYZ` 是空间参数，必须是三刺激值，不是 xy。

### `Lab_to_LCHab(...)` / `LCHab_to_Lab(...)`

```python
from color.spaces import Lab_to_LCHab, LCHab_to_Lab

LCHab = Lab_to_LCHab([50.0, 10.0, 20.0])
Lab = LCHab_to_Lab(LCHab)
```

### `XYZ_to_Luv(...)` / `Luv_to_XYZ(...)`

```python
from color.constants import D65_XYZ
from color.spaces import XYZ_to_Luv, Luv_to_XYZ

Luv = XYZ_to_Luv([19.01, 20.0, 21.78], whitepoint_XYZ=D65_XYZ)
XYZ = Luv_to_XYZ(Luv, whitepoint_XYZ=D65_XYZ)
```

### `Luv_to_LCHuv(...)` / `LCHuv_to_Luv(...)`

```python
from color.spaces import LCHuv_to_Luv, Luv_to_LCHuv

LCHuv = Luv_to_LCHuv([50.0, 12.0, 18.0])
Luv = LCHuv_to_Luv(LCHuv)
```

### `Luv_to_Lshuv(...)` / `Lshuv_to_Luv(...)`

用途：Luv 的另一种派生表达，使用 `L, s, h`。

```python
from color.spaces import Lshuv_to_Luv, Luv_to_Lshuv

Lshuv = Luv_to_Lshuv([50.0, 12.0, 18.0])
Luv = Lshuv_to_Luv(Lshuv)
```

### `XYZ_to_UVW(...)` / `UVW_to_XYZ(...)`

```python
from color.constants import D65_XYZ
from color.spaces import XYZ_to_UVW, UVW_to_XYZ

UVW = XYZ_to_UVW([19.01, 20.0, 21.78], whitepoint_XYZ=D65_XYZ)
XYZ = UVW_to_XYZ(UVW, whitepoint_XYZ=D65_XYZ)
```

注意：CIE UVW 是历史空间，适合复现和对照，不建议作为现代感知空间主线。

## D65-referred spaces：Oklab、IPT、Jzazbz

### `XYZ_to_Oklab(...)` / `Oklab_to_XYZ(...)`

```python
from color.spaces import XYZ_to_Oklab, Oklab_to_XYZ

Oklab = XYZ_to_Oklab([19.01, 20.0, 21.78])
XYZ_D65 = Oklab_to_XYZ(Oklab)
```

非 D65 输入先适应：

```python
from color.adaptation import adapt_to_D65
from color.constants import D50_XYZ
from color.spaces import XYZ_to_Oklab

XYZ_D65 = adapt_to_D65(XYZ_D50, source_white_XYZ=D50_XYZ)
Oklab = XYZ_to_Oklab(XYZ_D65)
```

### `Oklab_to_Oklch(...)` / `Oklch_to_Oklab(...)`

```python
from color.spaces import Oklab_to_Oklch, Oklch_to_Oklab

Oklch = Oklab_to_Oklch([0.5, 0.02, -0.03])
Oklab = Oklch_to_Oklab(Oklch)
```

### `XYZ_to_IPT(...)` / `IPT_to_XYZ(...)` / `IPT_hue_angle(...)`

```python
from color.spaces import IPT_hue_angle, IPT_to_XYZ, XYZ_to_IPT

IPT = XYZ_to_IPT([19.01, 20.0, 21.78])
XYZ_D65 = IPT_to_XYZ(IPT)
h = IPT_hue_angle(IPT)
```

### `XYZ_to_Jzazbz(...)` / `Jzazbz_to_XYZ(...)`

```python
from color.spaces import Jzazbz_to_XYZ, XYZ_to_Jzazbz

Jzazbz = XYZ_to_Jzazbz([19.01, 20.0, 21.78])
XYZ_D65 = Jzazbz_to_XYZ(Jzazbz)
```

### `Jzazbz_to_JzCzhz(...)` / `JzCzhz_to_Jzazbz(...)`

```python
from color.spaces import JzCzhz_to_Jzazbz, Jzazbz_to_JzCzhz

JzCzhz = Jzazbz_to_JzCzhz([0.02, 0.001, -0.002])
Jzazbz = JzCzhz_to_Jzazbz(JzCzhz)
```

## CAM02-UCS / LCD / SCD

### JMh 与 CAM02 均匀空间

```python
from color.spaces import (
    CAM02LCD_to_JMh_CIECAM02,
    CAM02SCD_to_JMh_CIECAM02,
    CAM02UCS_to_JMh_CIECAM02,
    JMh_CIECAM02_to_CAM02LCD,
    JMh_CIECAM02_to_CAM02SCD,
    JMh_CIECAM02_to_CAM02UCS,
)

JMh = [41.731, 0.109, 219.048]
ucs = JMh_CIECAM02_to_CAM02UCS(JMh)
lcd = JMh_CIECAM02_to_CAM02LCD(JMh)
scd = JMh_CIECAM02_to_CAM02SCD(JMh)

JMh_back = CAM02UCS_to_JMh_CIECAM02(ucs)
JMh_lcd = CAM02LCD_to_JMh_CIECAM02(lcd)
JMh_scd = CAM02SCD_to_JMh_CIECAM02(scd)
```

### XYZ 与 CAM02 均匀空间

默认观察条件：

```python
from color.spaces import XYZ_to_CAM02UCS, CAM02UCS_to_XYZ

cam02 = XYZ_to_CAM02UCS([19.01, 20.0, 21.78])
XYZ = CAM02UCS_to_XYZ(cam02)
```

显式观察条件：

```python
from color.constants import D65_XYZ
from color.spaces import SpaceSpec, convert_color

cam02 = convert_color(
    [19.01, 20.0, 21.78],
    "XYZ",
    SpaceSpec("CAM02-UCS", XYZ_w=D65_XYZ, L_A=318.31, Y_b=20.0),
)
```

LCD / SCD：

```python
from color.spaces import (
    CAM02LCD_to_XYZ,
    CAM02SCD_to_XYZ,
    XYZ_to_CAM02LCD,
    XYZ_to_CAM02SCD,
)

lcd = XYZ_to_CAM02LCD([19.01, 20.0, 21.78])
scd = XYZ_to_CAM02SCD([19.01, 20.0, 21.78])
XYZ_lcd = CAM02LCD_to_XYZ(lcd)
XYZ_scd = CAM02SCD_to_XYZ(scd)
```

注意：这些是基于 CIECAM02 色貌模型的均匀空间，不是色貌模型本身。

## CAM16-UCS / LCD / SCD

### JMh 与 CAM16 均匀空间

```python
from color.spaces import (
    CAM16LCD_to_JMh_CIECAM16,
    CAM16SCD_to_JMh_CIECAM16,
    CAM16UCS_to_JMh_CIECAM16,
    JMh_CIECAM16_to_CAM16LCD,
    JMh_CIECAM16_to_CAM16SCD,
    JMh_CIECAM16_to_CAM16UCS,
)

JMh = [41.731, 0.109, 219.048]
ucs = JMh_CIECAM16_to_CAM16UCS(JMh)
lcd = JMh_CIECAM16_to_CAM16LCD(JMh)
scd = JMh_CIECAM16_to_CAM16SCD(JMh)

JMh_back = CAM16UCS_to_JMh_CIECAM16(ucs)
JMh_lcd = CAM16LCD_to_JMh_CIECAM16(lcd)
JMh_scd = CAM16SCD_to_JMh_CIECAM16(scd)
```

### XYZ 与 CAM16 均匀空间

默认观察条件：

```python
from color.spaces import XYZ_to_CAM16UCS, CAM16UCS_to_XYZ

cam16 = XYZ_to_CAM16UCS([19.01, 20.0, 21.78])
XYZ = CAM16UCS_to_XYZ(cam16)
```

显式观察条件：

```python
from color.constants import D65_XYZ
from color.spaces import SpaceSpec, convert_color

cam16 = convert_color(
    [19.01, 20.0, 21.78],
    "XYZ",
    SpaceSpec("CAM16-UCS", XYZ_w=D65_XYZ, L_A=318.31, Y_b=20.0),
)
```

LCD / SCD：

```python
from color.spaces import (
    CAM16LCD_to_XYZ,
    CAM16SCD_to_XYZ,
    XYZ_to_CAM16LCD,
    XYZ_to_CAM16SCD,
)

lcd = XYZ_to_CAM16LCD([19.01, 20.0, 21.78])
scd = XYZ_to_CAM16SCD([19.01, 20.0, 21.78])
XYZ_lcd = CAM16LCD_to_XYZ(lcd)
XYZ_scd = CAM16SCD_to_XYZ(scd)
```

注意：CAM02/CAM16 均匀空间的观察条件属于空间参数，应在直接函数参数或
`SpaceSpec(...)` 中显式声明。
