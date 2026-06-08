# color.recovery 详细说明

`color.recovery` 负责从低维颜色刺激反推出一个可行光谱。当前分成两层：

```text
target + 三通道 responses -> effective spectrum
XYZ / xyY + illuminant + CMFs -> reflectance
registered reflectance datasets -> reflectance library
```

逐项顶层 API 的最小用法见 [`API_GUIDE.md`](API_GUIDE.md)。本文件保留反问题语义、
通用 spectrum recovery 与 reflectance recovery 的区别、算法约束和后续方法注册设计。

不做 `sRGB` 入口，不接入 `generators`。自发光 SPD 不需要单独入口，使用
`recover_spectrum_from_XYZ(...)` 即可。

## 模块边界

光谱恢复是反问题。同一个三通道响应可以对应很多条光谱，因此这里的结果不是“真实光谱”，而是在约束条件下求得的一条可行光谱。

如果输入来自 RGB、Lab、Luv 等空间，应先显式使用 `color.spaces` 转为 `XYZ`：

```python
XYZ = convert_color(value, "Lab", "XYZ")
reflectance = recover_reflectance_from_XYZ(XYZ)
```

## 通用光谱恢复

`recover_spectrum_from_responses(...)` 解决：

```text
target = A @ spectrum
A = interval * responses.T
```

`recover_spectrum_from_XYZ(...)` 和 `recover_spectrum_from_LMS(...)` 只是加载不同的三通道响应函数后调用这个底层入口。对于自发光场景，恢复出的 effective spectrum 可以直接解释为 SPD。

## 反射率恢复

反射率恢复构造与 `color.colorimetry.reflectance_to_XYZ(...)` 一致的线性积分矩阵：

```text
XYZ = A @ r
A = k * interval * (illuminant * CMFs).T
k = 100 / sum(illuminant * ybar * interval)
```

其中 `r` 是反射率谱。优化目标为：

```text
min ||A r - XYZ||² + smoothness * ||D r||²
subject to lower <= r <= upper
```

`D` 是二阶差分矩阵，用来抑制过度振荡。默认 `bounds=(0, 1)`，适合普通反射率。

不要把反射率恢复简单写成先恢复 `spectrum` 再除以 `illuminant`。那样约束施加在 effective spectrum 上，无法保证最后的 reflectance 保持在 `[0, 1]`。

## 方法注册表

当前只注册：

```text
bounded_least_squares
gaussian  # spectrum recovery only
multi_gaussian  # spectrum recovery only
auto_gaussian  # spectrum recovery only
meng2015  # reflectance recovery only
pca  # reflectance recovery only
dictionary  # reflectance recovery only
```

`gaussian`、`multi_gaussian` 和 `auto_gaussian` 只注册在 spectrum recovery 中。
它们恢复的是 effective spectrum / emission-like SPD，不是反射率。单高斯模型适合
单峰 LED 或窄带光源；多高斯模型适合双峰/多峰 LED，尤其是 purple/complementary
方向这类单峰光谱难以表达的色品。`auto_gaussian` 是策略分发：XYZ 入口下根据主波长
分析选择 single 或 multi Gaussian，不是新的数学模型。

`meng2015`、`pca` 和 `dictionary` 只注册在 reflectance recovery 中。`meng2015`
依赖反射率边界和照明体语义；`pca` / `dictionary` 依赖反射谱数据库。通用 spectrum
recovery 没有反射率先验，因此不提供这些 reflectance-only method。

Meng 2015 recovery 不使用数据库。它求解：

```text
min sum((r[i+1] - r[i])²)
subject to A @ r = XYZ
           lower <= r <= upper
```

这和 bounded least-squares 的折中目标不同。Meng 2015 把 `XYZ` 闭合作为等式约束，
再在可行反射率中寻找相邻波长变化最小的一条。因此它对可行性更敏感：如果目标 `XYZ`
在当前 `bounds`、illuminant、CMFs 和 shape 下无法由反射率产生，优化会失败。

PCA recovery 使用 `ReflectanceLibrary` 学习：

```text
r(λ) ≈ mean(λ) + B @ c
```

然后在 PCA 子空间中求系数 `c`，并直接约束重建反射率位于 `bounds` 内。它不是
把 bounded least-squares 的结果再投影到 PCA basis，也不是最后裁剪反射率。这样做的
原因是裁剪会破坏 `XYZ` 闭合，而优化约束能把物理范围和颜色匹配同时放进同一个问题。

spectrum recovery 和 reflectance recovery 使用分开的 registry，后续可以分别添加 basis、
Smits 等方法。

Dictionary recovery 使用真实反射谱样本作为字典：

```text
r(λ) = w @ library.reflectances
```

第一版固定使用凸组合语义：`w >= 0` 且 `sum(w) ≈ 1`，结果是库样本的加权平均。
这和 PCA 不同：PCA 使用统计主成分，dictionary 直接组合真实样本。当前 dictionary
不是 sparse dictionary，不会强制只使用少数几条样本；稀疏版本需要额外的候选筛选或
非光滑优化，后续再单独设计。

## 输出

- 单个 `(3,)` 输入返回 `SpectralDistribution`。
- 批量 `(n, 3)` 输入返回 `MultiSpectralDistribution`。
- 批量输出通道标签默认为 `sample_0, sample_1, ...`，也可以通过 `labels` 指定。

恢复后的对象可以继续用于：

```python
XYZ = reflectance_to_XYZ(reflectance, illuminant="D65")
```

闭合误差用于验证恢复结果是否满足目标颜色刺激。

## Reflectance library 数据层

`load_reflectance_library(...)` 把已经注册的 UEF 反射谱数据加载为统一波长
shape 的样本矩阵：

```text
reflectances.shape == (n_samples, n_wavelengths)
```

这一层不做新的 recovery 算法，只为后续 basis、PCA、dictionary recovery 提供
稳定的数据输入。默认数据库是 `munsell_matt`，默认 shape 是
`SpectralShape(400, 700, 5)`。这个默认值不是随意的：

- Munsell matt 是经典、相对干净的物体反射谱集合，适合作为第一版反射率先验。
- 400-700 nm / 5 nm 是当前 UEF 运行时反射谱共同覆盖范围，便于混合数据集。
- 反射率不裁剪，保留数据原值；例如纸张数据可能略高于 1。

数据库选择本质上是 recovery 先验，不是中性技术细节。用 Munsell matt 得到的
basis / dictionary 会偏向 Munsell 色样；显式混用 Agfa、paper、forest 等数据会改变
先验分布。`datasets="all_uef"` 只代表当前注册的 UEF 反射谱集合，不代表未来所有
反射谱来源。本模块不支持 `datasets="all"`，避免无意中混用不同来源、测量条件的数据。
