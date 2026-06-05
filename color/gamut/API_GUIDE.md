# color.gamut API 使用指南

本文档按 `color.gamut.__all__` 覆盖顶层 API。这里写最小使用案例；
色域边界语义、Pointer/MacAdam 背景、xy/Lab 覆盖率细节和模块边界见
[`README_DETAILS.md`](README_DETAILS.md)。

`color.gamut` 处理已经处于线性 `XYZ(Y=100)` 体系中的颜色刺激。它不做 RGB
编码/解码、不做色适应、不做色貌模型转换，也不负责普通光谱积分。

## 顶层 API 总览

### 对象与显示基色

| API | 功能 |
| --- | --- |
| `DisplayPrimaries` | 显示器基色定义 |
| `GamutBoundary` | 规则 `L* x hue` Lab/LCHab 色域边界 |
| `is_within_primary_gamut` | 判断 XYZ 是否可由基色线性混合得到 |
| `solve_primary_weights` | 求一组可行基色权重 |
| `compute_LCH_gamut_boundary` | 计算显示基色色域的 `C_max[L, h]` 边界 |

### 汇总分析与覆盖率

| API | 功能 |
| --- | --- |
| `GamutAnalysis` | 全量分析结果对象 |
| `analyze_gamut` | 计算 xy 面积、Lab 体积和参考覆盖率 |
| `xy_gamut_coverage`, `xy_gamut_area` | 从 RGB 名称、`DisplayPrimaries` 或 primary XYZ 计算 xy 覆盖/面积 |
| `xy_gamut_coverage_from_xy`, `xy_gamut_area_from_xy` | 从 xy 点或 xy 边界计算覆盖/面积 |
| `lab_gamut_volume`, `lab_gamut_coverage` | Lab/LCHab 体积和体积覆盖率 |

### 参考色域

| API | 功能 |
| --- | --- |
| `macadam_limits`, `macadam_limits_published_xy_boundary`, `is_within_macadam_limits` | MacAdam optimal-colour limits |
| `pointer_gamut`, `pointer_gamut_published_xy_boundary`, `is_within_pointer_gamut` | Pointer real-surface gamut |

## Display Primaries

### `DisplayPrimaries`

用途：保存显示器基色 XYZ、名称和白点。

从 RGB 标准读取：

```python
from color.gamut import DisplayPrimaries

srgb = DisplayPrimaries.from_RGB_colourspace("sRGB")
print(srgb.primaries_XYZ)
print(srgb.whitepoint_XYZ)
```

手动创建三基色：

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

手动创建多基色：

```python
from color.gamut import DisplayPrimaries

rgbc = DisplayPrimaries(
    primaries_XYZ=[
        [41.24, 21.26, 1.93],
        [35.76, 71.52, 11.92],
        [18.05, 7.22, 95.05],
        [20.0, 35.0, 75.0],
    ],
    names=("R", "G", "B", "C"),
)
```

注意：`primaries_XYZ` 每一行是线性基色刺激，不是 xy 色品坐标。

## Primary Feasibility And Weights

### `is_within_primary_gamut(XYZ, primaries, method="auto", tolerance=...)`

用途：判断一个或一批 `XYZ` 是否位于基色线性混合凸体内。

三基色：

```python
from color.gamut import DisplayPrimaries, is_within_primary_gamut

srgb = DisplayPrimaries.from_RGB_colourspace("sRGB")
inside = is_within_primary_gamut([20.0, 30.0, 40.0], srgb)
```

批量判断：

```python
inside = is_within_primary_gamut(
    [[20.0, 30.0, 40.0], [200.0, 200.0, 200.0]],
    srgb,
)
```

多基色：

```python
inside = is_within_primary_gamut([30.0, 40.0, 50.0], rgbc)
```

注意：`method="auto"` 下，三基色用矩阵，多基色用凸包半空间。

### `solve_primary_weights(XYZ, primaries, method="auto", objective="min_sum")`

用途：求一组能复现目标 XYZ 的基色权重。

三基色唯一解：

```python
from color.gamut import solve_primary_weights

weights = solve_primary_weights([20.0, 30.0, 40.0], srgb)
```

多基色可行解：

```python
weights = solve_primary_weights([30.0, 40.0, 50.0], rgbc)
```

注意：多基色解通常不唯一。当前返回的是一组可行解，不代表最佳显示驱动策略。

## Gamut Boundary

### `compute_LCH_gamut_boundary(...)`

用途：把显示基色色域重采样为规则 `L* x hue` 的最大 `C*` 边界。

RGB 名称：

