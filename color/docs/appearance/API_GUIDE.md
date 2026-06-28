# color.appearance API 使用指南

本文档按 `color.appearance.__all__` 覆盖顶层 API。这里写最小使用案例；
各色貌模型的公式、参考域和模型差异见 [`README_DETAILS.md`](README_DETAILS.md)。

`color.appearance` 只实现色貌模型本体：

```text
XYZ -> appearance correlates -> XYZ
```

CAM02-UCS / CAM16-UCS 等均匀颜色空间属于 `color.spaces`，不是本模块。

## 顶层 API 总览

### CIECAM02

| API | 功能 |
| --- | --- |
| `InductionFactors_CIECAM02` | CIECAM02 surround induction factors |
| `VIEWING_CONDITIONS_CIECAM02` | `Average` / `Dim` / `Dark` surround 预设 |
| `CIECAM02ViewingConditions` | 完整 CIECAM02 观察条件 |
| `CIECAM02Specification` | CIECAM02 外貌相关量容器 |
| `XYZ_to_CIECAM02` | CIECAM02 正向模型 |
| `CIECAM02_to_XYZ` | CIECAM02 反向模型 |

### CIECAM16

| API | 功能 |
| --- | --- |
| `InductionFactors_CIECAM16` | CIECAM16 surround induction factors |
| `VIEWING_CONDITIONS_CIECAM16` | `Average` / `Dim` / `Dark` surround 预设 |
| `CIECAM16ViewingConditions` | 完整 CIECAM16 观察条件 |
| `CIECAM16Specification` | CIECAM16 外貌相关量容器 |
| `XYZ_to_CIECAM16` | CIECAM16 正向模型 |
| `CIECAM16_to_XYZ` | CIECAM16 反向模型 |

### Hellwig2022

| API | 功能 |
| --- | --- |
| `InductionFactors_Hellwig2022` | Hellwig2022 surround induction factors |
| `VIEWING_CONDITIONS_HELLWIG2022` | `Average` / `Dim` / `Dark` surround 预设 |
| `Hellwig2022ViewingConditions` | 完整 Hellwig2022 观察条件 |
| `Hellwig2022Specification` | Hellwig2022 外貌相关量容器，包含 `J_HK` 与 `Q_HK` |
| `XYZ_to_Hellwig2022` | Hellwig2022 正向模型 |
| `Hellwig2022_to_XYZ` | Hellwig2022 反向模型 |

### ZCAM

| API | 功能 |
| --- | --- |
| `InductionFactors_ZCAM` | ZCAM surround induction factors |
| `VIEWING_CONDITIONS_ZCAM` | `Average` / `Dim` / `Dark` surround 预设 |
| `ZCAMViewingConditions` | 完整 ZCAM 观察条件 |
| `ZCAMSpecification` | ZCAM 外貌相关量容器，包含 `V`、`K`、`W` |
| `XYZ_to_ZCAM` | ZCAM 正向模型 |
| `ZCAM_to_XYZ` | ZCAM 反向模型 |

## 通用输入约定

- `XYZ` 和 `XYZ_w` 使用同一个参考域，项目推荐 `Y=100`。
- `Y_b` 必须与 `XYZ_w` 的亮度标度一致。
- `L_A` 是适应场亮度，不会随着 `XYZ` 数值标度自动缩放。
- `surround` 可用 `"Average"`、`"Dim"`、`"Dark"` 或 induction factor 对象。
- 反向模型需要 `J + h + C`，或 `J + h + M`。
- `HC` 当前保留为 `None`。
- ZCAM 的 PQ/HDR 语义更强，不要把 `XYZ / XYZ_w / Y_b / L_A` 随意归一化后混用。

## CIECAM02

### `InductionFactors_CIECAM02`

用途：手动定义 CIECAM02 surround induction factors。

```python
from color.appearance import InductionFactors_CIECAM02, XYZ_to_CIECAM02
from color.constants import D65_XYZ

custom_surround = InductionFactors_CIECAM02(F=1.0, c=0.69, N_c=1.0)

spec = XYZ_to_CIECAM02(
    [19.01, 20.0, 21.78],
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
    surround=custom_surround,
)
```

注意：普通场景优先使用字符串 surround 预设。

### `VIEWING_CONDITIONS_CIECAM02`

用途：查看 CIECAM02 的 surround 预设。

