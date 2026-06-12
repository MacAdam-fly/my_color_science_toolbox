# color.constants API 使用指南

本文档对应 `color.constants` 顶层公开常量。`constants` 是项目中重要标准数据的公共索引：白点 XYZ、RGB 标准矩阵、标准观察者转换矩阵和色适应矩阵。

英文快速入口见 [`README.md`](README.md)，中文设计说明见 [`README_DETAILS.md`](README_DETAILS.md)。

## API 总览

### 参考白点 / 照明体 XYZ

| API | 用途 |
| --- | --- |
| `A_XYZ` | CIE Illuminant A 白点 XYZ |
| `C_XYZ` | CIE Illuminant C 白点 XYZ |
| `D50_XYZ` | CIE D50 白点 XYZ |
| `D55_XYZ` | CIE D55 白点 XYZ |
| `D65_XYZ` | CIE D65 白点 XYZ |
| `E_XYZ` | 等能白点 XYZ |

### RGB 标准矩阵

| API | 用途 |
| --- | --- |
| `SRGB_TO_XYZ`, `XYZ_TO_SRGB` | linear sRGB 与 XYZ |
| `REC709_TO_XYZ`, `XYZ_TO_REC709` | linear Rec.709 与 XYZ |
| `REC2020_TO_XYZ`, `XYZ_TO_REC2020` | linear Rec.2020 与 XYZ |
| `ADOBE_RGB_TO_XYZ`, `XYZ_TO_ADOBE_RGB` | linear Adobe RGB (1998) 与 XYZ |
| `DISPLAY_P3_TO_XYZ`, `XYZ_TO_DISPLAY_P3` | linear Display P3 与 XYZ |
| `DCIP3_TO_XYZ`, `XYZ_TO_DCIP3` | linear DCI-P3 与 XYZ |
| `NTSC_1953_TO_XYZ`, `XYZ_TO_NTSC_1953` | linear NTSC (1953) 与 XYZ |

### RGB 标准定义表

| API | 用途 |
| --- | --- |
| `RGB_COLOURSPACE_DEFINITIONS` | 当前 canonical RGB 标准定义表 |
| `RGB_GAMUT_METADATA` | 向后兼容别名，指向 RGB 定义表 |
| `COMMON_GAMUTS` | 向后兼容矩阵索引 |

### 标准观察者 LMS/XYZ 矩阵

| API | 用途 |
| --- | --- |
| `LMS_2_DEGREE_TO_XYZ_2_DEGREE` | CIE 2006 2° LMS -> XYZ |
| `XYZ_2_DEGREE_TO_LMS_2_DEGREE` | CIE 2006 2° XYZ -> LMS |
| `LMS_10_DEGREE_TO_XYZ_10_DEGREE` | CIE 2006 10° LMS -> XYZ |
| `XYZ_10_DEGREE_TO_LMS_10_DEGREE` | CIE 2006 10° XYZ -> LMS |

### 色适应矩阵

| API | 用途 |
| --- | --- |
| `CAT_VON_KRIES` | Von Kries 色适应变换矩阵 |
| `CAT_BRADFORD` | Bradford 色适应变换矩阵 |
| `CAT_CAT02` | CAT02 色适应变换矩阵 |
| `CAT_CAT16` | CAT16 色适应变换矩阵 |
| `CHROMATIC_ADAPTATION_TRANSFORMS` | 支持的色适应矩阵索引 |

## 基本约定

- 白点 XYZ 使用项目统一的 `Y=100` 标度。
- RGB 矩阵是 linear RGB 与 `Y=100` XYZ 之间的矩阵。
- RGB transfer function 不在矩阵常量里执行；编码/解码由 `color.spaces.rgb` 处理。
- 常量尽量只读；不要在调用方原地修改。
- `constants` 提供标准数据索引，不负责执行转换算法。

## `A_XYZ` / `C_XYZ` / `D50_XYZ` / `D55_XYZ` / `D65_XYZ` / `E_XYZ`

参考白点 / 照明体 XYZ 常量，均为 `Y=100` 标度。

```python
from color.constants import A_XYZ, D50_XYZ, D65_XYZ

print(D65_XYZ)  # [95.047, 100.0, 108.883]
```

### 用作 Lab/Luv 白点

```python
from color.constants import D50_XYZ
from color.spaces import XYZ_to_Lab

Lab = XYZ_to_Lab([50.0, 40.0, 30.0], whitepoint_XYZ=D50_XYZ)
```

### 用作色适应源/目标白点

```python
from color.adaptation import chromatic_adaptation_XYZ
from color.constants import D50_XYZ, D65_XYZ

XYZ_D65 = chromatic_adaptation_XYZ(
    [50.0, 40.0, 30.0],
    source_white_XYZ=D50_XYZ,
    target_white_XYZ=D65_XYZ,
    transform="Bradford",
)
```

## RGB 矩阵常量

RGB 矩阵常量用于 linear RGB 与 `Y=100` XYZ 的直接矩阵关系。

### sRGB

```python
import numpy as np
from color.constants import SRGB_TO_XYZ, XYZ_TO_SRGB

linear_rgb = np.array([1.0, 1.0, 1.0])
XYZ = SRGB_TO_XYZ @ linear_rgb
rgb_roundtrip = XYZ_TO_SRGB @ XYZ
```