```python
from color.gamut import compute_LCH_gamut_boundary

boundary = compute_LCH_gamut_boundary(
    "sRGB",
    L_values=range(0, 101, 5),
    hue_values=range(0, 361, 5),
)
```

`DisplayPrimaries`：

```python
boundary = compute_LCH_gamut_boundary(srgb)
```

原始 primary XYZ rows：

```python
boundary = compute_LCH_gamut_boundary(srgb.primaries_XYZ)
```

注意：边界搜索使用 `Lab/LCHab`，默认白点来自 `DisplayPrimaries.whitepoint_XYZ`。

### `GamutBoundary`

用途：保存 `C_max[L, h]` 边界，并提供转换和统计方法。

```python
from color.gamut import compute_LCH_gamut_boundary, GamutBoundary

boundary: GamutBoundary = compute_LCH_gamut_boundary("Rec.2020")

LCH = boundary.to_LCHab()
Lab = boundary.to_Lab()
XYZ = boundary.to_XYZ()
xyY = boundary.to_xyY()
xy = boundary.xy_boundary()

slice_L50 = boundary.slice_L(50)
area_L50 = boundary.area_at_L(50)
volume = boundary.lab_volume()
xy_area = boundary.xy_area()
```

Lab 平面投影边界：

```python
ab = boundary.projected_ab_boundary()
projected_area = boundary.projected_ab_area()
rings, L_steps = boundary.gamut_rings([25, 50, 75, 100])
ring_area = boundary.ring_area()
```

注意：`projected_ab_boundary()` 只能解释为 Lab `a*b*` 平面包络，不要转成 xy 使用。

## xy Area And Coverage

### `xy_gamut_area(gamut)` / `xy_gamut_coverage(test, reference)`

用途：从 RGB 名称、`DisplayPrimaries` 或 primary XYZ rows 计算 xy 面积和覆盖率。

RGB 名称：

```python
from color.gamut import xy_gamut_area, xy_gamut_coverage

area = xy_gamut_area("sRGB")
coverage = xy_gamut_coverage("sRGB", "Rec.2020")
```

`DisplayPrimaries`：

```python
area = xy_gamut_area(srgb)
coverage = xy_gamut_coverage(srgb, DisplayPrimaries.from_RGB_colourspace("Rec.2020"))
```

primary XYZ rows：

```python
area = xy_gamut_area(srgb.primaries_XYZ)
coverage = xy_gamut_coverage(srgb.primaries_XYZ, rec2020.primaries_XYZ)
```

覆盖率方向：

```text
coverage(test, reference) = intersection(test, reference) / area(reference)
```

### `xy_gamut_area_from_xy(xy)` / `xy_gamut_coverage_from_xy(test_xy, reference_xy)`

用途：从已有 xy 点或 xy 边界计算面积和覆盖率。

三基色 xy 点：

```python
from color.gamut import xy_gamut_area_from_xy, xy_gamut_coverage_from_xy

srgb_xy = [
    [0.640, 0.330],
    [0.300, 0.600],
    [0.150, 0.060],
]
area = xy_gamut_area_from_xy(srgb_xy)
```

四基色 xy 点：

```python
rgbc_xy = [
    [0.640, 0.330],
    [0.300, 0.600],
    [0.150, 0.060],
    [0.220, 0.330],
]
area = xy_gamut_area_from_xy(rgbc_xy)
```

published boundary：

```python
from color.gamut import pointer_gamut_published_xy_boundary

coverage = xy_gamut_coverage_from_xy(
    srgb_xy,
    pointer_gamut_published_xy_boundary(),
)
```

注意：`*_from_xy` 会对输入点求凸包；点不需要排序或闭合。

## Lab Volume And Coverage

### `lab_gamut_volume(boundary)`

用途：计算 `GamutBoundary` 的 Lab/LCHab 体积。

```python
from color.gamut import compute_LCH_gamut_boundary, lab_gamut_volume

boundary = compute_LCH_gamut_boundary("sRGB")
volume = lab_gamut_volume(boundary)
```

等价对象方法：

```python
volume = boundary.lab_volume()
```

### `lab_gamut_coverage(test_boundary, reference_boundary)`

用途：计算方向性 Lab 体积覆盖率。

```python
from color.gamut import compute_LCH_gamut_boundary, lab_gamut_coverage

srgb = compute_LCH_gamut_boundary("sRGB")
rec2020 = compute_LCH_gamut_boundary("Rec.2020")

coverage = lab_gamut_coverage(srgb, rec2020)
```

注意：

- 白点色度不同会 warning，但继续计算，不自动色适应。
- 网格不同会 warning，并把 test boundary 插值到 reference grid。
- 单纯白点 `Y` 标度不同但色度相同，一般不会触发白点色度 warning。

