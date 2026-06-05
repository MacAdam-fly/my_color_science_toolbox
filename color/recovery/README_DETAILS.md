# color.recovery 详细说明

`color.recovery` 负责从低维颜色刺激反推出一个可行光谱。当前分成两层：

```text
target + 三通道 responses -> effective spectrum
XYZ / xyY + illuminant + CMFs -> reflectance
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
```

但 spectrum recovery 和 reflectance recovery 使用分开的 registry，后续可以分别添加 PCA、basis、Meng、Smits 等方法。

## 输出

- 单个 `(3,)` 输入返回 `SpectralDistribution`。
- 批量 `(n, 3)` 输入返回 `MultiSpectralDistribution`。
- 批量输出通道标签默认为 `sample_0, sample_1, ...`，也可以通过 `labels` 指定。

恢复后的对象可以继续用于：

```python
XYZ = reflectance_to_XYZ(reflectance, illuminant="D65")
```

闭合误差用于验证恢复结果是否满足目标颜色刺激。
