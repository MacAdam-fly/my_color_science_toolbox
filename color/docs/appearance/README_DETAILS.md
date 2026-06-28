# color.appearance 详细说明：CIECAM02、CIECAM16、Hellwig2022 与 ZCAM 计算公式

## AI Usage Notes

- Use this module when computing CIECAM02, CIECAM16, Hellwig2022 or ZCAM appearance correlates under explicit viewing conditions.
- Do not use this module for ordinary coordinate conversion, simple Delta E, or chromatic adaptation alone; route those to `spaces`, `difference`, or `adaptation`.
- Key assumptions: appearance results depend on viewing-condition parameters; input `XYZ` must already be defined in the intended reference scale and illuminant context.
- Common mistakes: treating appearance correlates as simple color-space coordinates; omitting viewing-condition assumptions; comparing outputs from different model/settings as if they were interchangeable.
- Related modules: use `spaces` for CAM02-UCS/CAM16-UCS conversions, `adaptation` for explicit whitepoint changes, and `colorimetry` for `XYZ` inputs.

本文档用于记录当前 `color.appearance` 中 CIECAM02、CIECAM16、Hellwig2022 与 ZCAM 色貌模型的主要计算公式。  
这些模型都属于颜色外貌模型，用来描述同一个 `XYZ` 刺激在指定观察条件下产生的明度、彩度、色相、鲜艳度等外貌相关量。

逐项顶层 API 的最小用法见 [`API_GUIDE.md`](API_GUIDE.md)。本文件保留模型公式、
参考域约定、模型差异和实现范围说明。

当前工程实现的参考域约定为：

- CIECAM02、CIECAM16 与 Hellwig2022 中，`XYZ` 与 `XYZ_w` 默认使用 `Y=100` 标度。
- ZCAM 的 PQ/HDR 语义更强，`XYZ`、`XYZ_w`、`Y_b` 与 `L_A` 不应随意归一化或混用标度。
- `XYZ`、`XYZ_w`、`Y_b` 必须处于一致的亮度参考域。
- 观察条件使用单个白点、背景亮度和适应亮度，颜色数据本身可以是单点 `(3,)` 或批量 `(..., 3)`。
- 基础正向模型输出 `J, C, h, s, Q, M, H, HC`，其中 `HC` 第一版保留为 `None`。
- Hellwig2022 额外输出 `J_HK, Q_HK`；ZCAM 额外输出 `V, K, W`。
- 反向模型支持由 `J, C, h` 或 `J, M, h` 回到 `XYZ`。

## 公共观察条件

这些模型都需要以下观察条件：

| 符号 | 含义 |
| --- | --- |
| `XYZ_w` | 参考白点三刺激值 |
| `L_A` | 适应场亮度 |
| `Y_b` | 背景亮度因子 |
| `F` | 最大适应程度因子 |
| `c` | 影响明度指数的 surround 参数 |
| `N_c` | 色度诱导因子 |
| `discount_illuminant` | 是否完全折扣照明体 |

当前默认观察条件为：

```python
XYZ_w = D65_XYZ
L_A = 64 / pi * 0.2
Y_b = 20
surround = "Average"
discount_illuminant = False
```

参考域缩放需要整体一致。当前实现允许使用非 `Y=100` 的 `XYZ_w`，例如
`XYZ_w = D65_XYZ * 2`，但这表示模型工作在 `Y_w=200` 的参考域中。
此时输入 `XYZ` 也应使用同一参考域；如果想保持与默认设置相同的背景相对亮度，
`Y_b` 也应同步缩放，例如从 `20` 改为 `40`。`L_A` 是适应场亮度参数，
不因为 `XYZ / XYZ_w / Y_b` 的数值参考域变化而自动缩放。

### Surround 参数

CIECAM02:

| surround | F | c | N_c |
| --- | ---: | ---: | ---: |
| Average | 1.0 | 0.69 | 1.0 |
| Dim | 0.9 | 0.59 | 0.95 |
| Dark | 0.8 | 0.525 | 0.8 |

CIECAM16:

| surround | F | c | N_c |
| --- | ---: | ---: | ---: |
| Average | 1.0 | 0.69 | 1.0 |
| Dim | 0.9 | 0.59 | 0.9 |
| Dark | 0.8 | 0.525 | 0.8 |

Hellwig2022:

| surround | F | c | N_c |
| --- | ---: | ---: | ---: |
| Average | 1.0 | 0.69 | 1.0 |
| Dim | 0.9 | 0.59 | 0.9 |
| Dark | 0.8 | 0.525 | 0.8 |

ZCAM:

