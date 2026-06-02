# gamut 详细说明

`color.gamut` 用来处理色域可达性、色域边界、覆盖率和常见参考物体色域。它关注的是已经处于线性 `XYZ(Y=100)` 体系中的颜色刺激，不负责 RGB 编码/解码、色适应、色貌观察条件或普通光谱积分。

当前模块可以分成六块：

1. 显示器基色定义与可达性判断。
2. `Lab/LCHab` 色域边界 `GamutBoundary`。
3. `xy` 面积覆盖率和 `Lab` 体积覆盖率。
4. Pointer real-surface gamut。
5. MacAdam optimal-colour limits。
6. 汇总分析入口 `analyze_gamut(...)`。

## 模块边界

本模块统一使用项目约定的 `XYZ(Y=100)` 标度。这里的 `XYZ` 是线性三刺激值，不是 encoded RGB。

`color.gamut` 不做以下事情：

- 不做 RGB transfer function。
- 不做色适应。
- 不做显示器校准和驱动策略优化。
- 不做色貌模型转换。
- 不做普通颜色的光谱积分。

如果需要从 sRGB、Display P3 或 Rec.2020 等 RGB 标准获得基色，模块会读取 `color.spaces.rgb` 中已经注册好的线性 `RGB -> XYZ` 矩阵。

## DisplayPrimaries

`DisplayPrimaries` 是显示器基色定义对象。

```python
from color.gamut import DisplayPrimaries

srgb = DisplayPrimaries.from_RGB_colourspace("sRGB")
```

核心字段：

- `primaries_XYZ`：shape 为 `(n, 3)`，每一行是一个基色的 `XYZ(Y=100)` 刺激值。
- `names`：基色名称，默认是 `P0, P1, ...`。
- `whitepoint_XYZ`：显示白点，默认是所有基色满输出之和。

注意：`primaries_XYZ` 不是 `xy` 色品坐标。它保留了亮度信息，因此可以用于三维可达性判断。

### 已注册自定义 RGB 空间

如果用户在 `color.spaces.rgb` 中创建并注册了自定义三基色 RGB 空间，`gamut` 模块可以像处理标准 RGB 空间一样读取它的线性 `RGB -> XYZ` 矩阵：

```python
from color.gamut import DisplayPrimaries, analyze_gamut, compute_LCH_gamut_boundary
from color.spaces import RGB_colourspace_from_primaries_xy, register_RGB_colourspace

custom = RGB_colourspace_from_primaries_xy(
    "Custom Display",
    primaries_xy=[[0.690, 0.310], [0.210, 0.720], [0.145, 0.055]],
    whitepoint_xy=[0.3127, 0.3290],
    transfer=("gamma", (2.2, 2.3, 2.1)),
)
register_RGB_colourspace(custom)

primaries = DisplayPrimaries.from_RGB_colourspace("Custom Display")
boundary = compute_LCH_gamut_boundary("Custom Display")
analysis = analyze_gamut("Custom Display")
```

这里 `gamut` 使用的是 RGB 空间的线性基色 XYZ 刺激。RGB 编码/解码、gamma、图像数值是否 clip 都不是色域边界计算本身的一部分。

## 基色可达性

点级可达性使用：

```python
from color.gamut import is_within_primary_gamut

inside = is_within_primary_gamut([20, 30, 40], srgb)
```

默认 `method="auto"`：

- 三基色：使用矩阵求解唯一线性权重。
- 四基色及以上：构造所有 `0/1` 基色开关组合形成的凸包，用半空间方程批量判断 inside。

多基色 inside 判断回答的是：

```text
这个 XYZ 是否位于多基色线性混合可以形成的三维凸体内？
```

它不回答“实际显示器应该用哪一组最佳驱动值”。

## 基色权重

权重求解使用：

```python
from color.gamut import solve_primary_weights

weights = solve_primary_weights([20, 30, 40], srgb)
```

三基色情况下，解是唯一的。多基色情况下，解通常不唯一；当前版本使用 `scipy.optimize.linprog` 返回一组可行解，默认目标是 `min_sum`。

这部分暂时只作为可行性工具。多基色显示器的真实驱动策略可能还需要考虑能耗、亮度分配、通道限制、视觉误差、设备标定，同色异谱等因素，当前模块不对这些策略作承诺。

## LCHab 色域边界

显示色域的三维边界可以重采样为规则的 `L* x hue` 网格：

```python
from color.gamut import compute_LCH_gamut_boundary

boundary = compute_LCH_gamut_boundary(
    "Rec.2020",
    L_values=range(0, 101, 5),
    hue_values=range(0, 361, 5),
    C_upper=260,
)
```

`GamutBoundary.C_max` 的含义是：

```text
C_max[L_index, hue_index] = 该 L* 和 hue 方向上的最大可达 C*
```

