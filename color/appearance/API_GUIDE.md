# color.appearance API 使用指南

本文档按 `color.appearance.__all__` 覆盖顶层 API。这里写最小使用案例；
CIECAM02/CIECAM16 的公式、参考域和模型差异见 [`README_DETAILS.md`](README_DETAILS.md)。

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

## 通用输入约定

- `XYZ` 和 `XYZ_w` 使用同一个参考域，项目推荐 `Y=100`。
- `Y_b` 必须与 `XYZ_w` 的亮度标度一致。
- `L_A` 是适应场亮度，不会随着 `XYZ` 数值标度自动缩放。
- `surround` 可用 `"Average"`、`"Dim"`、`"Dark"` 或 induction factor 对象。
- 反向模型需要 `J + h + C`，或 `J + h + M`。
- `HC` 当前保留为 `None`。

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
