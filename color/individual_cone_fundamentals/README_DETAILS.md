# individual_cone_fundamentals 详细说明

这个模块用于根据 Stockman & Rider 2023 的连续公式生成标准或个体化
LMS cone fundamentals。它不是静态数据读取模块，而是一个公式模型模块。

逐项顶层 API 的最小使用案例见 [`API_GUIDE.md`](API_GUIDE.md)。本文档保留模型定位、计算链路、默认参数和模块边界说明。

## 核心定位

模块默认返回原始列字典：

```python
{
    "wavelength": ...,
    "l": ...,
    "m": ...,
    "s": ...,
}
```

其中 `l/m/s` 是最终的 corneal energy LMS cone fundamentals，并且每个通道
独立归一化到峰值 1。这个结果可以直接用于后续光谱积分、LMS 响应计算、
个体观察者建模或包装成 `MultiSpectralDistribution`。

## 计算链路

Stockman/Rider 模型从 photopigment absorbance 出发：

```text
cone absorbance
-> retinal absorptance
-> corneal quantal sensitivity
-> corneal energy sensitivity
```

第一步用 Fourier polynomial 生成 L/M/S photopigment absorbance。然后用
photopigment optical density 计算 retinal absorptance，再加入 macular pigment
和 lens pigment 的 prereceptoral filtering，最后乘以 wavelength 从 quantal
体系转换到 energy 体系。

## 内部结构

公开 API 保持很小，但内部实现按职责拆分，避免所有公式和流程都堆在一个文件：

```text
color.individual_cone_fundamentals
├── constants.py    # 默认参数、参考文献、Fourier 系数
├── templates.py    # macular/lens density 与 cone absorbance 模板
├── transforms.py   # absorbance -> absorptance -> corneal quantal/energy
└── generation.py   # generate_individual_cone_fundamentals 生成流程
```

也就是说，`templates.py` 只关心“谱模板怎么生成”，`transforms.py` 只关心
“不同光学层级之间怎么变换”，`generation.py` 再把这些步骤串起来。

## 标准观察者默认参数

`observer_degree=2` 使用：

```python
photopigment_od = (0.50, 0.50, 0.40)
macular_density_460 = 0.350
lens_density_400 = 1.7649
```

`observer_degree=10` 使用：

```python
photopigment_od = (0.38, 0.38, 0.30)
macular_density_460 = 0.095
lens_density_400 = 1.7649
```

这些默认值用于复现 CIE 2006 / Stockman-Sharpe LMS fundamentals。论文中
说明 360-400 nm 区间包含扩展估计，因此严格标准对齐主要关注 400-830 nm。

## 个体化参数

常用参数包括：

```python
generate_individual_cone_fundamentals(
    l_shift_nm=2.0,
    m_shift_nm=-1.0,
    s_shift_nm=0.0,
    photopigment_od=(0.45, 0.52, 0.38),
    macular_density_460=0.50,
    lens_density_400=1.50,
)
```

- `l_shift_nm / m_shift_nm / s_shift_nm`：直接指定 cone photopigment 的峰值
  波长偏移。
- `photopigment_od`：控制 self-screening，影响曲线宽度。
- `macular_density_460`：控制短波段 macular pigment filtering。
- `lens_density_400`：控制 lens pigment filtering。

## L template

`l_template` 支持：

```python
"mean"
"ser180"
"ala180"
```

默认 `"mean"` 表示群体平均 L cone，其中 L mean 由 `0.56 * L(ser180)` 与
`0.44 * L(ala180)` 线性混合得到。若同时给 `l_shift_nm`，当前实现会把该
shift 同时施加到两个 L 多态模板上，再重新归一化。

## 与 generators 和 spectra 的关系

核心模块可以直接使用：

```python
from color.individual_cone_fundamentals import generate_individual_cone_fundamentals

raw = generate_individual_cone_fundamentals()
```

也可以走 generators 注册表：

```python
from color.generators import generate

raw = generate("individual_cone_fundamentals", "stockman_rider_2023")
```

如果后续要插值、对齐、采样或积分，推荐使用 spectra 为这个模型专门设计的包装入口：

```python
from color.spectra import from_individual_cone_fundamentals

lms = from_individual_cone_fundamentals(observer_degree=2)
l = lms["l"]
```

这个入口不是普通的手工 `from_columns(...)` 示例，而是一个专用 API。它内部调用
`color.generators.generate_individual_cone_fundamentals(...)`，然后包装成
`MultiSpectralDistribution`，并在 metadata 中保留 generator 类别、名称和生成参数。
