# color.recovery 详细说明

`color.recovery` 负责从低维颜色刺激反推出一条可行光谱。它解决的是反问题：

```text
高维光谱 -> 三通道响应  是多对一
三通道响应 -> 高维光谱  因此不是唯一解
```

本文件解释模块边界和算法语义。逐项 API 用法见
[`API_GUIDE.md`](API_GUIDE.md)。

## 模块职责

当前模块分三层：

```text
target + responses -> effective spectrum
XYZ / xyY + illuminant + CMFs -> reflectance
registered reflectance datasets -> ReflectanceLibrary
```

- `recover_spectrum_*` 恢复 effective spectrum。自发光场景下，它可以解释为 SPD。
- `recover_reflectance_*` 恢复物体反射率，需要 illuminant 和 CMFs。
- `ReflectanceLibrary` 是 PCA / dictionary 的数据库先验输入，不是恢复算法本身。

模块不提供 RGB 入口。RGB、Lab、Luv 等颜色空间应先显式通过 `color.spaces`
转换到 `XYZ`，再进入 recovery。

模块也不接入 `color.generators`。`generators` 负责正向生成理想光谱或数据字典；
`recovery` 负责从目标响应反求一条满足约束的光谱，两者语义不同。

## Spectrum Recovery

通用 spectrum recovery 解决：

```text
target = A @ spectrum
A = k * interval * responses.T
```

`recover_spectrum_from_responses(...)` 是底层入口。其它入口只是加载或转换三通道响应：

- `recover_spectrum_from_XYZ(...)` 使用 XYZ CMFs。
- `recover_spectrum_from_xyY(...)` 先把 xyY 转为 XYZ，再使用 XYZ CMFs。
- `recover_spectrum_from_LMS(...)` 使用 LMS fundamentals。

Spectrum recovery 不知道 illuminant 和物体反射率语义，因此不会提供 PCA、dictionary、
Meng 或 Burns 这类 reflectance-only 方法。

## Reflectance Recovery

反射率恢复构造与 `color.colorimetry.reflectance_to_XYZ(...)` 一致的矩阵：

```text
XYZ = A @ r
A = k * interval * (illuminant * CMFs).T
k = 100 / sum(illuminant * ybar * interval)
```

其中 `r` 是反射率。默认 `bounds=(0, 1)`，适合普通物体反射率。

不要把反射率恢复写成：

```text
先恢复 effective spectrum，再除以 illuminant
```

这样约束施加在 effective spectrum 上，不能保证最终 reflectance 仍处于物理范围内。

## Method Options

入口支持两种 method 写法：

```python
recover_reflectance_from_XYZ(XYZ, method="pca", library=library)
recover_reflectance_from_XYZ(XYZ, method=PCAReflectanceOptions(library=library))
```

字符串写法保留为兼容路径；推荐新代码使用 options 对象。原因很直接：不同算法的参数
差异很大，如果全部塞进一个函数签名，入口会越来越臃肿。

PCA 和 dictionary 必须显式传入 `ReflectanceLibrary`。数据库选择是恢复先验，不是普通
数值细节，因此入口不会通过 `library_datasets` 暗中加载默认库。

当前 method registry 的公共方法是：

```text
spectrum recovery:
  bounded_least_squares
  gaussian
  multi_gaussian
  auto_gaussian

reflectance recovery:
  bounded_least_squares
  burns2019
  meng2015
  pca
  dictionary
```

## Method Families

### Bounded Least-Squares

基础平滑最小二乘：

```text
min ||A r - target||² + smoothness * ||D r||²
subject to lower <= r <= upper
```

`D` 是二阶差分矩阵。它适合作为基线方法：自由度高，通常能较好闭合目标响应，但曲线
形状不一定像真实材料。

### Gaussian / Multi-Gaussian / Auto-Gaussian

这些方法只属于 spectrum recovery。它们恢复的是 emission-like effective spectrum，
不是 reflectance。

- `gaussian`：单峰高斯，适合单峰 LED 或窄带光源。
- `multi_gaussian`：双峰/三峰高斯，适合多峰 LED 或 purple/complementary 方向。
- `auto_gaussian`：策略分发。XYZ 入口下根据主波长分析选择 single 或 multi Gaussian。

`auto_gaussian` 不是新的数学模型。

### Burns 2019

Burns 2019 Method 3 使用变量变换：

```text
rho = (tanh(z) + 1) / 2
min z.T @ D @ z
subject to A @ rho = XYZ
```

这个变换让反射率天然处于 `(0, 1)`。工程实现中还显式处理黑点和白点：

```text
XYZ ≈ 0      -> rho = 0
XYZ ≈ white  -> rho = 1
```

否则边界值会使 Newton 系统病态。该方法不依赖数据库，但接近 object-colour solid
边界时仍可能失败。

