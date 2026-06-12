# individual_cone_fundamentals 详细说明

这个模块用于生成个体化 LMS cone fundamentals。它不是静态数据读取模块，
而是公式模型模块。逐项 API 使用案例见 [`API_GUIDE.md`](API_GUIDE.md)。

## 模块定位

所有模型都返回原始列字典：

```python
{
    "wavelength": ...,
    "l": ...,
    "m": ...,
    "s": ...,
}
```

其中 `l/m/s` 是最终的 corneal energy LMS cone fundamentals，并且每个通道
独立归一化到峰值 1。后续若需要插值、重采样或通道对象访问，应使用
`color.spectra` 的专用包装入口。

## 两条模型路线

### Stockman/Rider 2023

`generate_stockman_rider_2023_individual_cone_fundamentals(...)` 使用连续
Fourier 公式生成 photopigment absorbance、macular density 与 lens density。
它的默认参数用于复现 CIE 2006 / Stockman-Sharpe LMS fundamentals：

```python
observer_degree=2
photopigment_od=(0.50, 0.50, 0.40)
macular_density_460=0.350
lens_density_400=1.7649
```

`observer_degree=10` 时使用：

```python
photopigment_od=(0.38, 0.38, 0.30)
macular_density_460=0.095
```

这个模型的参数更接近“直接调节光谱组成”。`observer_degree` 只在 `2` 和
`10` 之间选择默认参数；如果需要个体差异，使用者直接指定
`photopigment_od`、`macular_density_460`、`lens_density_400` 和 L/M/S 峰值偏移。

Stockman/Rider 的正式中间产物入口是
`stockman_rider_2023_model_components(...)`。它接收和最终 LMS 生成函数相同的参数，
并返回已经应用当前观察者参数后的个体中间曲线：

```python
from color.individual_cone_fundamentals import stockman_rider_2023_model_components

components = stockman_rider_2023_model_components(
    l_shift_nm=2.0,
    macular_density_460=0.50,
    lens_density_400=1.50,
)
```

这些模板与最终 LMS 的关系是：

```text
photopigment_absorbance
-> retinal absorptance, controlled by photopigment OD
-> macular_density + lens_density filtering
-> corneal quantal sensitivity
-> corneal energy LMS fundamentals
```

Stockman/Rider 子模块仍保留 `cone_absorbance_spectra(...)`、
`macular_density_spectrum(...)` 和 `lens_density_spectrum(...)` 这些低层模板函数，
但它们返回的是未完整应用观察者参数的模板层。常规模型审查应优先使用
`stockman_rider_2023_model_components(...)`。

### Asano et al. 2016

`generate_asano2016_individual_cone_fundamentals(...)` 是 CIEPO06 / CIE 2006
physiological observer 的个体化扩展。它使用：

- `age`
- `field_size_degree`
- `lens_density_deviation`
- `macular_density_deviation`
- `photopigment_od_deviation`
- `photopigment_shift_nm`

Asano 的 lens age 公式需要拆分的 ocular media component：

```text
D_ocul,ave(λ) = D_ocul,1(λ) * age_factor(age) + D_ocul,2(λ)
```

因此新增了 `lens_ciepo06_components_5nm.csv`。现有 `lens_ss_*` 是
已经合成后的 lens density 曲线，不能严格支持 age-dependent lens 公式。

Asano 模型更接近“个体观察者模型”。它不是让使用者直接指定某一条 lens 或
macular 曲线，而是通过 `age`、`field_size_degree` 和 deviation 参数从平均观察者
推导个体观察者。

Asano 的正式中间产物入口是 `asano2016_model_components(...)`。它同样返回当前
参数下的个体曲线，例如 shifted absorbance、photopigment OD、retinal absorptance、
lens density、macular density、prereceptoral density、corneal quantal 和
corneal energy。

## 计算链路

两种模型的物理层级一致：

```text
low-density photopigment absorbance
-> retinal absorptance
-> macular + lens prereceptoral filtering
-> corneal quantal sensitivity
-> corneal energy sensitivity
-> per-channel peak normalisation
```

区别在于模板来源和参数化方式：

- Stockman/Rider 用连续公式直接生成模板。
- Asano 使用 CIE 2006 / CIEPO06 表格和论文中的 age/field/deviation 公式。

两个 components 函数返回统一字段：

```python
{
    "wavelength": ...,
    "photopigment_absorbance": ...,
    "photopigment_od": ...,
    "retinal_absorptance": ...,
    "macular_density": ...,
    "lens_density": ...,
    "prereceptoral_density": ...,
    "corneal_quantal": ...,
    "corneal_energy": ...,
}
```

其中 `corneal_energy` 是最终 LMS 曲线的数据来源；最终 `generate_*` 函数只是把
`corneal_energy[:, 0/1/2]` 拆成 `l/m/s` 返回。

更直接地说：

| 维度 | Stockman/Rider 2023 | Asano 2016 |
| --- | --- | --- |
| 参数语义 | 直接调 OD、density、shift | 用 age、field size、deviation 描述观察者 |
| lens | 单条模板按 `lens_density_400` 缩放 | `D_ocul,1 / D_ocul,2` 按年龄公式合成 |
| macular | 2/10 度默认值或手动指定 | 随 field size 变化后叠加 deviation |
| OD | 2/10 度默认值或手动指定 | 随 field size 变化后叠加 deviation |
| 适合场景 | 控制模型组件、复现 Stockman/Rider | 模拟个体观察者 age / field / deviation |

## 与 generators 和 spectra 的关系

核心模块直接生成原始字典：

```python
from color.individual_cone_fundamentals import (
    generate_asano2016_individual_cone_fundamentals,
)

raw = generate_asano2016_individual_cone_fundamentals(age=45)
```

`color.generators` 负责注册表分发：

```python
from color.generators import generate_individual_cone_fundamental

raw = generate_individual_cone_fundamental("asano2016", age=45)
```

`color.spectra` 负责包装成 `MultiSpectralDistribution`：

```python
from color.spectra import from_asano2016_individual_cone_fundamentals

lms = from_asano2016_individual_cone_fundamentals(age=45)
l = lms["l"]
```

## 当前边界

目前只生成确定性的单个观察者曲线，不实现 Asano 论文中的 Monte Carlo
population sampling。L/M/S 基因型、codon、hybrid 之类的上层推断也暂不实现；
使用者需要直接传入波长偏移或密度偏差。
