# gamut 详细说明

`color.gamut` 用于色域可达性、色域边界、覆盖率和标准物体色域的计算。当前模块主要覆盖两类对象：

- 显示器基色色域：由三基色或多基色线性叠加形成。
- 非显示器标准色域：目前包括 Pointer real-surface gamut。

模块使用项目统一的 `XYZ(Y=100)` 标度。这里的 `XYZ` 是线性刺激值，不是编码 RGB，也不包含 gamma / transfer function。

## 模块边界

`color.gamut` 只处理线性混合、几何边界和覆盖率，不处理：

- RGB 编码 / 解码。
- 显示器校准模型。
- 色适应。
- 色貌观察条件。
- 光谱积分。

如果需要从 RGB 标准获得显示基色，模块会使用 `color.spaces.rgb` 中的线性 `RGB -> XYZ` 矩阵：

```python
from color.gamut import DisplayPrimaries

srgb = DisplayPrimaries.from_RGB_colourspace("sRGB")
```

## DisplayPrimaries

`DisplayPrimaries` 是显示器基色定义对象：

```python
from color.gamut import DisplayPrimaries

primaries = DisplayPrimaries(
    primaries_XYZ=[
        [41.24, 21.26, 1.93],
        [35.76, 71.52, 11.92],
        [18.05, 7.22, 95.05],
    ],
    names=("R", "G", "B"),
)
```

字段含义：

- `primaries_XYZ`：shape 为 `(n, 3)`，每一行是一个基色的线性 `XYZ(Y=100)` 刺激值。
- `names`：可选，基色名称。
- `whitepoint_XYZ`：可选，默认等于所有基色满输出之和。

`DisplayPrimaries.from_RGB_colourspace("sRGB")` 可以从已注册 RGB 空间构造三基色显示器。

## 三基色与多基色

三基色显示器满足：

```text
XYZ = [R, G, B] @ primaries_XYZ
```

只要三基色矩阵满秩，给定一个 `XYZ` 就可以直接求唯一线性权重。

多基色显示器满足：

```text
XYZ = [P0, P1, ..., Pn] @ primaries_XYZ
```

当基色数大于 3 时，权重解通常不唯一。模块把所有 `0/1` 基色开关组合形成的刺激点构造成凸包：

```python
from color.gamut import is_within_primary_gamut

inside = is_within_primary_gamut(XYZ_batch, primaries)
```

默认策略：

- 三基色 inside 判断：矩阵求解。
- 四基色及以上 inside 判断：凸包半空间，支持批量向量化。
- 三基色权重求解：矩阵求逆。
- 四基色及以上权重求解：`scipy.optimize.linprog` 找到一组可行解。

```python
from color.gamut import solve_primary_weights

weights = solve_primary_weights([20, 30, 40], primaries)
```

多基色权重不唯一，当前结果只表示一组可行驱动，不代表真实显示器的最佳驱动策略。

## LCHab 边界

`compute_LCH_gamut_boundary(...)` 用于把显示器基色可达域转换成 Lab/LCHab 空间中的边界：

```text
给定 L* 和 hue，沿 C* 方向二分搜索最大可显示 chroma。
```

```python
from color.gamut import compute_LCH_gamut_boundary

boundary = compute_LCH_gamut_boundary(
    "Rec.2020",
    L_values=range(0, 101, 5),
    hue_values=range(0, 361, 5),
    C_upper=260,
)
```

返回对象是 `GamutBoundary`。核心数据是：

```text
C_max.shape == (len(L_values), len(hue_values))
```

它表示每个 `(L*, hue)` 方向上的最大 `C*`。

## GamutBoundary

`GamutBoundary` 主要用于保存、转换和统计离散 LCHab 边界：

```python
boundary.to_LCHab()
boundary.to_Lab()
boundary.to_XYZ()
boundary.slice_L(50)
```

统计函数：

```python
boundary.area_at_L(50)
boundary.areas()
boundary.volume()
boundary.gamut_rings([25, 50, 75, 100])
boundary.ring_area()
boundary.ring_areas([25, 50, 75, 100])
```

