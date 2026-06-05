# color.difference API 使用指南

本文档按 `color.difference.__all__` 覆盖顶层 API。这里写最小使用案例；
模块边界、公式分类和推荐工作流见 [`README_DETAILS.md`](README_DETAILS.md)。

`color.difference` 只计算两个已经位于同一颜色空间中的三维坐标差异。它不会自动把
RGB、XYZ 或其它空间转换成目标空间，也不会选择白点或观察条件。

## 顶层 API 总览

### Lab 标准色差

| API | 功能 |
| --- | --- |
| `JND_CIE1976` | CIE 1976 常见近似可觉察阈值 |
| `delta_E_CIE1976` | CIE 1976 Lab 欧氏色差 |
| `delta_E_CIE1994` | CIE 1994 Lab 色差 |
| `delta_E_CIE2000` | CIEDE2000 Lab 色差 |
| `delta_E_CMC` | CMC `l:c` Lab 色差 |

### 色貌均匀空间

| API | 功能 |
| --- | --- |
| `delta_E_CAM02UCS`, `delta_E_CAM02LCD`, `delta_E_CAM02SCD` | CAM02-UCS/LCD/SCD 坐标色差 |
| `delta_E_CAM16UCS`, `delta_E_CAM16LCD`, `delta_E_CAM16SCD` | CAM16-UCS/LCD/SCD 坐标色差 |

### 现代空间距离

| API | 功能 |
| --- | --- |
| `delta_E_Oklab` | Oklab 三维坐标距离 |
| `delta_E_Jzazbz` | Jzazbz 三维坐标距离 |

### 调度入口

| API | 功能 |
| --- | --- |
| `DELTA_E_METHODS` | method 名称到函数的只读映射 |
| `delta_E` | 按 method 分发到具体色差函数 |

## 输入规则

所有公开色差函数都要求最后一维为 3：

```python
Lab_1 = [50.0, 2.0, -80.0]
Lab_2 = [50.0, 0.0, -83.0]
```

支持批量和广播：

```python
import numpy as np

Lab_batch = np.array([
    [50.0, 2.0, -80.0],
    [60.0, 5.0, 20.0],
])
Lab_ref = np.array([50.0, 0.0, -83.0])
```

返回 shape 是广播后去掉最后一维。

## Lab 标准色差

### `JND_CIE1976`

用途：CIE 1976 色差中常见的近似 just noticeable difference 阈值。

```python
from color.difference import JND_CIE1976, delta_E_CIE1976

de76 = delta_E_CIE1976([50.0, 2.0, -80.0], [50.0, 0.0, -83.0])
is_noticeable = de76 > JND_CIE1976
```

注意：`JND_CIE1976 = 2.3` 只是 CIE 1976 的粗略参考，不应套用到所有色差公式。

### `delta_E_CIE1976(Lab_1, Lab_2)`

用途：Lab 空间欧氏距离。

单点：

```python
from color.difference import delta_E_CIE1976

de = delta_E_CIE1976([50.0, 2.0, -80.0], [50.0, 0.0, -83.0])
```

批量：

```python
de = delta_E_CIE1976(Lab_batch, Lab_ref)
```

### `delta_E_CIE1994(Lab_1, Lab_2, textiles=False)`

用途：CIE 1994 色差，支持 graphic arts 和 textiles 参数组。

默认 graphic arts：

```python
from color.difference import delta_E_CIE1994

de = delta_E_CIE1994([50.0, 2.0, -80.0], [50.0, 0.0, -83.0])
```

textiles：

```python
de_textile = delta_E_CIE1994(
    [50.0, 2.0, -80.0],
    [50.0, 0.0, -83.0],
    textiles=True,
)
```

### `delta_E_CIE2000(Lab_1, Lab_2, textiles=False)`

用途：CIEDE2000 色差。

```python
from color.difference import delta_E_CIE2000

de = delta_E_CIE2000([50.0, 2.6772, -79.7751], [50.0, 0.0, -82.7485])
```

textiles 参数：

```python
de_textile = delta_E_CIE2000(
    [50.0, 2.6772, -79.7751],
    [50.0, 0.0, -82.7485],
    textiles=True,
)
```

### `delta_E_CMC(Lab_1, Lab_2, l=2, c=1)`

用途：CMC `l:c` 色差。

默认 acceptability `2:1`：

```python
from color.difference import delta_E_CMC

de = delta_E_CMC([50.0, 2.0, -80.0], [50.0, 0.0, -83.0])
```

perceptibility `1:1`：

```python
de_11 = delta_E_CMC(
    [50.0, 2.0, -80.0],
    [50.0, 0.0, -83.0],
    l=1,
    c=1,
)
```

## 从 RGB/XYZ 显式转换到 Lab 后计算

RGB 输入必须先用 `color.spaces` 转成 Lab：

```python
from color.constants import D65_XYZ
from color.difference import delta_E_CIE2000
from color.spaces import SpaceSpec, convert_color

lab_spec = SpaceSpec("Lab", whitepoint_XYZ=D65_XYZ)

Lab_1 = convert_color([0.4, 0.5, 0.6], "sRGB", lab_spec)
Lab_2 = convert_color([0.42, 0.49, 0.58], "sRGB", lab_spec)

de = delta_E_CIE2000(Lab_1, Lab_2)
```

XYZ 输入也需要明确白点：

