# spaces - 详细指南

`color.spaces` 是项目中的颜色空间层，负责把已经得到的颜色数值在不同表示之间转换。

它和其他模块的边界是：

```text
color.colorimetry  负责基础色度学计算，例如 XYZ、xyY、光谱积分、色温、主波长等
color.adaptation   负责显式色适应，例如 D50 -> D65
color.appearance   负责色貌模型，例如 CIECAM02 / CIECAM16
color.spaces       负责颜色空间表示、注册、转换路由和路径可视化
```

## 核心设计

当前 `spaces` 的核心规则是：

```text
XYZ 是唯一全局中枢
公开 XYZ 标度统一为 Y=100
RGB 标准空间使用独立 RGB 注册表
普通颜色空间使用 SPACE_REGISTRY 注册
带参数的空间实例使用 SpaceSpec 表达
convert_color 只做空间路由，不做隐式色适应
describe_conversion_path 解释单条转换路径，不执行数值转换
plot_conversion_graph 展示当前注册的完整转换图谱
```

目录结构按职责拆分：

```text
color.spaces.rgb          RGB 标准、传递函数和 RGB <-> XYZ
color.spaces.basic        不依赖色貌模型的基础/经典空间
color.spaces.appearance   基于色貌模型输出构造的均匀空间
```

推荐使用者仍然从顶层 `color.spaces` 导入公开 API；子包主要用于保持内部实现和注册边界清楚。

## XYZ 标度与 D65-referred

`color.spaces` 的公开 `XYZ` 使用 `Y=100` 标度。这与 `color.colorimetry` 的光谱积分结果、`color.constants.D65_XYZ` 以及 `color.appearance` 的 CIECAM02/CIECAM16 参考域一致。

有些空间带有显式白点参数，例如：

```text
Lab / Luv / UVW
CAM02-UCS / CAM16-UCS
```

有些空间没有白点参数，并要求输入已经是 D65-referred XYZ：

```text
Oklab
IPT
Jzazbz
```

如果你的 XYZ 不是 D65-referred，请先显式适应：

```python
from color.adaptation import adapt_from_D65, adapt_to_D65
from color.constants import D50_XYZ
from color.spaces import Oklab_to_XYZ, XYZ_to_Oklab

XYZ_D65_referred = adapt_to_D65(XYZ_D50, source_white_XYZ=D50_XYZ)
Oklab = XYZ_to_Oklab(XYZ_D65_referred)

XYZ_D50 = adapt_from_D65(Oklab_to_XYZ(Oklab), target_white_XYZ=D50_XYZ)
```

这里的适应是调用者显式写出的步骤，不是 `convert_color(...)` 的隐式行为。

## RGB 空间

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

RGB 转换默认处理 encoded RGB，也就是常见图像和显示器中的 RGB 数值：

```python
XYZ = RGB_to_XYZ([0.25, 0.50, 0.75], colourspace="sRGB")
RGB = XYZ_to_RGB(XYZ, colourspace="sRGB")
```

如果输入已经是 linear RGB，需要关闭 transfer decoding：

```python
XYZ = RGB_to_XYZ(linear_rgb, colourspace="sRGB", apply_decoding=False)
```

如果希望输出 linear RGB，需要关闭 transfer encoding：

```python
linear_rgb = XYZ_to_RGB(XYZ, colourspace="sRGB", apply_encoding=False)
```

这些函数不会自动裁剪到 `[0, 1]`。超出范围的 RGB 数值可能表示中间计算结果或目标空间外颜色，是否 clip 应由调用方决定。

### RGB 到 RGB

RGB 空间之间通过 XYZ 中转：

```text
source RGB -> source XYZ -> target RGB
```

默认情况下，`RGB_to_RGB(...)` 不做色适应，只保持同一个 XYZ 刺激：

```python
from color.spaces import RGB_to_RGB

p3_rgb = RGB_to_RGB([0.25, 0.50, 0.75], "sRGB", "Display P3")
```

如果需要模拟 source white 到 target white 的适应，可以显式传入：

```python
srgb = RGB_to_RGB(
    [1.0, 1.0, 1.0],
    "DCI-P3",
    "sRGB",
    chromatic_adaptation="Bradford",
)
```

支持的色适应变换来自 `color.adaptation`：

```text
Von Kries
Bradford
CAT02
CAT16
```

这个能力只放在 `RGB_to_RGB(...)` 中。通用 `convert_color(...)` 不接受 `chromatic_adaptation` 参数。

## Basic Spaces

当前基础空间和辅助色度坐标包括：

```text
XYZ <-> xyY
XYZ <-> Lab <-> LCHab
XYZ <-> Luv <-> LCHuv
XYZ <-> UVW
XYZ <-> Oklab <-> Oklch
XYZ <-> IPT
XYZ <-> Jzazbz <-> JzCzhz
xy / uv1960 / u'v'1976 helpers
```