平面投影函数：

```python
boundary.projected_chroma()
boundary.projected_lightness()
boundary.projected_LCHab()
boundary.projected_ab()
boundary.projected_area()
```

这些投影函数的含义是：把所有 `L*` 层投影到同一个 hue 方向上，保留该 hue 的最大 `C*`。这适合画 Lab `a*b*` 平面色域，但不是 xy 色品图边界。

显示器 xy 边界函数：

```python
boundary.primary_xy_hull()
```

`primary_xy_hull()` 只对含有 `DisplayPrimaries` 的显示器边界有意义。它直接对显示基色 xy 点求凸包。Pointer 这类非显示器色域没有 primaries，调用该函数会抛 `ValueError`。

注意：不要把 `projected_LCHab()` 或 `projected_ab()` 再转换到 xy 后解释为 xy 边界。`Lab/LCHab -> XYZ -> xy` 会丢失亮度，而且是非线性映射，可能产生错误的突出或折返形状。

## xy 平面覆盖率

xy 覆盖率比较的是 CIE 1931 xy 平面上的二维面积：

```text
coverage(test, reference) = intersection_area(test, reference) / area(reference)
```

覆盖率有方向性：

```python
xy_gamut_coverage("sRGB", "Rec.2020")
xy_gamut_coverage("Rec.2020", "sRGB")
```

这两个结果不是同一个数。

### 输入为显示基色定义

如果输入是显示器基色定义，使用：

```python
from color.gamut import DisplayPrimaries, xy_gamut_coverage

# 1. RGB 标准名称。
coverage_names = xy_gamut_coverage("sRGB", "Rec.2020")

# 2. DisplayPrimaries。
srgb = DisplayPrimaries.from_RGB_colourspace("sRGB")
rec2020 = DisplayPrimaries.from_RGB_colourspace("Rec.2020")
coverage_objects = xy_gamut_coverage(srgb, rec2020)

# 3. (n, 3) 基色 XYZ 行。
coverage_XYZ = xy_gamut_coverage(srgb.primaries_XYZ, rec2020.primaries_XYZ)
```

`xy_gamut_coverage(...)` 会把基色 `XYZ` 转换到 xy，再对 xy 点求凸包。

### 输入已经是 xy 点或 xy hull

如果手里的数据已经是 `(n, 2)` 的 CIE xy 点或 xy 多边形，使用 `*_from_xy`：

```python
from color.gamut import (
    pointer_gamut_xy_boundary,
    xy_gamut_area_from_xy,
    xy_gamut_coverage_from_xy,
    xy_gamut_intersection_area_from_xy,
)

rec2020_xy = [
    [0.708, 0.292],
    [0.170, 0.797],
    [0.131, 0.046],
]
pointer_xy = pointer_gamut_xy_boundary()

area = xy_gamut_area_from_xy(pointer_xy)
intersection = xy_gamut_intersection_area_from_xy(rec2020_xy, pointer_xy)
coverage = xy_gamut_coverage_from_xy(rec2020_xy, pointer_xy)
```

三基色、四基色或更多基色 xy 点都可以直接传入：

```python
from color.gamut import xy_gamut_area_from_xy, xy_gamut_coverage_from_xy

srgb_xy = [
    [0.640, 0.330],
    [0.300, 0.600],
    [0.150, 0.060],
]

rgbc_xy = [
    [0.640, 0.330],
    [0.300, 0.600],
    [0.150, 0.060],
    [0.170, 0.350],
]

area_rgbc = xy_gamut_area_from_xy(rgbc_xy)
coverage = xy_gamut_coverage_from_xy(rgbc_xy, srgb_xy)
```

输入点不需要提前排序，也不需要闭合首尾。内部会对 xy 点求凸包：

- 三基色通常得到三角形。
- 四基色或更多基色得到凸多边形。
- 如果某个点落在其他点围成的区域内部，它不会扩大 xy 面积。