```python
from color.appearance import VIEWING_CONDITIONS_CIECAM02

print(VIEWING_CONDITIONS_CIECAM02["Average"])
print(VIEWING_CONDITIONS_CIECAM02["Dim"])
print(VIEWING_CONDITIONS_CIECAM02["Dark"])
```

### `CIECAM02ViewingConditions`

用途：把一组观察条件封装成对象，便于重复使用。

```python
from color.appearance import CIECAM02ViewingConditions, XYZ_to_CIECAM02
from color.constants import D65_XYZ

conditions = CIECAM02ViewingConditions(
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
    surround="Average",
    discount_illuminant=False,
)

spec = XYZ_to_CIECAM02([19.01, 20.0, 21.78], XYZ_w=conditions)
```

也可以用直接参数覆盖对象中的部分值：

```python
spec_dim = XYZ_to_CIECAM02(
    [19.01, 20.0, 21.78],
    XYZ_w=conditions,
    surround="Dim",
)
```

### `CIECAM02Specification`

用途：保存 CIECAM02 外貌相关量，也可作为反向模型输入。

由正向模型返回：

```python
from color.appearance import XYZ_to_CIECAM02

spec = XYZ_to_CIECAM02([19.01, 20.0, 21.78])
print(spec.J, spec.C, spec.h, spec.s, spec.Q, spec.M, spec.H, spec.HC)
```

手动构造反向输入：

```python
from color.appearance import CIECAM02Specification

spec_for_inverse = CIECAM02Specification(J=41.731, C=0.105, h=219.048)
```

### `XYZ_to_CIECAM02(...)`

用途：从 XYZ 计算 CIECAM02 外貌相关量。

直接传观察条件参数：

```python
from color.appearance import XYZ_to_CIECAM02
from color.constants import D65_XYZ

spec = XYZ_to_CIECAM02(
    [19.01, 20.0, 21.78],
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
    surround="Average",
)
```

批量输入：

```python
import numpy as np
from color.appearance import XYZ_to_CIECAM02
from color.constants import D65_XYZ

XYZ = np.array([
    [19.01, 20.0, 21.78],
    [57.0, 50.0, 35.0],
])

spec = XYZ_to_CIECAM02(XYZ, XYZ_w=D65_XYZ, L_A=318.31, Y_b=20.0)
print(spec.J.shape)
```

### `CIECAM02_to_XYZ(...)`

用途：由 CIECAM02 外貌相关量反算 XYZ。

用 `J + C + h`：

```python
from color.appearance import CIECAM02Specification, CIECAM02_to_XYZ
from color.constants import D65_XYZ

XYZ = CIECAM02_to_XYZ(
    CIECAM02Specification(J=41.731, C=0.105, h=219.048),
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
)
```

用 `J + M + h`：

```python
XYZ = CIECAM02_to_XYZ(
    CIECAM02Specification(J=41.731, M=0.109, h=219.048),
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
)
```

正反向闭合：

```python
from color.appearance import CIECAM02Specification, CIECAM02_to_XYZ, XYZ_to_CIECAM02
from color.constants import D65_XYZ

spec = XYZ_to_CIECAM02([19.01, 20.0, 21.78], XYZ_w=D65_XYZ, L_A=318.31, Y_b=20.0)
XYZ = CIECAM02_to_XYZ(
    CIECAM02Specification(J=spec.J, C=spec.C, h=spec.h),
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
)
```

## CIECAM16

### `InductionFactors_CIECAM16`

用途：手动定义 CIECAM16 surround induction factors。

```python
from color.appearance import InductionFactors_CIECAM16, XYZ_to_CIECAM16
from color.constants import D65_XYZ

custom_surround = InductionFactors_CIECAM16(F=1.0, c=0.69, N_c=1.0)

spec = XYZ_to_CIECAM16(
    [19.01, 20.0, 21.78],
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
    surround=custom_surround,
)
```

### `VIEWING_CONDITIONS_CIECAM16`

用途：查看 CIECAM16 的 surround 预设。

```python
from color.appearance import VIEWING_CONDITIONS_CIECAM16

print(VIEWING_CONDITIONS_CIECAM16["Average"])
print(VIEWING_CONDITIONS_CIECAM16["Dim"])
print(VIEWING_CONDITIONS_CIECAM16["Dark"])
```

注意：CIECAM16 的 `Dim` surround `N_c` 与 CIECAM02 不同。

### `CIECAM16ViewingConditions`

用途：把一组 CIECAM16 观察条件封装成对象。

