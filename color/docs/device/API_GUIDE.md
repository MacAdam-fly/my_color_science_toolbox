# color.device API 使用指南

本文档覆盖 `color.device.__all__` 中的顶层 API。

## API 总览

| API | 功能 |
| --- | --- |
| `PrimaryResponseDisplay` | 保存每个基色的 `LMS/XYZ/mel` 响应矩阵 |
| `melanopic_silent_range` | 在固定 LMS 或 XYZ 下求 melanopic 最小和最大端点 |

内部结果对象不作为顶层 API 单独导出；它只作为 `melanopic_silent_range(...)` 的返回值出现。

## `PrimaryResponseDisplay`

用途：保存多基色显示器的 primary response matrix。

`response_names` 必填，避免矩阵列语义不清。允许的响应列名只有：

```text
l, m, s, x, y, z, mel
```

LMS + mel：

```python
from color.device import PrimaryResponseDisplay

display = PrimaryResponseDisplay(
    [
        [0.70, 0.30, 0.02, 0.10],
        [0.25, 0.80, 0.10, 0.20],
        [0.05, 0.15, 0.70, 0.65],
        [0.20, 0.55, 0.45, 0.95],
    ],
    response_names=("l", "m", "s", "mel"),
    primary_names=("R", "G", "B", "C"),
)
```

XYZ + mel：

```python
display = PrimaryResponseDisplay(
    matrix,
    response_names=("X", "Y", "Z", "mel"),
)
```

完整响应矩阵：

```python
display = PrimaryResponseDisplay(
    matrix,
    response_names=("l", "m", "s", "X", "Y", "Z", "mel"),
)
```

计算某组权重的响应：

```python
weights = [0.35, 0.45, 0.30, 0.20]

responses = display.responses_from_weights(weights)
mel = display.melanopic_from_weights(weights)
```

如果 display 含对应列，也可以访问：

```python
LMS = display.LMS_from_weights(weights)
XYZ = display.XYZ_from_weights(weights)
```

从 primary SPD 构造完整响应矩阵：

```python
display = PrimaryResponseDisplay.from_primary_spds(primary_spds)
print(display.response_names)  # ("l", "m", "s", "x", "y", "z", "mel")
```

窄入口：

```python
lms_display = PrimaryResponseDisplay.from_primary_spds_lms_mel(primary_spds)
xyz_display = PrimaryResponseDisplay.from_primary_spds_xyz_mel(primary_spds)
```

注意：`from_primary_spds(...)` 默认同时计算 CIE 2006 10° LMS、CIE 2012 10° XYZ 和 CIE S 026 melanopic 响应；不会引入 rod/rh。

## `melanopic_silent_range`

用途：一次性求同一 LMS 或 XYZ 目标下 melanopic 的低端和高端。

LMS-silent：

```python
import numpy as np

from color.device import melanopic_silent_range

baseline = np.array([0.35, 0.45, 0.30, 0.20])
target_LMS = display.LMS_from_weights(baseline)

low, high = melanopic_silent_range(display, target_LMS, held="LMS")

print(low.weights)
print(high.weights)
print(low.melanopic, high.melanopic)
```

XYZ-silent：

```python
target_XYZ = display.XYZ_from_weights(baseline)

low, high = melanopic_silent_range(display, target_XYZ, held="XYZ")
```

批量目标：

```python
targets = display.LMS_from_weights([
    [0.35, 0.45, 0.30, 0.20],
    [0.25, 0.50, 0.25, 0.25],
])

low, high = melanopic_silent_range(display, targets, held="LMS")
print(low.weights.shape)  # (2, 4)
```

返回值：

```text
low, high
```

其中 `low` 和 `high` 都是结果对象，常用字段为：

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

求解路径：

- 四基色且保持三个响应时，内部使用一维零空间解析 fast path；批量目标会整批计算。
- 五基色及以上，内部使用 `scipy.optimize.linprog(method="highs")` 分别求 low/high。

用户通常不需要单独求某一个端点；需要最大或最小时，直接取 `low` 或 `high` 即可。
