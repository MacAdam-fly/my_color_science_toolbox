# color_science_toolbox 功能能力综述

这份文档用于向他人展示当前工程已经具备的功能。重点不是逐个介绍 API，而是说明：

1. 各模块之间如何关联。
2. 每个模块已经实现了哪些核心能力。
3. 这些能力如何串成完整颜色科学工作流。

## 1. 模块关系总览

当前工程的主线是从数据到光谱，从光谱到色度学结果，再进入颜色空间、色貌、色差、质量评价和可视化。

```text
color.data
  内置标准数据
      |
      v
color.datasets -----------+
  静态数据读取             |
                          v
color.generators ----> color.spectra ----> color.colorimetry
  公式生成数据          光谱对象封装        XYZ / LMS / 色温 / 主波长 / 光度量
                                              |
                                              v
                         +---------------- color.adaptation
                         |                  显式色适应
                         |
                         +---------------- color.appearance
                         |                  CIECAM02 / CIECAM16 色貌模型
                         |
                         +---------------- color.spaces
                         |                  RGB / Lab / Luv / Oklab / CAM-UCS 等空间转换
                         |
                         +---------------- color.difference
                         |                  Lab / CAM-UCS / Oklab / Jzazbz 色差
                         |
                         +---------------- color.quality
                         |                  SSI 光谱相似度
                         |
                         +---------------- color.plot
                                            光谱、色度图、色温、色域、转换图谱可视化
```

可以把整个项目理解为一条主链路：

```text
标准数据 / 公式数据
    -> 光谱信号
    -> XYZ / LMS / 色度学量
    -> 颜色空间 / 色貌 / 色差 / 可视化
```

## 2. 数据与光谱层

### `color.data`

`color.data` 是内置标准数据仓库。它保存的是静态数据文件，本身不负责计算。

当前覆盖的数据类型包括：

- 标准观察者数据。
- 标准照明体数据。
- 色卡反射率数据。
- 色彩系统数据。
- 色域和显示标准相关数据。

### `color.datasets`

`color.datasets` 负责读取和解析 `color.data` 中的静态文件，返回原始 `dict[str, ndarray]`。

它的核心能力是：

- 按 category / name 获取标准数据。
- 描述数据集元信息。
- 缓存读取结果。
- 处理 CSV、Excel、特殊格式文件和部分特殊 parser。
- 针对标准观察者提供常用语义入口。

当前重点支持的数据类别包括：

- 标准观察者：
  - XYZ CMFs。
  - LMS cone fundamentals。
  - 光视效率函数。
  - 色度坐标表。
  - prereceptoral filters。
  - photopigments。
- 标准照明体。
- 色卡数据。
- 色彩系统数据。

### `color.generators`

`color.generators` 负责由公式或参数生成光谱数据，输出同样是原始字典。

当前实现的生成能力包括：

- 黑体辐射光谱。
- CIE A 光源。
- CIE D 系列日光光谱。
- 理想光谱：
  - constant SPD。
  - zero SPD。
  - equal-energy SPD。
  - Gaussian SPD。
- LED 光谱：
  - single LED。
  - multi LED 混合光谱。

它和 `datasets` 的区别是：`datasets` 读取已有标准文件，`generators` 根据公式生成数据。

### `color.spectra`

`color.spectra` 把原始表格数据包装成可计算的光谱对象。

当前实现的光谱对象包括：

- `SpectralShape`：规则波长采样域。
- `SpectralDistribution`：单通道光谱。
- `MultiSpectralDistribution`：多通道光谱。

当前核心能力包括：

- 从 datasets 包装光谱对象。
- 从原始 column dict 包装光谱对象。
- 直接由数组构造光谱对象。
- 单通道和多通道访问。
- `keys()` 和 `[]` 访问，与原始 dict 使用体验对齐。
- 采样、插值、外推、trim、reshape、align。
- 多种插值方法，包括 linear、nearest、PCHIP、Sprague 等。
- numpy / pandas / dict 导出。
- 同 shape 光谱对象之间的简单算术。
- 常用标准观察者和 D65 照明体的便捷包装入口。