### xyY 与色度 helper

`xyY` 是完整三维颜色空间，可以和 XYZ 往返：

```python
from color.spaces import XYZ_to_xyY, xyY_to_XYZ

xyY = XYZ_to_xyY(XYZ)
XYZ_again = xyY_to_XYZ(xyY)
```

`xy`、`uv1960` 和 `u'v'1976` 是二维色度坐标，不包含亮度信息，因此只作为 helper 提供，不注册为空间节点：

```python
from color.spaces import (
    XYZ_to_xy,
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

当 `XYZ = [0, 0, 0]` 时，`xy` 没有定义。此时可通过 `SpaceSpec("xyY", fallback_xy=...)` 指定黑点的备用色度坐标，亮度仍为 `0`。

### Lab / Luv / UVW

`Lab` 和 `Luv` 需要 `whitepoint_XYZ` 参数。它表示参考白点的三刺激值，而不是 `xy` 色坐标：

```python
from color.constants import D50_XYZ
from color.spaces import Lab_to_XYZ, XYZ_to_Lab

Lab_D50 = XYZ_to_Lab(XYZ, whitepoint_XYZ=D50_XYZ)
XYZ_again = Lab_to_XYZ(Lab_D50, whitepoint_XYZ=D50_XYZ)
```

默认参考白点是 `D65_XYZ`，也就是 `Y=100` 标度下的 D65。

`UVW` 指 CIE 1964 `U*V*W*` 空间，是历史上的三维均匀空间。它已不是现代项目的主线推荐空间，但对复现旧文献和与 `colour` 对照仍有价值：

```python
from color.constants import D65_XYZ
from color.spaces import SpaceSpec, convert_color

UVW = convert_color(XYZ, "XYZ", SpaceSpec("UVW", whitepoint_XYZ=D65_XYZ))
XYZ_again = convert_color(UVW, SpaceSpec("UVW", whitepoint_XYZ=D65_XYZ), "XYZ")
```

`UVW` 支持 `whitepoint_XYZ` 或 `whitepoint_xy`，两者不能同时传入。

### Oklab / IPT / Jzazbz

这三个空间不带 `whitepoint_XYZ` 参数，要求输入是 D65-referred XYZ：

```python
from color.spaces import XYZ_to_IPT, IPT_hue_angle, XYZ_to_Jzazbz

IPT = XYZ_to_IPT(XYZ_D65_referred)
hue = IPT_hue_angle(IPT)
Jzazbz = XYZ_to_Jzazbz(XYZ_D65_referred)
```

`Jzazbz` 面向 HDR / 宽色域图像信号，公式内部包含 PQ / ST2084 风格的非线性压缩。本项目对外仍使用 `Y=100` XYZ 标度，内部会自动转换到公式需要的相对域。

### Cylindrical Derivatives

下列空间是圆柱/极坐标派生节点：

```text
Lab     -> LCHab:  L*, C*, h
Luv     -> LCHuv:  L*, C*, h
Oklab   -> Oklch:  L, C, h
Jzazbz  -> JzCzhz: Jz, Cz, hz
```

h 使用角度制，范围为 `[0, 360)`。

这些空间通过 parent 链接入路由：

```text
LCHab -> Lab -> XYZ
LCHuv -> Luv -> XYZ
Oklch -> Oklab -> XYZ
JzCzhz -> Jzazbz -> XYZ
```

## Appearance Uniform Spaces

当前 `spaces` 已接入两组基于色貌模型输出构造的均匀空间：

```text
CAM02-UCS / CAM02-LCD / CAM02-SCD
CAM16-UCS / CAM16-LCD / CAM16-SCD
```

它们不是新的色貌模型，而是把 `color.appearance` 中 CIECAM02 / CIECAM16 输出的 `J, M, h` 转换成更适合度量颜色距离的 `J', a', b'` 坐标。

CAM02 链路：

```text
XYZ -> CIECAM02(J, M, h) -> CAM02-UCS/LCD/SCD
CAM02-UCS/LCD/SCD -> CIECAM02(J, M, h) -> XYZ
```

CAM16 链路：

```text
XYZ -> CIECAM16(J, M, h) -> CAM16-UCS/LCD/SCD
CAM16-UCS/LCD/SCD -> CIECAM16(J, M, h) -> XYZ
```

两组空间都依赖观察条件，因此推荐用 `SpaceSpec` 显式写出参数：

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

这里的观察条件是空间参数，不是 `convert_color(...)` 在背后做了隐式色适应。

`UCS` 是通用均匀空间，`LCD` 偏向大色差，`SCD` 偏向小色差。

## SpaceSpec

空间不仅有名字，还可能有自己的参数：

```text
Lab(D50)
Luv(D65)
xyY(fallback_xy=D65)
sRGB(apply_decoding=False)
CAM16-UCS(XYZ_w=D65, L_A=318.31, Y_b=20)
```

