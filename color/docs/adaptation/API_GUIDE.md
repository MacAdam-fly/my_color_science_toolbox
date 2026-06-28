# color.adaptation API 使用指南

本文档按 `color.adaptation.__all__` 覆盖顶层 API。这里写最小使用案例；
模块边界、色适应语义和与 `color.spaces` 的关系见 [`README_DETAILS.md`](README_DETAILS.md)。

`color.adaptation` 只做显式 `XYZ` 白点适应：

```text
XYZ(source white) -> XYZ(target white)
```

它不做 RGB 编码/解码、不做色貌模型，也不参与 `convert_color(...)` 的隐式路由。

## 顶层 API 总览

| API | 功能 |
| --- | --- |
| `matrix_chromatic_adaptation_von_kries` | 计算 Von Kries 类色适应矩阵 |
| `chromatic_adaptation_XYZ` | 将 XYZ 从源白点适应到目标白点 |
| `chromatic_adaptation_Zhai2018` | Zhai 与 Luo 2018 两步色适应模型 |
| `adapt_to_D65` | 从任意源白点适应到项目 D65 |
| `adapt_from_D65` | 从项目 D65 适应到目标白点 |

矩阵常量不再作为 `color.adaptation` 顶层 API。高级验证或调试时从子模块导入：

```python
from color.adaptation.matrices import CAT_BRADFORD, CHROMATIC_ADAPTATION_TRANSFORMS

print(CAT_BRADFORD)
print(CHROMATIC_ADAPTATION_TRANSFORMS.keys())
```

## 色适应矩阵

### `matrix_chromatic_adaptation_von_kries(source_white_XYZ, target_white_XYZ, transform="Bradford")`

用途：计算从源白点到目标白点的 `3x3` 色适应矩阵。

```python
from color.adaptation import matrix_chromatic_adaptation_von_kries
from color.constants import D50_XYZ, D65_XYZ

M = matrix_chromatic_adaptation_von_kries(
    source_white_XYZ=D65_XYZ,
    target_white_XYZ=D50_XYZ,
    transform="Bradford",
)
```

不同 transform：

```python
M_cat16 = matrix_chromatic_adaptation_von_kries(
    D65_XYZ,
    D50_XYZ,
    transform="CAT16",
)
```

不做适应：

```python
I = matrix_chromatic_adaptation_von_kries(
    D65_XYZ,
    D50_XYZ,
    transform=None,
)
```

注意：`transform=None` 返回单位矩阵，表示 stimulus-matching 路径。

## XYZ 色适应

### `chromatic_adaptation_XYZ(XYZ, source_white_XYZ, target_white_XYZ, transform="Bradford")`

用途：把 `XYZ` 从源白点适应到目标白点。

单点：

```python
from color.adaptation import chromatic_adaptation_XYZ
from color.constants import D50_XYZ, D65_XYZ

XYZ_D50 = chromatic_adaptation_XYZ(
    [19.01, 20.0, 21.78],
    source_white_XYZ=D65_XYZ,
    target_white_XYZ=D50_XYZ,
    transform="Bradford",
)
```

批量：

```python
XYZ_D50 = chromatic_adaptation_XYZ(
    [[19.01, 20.0, 21.78], [57.0, 50.0, 35.0]],
    source_white_XYZ=D65_XYZ,
    target_white_XYZ=D50_XYZ,
    transform="CAT16",
)
```

不做适应但返回数值 copy：

```python
XYZ_same = chromatic_adaptation_XYZ(
    [19.01, 20.0, 21.78],
    source_white_XYZ=D65_XYZ,
    target_white_XYZ=D50_XYZ,
    transform=None,
)
```

注意：输入 `XYZ`、`source_white_XYZ` 和 `target_white_XYZ` 应使用一致的数值标度。
项目常用 `Y=100`。

## Zhai 2018 两步色适应

### `chromatic_adaptation_Zhai2018(XYZ, source_white_XYZ, target_white_XYZ, D_source=1.0, D_target=1.0, baseline_white_XYZ=None, transform="CAT02")`

用途：使用 Zhai 与 Luo 2018 two-step CAT 模型，把 `XYZ` 从源照明体适应到目标照明体。

这个函数不是 `transform="Bradford"` 的平级替代。`transform` 在这里仍表示内部响应空间矩阵，只支持 `"CAT02"` 和 `"CAT16"`；Zhai2018 本身是更高一层的两步适应模型。

```python
from color.adaptation import chromatic_adaptation_Zhai2018

XYZ_D65 = chromatic_adaptation_Zhai2018(
    [48.900, 43.620, 6.250],
    source_white_XYZ=[109.850, 100.0, 35.585],
    target_white_XYZ=[95.047, 100.0, 108.883],
    D_source=0.9407,
    D_target=0.9800,
    baseline_white_XYZ=[100.0, 100.0, 100.0],
    transform="CAT02",
)
```

`baseline_white_XYZ` 省略时，会使用与源白点 `Y` 标度一致的等能白点，例如常见 `Y=100` 工作流下为 `[100, 100, 100]`。

常见用途是给需要两步适应语义的色貌模型使用，例如 ZCAM；普通跨白点适应仍优先使用 `chromatic_adaptation_XYZ(...)`。

## D65 便捷入口

### `adapt_to_D65(XYZ, source_white_XYZ, transform="Bradford")`

用途：把任意白点参考的 XYZ 适应到项目 D65。常用于进入 Oklab / IPT / Jzazbz。

```python
from color.adaptation import adapt_to_D65
from color.constants import D50_XYZ
from color.spaces import XYZ_to_Oklab

XYZ_D65_referred = adapt_to_D65(
    XYZ_D50,
    source_white_XYZ=D50_XYZ,
    transform="Bradford",
)
Oklab = XYZ_to_Oklab(XYZ_D65_referred)
```

### `adapt_from_D65(XYZ_D65_referred, target_white_XYZ, transform="Bradford")`

用途：把 D65-referred XYZ 适应回目标白点。

```python
from color.adaptation import adapt_from_D65
from color.constants import D50_XYZ
from color.spaces import Oklab_to_XYZ

XYZ_D65_referred = Oklab_to_XYZ(Oklab)
XYZ_D50 = adapt_from_D65(
    XYZ_D65_referred,
    target_white_XYZ=D50_XYZ,
    transform="Bradford",
)
```

## 与 `color.spaces` 串联

普通空间转换不会隐式适应。需要跨白点时，应把适应步骤写出来：

```python
from color.adaptation import chromatic_adaptation_XYZ
from color.constants import D50_XYZ, D65_XYZ
from color.spaces import Lab_to_XYZ, XYZ_to_Luv

XYZ_D50 = Lab_to_XYZ(Lab_D50, whitepoint_XYZ=D50_XYZ)
XYZ_D65 = chromatic_adaptation_XYZ(
    XYZ_D50,
    source_white_XYZ=D50_XYZ,
    target_white_XYZ=D65_XYZ,
)
Luv_D65 = XYZ_to_Luv(XYZ_D65, whitepoint_XYZ=D65_XYZ)
```

RGB-to-RGB 是例外：`color.spaces.RGB_to_RGB(...)` 有显式
`chromatic_adaptation` 参数，因为 RGB 空间携带 media/display whitepoint。
但 `convert_color(...)` 仍不接受色适应参数。