`spectra` 是数据层进入计算层的关键桥梁。

## 3. 色度学计算层

### `color.colorimetry`

`color.colorimetry` 是当前工程中最核心的颜色科学计算层。

它已经实现的主要能力包括：

#### 光谱到响应值

- 自发光光谱到 `XYZ`。
- 反射率光谱在照明体下到 `XYZ`。
- 自发光光谱到 `LMS`。
- 反射率光谱在照明体下到 `LMS`。

这部分把 `spectra` 光谱对象转成后续颜色空间计算所需的三刺激值或锥响应。

#### 色度坐标转换

- `XYZ <-> xyY`。
- `XYZ -> xy`。
- `xy <-> CIE 1960 uv`。
- `xy <-> CIE 1976 u'v'`。

其中 `uv1960` 是 CCT / Duv 的核心图面，`u'v'1976` 与 Luv 相关。

#### LMS / XYZ 直接转换

- CIE 2006 LMS 到 XYZ。
- XYZ 到 CIE 2006 LMS。

#### 光度学和明度

- 明视觉光视效率函数。
- 暗视觉光视效率函数。
- luminous flux。
- luminous efficiency。
- luminous efficacy。
- CIE `L*` 与相对亮度 `Y` 的转换。

#### 主波长和纯度

- 主波长。
- 互补波长。
- 兴奋纯度。
- 色度纯度。
- 判断色度点是否位于色度轨迹内部。
- 完整色度分析结果对象。
- 根据主波长 + 纯度反向构造 xy。

#### 色温

- CCT 与 mired 转换。
- CIE D 系列 daylight xy。
- McCamy 1992 CCT 近似。
- Robertson 1968 CCT + Duv。
- Ohno 2013 CCT + Duv。
- CCT + Duv 到 xy 的反向构造。
- 完整色温分析结果对象。

## 4. 色适应与色貌模型

### `color.adaptation`

`color.adaptation` 负责显式色适应。

当前支持的色适应变换包括：

- Von Kries。
- Bradford。
- CAT02。
- CAT16。

它提供从源白点到目标白点的色适应矩阵，以及对 XYZ 数据执行色适应的函数。

工程设计上，色适应不会被普通空间转换偷偷执行。需要色适应时，使用者应显式调用这一层。

### `color.appearance`

`color.appearance` 负责色貌模型本体。

当前实现的色貌模型包括：

- CIECAM02。
- CIECAM16。

每个模型都支持：

- 正向：`XYZ -> appearance correlates`。
- 反向：`appearance specification -> XYZ`。
- Average / Dim / Dark 等观察环境。
- 自定义白点、适应场亮度、背景亮度等观察条件。

色貌模型输出的是 `J, C, h, s, Q, M, H` 等色貌相关量；它们本身不是普通颜色空间。基于色貌模型构造的均匀空间位于 `color.spaces`。

## 5. 颜色空间层

### `color.spaces`

`color.spaces` 负责颜色空间定义、注册和转换。它的核心设计是：

```text
XYZ 是唯一全局中枢
convert_color 负责空间路由
SpaceSpec 表达带参数的空间实例
RGB 标准空间使用独立注册表
```

### 已实现 RGB 标准空间

当前 RGB 层已经覆盖：

- sRGB。
- Rec.709 / ITU-R BT.709。
- Display P3 / P3-D65。
- DCI-P3。
- Rec.2020 / ITU-R BT.2020。
- Adobe RGB (1998)。
- NTSC (1953)。

RGB 层支持：

- RGB 到 XYZ。
- XYZ 到 RGB。
- RGB 到 RGB。
- sRGB 便捷入口。
- transfer function 编码 / 解码。
- 不自动裁剪 RGB。
- 可选显式 RGB-to-RGB 色适应参数。

### 已实现基础 / 经典颜色空间

当前 basic 空间包括：