### Meng 2015

Meng 2015 把目标闭合作为等式约束：

```text
min sum((r[i+1] - r[i])²)
subject to A @ r = XYZ
           lower <= r <= upper
```

因此它通常比折中型目标更重视 `XYZ` 闭合。如果目标在当前 illuminant、CMFs、
shape 和 bounds 下不可行，优化会失败。

### PCA

PCA 使用 `ReflectanceLibrary` 学习低维基底：

```text
r(λ) ≈ mean(λ) + B @ c
```

实现是在 PCA 子空间中直接优化系数 `c`，并在优化过程中约束重建反射率位于
`bounds` 内。它不是先求 bounded least-squares 再投影到 PCA basis，也不是最后再裁剪。
后处理裁剪会破坏 `XYZ` 闭合，因此物理范围和颜色匹配必须放在同一个优化问题里。

它的优势不在于最小 `XYZ` 闭合误差，而在于把解限制到数据库学到的真实物体反射谱
分布附近。这样通常会得到更自然的曲线，并减少测量噪声被解释成不合理振荡的风险。

代价是自由度低。如果目标样本不在当前 library 的 PCA 子空间附近，或者
`n_components` / regularization 设置保守，闭合误差可能大于 Meng、Burns 或
bounded least-squares。

### Dictionary

Dictionary 使用真实反射谱样本的凸组合：

```text
r(λ) = w @ library.reflectances
w >= 0
sum(w) = 1
```

它的优势是可解释性和保守性：结果由真实测量样本加权得到，不容易生成数据库中完全
没有出现过的光谱类型。

默认 `top_k=120` 表示先在响应空间筛选最接近目标的候选样本，再做凸组合优化。它不是
稀疏正则项，也不保证最终只使用少数样本。若目标不在候选样本响应凸包内，闭合误差
会明显变大。

## 如何评价结果

不同方法回答的问题不同：

```text
想要较小闭合误差          -> Meng / Burns / bounded least-squares
想要更像真实物体反射谱    -> PCA / dictionary
目标材料与 library 接近   -> PCA / dictionary 更有意义
目标材料与 library 不同   -> 数据库方法可能闭合误差较大
```

建议同时检查：

- `XYZ` / response closure error
- 曲线 roughness
- 反射率范围
- 与原始反射谱的 RMSE / MAE
- library 是否符合目标材料类型

因此，PCA / dictionary 误差比自由度更高的方法大，不一定表示算法错误；它可能只是说明
数据库先验和目标分布不匹配。

## Reflectance Library

`load_reflectance_library(...)` 把已注册反射谱数据对齐为统一矩阵：

```text
wavelengths   # (n_wavelengths,)
reflectances  # (n_samples, n_wavelengths)
labels        # 每条样本唯一标签
sources       # 每条样本来源数据集名
shape         # SpectralShape
metadata      # 数据集与样本统计
```

默认库是 `munsell_matt`，默认 shape 是 `SpectralShape(400, 700, 5)`。这个默认值的理由：

- Munsell matt 是经典、相对干净的物体反射谱集合。
- 400-700 nm / 5 nm 是当前 UEF 运行时反射谱共同覆盖范围。
- 数据库选择本身就是先验，不能隐式隐藏。

反射率数据保留原值，不在 library 加载时裁剪到 `[0, 1]`。例如某些纸张数据可能略高于
1；是否裁剪应由具体 recovery 方法的 bounds 或用户数据清洗策略决定。

PCA 和 dictionary 要求 recovery 积分矩阵与 `ReflectanceLibrary` 使用完全相同的
`SpectralShape`。如果显式传入 library，推荐省略 recovery 入口的 `shape`，让入口直接
使用 `library.shape`；若同时传入 `shape`，必须与 library 波长网格一致。

`datasets="all_uef"` 只代表当前注册的 UEF 反射谱集合，不代表未来所有反射谱来源。
模块不支持 `datasets="all"`，避免无意混用不同来源和测量条件。

## 输出对象

- 单个 `(3,)` 输入返回 `SpectralDistribution`。
- 批量 `(n, 3)` 输入返回 `MultiSpectralDistribution`。
- 批量标签默认是 `sample_0, sample_1, ...`，也可以通过 `labels` 指定。

恢复结果可以继续进入 `color.colorimetry` 验证闭合：

```python
XYZ = reflectance_to_XYZ(reflectance, illuminant="D65")
```

## 后续扩展边界

可以继续扩展新的 recovery methods，但应先判断它属于哪一层：

- effective spectrum method：注册到 `SPECTRUM_RECOVERY_METHODS`
- reflectance method：注册到 `REFLECTANCE_RECOVERY_METHODS`
- library-prior method：必须显式接受 `ReflectanceLibrary`

Basis、Smits、sparse dictionary 等可以后续作为新 method 扩展