`SpaceSpec` 用来把空间名称和参数绑定成一个空间实例：

```python
from color.constants import D50_XYZ, D65_XYZ
from color.spaces import SpaceSpec, convert_color

Lab_D50 = SpaceSpec("Lab", whitepoint_XYZ=D50_XYZ)
Luv_D65 = SpaceSpec("Luv", whitepoint_XYZ=D65_XYZ)

Luv = convert_color(Lab, Lab_D50, Luv_D65)
```

这条路径表示：

```text
Lab(D50) -> XYZ -> Luv(D65)
```

source 参数和 target 参数彼此独立，这比把参数塞进一个全局 kwargs 更清楚。

## convert_color 与色适应边界

`convert_color(...)` 是通用空间路由入口：

```python
from color.spaces import convert_color

Lab = convert_color(XYZ, "XYZ", "Lab")
Oklch = convert_color(XYZ_D65_referred, "XYZ", "Oklch")
sRGB = convert_color(Lab, "Lab", "sRGB")
```

它支持字符串、`ColorSpaceNode`、`RGBColorSpace` 和 `SpaceSpec`。

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

原因是：

```text
空间转换       描述同一个颜色刺激在不同空间中的数值表示
色适应         改变 XYZ，使其适配另一个参考白点/观察状态
```

两者语义不同，不应该在通用路由中混在一起。

## Path Description And Plotting

`describe_conversion_path(...)` 用来解释 `convert_color(...)` 会走哪条结构路径，但不执行实际数值转换：

```python
from color.spaces import describe_conversion_path

path = describe_conversion_path("JzCzhz", "Lab")
for edge in path.edges:
    print(edge.source, "->", edge.target, edge.operation)
```

输出路径会显式展示 parent 链和 XYZ 中枢：

```text
JzCzhz -> Jzazbz -> XYZ -> Lab
```

RGB 路径也会明确说明 `convert_color(...)` 的无隐式色适应规则：

```python
path = describe_conversion_path("sRGB", "Display P3")
print(path.edges[0].description)
```

```text
sRGB to XYZ; apply_decoding=True; chromatic_adaptation=None
```

绘制单条路径：

```python
from color.spaces import plot_conversion_path

fig, ax = plot_conversion_path(path)
```

绘制完整注册图谱：

```python
from color.spaces import plot_conversion_graph

fig, ax = plot_conversion_graph()
```

`plot_conversion_graph(...)` 是注册表驱动的。新增空间只要正确注册到 `SPACE_REGISTRY` 或 `RGB_COLORSPACES`，重新运行绘图函数时就会自动出现在图中。

## 注册表

通用颜色空间节点通过 `SPACE_REGISTRY` 管理：

```python
from color.spaces import get_colourspace_node, list_colourspace_nodes

node = get_colourspace_node("JzCzHz")
names = list_colourspace_nodes()
```

当前注册的通用节点：

```text
XYZ
xyY
Lab
LCHab
Luv
LCHuv
UVW
Oklab
Oklch
IPT
Jzazbz
JzCzhz
CAM02-UCS
CAM02-LCD
CAM02-SCD
CAM16-UCS
CAM16-LCD
CAM16-SCD
```

RGB 标准空间使用独立注册表：

```python
from color.spaces import get_RGB_colourspace, list_RGB_colourspaces

srgb = get_RGB_colourspace("sRGB")
rgb_names = list_RGB_colourspaces()
```

RGB 不直接混入 `SPACE_REGISTRY`，因为 RGB 标准不仅是空间节点，还包含 primaries、white point、transfer function 和转换矩阵。

## Examples

`examples/spaces` 中有五个示例：

```text
example_01_rgb_colourspace_conversion.py
example_02_colourspace_chain.py
example_03_cam_uniform_spaces.py
example_04_reference_accuracy.py
example_05_conversion_paths.py
```

它们分别覆盖：

```text
01 RGB 标准、gamut 三角形、RGB-to-RGB 预览
02 sRGB -> XYZ -> Lab/Luv/Oklab/Oklch -> sRGB 长链路
03 CAM02/CAM16 uniform spaces 与观察条件影响
04 与 colour 库的基础空间数值对照
05 单条转换路径图与完整 conversion graph
```

运行：

```powershell
.\.venv\Scripts\python.exe examples\spaces\example_01_rgb_colourspace_conversion.py
.\.venv\Scripts\python.exe examples\spaces\example_02_colourspace_chain.py
.\.venv\Scripts\python.exe examples\spaces\example_03_cam_uniform_spaces.py
.\.venv\Scripts\python.exe examples\spaces\example_04_reference_accuracy.py
.\.venv\Scripts\python.exe examples\spaces\example_05_conversion_paths.py
```

输出图像位于：

```text
examples/spaces/output/
```