计算方法是二分搜索：固定 `L*` 和 hue，沿 `C*` 方向搜索最大可显示边界。

常用转换：

```python
boundary.to_LCHab()
boundary.to_Lab()
boundary.to_XYZ()
boundary.to_xyY()
boundary.slice_L(50)
```

常用统计：

```python
boundary.area_at_L(50)     # L=50平面的面积
boundary.areas()           # 所有传入L_values对应的面积，直接用于lab_volume()的计算
boundary.lab_volume()      # 得到Lab空间的色域体积
boundary.xy_area()         # 得到xy平面的色域面积
boundary.gamut_rings([25, 50, 75, 100])
```

`lab_volume()` 是用各个 `L*` 切片面积沿亮度轴积分得到的近似 `Lab` 体积。它依赖 `L_values` 和 `hue_values` 的采样密度。

`to_xyY()` 会先调用 `to_XYZ()`，再转换为 `[x, y, Y]`。黑点或零 `XYZ` 点会使用当前 `whitepoint_XYZ` 反推的 xy 作为 fallback，避免可视化时把黑点错误画到 `(0, 0)`。它适合绘制和检查亮度-色品关系；真正的 xy 平面边界仍然应使用 `xy_boundary()`。

## xy_boundary 与 Lab 投影边界

这是当前 `gamut` 模块里最容易混淆的部分。

### xy_boundary()

如果需要 CIE 1931 `xy` 平面边界，使用：

```python
xy = boundary.xy_boundary()
```

`xy_boundary()` 的语义是“这个色域对象在 xy 平面上最合适的边界”。

具体规则：

1. 显示基色色域：返回基色 `XYZ -> xy` 后的凸包。
2. Pointer：返回 published 32 点 Pointer xy boundary。
3. MacAdam cached：返回缓存表中正亮度点的 xy 凸包。
4. computed MacAdam：返回计算得到的 optimal-colour 顶点在 xy 平面的凸包。
5. 普通无特化 `GamutBoundary`：退回到 `to_XYZ()` 采样点投影到 xy 后的凸包。

对于显示器色域，`xy_boundary()` 本质上就是基色 xy hull。对于 Pointer 和 MacAdam，它不是从 `projected_ab_boundary()` 转换来的。

### projected_ab_boundary()

如果需要 Lab `a*b*` 平面投影边界，使用：

```python
ab = boundary.projected_ab_boundary()
area = boundary.projected_ab_area()
```

这类 `projected_*_boundary()` 函数做的是：

```text
对每个 hue，在所有 L* 切面里取最大 C*
```

它适合比较 Lab 平面色域，但不能再转换到 xy 并解释为 xy 色域边界。原因是 `Lab/LCHab -> XYZ -> xy` 是非线性映射，而且 xy 会丢失亮度；直接把 Lab 投影边界转成 xy 会产生错误形状。

## xy 面积覆盖率

xy 覆盖率比较的是 CIE 1931 xy 平面的二维面积。

定义：

```text
coverage(test, reference) = intersection_area(test, reference) / area(reference)
```

它是单向的：

```python
xy_gamut_coverage("sRGB", "Rec.2020")
xy_gamut_coverage("Rec.2020", "sRGB")
```

这两个结果通常不同。

### 输入是 RGB 名称、DisplayPrimaries 或 primary XYZ

```python
from color.gamut import DisplayPrimaries, xy_gamut_coverage

srgb = DisplayPrimaries.from_RGB_colourspace("sRGB")
rec2020 = DisplayPrimaries.from_RGB_colourspace("Rec.2020")

coverage_1 = xy_gamut_coverage("sRGB", "Rec.2020")
coverage_2 = xy_gamut_coverage(srgb, rec2020)
coverage_3 = xy_gamut_coverage(srgb.primaries_XYZ, rec2020.primaries_XYZ)
```

这一路径会先把 primary `XYZ` 转为 `xy`，再求凸包。

### 输入已经是 xy 点或 xy 边界

```python
from color.gamut import pointer_gamut_published_xy_boundary, xy_gamut_coverage_from_xy
from color.gamut.coverage import xy_gamut_area_from_xy

rec2020_xy = [
    [0.708, 0.292],
    [0.170, 0.797],
    [0.131, 0.046],
]
pointer_xy = pointer_gamut_published_xy_boundary()

area = xy_gamut_area_from_xy(pointer_xy)
coverage = xy_gamut_coverage_from_xy(rec2020_xy, pointer_xy)
```

`*_from_xy` 函数会对输入 xy 点求凸包。三基色、四基色和更多基色的 xy 点都可以直接传入。点不需要预排序，也不需要首尾闭合。

如果未来要比较凹多边形边界，需要单独设计 polygon API；当前 xy coverage API 使用的是凸包语义。