注意：这里的 `linear_rgb` 不是 encoded sRGB。encoded RGB 的解码/编码应使用 `color.spaces.rgb`。

### Rec.2020

```python
import numpy as np
from color.constants import REC2020_TO_XYZ, XYZ_TO_REC2020

linear_rec2020 = np.array([0.4, 0.5, 0.6])
XYZ = REC2020_TO_XYZ @ linear_rec2020
linear_rec2020_back = XYZ_TO_REC2020 @ XYZ
```

### Display P3 / DCI-P3

```python
from color.constants import DISPLAY_P3_TO_XYZ, DCIP3_TO_XYZ

display_p3_white = DISPLAY_P3_TO_XYZ @ [1.0, 1.0, 1.0]
dci_p3_white = DCIP3_TO_XYZ @ [1.0, 1.0, 1.0]
```

Display P3 和 DCI-P3 基色相近，但白点和 transfer 语义不同，因此矩阵也不同。

### Adobe RGB / Rec.709 / NTSC 1953

```python
from color.constants import ADOBE_RGB_TO_XYZ, NTSC_1953_TO_XYZ, REC709_TO_XYZ

adobe_white = ADOBE_RGB_TO_XYZ @ [1.0, 1.0, 1.0]
rec709_white = REC709_TO_XYZ @ [1.0, 1.0, 1.0]
ntsc_white = NTSC_1953_TO_XYZ @ [1.0, 1.0, 1.0]
```

## `RGB_COLOURSPACE_DEFINITIONS`

RGB 标准定义表，供 `color.spaces.rgb` 构造标准 `RGBColorSpace` 使用。

```python
from color.constants import RGB_COLOURSPACE_DEFINITIONS

srgb = RGB_COLOURSPACE_DEFINITIONS["sRGB"]

print(srgb["name"])
print(srgb["aliases"])
print(srgb["primaries"])
print(srgb["white_xy"])
print(srgb["transfer"])
print(srgb["matrix_RGB_to_XYZ"])
```

每个定义包含：

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

## `RGB_GAMUT_METADATA`

向后兼容别名，当前指向 `RGB_COLOURSPACE_DEFINITIONS`。

```python
from color.constants import RGB_COLOURSPACE_DEFINITIONS, RGB_GAMUT_METADATA

print(RGB_GAMUT_METADATA is RGB_COLOURSPACE_DEFINITIONS)  # True
```

新代码应优先使用 `RGB_COLOURSPACE_DEFINITIONS`。

## `COMMON_GAMUTS`

向后兼容矩阵索引，提供旧风格的 `to_xyz/from_xyz` 访问。

```python
from color.constants import COMMON_GAMUTS

srgb_matrices = COMMON_GAMUTS["sRGB"]
XYZ = srgb_matrices["to_xyz"] @ [1.0, 1.0, 1.0]
```

新代码通常应使用 `color.spaces.rgb` 或 `RGB_COLOURSPACE_DEFINITIONS`。

## 标准观察者 LMS/XYZ 矩阵

这些矩阵用于 CIE 2006 标准观察者 LMS 与 XYZ 之间的直接转换。

### 2° 观察者

```python
from color.constants import (
    LMS_2_DEGREE_TO_XYZ_2_DEGREE,
    XYZ_2_DEGREE_TO_LMS_2_DEGREE,
)

LMS = [10.0, 8.0, 3.0]
XYZ = LMS_2_DEGREE_TO_XYZ_2_DEGREE @ LMS
LMS_back = XYZ_2_DEGREE_TO_LMS_2_DEGREE @ XYZ
```

### 10° 观察者

```python
from color.constants import (
    LMS_10_DEGREE_TO_XYZ_10_DEGREE,
    XYZ_10_DEGREE_TO_LMS_10_DEGREE,
)

XYZ = [20.0, 30.0, 10.0]
LMS = XYZ_10_DEGREE_TO_LMS_10_DEGREE @ XYZ
XYZ_back = LMS_10_DEGREE_TO_XYZ_10_DEGREE @ LMS
```

如果你只需要公共转换函数，优先使用 `color.colorimetry` 中的 LMS/XYZ 转换入口；直接矩阵更适合底层计算或检查。

## 色适应矩阵常量

这些矩阵是 Von Kries 类色适应算法使用的 cone-response transform 矩阵。

### 单个矩阵

```python
from color.constants import CAT_BRADFORD, CAT_CAT16

print(CAT_BRADFORD.shape)  # (3, 3)
print(CAT_CAT16.shape)     # (3, 3)
```

### 通过索引读取

```python
from color.constants import CHROMATIC_ADAPTATION_TRANSFORMS

matrix = CHROMATIC_ADAPTATION_TRANSFORMS["Bradford"]
```

实际色适应推荐使用 `color.adaptation`：

```python
from color.adaptation import matrix_chromatic_adaptation_von_kries
from color.constants import D50_XYZ, D65_XYZ

M = matrix_chromatic_adaptation_von_kries(D50_XYZ, D65_XYZ, transform="Bradford")
```
