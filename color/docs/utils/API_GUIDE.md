# color.utils API 使用指南

本文档对应 `color.utils` 顶层公开 API。`utils` 是全库底层工具层，只处理数组、名字、method 分发和数值尺度这类机械问题，不实现颜色科学公式。

完整设计边界见 [`README_DETAILS.md`](README_DETAILS.md)，英文快速入口见 [`README.md`](README.md)。

## API 总览

### 数组输入与广播

| API | 用途 |
| --- | --- |
| `as_float_array` | 转成 `float64` 数组，并可检查 finite |
| `as_float_result` | 将 0 维数组转成 NumPy scalar，数组保持数组 |
| `as_last_axis` | 校验最后一维长度为指定通道数 |
| `as_last_axis_triplets` | 校验最后一维为 3 |
| `as_last_axis_pairs` | 校验最后一维为 2 |
| `broadcast_last_axis` | 校验并广播两个固定通道数组 |
| `broadcast_triplets` | 广播两个三通道数组 |
| `broadcast_pairs` | 广播两个二维数组 |
| `split_last_axis` | 拆分最后一维通道 |

### 名字规范化

| API | 用途 |
| --- | --- |
| `canonicalize_name` | 普通名字/alias 规范化 |
| `canonicalize_resource_name` | 数据资源名规范化，保留 `0.1 nm`、`λ`、`°` 语义 |
| `canonical_method_name` | method/option 语义入口 |

### Method 分发

| API | 用途 |
| --- | --- |
| `build_method_index` | 从主方法名和 aliases 构建查询索引 |
| `resolve_method` | 解析用户传入 method 并返回对应函数 |
| `filter_kwargs` | 只保留目标函数签名接受的 kwargs |

### 数值尺度

| API | 用途 |
| --- | --- |
| `to_domain_1` | 转到 `[0, 1]` 数值域 |
| `to_domain_100` | 转到 `[0, 100]` 数值域 |
| `from_range_1` | 从 `[0, 1]` range 转到目标尺度 |
| `from_range_100` | 从 `[0, 100]` range 转到目标尺度 |
| `to_domain_degrees` | 转到角度制 degrees |
| `from_range_degrees` | 从角度制 degrees 转到目标尺度 |

## `as_float_array(value, name="value", finite=True)`

把输入转换为 `np.float64` 数组。

```python
from color.utils import as_float_array

values = as_float_array([1, 2, 3], name="values")
print(values.dtype)
```

允许非有限值的场景：

```python
import numpy as np
from color.utils import as_float_array

values = as_float_array([1.0, np.nan], finite=False)
```

注意：它只检查数值类型和 finite，不检查 shape、正值、范围或颜色科学语义。

## `as_float_result(value)`

用于函数返回阶段，让标量结果保持 NumPy scalar，批量结果保持数组。

```python
import numpy as np
from color.utils import as_float_result

print(as_float_result(np.array(1.25)))      # np.float64(1.25)
print(as_float_result(np.array([1.0, 2.0])))  # array([1., 2.])
```

## `as_last_axis(value, size, name="value", finite=True)`

校验输入最后一维长度。

```python
from color.utils import as_last_axis

xy = as_last_axis([[0.3, 0.3], [0.4, 0.2]], 2, name="xy")
XYZ = as_last_axis([95.05, 100.0, 108.88], 3, name="XYZ")
```

图像式输入也可以：

```python
import numpy as np
from color.utils import as_last_axis

rgb_image = as_last_axis(np.zeros((64, 64, 3)), 3, name="RGB image")
```

## `as_last_axis_triplets(value, name="value", finite=True)`

三通道坐标便捷入口。

```python
from color.utils import as_last_axis_triplets

Lab = as_last_axis_triplets([50.0, 2.0, -3.0], name="Lab")
```

批量输入：

```python
XYZ = as_last_axis_triplets(
    [[95.05, 100.0, 108.88], [41.24, 21.26, 1.93]],
    name="XYZ",
)
```

常用于 `XYZ`、`RGB`、`Lab`、`Luv`、`Oklab`、`Jzazbz` 等三通道数据。

## `as_last_axis_pairs(value, name="value", finite=True)`

二维坐标便捷入口。

```python
from color.utils import as_last_axis_pairs

xy = as_last_axis_pairs([0.3127, 0.3290], name="xy")
```

