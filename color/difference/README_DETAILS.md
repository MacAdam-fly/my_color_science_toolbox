# color.difference 详细说明

`color.difference` 是色差计算层。它的职责很窄：计算两个已经位于同一颜色空间中的三维坐标差异。

它不负责：

- RGB、XYZ、Lab、CAM、Oklab、Jzazbz 之间的转换。
- 白点选择。
- 色适应。
- CIECAM02 / CIECAM16 观察条件管理。

这些工作应该在 `color.spaces` 或 `color.adaptation` 中显式完成，然后再把得到的坐标交给 `color.difference`。

## 模块结构

当前结构按公式来源和空间族拆分：

```text
color/difference/
├── lab_delta_e.py          # CIE 1976 / 1994 / 2000 / CMC
├── appearance_delta_e.py   # CAM02-UCS/LCD/SCD, CAM16-UCS/LCD/SCD
├── oklab_delta_e.py        # Oklab 坐标距离
├── jzazbz_delta_e.py       # Jzazbz 坐标距离
├── methods.py              # delta_E(...) 方法注册与分发
└── _utils.py               # 三通道输入校验、广播、结果处理
```

## 输入约定

所有公开函数都接受最后一维为 3 的数组：

```python
delta_E_CIE2000([50, 2, -80], [50, 0, -83])
delta_E_Oklab(oklab_batch, oklab_single)
```

规则是：

- 单点：`(3,)`
- 批量：`(..., 3)`
- 支持 NumPy 广播
- 返回 shape 为广播后去掉最后一维
- 非有限值和非法 shape 抛 `ValueError`

统一输入规则不代表统一数学公式。CIE 1994、CIEDE2000、CMC 内部都有明度、彩度、色相和权重项；Oklab / Jzazbz 是直接三维欧氏距离；CAM02/CAM16-UCS 系列是带 `K_L` 的加权欧氏距离。

## Lab 标准色差

`lab_delta_e.py` 提供：

```python
delta_E_CIE1976
delta_E_CIE1994
delta_E_CIE2000
delta_E_CMC
```

这些函数的输入必须是同一 Lab 空间中的坐标。换句话说，调用者需要先决定参考白点，例如：

```python
from color.constants import D65_XYZ
from color.spaces import SpaceSpec, convert_color

Lab = convert_color(rgb, "sRGB", SpaceSpec("Lab", whitepoint_XYZ=D65_XYZ))
```

`JND_CIE1976 = 2.3` 是 CIE 1976 色差中常见的近似可觉察差异阈值，只适合作为粗略参考，不应被当作所有色差公式的统一判断标准。

## 色貌均匀空间色差

`appearance_delta_e.py` 提供：

```python
delta_E_CAM02UCS
delta_E_CAM02LCD
delta_E_CAM02SCD
delta_E_CAM16UCS
delta_E_CAM16LCD
delta_E_CAM16SCD
```

这些函数的输入是 `J'a'b'` 坐标，不是 CIECAM02 / CIECAM16 的完整 appearance specification，也不是 XYZ。

观察条件应该在 `spaces` 转换阶段指定。真实使用色貌均匀空间时，建议显式写出 `SpaceSpec(...)`，

```python
from color.constants import D65_XYZ
from color.spaces import SpaceSpec, convert_color

cam16_spec = SpaceSpec(
    "CAM16-UCS",
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
    surround="Average",
    discount_illuminant=False,
)

cam16 = convert_color(rgb, "sRGB", cam16_spec)
```

然后再计算：

```python
delta_E_CAM16UCS(cam16_1, cam16_2)
```

`difference` 不接收 `surround`、`L_A`、`Y_b` 等参数，因为它只看到已经转换好的坐标。

## Oklab / Jzazbz 距离

`oklab_delta_e.py` 和 `jzazbz_delta_e.py` 提供：

```python
delta_E_Oklab
delta_E_Jzazbz
```

它们只是对应空间中的三维欧氏距离。这些函数很有用，但语义上不同于 CIEDE2000 这样的标准 Lab 色差公式。

特别注意：Oklab 和 Jzazbz 在 `color.spaces` 中要求输入 XYZ 已经符合项目约定的 D65-referred 语义。如果数据来自其他白点，应先显式色适应，再进入这些空间。

## delta_E 调度入口

`delta_E(a, b, method="CIE 2000", **kwargs)` 是统一调度入口，支持：

```text
CIE 1976
CIE 1994
CIE 2000
CMC
CAM02-UCS
CAM02-LCD
CAM02-SCD
CAM16-UCS
CAM16-LCD
CAM16-SCD
Oklab
Jzazbz
```

它只根据 `method` 选择公式，不会检查 `a` 和 `b` 是否真的来自对应空间。因此：

```python
delta_E(a, b, method="Oklab")
```

意味着“把 `a` 和 `b` 当作 Oklab 坐标计算距离”，而不是“自动把 `a` 和 `b` 转成 Oklab”。

## 推荐工作流

如果数据已经是目标空间坐标：

```python
delta_E_CIE2000(Lab_1, Lab_2)
```

如果数据还是 RGB：

```python
Lab_1 = convert_color(rgb_1, "sRGB", SpaceSpec("Lab", whitepoint_XYZ=D65_XYZ))
Lab_2 = convert_color(rgb_2, "sRGB", SpaceSpec("Lab", whitepoint_XYZ=D65_XYZ))
delta_E_CIE2000(Lab_1, Lab_2)
```

如果要使用 CAM16-UCS，推荐把观察条件写清楚：

```python
from color.constants import D65_XYZ
from color.spaces import SpaceSpec, convert_color

cam16_spec = SpaceSpec(
    "CAM16-UCS",
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
    surround="Average",
    discount_illuminant=False,
)

cam16_1 = convert_color(rgb_1, "sRGB", cam16_spec)
cam16_2 = convert_color(rgb_2, "sRGB", cam16_spec)

delta_E_CAM16UCS(cam16_1, cam16_2)
```

如果要比较不同观察环境，例如 `Average` 和 `Dim`，也应该在 `SpaceSpec(...)` 层面创建不同坐标，而不是把 `surround` 传给 `delta_E_CAM16UCS(...)`。核心原则是：先用 `spaces` 明确得到目标空间坐标，再用 `difference` 计算差异。