- `xyY`。
- `Lab`。
- `LCHab`。
- `Luv`。
- `LCHuv`。
- `UVW`。
- `Oklab`。
- `Oklch`。
- `IPT`。
- `Jzazbz`。
- `JzCzhz`。

其中：

- `xy`、`uv1960`、`u'v'1976` 是二维色度 helper，不注册为完整颜色空间节点。
- `Lab / Luv / UVW` 带参考白点参数。
- `Oklab / IPT / Jzazbz` 要求 D65-referred XYZ。

### 已实现色貌均匀空间

基于 CIECAM02 的均匀空间：

- CAM02-UCS。
- CAM02-LCD。
- CAM02-SCD。

基于 CIECAM16 的均匀空间：

- CAM16-UCS。
- CAM16-LCD。
- CAM16-SCD。

这些空间依赖 `color.appearance` 中的色貌模型，并通过 `SpaceSpec` 接收观察条件参数。

### 转换路由能力

`spaces` 目前可以完成：

- RGB 与 XYZ 之间转换。
- XYZ 与各颜色空间之间转换。
- 派生空间与父空间之间转换，例如 `LCHab <-> Lab`、`Oklch <-> Oklab`。
- 不同颜色空间之间通过 XYZ 中枢转换。
- 描述单条转换路径。
- 绘制当前注册的完整转换图谱。

## 6. 色差与光源质量

### `color.difference`

`difference` 只负责计算同一颜色空间内两个坐标的差异，不负责颜色空间转换。

当前实现的色差包括：

#### 标准 Lab 色差

- CIE 1976。
- CIE 1994。
- CIE 2000。
- CMC。

#### 色貌均匀空间距离

- CAM02-UCS。
- CAM02-LCD。
- CAM02-SCD。
- CAM16-UCS。
- CAM16-LCD。
- CAM16-SCD。

#### 现代空间距离

- Oklab。
- Jzazbz。

典型使用方式是先用 `spaces` 转到目标空间，再用 `difference` 计算距离。

### `color.quality`

`quality` 是光源质量指标模块。

当前实现：

- Academy Spectral Similarity Index，简称 SSI。

SSI 比较两个光谱分布本身的相似度，不等同于 CRI、TM-30 或 CQS。它最适合用来比较测试光源和参考光源的光谱形状接近程度。

## 7. 可视化层

### `color.plot`

`plot` 负责把已有计算结果可视化，不改变计算结果。

当前已经实现的绘图能力包括：

#### 光谱绘图

- 单通道光谱曲线。
- 多通道光谱曲线。
- 统一光谱坐标轴样式。

#### 色度图

- CIE 1931 xy 色度图。
- CIE 1960 UCS uv 色度图。
- CIE 1976 UCS u'v' 色度图。
- 色度图近似 sRGB 背景填色。
- xy 点叠加绘制。

#### 色温图

- CIE 1960 uv 中的普朗克轨迹。
- CIE 1960 uv 中的 CIE D 日光轨迹。
- CCT + Duv 偏移点。
- CCT 与 mired 曲线。

#### 色块和色域

- XYZ 到 sRGB 预览色块。
- 色块 strip。
- 色块 grid。
- RGB 色域三角形。

#### 转换关系图

- 单条颜色空间转换路径。
- 当前注册颜色空间的完整转换图谱。

## 8. 支撑模块

### `color.constants`

保存项目中重要的标准常量，例如：

- 标准白点。
- RGB 显示标准定义。
- 色适应矩阵。
- LMS / XYZ 转换矩阵。

### `color.math`

提供数学基础能力，尤其是光谱插值相关算法。当前主要服务 `spectra`。

### `color.utils`

提供跨模块复用的基础工具，包括：

- 数组形状和有限值校验。
- name / method canonicalization。
- method dispatch。
- kwargs 过滤。
- 数值尺度转换 helper。

它是底层工具层，不承载颜色科学语义。

## 9. 已经可以展示的完整能力链路

### 光谱到颜色空间再到色差

