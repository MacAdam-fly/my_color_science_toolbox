# spaces - 详细指南

`color.spaces` 是项目中的颜色空间层，负责把已经得到的颜色数值在不同颜色表示之间转换。

它和 `color.colorimetry` 的关系是：

```text
color.colorimetry  负责基础色度学计算，例如 XYZ、xyY、光谱积分、色温、主波长等
color.spaces       负责颜色空间表示和空间之间的转换路由
```

目前 `spaces` 的核心设计是：

```text
XYZ 是唯一全局中枢
RGB 标准空间有独立注册表
普通颜色空间通过 SPACE_REGISTRY 注册
带参数的空间实例用 SpaceSpec 表达
convert_color 负责路由，不做隐式色适应
```

## 当前已实现内容

### RGB 空间

已注册的 RGB 标准包括：

```text
sRGB
Rec.709
Display P3
DCI-P3
Rec.2020
Adobe RGB (1998)
NTSC (1953)
```

主要 API：

```python
from color.spaces import (
    RGB_to_XYZ,
    XYZ_to_RGB,
    RGB_to_RGB,
    sRGB_to_XYZ,
    XYZ_to_sRGB,
    get_RGB_colourspace,
    list_RGB_colourspaces,
)
```

RGB 转换默认处理的是 encoded RGB，也就是常见图像和显示器中的 RGB 数值：

```python
XYZ = RGB_to_XYZ([0.25, 0.50, 0.75], colourspace="sRGB")
RGB = XYZ_to_RGB(XYZ, colourspace="sRGB")
```

如果输入已经是 linear RGB，需要显式关闭 transfer decoding：

```python
XYZ = RGB_to_XYZ(linear_rgb, colourspace="sRGB", apply_decoding=False)
```

如果希望得到 linear RGB，而不是编码后的显示 RGB：

```python
linear_rgb = XYZ_to_RGB(XYZ, colourspace="sRGB", apply_encoding=False)
```

这些函数不会自动裁剪到 `[0, 1]`。超出范围的 RGB 数值可能表示中间计算结果或目标空间外颜色，是否 clip 应由调用方决定。

### RGB 到 RGB

RGB 空间之间通过 XYZ 中转：

```text
source RGB -> source XYZ -> target RGB
```

例如：

```python
from color.spaces import RGB_to_RGB

p3_rgb = RGB_to_RGB([0.25, 0.50, 0.75], "sRGB", "Display P3")
```

默认情况下，`RGB_to_RGB(...)` 不做色适应，只保持同一个 XYZ 刺激。

如果确实需要把 source white 适应到 target white，可以显式传入：

```python
srgb = RGB_to_RGB(
    [1.0, 1.0, 1.0],
    "DCI-P3",
    "sRGB",
    chromatic_adaptation="Bradford",
)
```

这里RGB颜色空间之间使用色适应参数的目的是区分：色度转换和带感知的色度转换，启动色适应的目的是对实际显示观看的模拟，模拟显示设备白点变化带来的色适应变化

支持的色适应变换来自 `color.adaptation`：

```text
Von Kries
Bradford
CAT02
CAT16
```

注意：这个能力只放在 `RGB_to_RGB(...)` 中。通用的 `convert_color(...)` 不做隐式色适应。

## XYZ、xyY 和 xy

`xyY` 是完整三维颜色空间，可以和 XYZ 往返：

```python
from color.spaces import XYZ_to_xyY, xyY_to_XYZ

xyY = XYZ_to_xyY(XYZ)
XYZ_again = xyY_to_XYZ(xyY)
```

`xy` 只有色度，没有亮度，因此不是完整可逆空间：

```python
from color.spaces import XYZ_to_xy, xyY_to_xy

xy = XYZ_to_xy(XYZ)
```

因此：

```text
xyY 注册为空间节点
xy 只作为色度投影辅助函数，不注册为空间节点
```

同理，`uv1960` 和 `u'v'1976` 也是二维色度坐标，不包含亮度信息，因此只作为 helper 提供，不注册为空间节点：

```python
from color.spaces import (
    xy_to_uv1960,
    XYZ_to_uv1960,
    uv1960_to_xy,
    xy_to_upvp1976,
    XYZ_to_upvp1976,
    upvp1976_to_xy,
)
```

其中 `uv1960` 常用于 CCT / Duv 计算，`u'v'1976` 是 CIE Luv 的基础色度图。二者关系为：