```python
from color.constants import D50_XYZ
from color.spaces import SpaceSpec, convert_color

Lab_1 = convert_color(XYZ_1, "XYZ", SpaceSpec("Lab", whitepoint_XYZ=D50_XYZ))
Lab_2 = convert_color(XYZ_2, "XYZ", SpaceSpec("Lab", whitepoint_XYZ=D50_XYZ))
de = delta_E_CIE2000(Lab_1, Lab_2)
```

## 色貌均匀空间色差

### `delta_E_CAM02UCS(...)` / `delta_E_CAM02LCD(...)` / `delta_E_CAM02SCD(...)`

用途：计算已经处于 CAM02-UCS/LCD/SCD 中的 `J'a'b'` 坐标距离。

直接坐标：

```python
from color.difference import delta_E_CAM02UCS

de = delta_E_CAM02UCS([40.0, 1.0, -2.0], [41.0, 0.5, -1.5])
```

从 RGB 显式转换，带观察条件：

```python
from color.constants import D65_XYZ
from color.difference import delta_E_CAM02UCS
from color.spaces import SpaceSpec, convert_color

cam02_spec = SpaceSpec(
    "CAM02-UCS",
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
    surround="Average",
)

cam02_1 = convert_color([0.4, 0.5, 0.6], "sRGB", cam02_spec)
cam02_2 = convert_color([0.42, 0.49, 0.58], "sRGB", cam02_spec)

de = delta_E_CAM02UCS(cam02_1, cam02_2)
```

LCD / SCD：

```python
from color.difference import delta_E_CAM02LCD, delta_E_CAM02SCD

de_lcd = delta_E_CAM02LCD(cam02_lcd_1, cam02_lcd_2)
de_scd = delta_E_CAM02SCD(cam02_scd_1, cam02_scd_2)
```

### `delta_E_CAM16UCS(...)` / `delta_E_CAM16LCD(...)` / `delta_E_CAM16SCD(...)`

用途：计算已经处于 CAM16-UCS/LCD/SCD 中的 `J'a'b'` 坐标距离。

```python
from color.constants import D65_XYZ
from color.difference import delta_E_CAM16UCS
from color.spaces import SpaceSpec, convert_color

cam16_spec = SpaceSpec(
    "CAM16-UCS",
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
    surround="Average",
    discount_illuminant=False,
)

cam16_1 = convert_color([0.4, 0.5, 0.6], "sRGB", cam16_spec)
cam16_2 = convert_color([0.42, 0.49, 0.58], "sRGB", cam16_spec)

de = delta_E_CAM16UCS(cam16_1, cam16_2)
```

LCD / SCD：

```python
from color.difference import delta_E_CAM16LCD, delta_E_CAM16SCD

de_lcd = delta_E_CAM16LCD(cam16_lcd_1, cam16_lcd_2)
de_scd = delta_E_CAM16SCD(cam16_scd_1, cam16_scd_2)
```

注意：观察条件属于 `SpaceSpec(...)` 转换阶段，不属于 `difference` 参数。

## Oklab / Jzazbz 坐标距离

### `delta_E_Oklab(Oklab_1, Oklab_2)`

用途：Oklab 三维欧氏距离。

```python
from color.difference import delta_E_Oklab
from color.spaces import convert_color

oklab_1 = convert_color([0.4, 0.5, 0.6], "sRGB", "Oklab")
oklab_2 = convert_color([0.42, 0.49, 0.58], "sRGB", "Oklab")

de = delta_E_Oklab(oklab_1, oklab_2)
```

注意：Oklab 在 `color.spaces` 中要求 D65-referred XYZ。如果输入不是 sRGB 这类
D65 路径，应先显式色适应。

### `delta_E_Jzazbz(Jzazbz_1, Jzazbz_2)`

用途：Jzazbz 三维欧氏距离。

```python
from color.difference import delta_E_Jzazbz
from color.spaces import convert_color

jz_1 = convert_color([0.4, 0.5, 0.6], "sRGB", "Jzazbz")
jz_2 = convert_color([0.42, 0.49, 0.58], "sRGB", "Jzazbz")

de = delta_E_Jzazbz(jz_1, jz_2)
```

注意：这里的 `delta_E_Jzazbz` 是空间坐标距离，不是 CIE 标准 Delta E 公式。

## 调度入口

### `DELTA_E_METHODS`

用途：查看当前可用 method 和底层函数。

```python
from color.difference import DELTA_E_METHODS

print(DELTA_E_METHODS.keys())
print(DELTA_E_METHODS["CIE 2000"])
```

### `delta_E(a, b, method="CIE 2000", **kwargs)`

用途：按 method 名称分发到具体色差函数。

Lab method：

```python
from color.difference import delta_E

de = delta_E(
    [50.0, 2.6772, -79.7751],
    [50.0, 0.0, -82.7485],
    method="CIE 2000",
)
```

带参数 method：

```python
de = delta_E(
    [50.0, 2.0, -80.0],
    [50.0, 0.0, -83.0],
    method="CMC",
    l=1,
    c=1,
)
```

别名：

```python
de = delta_E(Lab_1, Lab_2, method="CIEDE2000")
de = delta_E(cam16_1, cam16_2, method="CAM16UCS")
de = delta_E(oklab_1, oklab_2, method="OKLAB")
```

注意：`delta_E(...)` 只根据 `method` 选择公式，不检查输入是否真的来自对应空间。
