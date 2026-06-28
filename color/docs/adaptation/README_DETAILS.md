# color.adaptation - 色适应模块详细说明

## AI Usage Notes

- Use this module when explicitly adapting `XYZ` values between source and target whitepoints.
- Do not use this module for color appearance modeling, RGB transfer functions, or implicit conversion inside `convert_color(...)`; route those to `appearance` or `spaces`.
- Key assumptions: adaptation operates on `XYZ` values and explicit whitepoints; it does not infer viewing conditions or source illuminants automatically.
- Common mistakes: expecting `spaces.convert_color(...)` to adapt whitepoints; adapting RGB values directly; using adaptation to compare spectra before computing `XYZ`.
- Related modules: use `spaces` after adaptation for Lab/Oklab/etc., `colorimetry` to obtain `XYZ`, and `appearance` for viewing-condition-dependent correlates.

`color.adaptation` 是显式色适应模块。它处理的是同一个颜色刺激在不同参考白点
之间的 `XYZ` 表达变化：

```text
XYZ(source white) -> XYZ(target white)
```

逐项顶层 API 的最小用法见 [`API_GUIDE.md`](API_GUIDE.md)。本文件保留模块边界、
Von Kries 类色适应语义、D65 便捷入口和与 `color.spaces` 的关系说明。

## 模块边界

`adaptation` 不属于某一个颜色空间。它是 `spaces`、`appearance` 和 RGB 工作流都可能
用到的基础模块。

它不负责：

- RGB transfer function。
- RGB 色域转换。
- Lab / Luv / Oklab 等空间公式。
- 色貌模型观察条件。
- 数值尺度转换，例如 `[0, 1] <-> Y=100`。

数值尺度转换属于 `color.utils.scale`；参考白点变化才属于 `color.adaptation`。

## 支持的 transform

当前支持四个 Von Kries 类 transform：

```text
Von Kries
Bradford
CAT02
CAT16
```

对应矩阵从 `color.constants.adaptation_matrices` 维护，并通过
`color.adaptation.matrices` 提供高级入口：

```python
from color.adaptation.matrices import (
    CAT_VON_KRIES,
    CAT_BRADFORD,
    CAT_CAT02,
    CAT_CAT16,
    CHROMATIC_ADAPTATION_TRANSFORMS,
)
```

这些矩阵不再放在 `color.adaptation` 顶层；普通工作流应使用
`chromatic_adaptation_XYZ(...)` 或 D65 便捷函数。

## Zhai 2018 两步色适应

`chromatic_adaptation_Zhai2018(...)` 是 Zhai 与 Luo 2018 two-step CAT 模型。
它不是 `Bradford`、`CAT02`、`CAT16` 这类 `transform` 的平级 method；它是更高一层的
显式模型，内部再使用 `CAT02` 或 `CAT16` 响应空间。

一步 Von Kries 类适应可以概括为：

```text
source white -> target white
```

Zhai2018 引入 baseline illuminant 和两侧适应程度：

```text
source illuminant -> baseline illuminant -> target illuminant
```

因此它需要额外参数：

- `D_source`：源照明体适应程度。
- `D_target`：目标照明体适应程度。
- `baseline_white_XYZ`：基线照明体，省略时使用与源白点 `Y` 标度一致的等能白点。
- `transform`：内部响应空间，仅支持 `"CAT02"` 或 `"CAT16"`。

普通白点变换仍应优先使用 `chromatic_adaptation_XYZ(...)`。Zhai2018 主要用于需要
不完全适应语义的高级模型，例如 ZCAM。

## Von Kries 类矩阵计算

`matrix_chromatic_adaptation_von_kries(...)` 的计算结构为：

```text
source_cone = M source_white_XYZ
target_cone = M target_white_XYZ
scale = target_cone / source_cone

M_adapt = inv(M) diag(scale) M
```

其中 `M` 是所选 transform 矩阵。得到的 `M_adapt` 用于：

```text
XYZ_target = M_adapt XYZ_source
```

代码中采用行向量约定，因此实现形式是：

```python
XYZ_target = XYZ_source @ M_adapt.T
```

## transform=None

`transform=None` 表示不做色适应：

```python
from color.adaptation import chromatic_adaptation_XYZ
from color.constants import D50_XYZ, D65_XYZ

XYZ_same = chromatic_adaptation_XYZ(
    XYZ,
    source_white_XYZ=D65_XYZ,
    target_white_XYZ=D50_XYZ,
    transform=None,
)
```

这会返回数值 copy。语义上它对应 stimulus matching：保持同一个 `XYZ` 刺激，不模拟
从 source white 到 target white 的观察适应变化。

## D65-referred 工作流

`Oklab`、`IPT`、`Jzazbz` 等空间没有显式白点参数，工程约定它们要求
D65-referred `XYZ(Y=100)`。

如果输入是 D50-referred XYZ，应先适应到 D65：

```python
from color.adaptation import adapt_to_D65
from color.constants import D50_XYZ
from color.spaces import XYZ_to_Oklab

XYZ_D65_referred = adapt_to_D65(XYZ_D50, source_white_XYZ=D50_XYZ)
Oklab = XYZ_to_Oklab(XYZ_D65_referred)
```

从这些空间反算后，如果需要回到 D50：

```python
from color.adaptation import adapt_from_D65
from color.constants import D50_XYZ
from color.spaces import Oklab_to_XYZ

XYZ_D65_referred = Oklab_to_XYZ(Oklab)
XYZ_D50 = adapt_from_D65(XYZ_D65_referred, target_white_XYZ=D50_XYZ)
```

`adapt_to_D65(...)` 和 `adapt_from_D65(...)` 只是薄封装：

```text
adapt_to_D65(XYZ, source)     = chromatic_adaptation_XYZ(XYZ, source, D65_XYZ)
adapt_from_D65(XYZ, target)   = chromatic_adaptation_XYZ(XYZ, D65_XYZ, target)
```

## 与 color.spaces 的关系

`convert_color(...)` 不做隐式色适应。这是当前工程的明确设计：

```text
Lab(D50) -> XYZ(D50)
XYZ(D50) -> chromatic_adaptation_XYZ(D50 to D65)
XYZ(D65) -> Luv(D65)
```

应写成：

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

`RGB_to_RGB(...)` 是一个高层例外：它提供显式 `chromatic_adaptation` 参数，因为
RGB 空间带有 display/media whitepoint，RGB 空间之间转换时有时需要表达
source white 到 target white 的适应。即便如此，适应仍然必须由参数显式开启。

## 输入标度

`source_white_XYZ`、`target_white_XYZ` 和输入 `XYZ` 应使用一致标度。项目默认采用
`Y=100`，例如：

```python
from color.constants import D50_XYZ, D65_XYZ
```

如果使用 `Y=1` 白点，则输入 `XYZ` 也应处于相同标度。色适应矩阵本身依赖白点比值，
但混用不同标度会让结果语义不清楚。

## 当前未实现

当前模块不实现：

- CMCCAT2000。
- Fairchild 1990。
- 完整色貌模型观察条件。
- RGB LUT / ICC 级别的适应与色彩管理。

这些内容后续可以独立设计，不应混入当前 Von Kries 基础模块。