```text
u' = u
v' = 1.5 v
```

当 `XYZ = [0, 0, 0]` 时，`x = X / (X + Y + Z)` 和 `y = Y / (X + Y + Z)` 没有定义。
这时可以使用 `fallback_xy`：

```python
from color.spaces import SpaceSpec, convert_color

xyY = convert_color(
    [0.0, 0.0, 0.0],
    "XYZ",
    SpaceSpec("xyY", fallback_xy=(0.3127, 0.3290)),
)
```

这里的 `fallback_xy` 只是黑色点的备用色度坐标，亮度 `Y` 仍然是 `0`。

## Lab、Luv、Oklab 和 LCH

目前实现了：

```text
XYZ <-> Lab <-> LCHab
XYZ <-> Luv <-> LCHuv
XYZ <-> UVW
XYZ <-> Oklab <-> Oklch
```

主要 API：

```python
from color.spaces import (
    XYZ_to_Lab,
    Lab_to_XYZ,
    Lab_to_LCHab,
    LCHab_to_Lab,
    XYZ_to_Luv,
    Luv_to_XYZ,
    Luv_to_LCHuv,
    LCHuv_to_Luv,
    XYZ_to_UVW,
    UVW_to_XYZ,
    XYZ_to_Oklab,
    Oklab_to_XYZ,
    Oklab_to_Oklch,
    Oklch_to_Oklab,
)
```

### Lab 和 Luv 的参考白点

`Lab` 和 `Luv` 都需要参考白点。项目中使用的参数名是：

```python
whitepoint_XYZ
```

它表示参考白点的三刺激值，而不是 `xy` 色坐标。

默认值是 `Y=100` 标度下的 D65：

```python
from color.spaces import DEFAULT_WHITEPOINT_XYZ
```

等价于：

```python
from color.constants import D65_XYZ

DEFAULT_WHITEPOINT_XYZ = D65_XYZ
```

使用 D50 参考白点的例子：

```python
from color.constants import D50_XYZ
from color.spaces import XYZ_to_Lab, Lab_to_XYZ

white = D50_XYZ

Lab = XYZ_to_Lab(XYZ, whitepoint_XYZ=white)
XYZ_again = Lab_to_XYZ(Lab, whitepoint_XYZ=white)
```

第一版中，`whitepoint_XYZ` 是空间参数，只接受单个 `(3,)` 三刺激值。
颜色数据本身仍然支持 `(..., 3)` 批量数组。

### Oklab

`Oklab` 不需要 `whitepoint_XYZ` 参数：

```python
from color.spaces import XYZ_to_Oklab, Oklab_to_XYZ

Oklab = XYZ_to_Oklab(XYZ)
XYZ_again = Oklab_to_XYZ(Oklab)
```

### CIE UVW

`UVW` 指 CIE 1964 `U*V*W*` 空间，是一个历史上的三维均匀颜色空间。它已经不是现代项目中最推荐的感知空间，但对于复现旧文献和与 `colour` 对照仍然有价值。

它是完整三维空间，因此注册进 `SPACE_REGISTRY`：

```python
from color.constants import D65_XYZ
from color.spaces import SpaceSpec, convert_color

UVW = convert_color(XYZ, "XYZ", SpaceSpec("UVW", whitepoint_XYZ=D65_XYZ))
XYZ_again = convert_color(UVW, SpaceSpec("UVW", whitepoint_XYZ=D65_XYZ), "XYZ")
```

`UVW` 支持两种白点参数：

```python
SpaceSpec("UVW", whitepoint_XYZ=D65_XYZ)
SpaceSpec("UVW", whitepoint_xy=(0.3127, 0.3290))
```

两者不能同时传入，避免参考白点来源不清。

### LCH 派生空间

`LCHab`、`LCHuv`、`Oklch` 是对应直角空间的极坐标形式：

```text
Lab   -> LCHab: L*, C*, h
Luv   -> LCHuv: L*, C*, h
Oklab -> Oklch: L, C, h
```

h 使用角度制，范围为 `[0, 360)`。

这些空间是派生节点，不直接连接 XYZ：

```text
LCHab -> Lab -> XYZ
LCHuv -> Luv -> XYZ
Oklch -> Oklab -> XYZ
```

## SpaceSpec：带参数的空间实例