| surround | F_s | F | c | N_c |
| --- | ---: | ---: | ---: | ---: |
| Average | 0.69 | 1.0 | 0.69 | 1.0 |
| Dim | 0.59 | 0.9 | 0.59 | 0.9 |
| Dark | 0.525 | 0.8 | 0.525 | 0.8 |

CIECAM02 与 CIECAM16 / Hellwig2022 在 `Dim` surround 下的 `N_c` 不同，这是当前实现需要保留的标准差异。

## 公共中间量

令参考白点为：

```text
XYZ_w = [X_w, Y_w, Z_w]
```

背景相对亮度：

```text
n = Y_b / Y_w
```

亮度适应因子：

```text
k = 1 / (5 L_A + 1)
F_L = 0.2 k^4 (5 L_A) + 0.1 (1 - k^4)^2 (5 L_A)^(1/3)
```

背景相关因子：

```text
N_bb = N_cb = 0.725 (1 / n)^0.2
z = 1.48 + sqrt(n)
```

照明体适应程度：

```text
D = F [1 - (1 / 3.6) exp((-L_A - 42) / 92)]
```

如果 `discount_illuminant=True`：

```text
D = 1
```

当前 CIECAM02 与 CIECAM16 实现都会把 `D` 裁剪到 `[0, 1]`，避免极端观察条件下出现不符合物理意义的适应程度。

## CIECAM02 正向计算

CIECAM02 的关键特点是：先使用 CAT02 得到 cone response，再做完全色适应，然后转换到 Hunt-Pointer-Estevez 响应空间进行非线性压缩。

### 1. CAT02 cone response

CAT02 矩阵来自 `color.adaptation.CAT_CAT02`：

```text
RGB = M_CAT02 XYZ
RGB_w = M_CAT02 XYZ_w
```

### 2. 完全色适应

每个通道的适应系数为：

```text
D_RGB = D Y_w / RGB_w + 1 - D
```

刺激与白点的适应后响应为：

```text
RGB_c = D_RGB * RGB
RGB_wc = D_RGB * RGB_w
```

### 3. CAT02 到 HPE

当前实现使用：

```text
M_XYZ_to_HPE =
[[ 0.38971, 0.68898, -0.07868],
 [-0.22981, 1.18340,  0.04641],
 [ 0.0,     0.0,      1.0    ]]
```

并构造：

```text
M_CAT02_to_HPE = M_XYZ_to_HPE inv(M_CAT02)
```

因此：

```text
RGB_p = M_CAT02_to_HPE RGB_c
RGB_pw = M_CAT02_to_HPE RGB_wc
```

### 4. 非线性响应压缩

对每个通道：

```text
x = (F_L |RGB_p| / 100)^0.42
RGB_a = sign(RGB_p) 400 x / (27.13 + x) + 0.1
```

白点同理得到 `RGB_aw`。

### 5. 对立维度

令：

```text
RGB_a = [R_a, G_a, B_a]
```

则：

```text
a = R_a - 12 G_a / 11 + B_a / 11
b = (R_a + G_a - 2 B_a) / 9
```

色相角：

```text
h = atan2(b, a)
```

并转换为角度制，范围归一到 `[0, 360)`。

### 6. Hue quadrature

当前实现使用 CIECAM02/CIECAM16 常用 hue quadrature 表：

```text
h_i = [20.14, 90.00, 164.25, 237.53, 380.14]
e_i = [0.8,   0.7,   1.0,    1.2,    0.8]
H_i = [0,     100,   200,    300,    400]
```

在相邻 hue 区间内：

```text
H = H_i + 100 ((h - h_i) / e_i)
    / [((h - h_i) / e_i) + ((h_{i+1} - h) / e_{i+1})]
```

当前代码还显式处理了红色区间两端的环绕情况。

### 7. 偏心率因子

```text
e_t = 0.25 [cos(2 + h pi / 180) + 3.8]
```

### 8. 非彩色响应

```text
A = (2 R_a + G_a + B_a / 20 - 0.305) N_bb
A_w = (2 R_aw + G_aw + B_aw / 20 - 0.305) N_bb
```

### 9. 外貌相关量

明度：

```text
J = 100 (A / A_w)^(c z)
```

亮度感：

```text
Q = (4 / c) sqrt(J / 100) (A_w + 4) F_L^0.25
```

临时色度量：

```text
t = (50000 / 13) N_c N_cb e_t sqrt(a^2 + b^2)
    / (R_a + G_a + 21 B_a / 20)
```

彩度：

```text
C = t^0.9 sqrt(J / 100) (1.64 - 0.29^n)^0.73
```

鲜艳度：

```text
M = C F_L^0.25
```

饱和度：

```text
s = 100 sqrt(M / Q)
```

## CIECAM16 正向计算