## Lab 体积覆盖率

Lab 覆盖率比较的是两个 `GamutBoundary` 的三维 `C_max[L, h]` 体积。

```python
from color.gamut import compute_LCH_gamut_boundary, lab_gamut_coverage

srgb_boundary = compute_LCH_gamut_boundary("sRGB")
rec2020_boundary = compute_LCH_gamut_boundary("Rec.2020")

coverage = lab_gamut_coverage(srgb_boundary, rec2020_boundary)
```

定义：

```text
coverage(test, reference) = overlap_volume(test, reference) / volume(reference)
```

`lab_gamut_coverage(...)` 只接受 `GamutBoundary`。这样可以明确比较时使用的白点、`L_values` 网格、`hue_values` 网格和边界搜索参数。

两个 warning 需要注意：

1. 白点色度不同。
   函数会发出 `UserWarning`，但继续计算。它不会自动做色适应，只会直接比较两个已经存在的 `C_max` 边界。
   如果两个边界只是白点 `Y` 标度不同，例如 `D65_XYZ` 与 `2 * D65_XYZ`，不会触发这个 warning。只要每个边界内部的 `primaries_XYZ` 和 `whitepoint_XYZ` 同尺度，Lab 边界由 `XYZ / XYZn` 比值决定，单纯整体亮度标度不会改变体积和覆盖率。

2. `L_values` 或 `hue_values` 网格不同。
   函数会发出 `UserWarning`，并把 test boundary 插值到 reference boundary 的网格上再计算。

严谨比较时，建议使用相同白点色度和相同网格生成待比较边界。`Y=100` 是项目默认约定，但 Lab 覆盖率本身要求的是每个边界内部尺度自洽，而不是两个边界的白点 `Y` 数值必须完全相等。

## GamutAnalysis

`analyze_gamut(...)` 是全量分析入口，用来把常用指标集中到一个结果对象中。

```python
from color.gamut import analyze_gamut

analysis = analyze_gamut("sRGB")

analysis.xy_area
analysis.xy_coverage_rec2020
analysis.xy_coverage_pointer
analysis.xy_coverage_macadam_d65

analysis.lab_volume
analysis.projected_ab_area
analysis.ring_area
analysis.volume_coverage_rec2020
analysis.volume_coverage_pointer
analysis.volume_coverage_macadam_d65
analysis.warnings
```

输入可以是：

```python
analyze_gamut("sRGB")
analyze_gamut(DisplayPrimaries(...))
analyze_gamut(existing_boundary)
```

如果输入是 RGB 名称或 `DisplayPrimaries`，函数会先调用 `compute_LCH_gamut_boundary(...)`。如果输入已经是 `GamutBoundary`，则直接分析这个对象，不重复构造。

当前固定参考体系：

- Rec.2020：显示色域上限参考。
- Pointer：真实物体表面颜色参考。
- D65 MacAdam limits：D65 下理论物体色极限参考。

所有覆盖率都是单向：

```text
coverage(current, reference) = 当前色域覆盖参考色域的比例
```

第一版不计算 `xy_coverage_visible_locus`，也不计算马蹄形光谱轨迹覆盖率。MacAdam D65 xy boundary 和 CIE 1931 visible locus 不是同一个对象。

`analyze_gamut(...)` 不做自动色适应。底层 `lab_gamut_coverage(...)` 发出的白点或网格 warning 会同步记录到：

```python
analysis.warnings
```

## Pointer 色域

Pointer gamut 描述真实表面颜色的大致经验范围，不是显示器基色色域。

```python
from color.gamut import (
    is_within_pointer_gamut,
    pointer_gamut,
    pointer_gamut_published_xy_boundary,
)

pointer = pointer_gamut()
pointer_xy = pointer_gamut_published_xy_boundary()
inside = is_within_pointer_gamut([32.05, 41.31, 51.00])
```

`pointer_gamut()` 返回 `PointerGamutBoundary`，其 `C_max` 来自 `color.datasets.gamut_data.get_gamut_data("pointer")` 中的规则 `L* x hue` 表。

Pointer 的 `xy_boundary()` 与 `pointer_gamut_published_xy_boundary()` 返回同一组 published 32 点 xy 边界。这个边界用于 xy 图和 xy 面积覆盖率；不是从 Lab 边界投影得到的。

Pointer 可用于：

```python
pointer.lab_volume()
pointer.projected_ab_boundary()
lab_gamut_coverage(display_boundary, pointer)
is_within_pointer_gamut(XYZ)
```

`is_within_pointer_gamut(...)` 基于 Pointer 体积 mesh 判断输入 `XYZ(Y=100)` 是否位于 Pointer 色域内。

## MacAdam limits