空间不仅有名字，还可能有自己的参数。

例如：

```text
Lab(D50)
Luv(D65)
xyY(fallback_xy=D65)
sRGB(apply_decoding=False)
```

因此项目引入了 `SpaceSpec`：

```python
from color.spaces import SpaceSpec
from color.constants import D50_XYZ, D65_XYZ

Lab_D50 = SpaceSpec("Lab", whitepoint_XYZ=D50_XYZ)
Luv_D65 = SpaceSpec("Luv", whitepoint_XYZ=D65_XYZ)
```

`SpaceSpec` 的意义是把“空间类型”和“空间参数”绑定成一个空间实例。

这解决了一个很重要的问题：

```text
Lab(D50) -> Luv(D65)
```

这里 source 和 target 都需要白点参数，而且两个参数不一样。

使用 `SpaceSpec` 可以明确表达：

```python
from color.spaces import convert_color

Luv = convert_color(Lab, Lab_D50, Luv_D65)
```

这条路径的含义是：

```text
Lab(D50) -> XYZ
XYZ -> Luv(D65)
```

它只是参数化空间转换，不等于色适应。

## convert_color 的设计边界

`convert_color(...)` 是通用空间路由入口：

```python
from color.spaces import convert_color

Lab = convert_color(XYZ, "XYZ", "Lab")
Oklch = convert_color(XYZ, "XYZ", "Oklch")
sRGB = convert_color(Lab, "Lab", "sRGB")
```

它支持字符串和 `SpaceSpec` 混用：

```python
from color.constants import D50_XYZ, D65_XYZ
from color.spaces import SpaceSpec, convert_color

LCHab_D50 = convert_color(
    XYZ,
    "XYZ",
    SpaceSpec("LCHab", whitepoint_XYZ=D50_XYZ),
)

Luv_D65 = convert_color(
    LCHab_D50,
    SpaceSpec("LCHab", whitepoint_XYZ=D50_XYZ),
    SpaceSpec("Luv", whitepoint_XYZ=D65_XYZ),
)
```

### 不做隐式色适应

`convert_color(...)` 不接受：

```python
chromatic_adaptation=...
```

如果需要色适应，应显式写出中间步骤：

```python
from color.adaptation import chromatic_adaptation_XYZ

XYZ_source = convert_color(Lab, SpaceSpec("Lab", whitepoint_XYZ=D50_XYZ), "XYZ")
XYZ_target = chromatic_adaptation_XYZ(
    XYZ_source,
    source_white_XYZ=D50_XYZ,
    target_white_XYZ=D65_XYZ,
    transform="Bradford",
)
Luv = convert_color(XYZ_target, "XYZ", SpaceSpec("Luv", whitepoint_XYZ=D65_XYZ))
```

这样做的原因是：

```text
空间转换       描述同一个颜色刺激在不同空间中的数值表示
色适应         改变 XYZ，使其适配另一个参考白点/观察状态
```

两者语义不同，不应该在通用路由中混在一起。

## 注册表结构

通用颜色空间节点通过 `SPACE_REGISTRY` 管理：

```python
from color.spaces import get_colourspace_node, list_colourspace_nodes

node = get_colourspace_node("LCHab")
names = list_colourspace_nodes()
```

目前注册的通用空间节点包括：

```text
XYZ
xyY
Lab
LCHab
Luv
LCHuv
Oklab
Oklch
UVW
CAM02-UCS
CAM02-LCD
CAM02-SCD
CAM16-UCS
CAM16-LCD
CAM16-SCD
```

RGB 标准空间不直接混入 `SPACE_REGISTRY`，而是使用独立的 RGB 注册表：

```python
from color.spaces import get_RGB_colourspace, list_RGB_colourspaces

srgb = get_RGB_colourspace("sRGB")
names = list_RGB_colourspaces()
```

这样做是因为 RGB 标准空间不仅是数学空间，还包含：

```text
primaries
white_xy
transfer
RGB_to_XYZ matrix
XYZ_to_RGB matrix
```

这些信息比普通空间节点更具体，因此单独管理更清楚。

## 与 colour 库的差异

`colour` 的 `convert(...)` 使用大型转换图，并允许按转换函数名传参，例如：

```python
colour.convert(
    Lab,
    "CIE Lab",
    "CIE Luv",
    Lab_to_XYZ={"illuminant": D50_xy},
    XYZ_to_Luv={"illuminant": D65_xy},
)
```