CIECAM16 的整体结构与 CIECAM02 类似，但前段响应空间不同。

当前实现使用 `CAT_CAT16`。它与 CIECAM16 / CAM16 文献中常写的 `M_16` 是同一个响应变换矩阵：

```text
CAT_CAT16 = M_16 =
[[ 0.401288,  0.650173, -0.051461],
 [-0.250268,  1.204414,  0.045854],
 [-0.002079,  0.048952,  0.953127]]
```

### 1. CIECAM16 RGB response

```text
RGB = CAT_CAT16 XYZ
RGB_w = CAT_CAT16 XYZ_w
```

### 2. 完全色适应

```text
D_RGB = D Y_w / RGB_w + 1 - D
RGB_c = D_RGB * RGB
RGB_wc = D_RGB * RGB_w
```

### 3. 非线性响应压缩

CIECAM16 不再经过 CIECAM02 的 `CAT02 -> HPE` 转换步骤，而是直接对适应后的 `RGB_c` 压缩：

```text
x = (F_L |RGB_c| / 100)^0.42
RGB_a = sign(RGB_c) 400 x / (27.13 + x) + 0.1
```

白点同理得到 `RGB_aw`。

### 4. 后续外貌相关量

得到 `RGB_a` 与 `RGB_aw` 后，CIECAM16 当前实现继续使用与 CIECAM02 相同形式的：

- 对立维度 `a, b`
- 色相角 `h`
- hue quadrature `H`
- 偏心率因子 `e_t`
- 非彩色响应 `A, A_w`
- 外貌相关量 `J, Q, t, C, M, s`

因此两者最主要的公式差异集中在前段响应空间与色适应路径上。

## CIECAM02 反向计算

反向转换要求输入：

```text
J, h, C
```

或者：

```text
J, h, M
```

如果只给出 `M`：

```text
C = M / F_L^0.25
```

### 1. 恢复非彩色响应

```text
A = A_w (J / 100)^(1 / (c z))
```

### 2. 恢复临时色度量

```text
t = [C / (sqrt(J / 100) (1.64 - 0.29^n)^0.73)]^(1 / 0.9)
```

### 3. 构造反向辅助量

```text
P_1 = (50000 / 13) N_c N_cb e_t / t
P_2 = A / N_bb + 0.305
P_3 = 21 / 20
```

当 `C` 接近 0 时，当前实现把对立维度设为：

```text
a = 0
b = 0
```

### 4. 从 hue 恢复对立维度

令：

```text
sin_h = sin(h)
cos_h = cos(h)
n_p = P_2 (2 + P_3) 460 / 1403
```

如果 `|sin_h| >= |cos_h|`：

```text
b = n_p / [
    P_1 / sin_h
    + (2 + P_3) (220 / 1403) (cos_h / sin_h)
    - 27 / 1403
    + P_3 (6300 / 1403)
]
a = b cos_h / sin_h
```

否则：

```text
a = n_p / [
    P_1 / cos_h
    + (2 + P_3) (220 / 1403)
    - (27 / 1403 - P_3 6300 / 1403) (sin_h / cos_h)
]
b = a sin_h / cos_h
```

### 5. 从对立维度恢复压缩响应

```text
[R_a, G_a, B_a]^T =
1 / 1403 *
[[460,  451,   288 ],
 [460, -891,  -261 ],
 [460, -220, -6300]] [P_2, a, b]^T
```

### 6. 反向非线性压缩

```text
m = |RGB_a - 0.1|
RGB_p = sign(RGB_a - 0.1) 100 / F_L
        [27.13 m / (400 - m)]^(1 / 0.42)
```

### 7. 回到 XYZ

CIECAM02 需要先从 HPE 回到 CAT02：

```text
RGB_c = M_HPE_to_CAT02 RGB_p
RGB = RGB_c / D_RGB
XYZ = inv(M_CAT02) RGB
```

## CIECAM16 反向计算

CIECAM16 反向的 `J, C/M, h -> A -> t -> a,b -> RGB_a -> RGB_c` 路径与 CIECAM02 相同。

区别在最后一步：

```text
RGB_c = inverse_compression(RGB_a)
RGB = RGB_c / D_RGB
XYZ = inv(CAT_CAT16) RGB
```

也就是说，CIECAM16 不需要 CIECAM02 的 HPE 与 CAT02 之间的转换。

## CIECAM02 与 CIECAM16 的核心差异