```python
from color.appearance import CIECAM16ViewingConditions, XYZ_to_CIECAM16
from color.constants import D65_XYZ

conditions = CIECAM16ViewingConditions(
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
    surround="Average",
)

spec = XYZ_to_CIECAM16([19.01, 20.0, 21.78], XYZ_w=conditions)
```

### `CIECAM16Specification`

用途：保存 CIECAM16 外貌相关量，也可作为反向模型输入。

```python
from color.appearance import CIECAM16Specification

spec_for_inverse = CIECAM16Specification(J=41.7, C=0.1, h=219.0)
```

### `XYZ_to_CIECAM16(...)`

用途：从 XYZ 计算 CIECAM16 外貌相关量。

```python
from color.appearance import XYZ_to_CIECAM16
from color.constants import D65_XYZ

spec = XYZ_to_CIECAM16(
    [19.01, 20.0, 21.78],
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
    surround="Average",
)
```

批量输入：

```python
import numpy as np
from color.appearance import XYZ_to_CIECAM16
from color.constants import D65_XYZ

XYZ = np.array([
    [19.01, 20.0, 21.78],
    [57.0, 50.0, 35.0],
])

spec = XYZ_to_CIECAM16(XYZ, XYZ_w=D65_XYZ, L_A=318.31, Y_b=20.0)
```

### `CIECAM16_to_XYZ(...)`

用途：由 CIECAM16 外貌相关量反算 XYZ。

用 `J + C + h`：

```python
from color.appearance import CIECAM16Specification, CIECAM16_to_XYZ
from color.constants import D65_XYZ

XYZ = CIECAM16_to_XYZ(
    CIECAM16Specification(J=41.7, C=0.1, h=219.0),
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
)
```

用 `J + M + h`：

```python
XYZ = CIECAM16_to_XYZ(
    CIECAM16Specification(J=41.7, M=0.1, h=219.0),
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
)
```

正反向闭合：

```python
from color.appearance import CIECAM16Specification, CIECAM16_to_XYZ, XYZ_to_CIECAM16
from color.constants import D65_XYZ

spec = XYZ_to_CIECAM16([19.01, 20.0, 21.78], XYZ_w=D65_XYZ, L_A=318.31, Y_b=20.0)
XYZ = CIECAM16_to_XYZ(
    CIECAM16Specification(J=spec.J, C=spec.C, h=spec.h),
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
)
```

## Hellwig2022

Hellwig2022 的调用方式与 CIECAM16 接近，使用 CAT16 前段响应空间，但外貌相关量公式不同，并额外返回
`J_HK`、`Q_HK` 两个 Helmholtz-Kohlrausch 扩展相关量。

### `VIEWING_CONDITIONS_HELLWIG2022`

用途：查看 Hellwig2022 的 surround 预设。

```python
from color.appearance import VIEWING_CONDITIONS_HELLWIG2022

print(VIEWING_CONDITIONS_HELLWIG2022["Average"])
print(VIEWING_CONDITIONS_HELLWIG2022["Dim"])
print(VIEWING_CONDITIONS_HELLWIG2022["Dark"])
```

注意：Hellwig2022 的 `Dim` surround 使用 `N_c=0.9`，不要复用 CIECAM02 的 `N_c=0.95`。

### `Hellwig2022ViewingConditions`

用途：把一组 Hellwig2022 观察条件封装成对象。

```python
from color.appearance import Hellwig2022ViewingConditions, XYZ_to_Hellwig2022

conditions = Hellwig2022ViewingConditions(
    XYZ_w=[95.05, 100.0, 108.88],
    L_A=318.31,
    Y_b=20.0,
    surround="Average",
)

spec = XYZ_to_Hellwig2022([19.01, 20.0, 21.78], XYZ_w=conditions)
```

### `Hellwig2022Specification`

用途：保存 Hellwig2022 外貌相关量，也可作为反向模型输入。

```python
from color.appearance import Hellwig2022Specification

spec_for_inverse = Hellwig2022Specification(J=41.7312, C=0.0258, h=217.068)
```

### `XYZ_to_Hellwig2022(...)`

用途：从 XYZ 计算 Hellwig2022 外貌相关量。

```python
from color.appearance import XYZ_to_Hellwig2022

spec = XYZ_to_Hellwig2022(
    [19.01, 20.0, 21.78],
    XYZ_w=[95.05, 100.0, 108.88],
    L_A=318.31,
    Y_b=20.0,
)

print(spec.J, spec.C, spec.h, spec.J_HK, spec.Q_HK)
```

### `Hellwig2022_to_XYZ(...)`

