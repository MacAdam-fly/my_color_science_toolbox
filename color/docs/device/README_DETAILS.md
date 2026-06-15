# color.device 详细说明

## AI Usage Notes

- Use this module when solving melanopic/ipRGC silent substitution from primary response matrices or primary SPDs.
- Do not use this module as a general multi-primary RGB color-space converter, ICC/LUT system, display calibration suite, or gamut coverage tool.
- Key assumptions: response columns must be explicitly named; `mel` is required; held responses are currently `LMS` or `XYZ`; optimization changes melanopic response while holding the selected triplet fixed.
- Common mistakes: passing an `XYZ+mel` matrix without declaring response names; using `gamut` for silent substitution; expecting unique multi-primary drive weights.
- Related modules: use `spectra`/`colorimetry` to derive primary responses, `gamut` for reachable color boundaries, and `plot`/`io` for result visualization.

`color.device` 用来处理显示设备 primary weights、响应矩阵和设备驱动优化。
当前版本只实现多基色显示器的 melanopic / ipRGC 沉默替代：

```text
保持 LMS 或 XYZ 三刺激响应不变，寻找 melanopic 响应的最小端点和最大端点。
```

逐项顶层 API 的最小用法见 [`API_GUIDE.md`](API_GUIDE.md)。本文档只说明模块边界和求解语义。

## 模块边界

`color.device` 不等同于 `color.gamut`。

- `color.gamut` 关注某个颜色刺激是否在设备基色可达域内，以及色域边界在哪里。
- `color.device` 关注在给定可达响应下，primary weights 应该如何选择。

沉默替代不是普通颜色空间转换。多基色显示器中，同一个 LMS 或 XYZ 响应通常对应多组 primary weights；这些不同权重可以产生不同的 melanopic / ipRGC 激活。

当前模块不处理：

- RGB/RGBC 颜色空间转换。
- ICC、LUT、显示器校准。
- 时间调制。
- rod-silent 或 scotopic-control 约束。
- 任意多目标优化。

这些能力可以后续扩展，但不进入当前版本的公共边界。

## 响应矩阵优先

核心输入是响应矩阵：

```text
primary_responses.shape == (n_primaries, n_responses)
```

其中行是显示器基色，列是响应通道。`response_names` 必须显式传入，避免把 `XYZ+mel` 矩阵误当成 `LMS+mel` 矩阵使用。

允许的响应列名只有：

```text
l, m, s, x, y, z, mel
```

规则：

- `mel` 必须存在。
- `l/m/s` 或 `x/y/z` 至少完整存在一组。
- 输入大小写宽松，内部统一为小写。
- canonical 后重复的列名会报错，例如 `("X", "x", "mel")`。

## 从 primary SPD 构造响应

`PrimaryResponseDisplay.from_primary_spds(...)` 是从光谱基色构造响应矩阵的完整入口，默认输出：

```text
l, m, s, x, y, z, mel
```

默认使用：

- CIE 2006 10° LMS linear-energy fundamentals。
- CIE 2012 10° XYZ CMFs。
- CIE S 026 melanopic / ipRGC action spectrum。
- melanopic 曲线的 `380-780 nm / 1 nm` 采样域。

如果只需要窄响应矩阵，可以使用：

```python
PrimaryResponseDisplay.from_primary_spds_lms_mel(...)
PrimaryResponseDisplay.from_primary_spds_xyz_mel(...)
```

ipRGC/melanopic 数据不区分 2° / 10°。ipRGC 主要分布在外周，通常讨论外周 ipRGC 激活；cone fundamentals 或 XYZ CMFs 的观察者视角由用户选择，默认使用 10°。

## 求解语义

公共求解入口只有：

```python
melanopic_silent_range(display, target_responses, held="LMS")
```

它一次返回两个端点：

```text
low, high = melanopic_silent_range(...)
```

其中：

- `low` 是 melanopic 响应最小的可行权重。
- `high` 是 melanopic 响应最大的可行权重。

约束为：

```text
M_held @ w = target_responses
0 <= w <= 1
minimize / maximize M_mel @ w
```

`held` 只支持：

```text
held="LMS" -> 保持 l/m/s
held="XYZ" -> 保持 x/y/z
```

少于四个基色时，在保持三个响应不变的同时调节 melanopic 没有自由度，因此会直接报错。

## 四基色 fast path 与多基色 LP

当显示器正好有四个基色，并保持三个响应不变时，可行解是一维零空间：

```text
w = w0 + t z
```

此时 `melanopic_silent_range(...)` 使用解析 fast path：

1. 求一个 particular solution `w0`。
2. 求保持响应不变的零空间方向 `z`。
3. 根据权重边界得到可行 `t` 区间。
4. 根据 melanopic 斜率在区间两端直接得到 low/high。

批量目标下，四基色路径会预计算 held matrix 的伪逆和零空间方向，然后用 NumPy 一次性计算所有目标的 `w0` 和可行 `t` 区间；不会逐点调用线性规划。

五个或更多基色时，零空间维度大于一。在 box constraints 下，全局最小/最大 melanopic 端点是线性规划问题，不能用普通 `numpy.linalg` 一次求出。因此当前实现继续用 `scipy.optimize.linprog(method="highs")` 分别求 low/high。

## 批量目标

`target_responses` 支持：

```text
(3,)
(..., 3)
```

批量目标下，四基色情况走整批解析 fast path；五基色及以上仍逐点走线性规划。任一点不可行时，错误信息会包含失败的 `flat index`。

## 返回结果

`melanopic_silent_range(...)` 返回 `(low, high)`。每个结果对象包含：

```text
weights           求解得到的 primary weights
responses         当前 weights 产生的完整响应向量
target_responses  请求保持的 LMS 或 XYZ 目标
melanopic         当前 melanopic 响应
held              LMS 或 XYZ
objective         minimize_mel 或 maximize_mel
residual          held response residual
success           求解是否成功
```

结果对象类型保留在 `color.device.silent_substitution` 子模块中，顶层 `color.device` 不单独导出它。