这个设计适合显示器 primary xy gamut。如果未来要保留凹边界，需要单独设计 polygon API，不能继续用当前凸包逻辑。

## Lab 体积覆盖率

Lab 覆盖率比较的是两个 `GamutBoundary` 的三维边界体积：

```text
coverage(test, reference) = overlap_volume(test, reference) / volume(reference)
```

```python
from color.gamut import compute_LCH_gamut_boundary, lab_gamut_coverage

srgb_boundary = compute_LCH_gamut_boundary("sRGB")
rec2020_boundary = compute_LCH_gamut_boundary("Rec.2020")

coverage = lab_gamut_coverage(srgb_boundary, rec2020_boundary)
```

`lab_gamut_coverage(...)` 只接受 `GamutBoundary`，不接受 RGB 名称、基色 XYZ 或 xy 点。这样可以明确边界计算时使用的白点、L 网格、hue 网格和搜索参数。

计算时有两个重要 warning：

1. `whitepoint_XYZ` 不一致

   如果两个边界的 `whitepoint_XYZ` 不同，会抛出 `UserWarning`。代码仍继续计算，但不会隐式做色适应；它只是直接比较已经存储的 `C_max[L, h]`。

2. `L_values` / `hue_values` 网格不一致

   如果两个边界的亮度网格或 hue 网格不同，会抛出 `UserWarning`。代码会把 test boundary 插值到 reference boundary 的网格后再计算覆盖率。

严格报告中，建议使用相同白点和相同网格生成待比较边界。

注意：xy 覆盖率、Lab 体积覆盖率和 `projected_area()` 是不同指标，不能直接比较数值大小。

## Pointer 色域

Pointer 色域是经验物体色域，描述真实表面颜色的大致范围。它不是显示器基色色域，因此没有 `DisplayPrimaries`。

```python
from color.gamut import (
    is_within_pointer_gamut,
    pointer_gamut_boundary,
    pointer_gamut_xy_boundary,
)

pointer = pointer_gamut_boundary()
pointer_xy = pointer_gamut_xy_boundary()
inside = is_within_pointer_gamut([32.05, 41.31, 51.00])
```

Pointer 的 `GamutBoundary` 来自 `color.datasets.gamut_data.get_gamut_data("pointer")` 中的规则 `L* × hue` 数据：

```text
L*: 20, 30, ..., 90
hue: 0, 10, ..., 360
```

它可以用于：

```python
pointer.volume()
pointer.projected_ab()
lab_gamut_coverage(display_boundary, pointer)
```

但不能使用：

```python
pointer.primary_xy_hull()
```

因为 Pointer 不是显示基色凸包。

`pointer_gamut_xy_boundary()` 返回和 `colour.models.CCS_POINTER_GAMUT_BOUNDARY` 一致的 32 点 published Pointer xy 边界，并闭合首尾。它用于 CIE 1931 xy 图展示，不用于 Lab 体积判断。

`is_within_pointer_gamut(...)` 使用 Pointer 体积 mesh 判断输入 `XYZ(Y=100)` 是否位于 Pointer real-surface gamut 内。

## mesh 工具

`is_within_mesh_volume(XYZ, vertices_XYZ)` 是通用 mesh inside 判断工具。Pointer inside 判断就是基于它实现的。它要求 `vertices_XYZ` 是三维点云，并使用 `scipy.spatial.Delaunay.find_simplex(...)`。

## examples

`examples/gamut` 提供六个示例：

- `example_01_display_primary_gamut.py`：三基色 / 多基色 inside 判断和权重求解。
- `example_02_lch_boundary_metrics.py`：LCH 边界、切片面积和体积。
- `example_03_gamut_solids_3d.py`：Lab 三维色立体绘制。
- `example_04_projected_plane_and_rings.py`：平面投影、固定 L 切片和 gamut rings。
- `example_05_gamut_coverage.py`：xy 和 Lab 覆盖率矩阵。
- `example_06_pointer_gamut.py`：Pointer 色域、Pointer xy 边界和显示器覆盖率。