批量输入：

```python
points = as_last_axis_pairs([[0.3, 0.3], [0.6, 0.2]], name="points")
```

常用于 `xy`、`uv1960`、`u'v'1976` 和二维绘图点。

## `broadcast_last_axis(value_1, value_2, size, ...)`

先校验两个输入的最后一维长度，再广播前置维度。

```python
from color.utils import broadcast_last_axis

a, b = broadcast_last_axis(
    [50.0, 0.0, 0.0],
    [[50.0, 1.0, 0.0], [50.0, 0.0, 2.0]],
    3,
    name_1="Lab_1",
    name_2="Lab_2",
)

print(a.shape)  # (2, 3)
print(b.shape)  # (2, 3)
```

适合写通用的两输入计算函数，例如色差、几何距离、坐标差。

## `broadcast_triplets(value_1, value_2, ...)`

三通道广播便捷入口。

```python
import numpy as np
from color.utils import broadcast_triplets

Lab_1, Lab_2 = broadcast_triplets(
    [50.0, 0.0, 0.0],
    np.array([[50.0, 1.0, 0.0], [50.0, 0.0, 2.0]]),
    name_1="Lab_1",
    name_2="Lab_2",
)
```

## `broadcast_pairs(value_1, value_2, ...)`

二维坐标广播便捷入口。

```python
from color.utils import broadcast_pairs

xy_1, xy_2 = broadcast_pairs(
    [0.3127, 0.3290],
    [[0.30, 0.32], [0.40, 0.35]],
    name_1="whitepoint_xy",
    name_2="sample_xy",
)
```

## `split_last_axis(value)`

把最后一维拆成通道。

```python
from color.utils import as_last_axis_triplets, split_last_axis

Lab = as_last_axis_triplets([[50.0, 1.0, 2.0], [60.0, -3.0, 4.0]])
L, a, b = split_last_axis(Lab)
```

注意：`split_last_axis(...)` 不做 float 转换和 finite 检查。需要校验时先调用 `as_last_axis_*`。

## `canonicalize_name(value)`

普通名字规范化：忽略大小写和常见分隔符，只保留 ASCII 字母数字。

```python
from color.utils import canonicalize_name

print(canonicalize_name("CAM16-UCS"))  # "cam16ucs"
print(canonicalize_name("Jz Az Bz"))   # "jzazbz"
```

基础规则会丢失资源名里的特殊语义：

```python
print(canonicalize_name("0.1 nm"))  # "01nm"
```

因此 dataset/generator 资源名应使用 `canonicalize_resource_name(...)`。

## `canonicalize_resource_name(value)`

数据资源名规范化。它会保留小数采样间隔和常见科学符号语义。

```python
from color.utils import canonicalize_resource_name

print(canonicalize_resource_name("0.1 nm"))        # "0p1nm"
print(canonicalize_resource_name("V(λ)"))          # "vlambda"
print(canonicalize_resource_name("10° observer"))  # "10degreeobserver"
```

适合 `datasets`、`generators` 这种资源注册表，不适合普通 method 分发。

## `canonical_method_name(value)`

method/option/transform 名称的语义入口，底层等价于 `canonicalize_name(...)`。

```python
from color.utils import canonical_method_name

print(canonical_method_name("CIE 2000"))      # "cie2000"
print(canonical_method_name("Bounded LSQ"))   # "boundedlsq"
```

保留这个函数主要是为了代码可读性：看到它就知道当前在处理 method/option，而不是数据资源名。

## `build_method_index(method_aliases)`

从主方法名和 alias 构建 canonical 查询表。

```python
from color.utils import build_method_index

ALIASES = {
    "CIE 2000": ("cie2000", "CIEDE2000"),
    "CMC": ("cmc1984",),
}

METHOD_INDEX = build_method_index(ALIASES)
print(METHOD_INDEX["ciede2000"])  # "CIE 2000"
```

主方法名本身也会加入索引。

## `resolve_method(method, method_index, methods)`

解析用户传入 method，并返回主方法名和函数对象。

```python
from color.utils import build_method_index, resolve_method

def method_a(x):
    return x + 1

METHODS = {"Method A": method_a}
METHOD_INDEX = build_method_index({"Method A": ("a", "method-a")})

name, function = resolve_method("method-a", METHOD_INDEX, METHODS)
print(name)         # "Method A"
print(function(2))  # 3
```