```text
LED / 黑体 / 色卡反射率
    -> spectra 光谱对象
    -> colorimetry 积分得到 XYZ / LMS
    -> spaces 转到 Lab / CAM16-UCS / Oklab
    -> difference 计算色差
```

### 色卡反射率计算

```text
color_cards 数据
    -> 某个 patch 的反射率光谱
    -> D65 照明体 + CIE 1931 CMFs
    -> reflectance_to_XYZ
    -> Lab / Luv / CAM-UCS
    -> 色差或可视化
```

### RGB 图像或 RGB 数值处理

```text
sRGB encoded RGB
    -> RGB_to_XYZ
    -> Lab / LCHab / Oklab / Jzazbz / CAM16-UCS
    -> 修改空间坐标
    -> XYZ_to_sRGB
    -> 预览或输出
```

### 色温分析和可视化

```text
xy / uv
    -> CCT + Duv
    -> 反向构造 xy
    -> CIE 1960 uv 色温轨迹图
```

### 主波长和色品几何分析

```text
xy 色度点
    -> 主波长 / 互补波长 / 纯度
    -> 主波长 + 纯度反向构造 xy
```

## 10. 工程规模概览

以下统计排除了 `.venv`、`.git`、`__pycache__` 和 `.pytest_tmp` 等目录。这里的“有效代码行”按物理行统计：非空、非 `#` 开头的 Python 行会计入；docstring 计入有效代码行。

### 总体规模

| 项目 | 数量 |
| --- | ---: |
| Python 文件总数 | 215 |
| Python 总行数 | 26,443 |
| 有效代码行 | 21,190 |
| 空行 | 4,969 |
| 注释行 | 284 |
| Markdown 文档 | 48 |
| 内置数据文件 | 116 |
| 测试文件 | 59 |
| example 文件 | 44 |

### 按用途拆分

| 类型 | 文件数 | 总行数 | 有效代码行 |
| --- | ---: | ---: | ---: |
| 核心源码 `color/` 非 tests | 109 | 13,895 | 11,381 |
| 测试 | 59 | 7,593 | 5,822 |
| examples | 44 | 4,851 | 3,911 |
| 其他根目录脚本 | 3 | 104 | 76 |

### 核心模块代码量

| 模块 | Python 文件 | 有效代码行 |
| --- | ---: | ---: |
| `color.spaces` | 35 | 4,021 |
| `color.colorimetry` | 28 | 2,921 |
| `color.datasets` | 17 | 2,599 |
| `color.spectra` | 9 | 1,609 |
| `color.plot` | 11 | 1,192 |
| `color.difference` | 12 | 926 |
| `color.generators` | 10 | 920 |
| `color.appearance` | 6 | 843 |
| `color.constants` | 9 | 555 |
| `color.utils` | 9 | 548 |
| `color.adaptation` | 4 | 306 |
| `color.math` | 5 | 303 |
| `color.quality` | 4 | 191 |

从规模上看，项目已经不是零散脚本集合，而是一个拥有标准数据、核心计算、颜色空间、色差评价、质量评价、可视化、测试和示例的中等规模颜色科学工具箱。

## 11. 当前工程能力总结

当前项目已经形成了较完整的颜色科学主干：

- 能读取和生成光谱数据。
- 能把离散光谱封装成可插值、可对齐的对象。
- 能完成光谱到 XYZ / LMS 的核心色度学计算。
- 能做色温、主波长、光度量、明度等常用色度学分析。
- 能进行显式色适应和 CIECAM02 / CIECAM16 色貌计算。
- 能在多个 RGB、经典空间、现代空间和 CAM 均匀空间之间转换。
- 能计算 Lab、CAM-UCS、Oklab、Jzazbz 等空间中的色差。
- 能计算 SSI 光谱相似度。
- 能绘制光谱、色度图、色温轨迹、色域和转换图谱。

也就是说，当前工程已经可以从“标准数据或光谱生成”一路串到“颜色计算、空间转换、色差评价和可视化展示”。