本项目采用更显式的 `SpaceSpec`：

```python
convert_color(
    Lab,
    SpaceSpec("Lab", whitepoint_XYZ=D50_XYZ),
    SpaceSpec("Luv", whitepoint_XYZ=D65_XYZ),
)
```

这样 source 参数和 target 参数更清楚，也更适合后续接入色貌模型这类复杂空间。

## CAM02-UCS 与 CAM16-UCS 系列

目前 `spaces` 已经接入两组基于色貌模型的均匀颜色空间：

```text
CAM02-UCS / CAM02-LCD / CAM02-SCD
CAM16-UCS / CAM16-LCD / CAM16-SCD
```

它们都不是新的色貌模型，而是把色貌模型输出的 `J, M, h` 再转换成更适合度量颜色距离的 `J', a', b'` 均匀空间。

CAM02 系列的链路是：

```text
XYZ -> CIECAM02(J, M, h) -> CAM02-UCS/LCD/SCD
CAM02-UCS/LCD/SCD -> CIECAM02(J, M, h) -> XYZ
```

CAM16 系列的链路是：

```text
XYZ -> CIECAM16(J, M, h) -> CAM16-UCS/LCD/SCD
CAM16-UCS/LCD/SCD -> CIECAM16(J, M, h) -> XYZ
```

两组空间都依赖观察条件，因此推荐用 `SpaceSpec` 显式写出参数。这里的观察条件是均匀空间定义的一部分，不是 `convert_color(...)` 在背后做了隐式色适应：

```python
from color.constants import D65_XYZ
from color.spaces import SpaceSpec, convert_color

cam16 = convert_color(
    XYZ,
    "XYZ",
    SpaceSpec("CAM16-UCS", XYZ_w=D65_XYZ, L_A=318.31, Y_b=20),
)
XYZ_again = convert_color(
    cam16,
    SpaceSpec("CAM16-UCS", XYZ_w=D65_XYZ, L_A=318.31, Y_b=20),
    "XYZ",
)
```

`UCS` 是通用均匀空间；`LCD` 更偏向大色差；`SCD` 更偏向小色差。CAM16 系列的空间名称沿用标准写法 `CAM16-*`，但底层 JMh 辅助函数使用项目统一的 `CIECAM16` 命名，例如 `JMh_CIECAM16_to_CAM16UCS`。

需要注意的是，CAM02-UCS / CAM16-UCS 并不是色貌模型本身。色貌模型位于 `color.appearance`，负责计算 `J, C, h, M, s` 等色貌相关量；这里的 `spaces` 层只是把其中的 `J, M, h` 包装为更适合做空间距离比较的 `J', a', b'` 坐标。

## 示例

`examples/spaces` 中有三个主要示例：

```text
example_01_rgb_colourspace_conversion.py
example_02_colourspace_chain.py
example_03_cam_uniform_spaces.py
```

第一个示例展示 RGB 空间内部转换和 gamut 可视化。

第二个示例展示：

```text
sRGB -> XYZ -> Lab -> LCHab -> Luv -> LCHuv -> Oklab -> Oklch -> XYZ -> sRGB
```

并演示 `SpaceSpec` 白点参数如何参与转换链路。

第三个示例展示：

```text
sRGB -> XYZ -> CAM02-UCS/LCD/SCD -> XYZ -> sRGB
sRGB -> XYZ -> CAM16-UCS/LCD/SCD -> XYZ -> sRGB
```

并绘制 CAM02-UCS 与 CAM16-UCS 的坐标差异，以及 Average / Dim surround 对两组均匀空间坐标的影响。

运行：

```powershell
.\.venv\Scripts\python.exe examples\spaces\example_01_rgb_colourspace_conversion.py
.\.venv\Scripts\python.exe examples\spaces\example_02_colourspace_chain.py
.\.venv\Scripts\python.exe examples\spaces\example_03_cam_uniform_spaces.py
```

输出图像位于：

```text
examples/spaces/output/
```

## 后续计划

当前 `spaces` 主体已经形成：

```text
RGB
XYZ / xyY
Lab / Luv / Oklab
LCHab / LCHuv / Oklch
CAM02-UCS / CAM16-UCS
SpaceSpec
convert_color
```

后续可以继续考虑：

```text
IPT
Jzazbz
```
