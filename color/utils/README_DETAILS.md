# color.utils 详细说明

`color.utils` 是全库共享的底层工具层。它不实现颜色科学公式，也不表达业务对象，只负责多个模块都会反复遇到的基础问题：

- NumPy 输入如何统一转换为 `float64`。
- 最后一维通道数如何校验。
- 单点和批量输入如何广播。
- 标量结果和数组结果如何返回。
- `method="..."` 参数如何规范化、解析别名和分发。
- `[0, 1]`、`[0, 100]`、角度这类纯数值尺度如何显式转换。

## 设计边界

可以放进 `utils` 的内容：

- 多个模块都会用到的小函数。
- 只依赖标准库和 NumPy 的工具。
- 输入校验、广播、method 解析、简单数值尺度转换。

不应该放进 `utils` 的内容：

- 颜色空间转换公式。
- 色差公式。
- 光谱积分公式。
- 色貌模型公式。
- 数据集读取或注册表业务逻辑。
- 只服务某一个模块、且带强领域语义的局部 helper。

一句话原则：

```text
utils 只放“工具”，不放“颜色科学含义”。
```

## arrays.py

`arrays.py` 负责统一数组输入和输出行为。

常用入口：

```python
as_float_array(value, name="value", finite=True)
as_float_result(value)
as_last_axis(value, size, name="value", finite=True)
as_last_axis_triplets(value, name="value", finite=True)
as_last_axis_pairs(value, name="value", finite=True)
broadcast_last_axis(value_1, value_2, size, ...)
broadcast_triplets(...)
broadcast_pairs(...)
split_last_axis(value)
```

典型用法：

```python
XYZ = as_last_axis_triplets(XYZ, name="XYZ")
xy = as_last_axis_pairs(xy, name="xy")
Lab_1, Lab_2 = broadcast_triplets(Lab_1, Lab_2, name_1="Lab_1", name_2="Lab_2")
L, a, b = split_last_axis(Lab)
```

这类 helper 只处理“数组形状和有限值”问题。如果某个参数要求正值、要求单个白点、要求波长严格递增，这些仍应由对应模块自己校验。

## methods.py

`methods.py` 负责统一处理 `method="..."` 风格参数。

常用入口：

```python
canonical_method_name(name)
build_method_index(method_aliases)
resolve_method(method, method_index, methods)
filter_kwargs(function, kwargs)
```

典型用法：

```python
METHODS = {"CIE 2000": delta_E_CIE2000}
ALIASES = {"CIE 2000": ("cie2000", "CIEDE2000")}
INDEX = build_method_index(ALIASES)

_, function = resolve_method("CIEDE2000", INDEX, METHODS)
result = function(a, b, **filter_kwargs(function, kwargs))
```

`canonical_method_name(...)` 会忽略大小写、空格、下划线和连字符：

```text
"CIE 2000"  -> "cie2000"
"CAM16-UCS" -> "cam16ucs"
"Jz Az Bz"  -> "jzazbz"
```

## scale.py

`scale.py` 负责显式的纯数值尺度转换。它主要用于减少 `[0, 1]` 与 `[0, 100]` 混用造成的误解，尤其适合 `XYZ`、相对亮度、归一化角度等场景。

常用入口：

```python
to_domain_1(value, source_scale="100", scale_factor=100.0)
to_domain_100(value, source_scale="1", scale_factor=100.0)
from_range_1(value, target_scale="100", scale_factor=100.0)
from_range_100(value, target_scale="1", scale_factor=100.0)
to_domain_degrees(value, source_scale="1", scale_factor=360.0)
from_range_degrees(value, target_scale="1", scale_factor=360.0)
```

示例：

```python
XYZ_relative = to_domain_1(XYZ_Y100)
XYZ_Y100 = to_domain_100(XYZ_relative)
h_degrees = to_domain_degrees(h_normalized)
h_normalized = from_range_degrees(h_degrees)
```

`source_scale="reference"` 或 `target_scale="reference"` 表示不做缩放，只返回 float copy。这适合某些函数接收 scale 参数但需要保持参考域原样的情况。