用途：由 Hellwig2022 外貌相关量反算 XYZ。反向只使用 `J + h + C` 或 `J + h + M`。

```python
from color.appearance import Hellwig2022Specification, Hellwig2022_to_XYZ, XYZ_to_Hellwig2022

XYZ_w = [95.05, 100.0, 108.88]
spec = XYZ_to_Hellwig2022([19.01, 20.0, 21.78], XYZ_w=XYZ_w, L_A=318.31, Y_b=20.0)
XYZ = Hellwig2022_to_XYZ(
    Hellwig2022Specification(J=spec.J, C=spec.C, h=spec.h),
    XYZ_w=XYZ_w,
    L_A=318.31,
    Y_b=20.0,
)
```

## ZCAM

ZCAM 面向 HDR/PQ 语义更强的外貌建模。它内部使用 Zhai 2018 两步色适应进入 D65 参考，再进入
Safdar 2021 / ZCAM 版本的 `Izazbz` 中间空间。使用时要保持 `XYZ`、`XYZ_w`、`Y_b`、`L_A` 的
绝对亮度语义一致，不要把一部分参数归一化而另一部分仍保留原尺度。

### `VIEWING_CONDITIONS_ZCAM`

用途：查看 ZCAM 的 surround 预设。

```python
from color.appearance import VIEWING_CONDITIONS_ZCAM

print(VIEWING_CONDITIONS_ZCAM["Average"])
print(VIEWING_CONDITIONS_ZCAM["Dim"])
print(VIEWING_CONDITIONS_ZCAM["Dark"])
```

预设参数为：

| surround | F_s | F | c | N_c |
| --- | ---: | ---: | ---: | ---: |
| Average | 0.69 | 1.0 | 0.69 | 1.0 |
| Dim | 0.59 | 0.9 | 0.59 | 0.9 |
| Dark | 0.525 | 0.8 | 0.525 | 0.8 |

### `ZCAMViewingConditions`

用途：把一组 ZCAM 观察条件封装成对象。

```python
from color.appearance import XYZ_to_ZCAM, ZCAMViewingConditions

conditions = ZCAMViewingConditions(
    XYZ_w=[256.0, 264.0, 202.0],
    L_A=264.0,
    Y_b=100.0,
    surround="Average",
)

spec = XYZ_to_ZCAM([185.0, 206.0, 163.0], XYZ_w=conditions)
```

### `ZCAMSpecification`

用途：保存 ZCAM 外貌相关量，也可作为反向模型输入。

```python
from color.appearance import ZCAMSpecification

spec_for_inverse = ZCAMSpecification(J=92.2504, C=3.0217, h=196.3246)
```

### `XYZ_to_ZCAM(...)`

用途：从 XYZ 计算 ZCAM 外貌相关量。

```python
from color.appearance import XYZ_to_ZCAM

spec = XYZ_to_ZCAM(
    [185.0, 206.0, 163.0],
    XYZ_w=[256.0, 264.0, 202.0],
    L_A=264.0,
    Y_b=100.0,
)

print(spec.J, spec.C, spec.h, spec.M, spec.V)
```

### `ZCAM_to_XYZ(...)`

用途：由 ZCAM 外貌相关量反算 XYZ。反向只使用 `J + h + C` 或 `J + h + M`。

```python
from color.appearance import XYZ_to_ZCAM, ZCAMSpecification, ZCAM_to_XYZ

XYZ_w = [256.0, 264.0, 202.0]
spec = XYZ_to_ZCAM([185.0, 206.0, 163.0], XYZ_w=XYZ_w, L_A=264.0, Y_b=100.0)
XYZ = ZCAM_to_XYZ(
    ZCAMSpecification(J=spec.J, C=spec.C, h=spec.h),
    XYZ_w=XYZ_w,
    L_A=264.0,
    Y_b=100.0,
)
```

## 与 `color.spaces` 的关系

如果目标是 CAM02-UCS / CAM16-UCS 均匀空间，不要直接在本模块里手动拼装。
推荐使用 `color.spaces`：

```python
from color.constants import D65_XYZ
from color.spaces import SpaceSpec, convert_color

cam16_ucs = convert_color(
    [19.01, 20.0, 21.78],
    "XYZ",
    SpaceSpec("CAM16-UCS", XYZ_w=D65_XYZ, L_A=318.31, Y_b=20.0),
)
```

`color.appearance` 负责色貌模型；`color.spaces` 负责把色貌模型结果组织成可路由的均匀颜色空间。