## High-Level Analysis

### `GamutAnalysis`

用途：保存 `analyze_gamut(...)` 的结果。

字段包括：

```python
name
boundary
xy_area
xy_coverage_rec2020
xy_coverage_pointer
xy_coverage_macadam_d65
lab_volume
projected_ab_area
ring_area
volume_coverage_rec2020
volume_coverage_pointer
volume_coverage_macadam_d65
warnings
```

### `analyze_gamut(gamut, ...)`

用途：一次性计算常用面积、体积和参考覆盖率。

RGB 名称：

```python
from color.gamut import analyze_gamut

analysis = analyze_gamut("sRGB")
print(analysis.xy_area)
print(analysis.lab_volume)
print(analysis.volume_coverage_pointer)
```

`DisplayPrimaries`：

```python
analysis = analyze_gamut(srgb, name="sRGB from primaries")
```

已有 `GamutBoundary`：

```python
boundary = compute_LCH_gamut_boundary("Display P3")
analysis = analyze_gamut(boundary, name="Display P3")
```

自定义参考边界：

```python
reference = compute_LCH_gamut_boundary("Rec.2020")
analysis = analyze_gamut("sRGB", rec2020_boundary=reference)
```

注意：所有覆盖率都是“当前色域覆盖参考色域的比例”，不是双向相似度。

## Pointer Gamut

### `pointer_gamut()`

用途：返回 Pointer real-surface gamut 边界对象。

```python
from color.gamut import pointer_gamut

pointer = pointer_gamut()
print(pointer.lab_volume())
print(pointer.xy_boundary())
```

### `pointer_gamut_published_xy_boundary()`

用途：直接获取 published Pointer xy boundary。

```python
from color.gamut import pointer_gamut_published_xy_boundary

xy = pointer_gamut_published_xy_boundary()
```

注意：这和 `pointer_gamut().xy_boundary()` 是同一语义边界。

### `is_within_pointer_gamut(XYZ, tolerance=...)`

用途：判断 XYZ 是否位于 Pointer 色域内。

```python
from color.gamut import is_within_pointer_gamut

inside = is_within_pointer_gamut([32.05, 41.31, 51.00])
batch = is_within_pointer_gamut([[32.05, 41.31, 51.00], [200.0, 200.0, 200.0]])
```

## MacAdam Limits

### `macadam_limits(illuminant="D65", source="auto", ...)`

用途：返回 MacAdam optimal-colour limits 边界。

默认读取缓存 published 数据：

```python
from color.gamut import macadam_limits

d65 = macadam_limits("D65")
a = macadam_limits("A")
c = macadam_limits("C")
```

强制 published：

```python
d65 = macadam_limits("D65", source="published")
```

强制 computed：

```python
from color.spectra import SpectralShape

computed = macadam_limits(
    "D65",
    source="computed",
    shape=SpectralShape(400, 700, 5),
    L_values=range(0, 101, 10),
    hue_values=range(0, 361, 10),
)
```

注意：`source="auto"` 下，普通 `A/C/D65` 走缓存；自定义 CMFs、照明体或 shape 走 computed。

### `macadam_limits_published_xy_boundary(illuminant="D65")`

用途：获取 published MacAdam xy boundary。

```python
from color.gamut import macadam_limits_published_xy_boundary

xy = macadam_limits_published_xy_boundary("D65")
```

### `is_within_macadam_limits(XYZ, illuminant="D65", source="auto", ...)`

用途：判断 XYZ 是否位于 MacAdam limits 内。

```python
from color.gamut import is_within_macadam_limits

inside = is_within_macadam_limits([39.57, 51.0, 32.89], "D65")
batch = is_within_macadam_limits(
    [[39.57, 51.0, 32.89], [200.0, 200.0, 200.0]],
    "D65",
)
```

computed 判断：

```python
inside = is_within_macadam_limits(
    [39.57, 51.0, 32.89],
    "D65",
    source="computed",
    shape=SpectralShape(400, 700, 5),
)
```

## 常见串联

### 自定义 RGB 空间进入 gamut 分析

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

### Pointer / MacAdam / Display 的覆盖率比较

```python
from color.gamut import (
    compute_LCH_gamut_boundary,
    lab_gamut_coverage,
    macadam_limits,
    pointer_gamut,
)

rec2020 = compute_LCH_gamut_boundary("Rec.2020")
pointer = pointer_gamut()
macadam = macadam_limits("D65")

pointer_coverage = lab_gamut_coverage(rec2020, pointer)
macadam_coverage = lab_gamut_coverage(rec2020, macadam)
```
