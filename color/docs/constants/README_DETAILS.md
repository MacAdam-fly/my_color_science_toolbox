# color.constants 详细说明

## AI Usage Notes

- Use this module when a workflow needs shared standard constants such as whitepoints, matrices, display standards, or named reference values.
- Do not use this module for computed data loading, generated spectra, or algorithm execution.
- Key assumptions: constants are shared reference values; changing them affects many modules conceptually, so prefer explicit local parameters for experiments.
- Common mistakes: treating constants as mutable configuration; assuming all standard datasets live here instead of `datasets`; using constants without checking scale conventions.
- Related modules: use `datasets` for static tabular data, `spaces` for RGB/color-space definitions, and `adaptation` for transform application.

`color.constants` 是项目中重要标准常量的公共索引。它不执行算法，只保存被多个模块共享的标准数据，例如参考白点、RGB 标准矩阵、LMS/XYZ 转换矩阵和色适应矩阵。

逐项顶层 API 的最小使用案例见 [`API_GUIDE.md`](API_GUIDE.md)。本文档保留设计边界、文件结构和常量语义说明。

## 模块定位

```text
color.constants
  -> 标准常量和跨模块共享数据

color.spaces / color.colorimetry / color.adaptation / color.appearance / color.gamut
  -> 使用这些常量执行具体计算
```

设计原则：

- 标准数据集中保存，避免多个模块各自复制。
- 常量文件按语义分组。
- 大多数矩阵设为只读，避免调用方原地修改。
- `constants` 不依赖上层科学模块，尽量保持底层稳定。

## 文件结构

| 文件 | 职责 |
| --- | --- |
| `illuminants_XYZ.py` | 参考白点 / 照明体 XYZ 常量 |
| `display_standards.py` | RGB 显示/成像标准矩阵和定义表 |
| `standard_observer_matrices.py` | CIE 2006 LMS/XYZ 观察者转换矩阵 |
| `adaptation_matrices.py` | Von Kries 类色适应矩阵 |

## XYZ 标度

当前常量使用项目统一的 `Y=100` XYZ 标度：

```python
from color.constants import D65_XYZ

print(D65_XYZ)
# [95.047, 100.0, 108.883]
```

RGB 矩阵也对应 `Y=100` XYZ：

```python
from color.constants import SRGB_TO_XYZ

white = SRGB_TO_XYZ @ [1.0, 1.0, 1.0]
# 接近 D65_XYZ
```

这和 `color.spaces`、`color.colorimetry`、`color.appearance` 当前参考域保持一致。

## 参考白点 / 照明体 XYZ

顶层导出：

```text
A_XYZ
C_XYZ
D50_XYZ
D55_XYZ
D65_XYZ
E_XYZ
```

这些常量用于：

- Lab/Luv/UVW 等参考白点参数。
- 色适应源/目标白点。
- CIECAM02/CIECAM16 的 `XYZ_w` 默认或示例。
- gamut / MacAdam / Pointer 等 Lab 参考域。

注意：这些是白点三刺激值，不是光谱。需要完整照明体 SPD 时，应使用 `datasets` 或 `generators`。

## RGB 标准矩阵和定义

`display_standards.py` 保存：

- 常见 RGB 标准的 linear RGB -> XYZ 矩阵。
- XYZ -> linear RGB 逆矩阵。
- `RGB_COLOURSPACE_DEFINITIONS` 标准定义表。

第一批标准包括：

```text
sRGB
Rec.709
Display P3
DCI-P3
Rec.2020
Adobe RGB (1998)
ProPhoto RGB
NTSC (1953)
```

RGB 定义表字段：

```text
name
aliases
primaries
white_xy
white_name
transfer
matrix_RGB_to_XYZ
matrix_XYZ_to_RGB
reference
```

`color.spaces.rgb` 使用这张表构建标准 `RGBColorSpace` 注册表。自定义 RGB 空间不写入 `constants`，而是在 `color.spaces.rgb` 中通过 constructor 和 registry 管理。

## RGB 矩阵和 transfer 的边界

矩阵常量只表示 linear RGB 与 XYZ 的线性关系。

它不负责：

- sRGB / BT.709 / BT.2020 编码解码。
- gamma 或三通道 gamma。
- PQ / HLG。
- RGB 到 RGB 的色适应策略。

这些由 `color.spaces.rgb` 处理。

## 兼容索引

当前保留两个兼容入口：

```text
RGB_GAMUT_METADATA
COMMON_GAMUTS
```

`RGB_GAMUT_METADATA` 现在只是 `RGB_COLOURSPACE_DEFINITIONS` 的别名。新代码应优先使用 `RGB_COLOURSPACE_DEFINITIONS` 或 `color.spaces.rgb`。

`COMMON_GAMUTS` 是旧式矩阵索引，保留是为了减少旧代码断裂。新代码通常不需要它。

## 标准观察者矩阵

顶层导出：

```text
LMS_2_DEGREE_TO_XYZ_2_DEGREE
XYZ_2_DEGREE_TO_LMS_2_DEGREE
LMS_10_DEGREE_TO_XYZ_10_DEGREE
XYZ_10_DEGREE_TO_LMS_10_DEGREE
```

这些矩阵用于 CIE 2006 标准观察者响应值和 XYZ 之间的直接转换。

如果只是日常转换，优先使用 `color.colorimetry` 中的函数；如果需要检查矩阵、写底层计算或做验证，可以直接使用这些常量。

## 色适应矩阵

顶层导出：

```text
CAT_VON_KRIES
CAT_BRADFORD
CAT_CAT02
CAT_CAT16
CHROMATIC_ADAPTATION_TRANSFORMS
```

这些是 Von Kries 类色适应算法的 cone-response transform 矩阵。

实际色适应应使用：

```python
from color.adaptation import chromatic_adaptation_XYZ
```

而不是手动拼接矩阵，除非你正在实现或验证底层算法。

## 为什么不把常量放回各自模块

之前讨论过两种方案：

```text
方案 A：常量放各自模块，constants 只做索引。
方案 B：重要标准常量直接放 constants。
```

目前采用方案 B。原因是：

- 使用者通常希望在一个地方快速找到重要标准常量。
- 直接索引其他模块容易制造导入循环。
- `constants` 作为底层模块更适合被 `spaces`、`adaptation`、`appearance` 等模块共同引用。

因此：

- `constants` 保存标准数据。
- 上层模块保存算法和对象行为。

## 新增常量的建议

新增常量前应先判断：

1. 是否是标准数据或多个模块共享的数据。
2. 是否需要长期稳定公开。
3. 是否会导致导入循环。
4. 是否只是某个模块内部算法的临时系数。

如果只是某个算法内部使用的局部系数，应优先放在对应模块内部，而不是提升到 `constants`。