MacAdam limits 描述给定照明体下 optimal colour stimuli 的理论物体色边界。

普通用户只需要使用统一入口：

```python
from color.gamut import (
    is_within_macadam_limits,
    macadam_limits,
    macadam_limits_published_xy_boundary,
)

boundary = macadam_limits("D65")
xy = macadam_limits_published_xy_boundary("D65")
inside = is_within_macadam_limits([39.57, 51.0, 32.89], "A")
```

### source 分发

`macadam_limits(...)` 和 `is_within_macadam_limits(...)` 都支持：

```python
source="auto"       # 默认
source="published"  # 强制使用缓存 A/C/D65 数据
source="computed"   # 强制实时计算
```

默认 `source="auto"`：

- `illuminant="A" | "C" | "D65"` 且没有传入 `cmfs` 或 `shape` 时，使用缓存数据。
- 传入自定义 CMFs、照明体对象或 spectral shape 时，使用 computed 路线。

`source="published"` 只接受 `A / C / D65`，不接受 `cmfs` 或 `shape`。

### 缓存数据

缓存数据位于：

```text
color/data/gamut_data/MacAdamLimits_A.csv
color/data/gamut_data/MacAdamLimits_C.csv
color/data/gamut_data/MacAdamLimits_D65.csv
```

字段包括：

```text
x, y, Y, X, Z, L, a, b, C, h
```

其中 `x/y/Y` 是 xyY 语义，`X/Z` 由 xyY 派生，`L/a/b/C/h` 用对应照明体白点派生。数据使用项目统一 `Y=100` 标度。

### computed 路线

computed MacAdam 使用 `docs/macadam_limits.md` 中描述的亮度因子法，不再使用旧的 0/1 pulse-wave 枚举。

核心链路：

```text
L* -> R = Y / Yn
   -> 求 Type 1 / Type 2 矩形反射谱
   -> 在 illuminant × CMFs 空间积分得到 XYZ
   -> 转换到 Lab/LCHab
   -> 重采样为规则 C_max[L, h]
```

这里 `R` 由 `L*` 唯一决定，不是额外自由参数。

示例：

```python
from color.gamut import macadam_limits
from color.spectra import SpectralShape

boundary = macadam_limits(
    "D65",
    source="computed",
    shape=SpectralShape(400, 700, 5),
    L_values=range(0, 101, 10),
    hue_values=range(0, 361, 10),
)
```

高级接口仍保留在 `color.gamut.macadam` 子包中：

```python
from color.gamut.macadam import (
    computed_macadam_limits,
    computed_macadam_limits_data,
    computed_macadam_limits_XYZ,
)
```

这些接口用于开发、数据再生成和研究，不作为 `color.gamut` 顶层常用 API。

当前 computed 默认值以代码为准：

- CMFs：`cie1931_xyz_1nm`
- illuminant：`D65`
- spectral shape：`SpectralShape(400, 700, 2)`
- XYZ 标度：`Y=100`

## mesh 工具

`is_within_mesh_volume(XYZ, vertices_XYZ)` 位于 `color.gamut.mesh`。它是底层体积 inside 判断工具，基于 `scipy.spatial.Delaunay.find_simplex(...)`。

Pointer inside 判断和部分 MacAdam 内部逻辑会用到 mesh 或凸包工具，但该函数不从 `color.gamut` 顶层导出。

## examples

`examples/gamut` 目前包含十一个示例：

- `example_01_display_primary_gamut.py`：三基色/多基色 inside 判断和权重求解。
- `example_02_lch_boundary_metrics.py`：LCH 边界、切片面积、体积和投影面积。
- `example_03_gamut_solids_3d.py`：Lab 三维色立体。
- `example_04_projected_plane_and_rings.py`：xy、LCH 极坐标、Lab 平面、gamut rings。
- `example_05_gamut_coverage.py`：xy 和 Lab 覆盖率矩阵。
- `example_06_pointer_gamut.py`：Pointer 色域、Pointer xy boundary 和显示器覆盖率。
- `example_07_macadam_limits.py`：A/C/D65 MacAdam limits 与 Pointer/显示色域比较。
- `example_08_computed_macadam_limits.py`：computed MacAdam 与缓存数据对比。
- `example_09_gamut_analysis.py`：`analyze_gamut(...)` 汇总分析。
- `example_10_macadam_rgbc_solids.py`：D65 MacAdam limits 与 RGBC 显示色域在 xyY 和 Lab 中的三维形状比较。
- `example_11_custom_rgb_colourspace_gamut.py`：自定义三基色 RGB 空间的创建、注册、转换和 gamut analysis。

## 当前未覆盖内容

当前 `gamut` 模块还没有实现：

- 多基色真实驱动策略优化。
- 非凸 xy 多边形覆盖率。