| 项目 | CIECAM02 | CIECAM16 |
| --- | --- | --- |
| 前段响应矩阵 | `CAT_CAT02` | `CAT_CAT16` |
| 压缩前是否进入 HPE | 是，`CAT02 -> HPE` | 否，直接压缩适应后的 `RGB_c` |
| `Dim` surround 的 `N_c` | `0.95` | `0.9` |
| 输出相关量 | `J, C, h, s, Q, M, H, HC` | `J, C, h, s, Q, M, H, HC` |
| 反向输入 | `J+h+C` 或 `J+h+M` | `J+h+C` 或 `J+h+M` |

可以把两者理解为：

- CIECAM02 是较早的经典色貌模型，后续 CAM02-UCS / CAM02-LCD / CAM02-SCD 等均匀空间建立在它的 `J, M, h` 结果上。
- CIECAM16 是更新的色貌模型，前段响应空间和部分 surround 参数做了调整，但外貌相关量的组织方式与 CIECAM02 高度相似。

## Hellwig2022 与 ZCAM 补充说明

Hellwig2022 使用 CAT16 前段响应空间，但不是 CIECAM16 的简单别名。它的亮度、彩度、鲜艳度和饱和度相关量使用独立公式：

- `Q = (2 / c) (J / 100) A_w`
- `M = 43 N_c e_t sqrt(a^2 + b^2)`
- `C = 35 M / A_w`
- `s = 100 M / Q`

正向模型还计算 Helmholtz-Kohlrausch 扩展相关量：

```text
J_HK = J + f(h) C^0.587
Q_HK = (2 / c) (J_HK / 100) A_w
```

反向模型当前仍只使用 `J + C + h` 或 `J + M + h`，不把 `J_HK` 当作反向输入。

ZCAM 内部先使用 Zhai 2018 两步色适应把刺激从参考白点适应到 D65，再进入 Safdar 2021 / ZCAM 版本的
`Izazbz` 中间空间。ZCAM 的公式包含 PQ / ST2084 风格的非线性压缩，因此它比 CIECAM02、CIECAM16、
Hellwig2022 更依赖输入数值的绝对亮度语义。实际使用时应保持 `XYZ`、`XYZ_w`、`Y_b`、`L_A` 的标度一致；
不要把 `XYZ` 归一化到 `[0, 1]` 后仍使用原来的 `L_A` 和 `Y_b`。

## 当前工程实现范围

当前 `color.appearance` 已实现：

```python
from color.appearance import (
    XYZ_to_CIECAM02,
    CIECAM02_to_XYZ,
    CIECAM02Specification,
    CIECAM02ViewingConditions,
    XYZ_to_CIECAM16,
    CIECAM16_to_XYZ,
    CIECAM16Specification,
    CIECAM16ViewingConditions,
    XYZ_to_Hellwig2022,
    Hellwig2022_to_XYZ,
    Hellwig2022Specification,
    Hellwig2022ViewingConditions,
    XYZ_to_ZCAM,
    ZCAM_to_XYZ,
    ZCAMSpecification,
    ZCAMViewingConditions,
)
```

已支持：

- CIECAM02 正向与反向转换。
- CIECAM16 正向与反向转换。
- Hellwig2022 正向与反向转换。
- ZCAM 正向与反向转换。
- `Average`、`Dim`、`Dark` surround。
- `J, C, h` 与 `J, M, h` 两种反向输入方式。
- 单点和批量输入。

暂未实现：

- `HC` hue composition 的完整计算。
- 每个样本使用不同观察条件。
- CIECAM16-UCS / CAM16-UCS 空间。
- ZCAM-UCS、ZCAM 色差公式。
- RLAB、LLAB 等当前未纳入 V1 闭环范围的模型。

## 简单使用示例

```python
import numpy as np

from color.appearance import (
    CIECAM02Specification,
    CIECAM02_to_XYZ,
    XYZ_to_CIECAM02,
    XYZ_to_CIECAM16,
    XYZ_to_Hellwig2022,
    XYZ_to_ZCAM,
)
from color.constants import D65_XYZ

XYZ = np.array([19.01, 20.00, 21.78])

cam02 = XYZ_to_CIECAM02(
    XYZ,
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
    surround="Average",
)

XYZ_reconstructed = CIECAM02_to_XYZ(
    CIECAM02Specification(J=cam02.J, C=cam02.C, h=cam02.h),
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
    surround="Average",
)

cam16 = XYZ_to_CIECAM16(
    XYZ,
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
    surround="Average",
)

hellwig = XYZ_to_Hellwig2022(
    XYZ,
    XYZ_w=D65_XYZ,
    L_A=318.31,
    Y_b=20.0,
    surround="Average",
)

zcam = XYZ_to_ZCAM(
    [185.0, 206.0, 163.0],
    XYZ_w=[256.0, 264.0, 202.0],
    L_A=264.0,
    Y_b=100.0,
    surround="Average",
)
```
