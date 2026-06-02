# color.recovery 详细说明

`color.recovery` 负责从低维颜色刺激反推出一个可行的反射谱。第一版只做：

```text
XYZ / xyY -> reflectance
```

不做 `sRGB` 入口，不接入 `generators`，也不做自发光光谱恢复。

## 模块边界

恢复反射谱是反问题。同一个 `XYZ` 在同一个照明体和观察者下可以对应很多条反射谱，因此这里的结果不是“真实光谱”，而是在约束条件下求得的一条可行反射谱。

如果输入来自 RGB、Lab、Luv 等空间，应先显式使用 `color.spaces` 转为 `XYZ`：

```python
XYZ = convert_color(value, "Lab", "XYZ")
reflectance = recover_reflectance_from_XYZ(XYZ)
```

## 数学模型

当前实现构造与 `color.colorimetry.reflectance_to_XYZ(...)` 一致的线性积分矩阵：

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

## 输出

- 单个 `(3,)` 输入返回 `SpectralDistribution`。
- 批量 `(n, 3)` 输入返回 `MultiSpectralDistribution`。
- 批量输出通道标签默认为 `sample_0, sample_1, ...`，也可以通过 `labels` 指定。

恢复后的对象可以继续用于：

```python
XYZ = reflectance_to_XYZ(reflectance, illuminant="D65")
```

闭合误差用于验证恢复结果是否满足目标颜色刺激。