未知 method 会抛 `ValueError`，并列出可用方法。

## `filter_kwargs(function, kwargs)`

只保留目标函数签名接受的关键字参数。

```python
from color.utils import filter_kwargs

def f(x, *, alpha=1.0):
    return x * alpha

kwargs = {"alpha": 2.0, "unused": True}
print(filter_kwargs(f, kwargs))  # {"alpha": 2.0}
```

注意：这是静默过滤。如果 API 需要对未知参数严格报错，应在调用前自行检查。

## `to_domain_1(value, source_scale="100", ...)`

把输入转到 `[0, 1]` 数值域。

```python
from color.utils import to_domain_1

print(to_domain_1([0, 50, 100], source_scale="100"))
# [0.  0.5 1. ]
```

从已经是 `[0, 1]` 的输入进入：

```python
print(to_domain_1([0, 0.5, 1], source_scale="1"))
# [0.  0.5 1. ]
```

## `to_domain_100(value, source_scale="1", ...)`

把输入转到 `[0, 100]` 数值域。

```python
from color.utils import to_domain_100

print(to_domain_100([0, 0.5, 1], source_scale="1"))
# [  0.  50. 100.]
```

输入已经是 `[0, 100]` 时：

```python
print(to_domain_100([0, 50, 100], source_scale="100"))
# [  0.  50. 100.]
```

## `from_range_1(value, target_scale="100", ...)`

把已经处于 `[0, 1]` range 的值转到目标尺度。

```python
from color.utils import from_range_1

print(from_range_1([0, 0.5, 1], target_scale="100"))
# [  0.  50. 100.]
```

目标也可以保持 `[0, 1]`：

```python
print(from_range_1([0, 0.5, 1], target_scale="1"))
# [0.  0.5 1. ]
```

## `from_range_100(value, target_scale="1", ...)`

把已经处于 `[0, 100]` range 的值转到目标尺度。

```python
from color.utils import from_range_100

print(from_range_100([0, 50, 100], target_scale="1"))
# [0.  0.5 1. ]
```

目标也可以保持 `[0, 100]`：

```python
print(from_range_100([0, 50, 100], target_scale="100"))
# [  0.  50. 100.]
```

## `to_domain_degrees(value, source_scale="1", ...)`

把角度类输入转到 degrees。

```python
from color.utils import to_domain_degrees

print(to_domain_degrees(0.5, source_scale="1"))       # 180.0
print(to_domain_degrees(50, source_scale="100"))      # 180.0
print(to_domain_degrees(180, source_scale="degrees")) # 180.0
```

## `from_range_degrees(value, target_scale="1", ...)`

把 degrees 转到目标角度尺度。

```python
from color.utils import from_range_degrees

print(from_range_degrees(180, target_scale="1"))        # 0.5
print(from_range_degrees(180, target_scale="100"))      # 50.0
print(from_range_degrees(180, target_scale="degrees"))  # 180.0
```

## 常见组合模式

### 写一个三通道批量距离函数

```python
import numpy as np
from color.utils import broadcast_triplets, as_float_result


def distance_3d(a, b):
    a, b = broadcast_triplets(a, b, name_1="a", name_2="b")
    return as_float_result(np.linalg.norm(a - b, axis=-1))
```

### 写一个 method 分发入口

```python
from color.utils import build_method_index, resolve_method, filter_kwargs


def linear(x, *, scale=1):
    return scale * x


def square(x):
    return x * x


METHODS = {"linear": linear, "square": square}
METHOD_INDEX = build_method_index({"linear": ("lin",), "square": ("sqr",)})


def apply_method(x, method="linear", **kwargs):
    name, function = resolve_method(method, METHOD_INDEX, METHODS)
    return function(x, **filter_kwargs(function, kwargs))
```

### 区分普通名字和资源名字

```python
from color.utils import canonicalize_name, canonicalize_resource_name

print(canonicalize_name("0.1 nm"))           # "01nm"
print(canonicalize_resource_name("0.1 nm"))  # "0p1nm"
```

如果这个字符串是方法名，`"01nm"` 通常没问题；如果它是数据资源名，`"0p1nm"` 才能保留 0.1 nm 采样间隔语义。
