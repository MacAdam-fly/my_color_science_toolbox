# color.utils 详细说明

`color.utils` 是全库共享的底层工具层。它不实现颜色科学公式，也不表达具体业务对象，只负责多个模块都会反复遇到的基础问题：

- NumPy 输入如何统一转换为 `float64`。
- 数组最后一维的通道数量如何校验。
- 单点和批量输入如何广播。
- 标量结果和数组结果如何返回。
- `method="..."` 这类参数如何规范化、解析别名和分发。
- datasets / generators 这类资源名如何规范化。
- `[0, 1]`、`[0, 100]`、角度这类纯数值尺度如何显式转换。

一句话原则：

```text
utils 只放工具，不放颜色科学含义。
```

## 设计边界

可以放进 `utils` 的内容：

- 多个模块都会用到的小函数。
- 只依赖标准库和 NumPy 的工具。
- 输入校验、广播、method 解析、名称规范化、简单数值尺度转换。

不应放进 `utils` 的内容：

- 颜色空间转换公式。
- 色差公式。
- 光谱积分公式。
- 色貌模型公式。
- 数据集读取、注册表业务逻辑。
- 只服务某一个模块、且带强领域语义的局部 helper。

例如白点必须为正、波长必须递增、CCT 必须在某个物理范围内，这些虽然也像“校验”，但它们有明确领域含义，应留在对应模块中。

## arrays.py

`arrays.py` 负责统一数组输入、shape 校验和广播行为。

### `as_float_array(value, name="value", finite=True)`

把输入转换为 `np.float64` 数组。

- `finite=True` 时要求所有值有限，遇到 `nan / inf` 抛 `ValueError`。
- `name` 用于错误信息，例如 `XYZ must be finite`。
- 不复制无必要的数据，主要用于函数入口的基础转换。

### `as_float_result(value)`

把结果转换为 `np.float64`，并保留 NumPy 的标量/数组返回习惯。

- 输入是标量形状时返回 NumPy scalar。
- 输入是数组形状时返回数组。

### `as_last_axis(value, size, name="value", finite=True)`

把输入转换为 float 数组，并要求最后一维长度为 `size`。

```python
xy = as_last_axis(xy, 2, name="xy")
XYZ = as_last_axis(XYZ, 3, name="XYZ")
```

它只检查“最后一维通道数”和“有限值”。如果还需要正值、单调递增、范围限制，应由调用模块自己处理。

### `as_last_axis_triplets(value, name="value", finite=True)`

`as_last_axis(value, 3, ...)` 的便捷入口。常用于 `XYZ`、`RGB`、`Lab`、`Luv`、`Oklab`、`Jzazbz` 等三通道坐标。

### `as_last_axis_pairs(value, name="value", finite=True)`

`as_last_axis(value, 2, ...)` 的便捷入口。常用于 `xy`、`uv`、`u'v'` 和二维点坐标。

### `broadcast_last_axis(value_1, value_2, size, name_1="value_1", name_2="value_2", finite=True)`

先校验两个输入最后一维都是 `size`，再用 NumPy 广播到共同形状。适合两个同类型坐标之间的运算。

如果前置维度无法广播，会抛带有两个 shape 的 `ValueError`。

### `broadcast_triplets(value_1, value_2, name_1="value_1", name_2="value_2", finite=True)`

`broadcast_last_axis(..., size=3)` 的便捷入口。常用于 Lab 色差、Oklab 色差和任意三通道坐标差异。

### `broadcast_pairs(value_1, value_2, name_1="value_1", name_2="value_2", finite=True)`

`broadcast_last_axis(..., size=2)` 的便捷入口。常用于两组 `xy` 或两组 `uv` 点。

### `split_last_axis(value)`

把数组最后一维拆成多个通道数组。

```python
L, a, b = split_last_axis(Lab)
x, y = split_last_axis(xy)
```

它不做 float 转换，也不做有限值检查，只是结构拆分工具。

## methods.py

`methods.py` 只负责 `method="..."` 风格参数的注册表分发，不再自己实现字符串 canonical 规则。名字规范化统一来自 `names.py`。

### `canonical_method_name(name)`

这是从 `names.py` re-export 的语义入口，用于 method、option、空间别名、色适应 transform 等名称。

它等价于基础 `canonicalize_name(...)`：忽略大小写，移除空格、连字符、下划线、斜线等非 ASCII 字母数字字符。

```text
"CIE 2000"  -> "cie2000"
"CAM16-UCS" -> "cam16ucs"
"Jz Az Bz"  -> "jzazbz"
"0.1 nm"    -> "01nm"
```

注意：它不适合 dataset/generator 资源名，因为它会把 `"0.1 nm"` 变成 `"01nm"`，丢失小数点语义。资源名应使用 `canonicalize_resource_name(...)`。

### `build_method_index(method_aliases)`

根据方法名和别名表构建查找索引。

```python
ALIASES = {
    "CIE 2000": ("cie2000", "CIEDE2000"),
    "Oklab": ("OKLab", "OKLAB"),
}
```

输出会把主名和所有 alias 都映射回规范方法名：

```python
index["ciede2000"] == "CIE 2000"
index["oklab"] == "Oklab"
```

### `resolve_method(method, method_index, methods)`

把用户传入的 `method` 解析成规范方法名和对应函数。

返回：

```python
canonical_name, function
```

如果未知 method，会抛 `ValueError`，并列出可用方法。

### `filter_kwargs(function, kwargs)`

只保留目标函数签名中接受的关键字参数。通用 dispatch 函数可能收到一批 kwargs，但不同 method 函数只接受其中一部分。

```python
kwargs = filter_kwargs(delta_E_CIE2000, {"textiles": True, "unused": 1})
```

如果 `delta_E_CIE2000` 接受 `textiles` 但不接受 `unused`，结果只保留 `textiles`。

## names.py

`names.py` 是所有名字规范化的统一入口，分为基础名字规则和资源名字规则。

### `canonicalize_name(value)`

基础名字规范化。适合 method、option、空间 alias、transform 名称这类普通标识符。

规则：

- 使用 `casefold()` 忽略大小写。
- 只保留 ASCII 字母和数字。
- 空格、连字符、下划线、斜线、小数点等都会被移除。

```text
"CIE 2000"        -> "cie2000"
"CAM16-UCS"       -> "cam16ucs"
"0.1 nm"          -> "01nm"
"V(λ)"            -> "v"
"10° observer"    -> "10observer"
```

### `canonical_method_name(value)`

method/option/alias 的语义别名，内部直接调用 `canonicalize_name(...)`。保留它是为了让 method 分发代码读起来更自然：

```python
key = canonical_method_name(method)
```

### `canonicalize_resource_name(value)`

资源名字规范化。适合 datasets、generators 和标准数据类别名。

它会先保留颜色科学资源名中的重要语义，再调用基础 `canonicalize_name(...)`：

- 数字之间的小数点转换为 `p`，例如 `0.1 -> 0p1`。
- `°` 转为 `degree`。
- `λ` 转为 `lambda`。

```text
"CIE 1931 XYZ 1 nm" -> "cie1931xyz1nm"
"cie_1931-xyz/1nm" -> "cie1931xyz1nm"
"0.1 nm"           -> "0p1nm"
"V(λ)"             -> "vlambda"
"10° observer"     -> "10degreeobserver"
```

当前使用者：

- `color.datasets`
- `color.generators`
- `datasets.standard_observers` 的类别 alias 解析

不要把基础 `canonicalize_name(...)` 直接用于数据资源注册表，否则可能把 `0.1 nm` 和其它采样间隔名字变得难以区分。

## scale.py

`scale.py` 负责显式的纯数值尺度转换。它只处理数值缩放，不表达白点适应、积分归一化或色貌观察条件。

支持的普通尺度：

```text
"1"         表示 [0, 1] 或相对 1 的数值域
"100"       表示 [0, 100] 或 Y=100 的数值域
"reference" 表示保持当前参考域，不做缩放
```

支持的角度尺度额外包括：

```text
"degrees"   表示角度制
```

### `to_domain_1(value, source_scale="100", scale_factor=100.0, name="value")`

把输入转换到 `[0, 1]` 数值域。

- `source_scale="100"`：除以 `scale_factor`，默认除以 `100`。
- `source_scale="1"`：不缩放，只返回 float 结果。
- `source_scale="reference"`：不缩放，只返回 float 结果。

### `to_domain_100(value, source_scale="1", scale_factor=100.0, name="value")`

把输入转换到 `[0, 100]` 数值域。

- `source_scale="1"`：乘以 `scale_factor`，默认乘以 `100`。
- `source_scale="100"`：不缩放。
- `source_scale="reference"`：不缩放。

### `from_range_1(value, target_scale="100", scale_factor=100.0, name="value")`

把一个已经处于 `[0, 1]` range 的值转换到目标尺度。

- `target_scale="100"`：乘以 `scale_factor`。
- `target_scale="1"`：不缩放。
- `target_scale="reference"`：不缩放。

### `from_range_100(value, target_scale="1", scale_factor=100.0, name="value")`

把一个已经处于 `[0, 100]` range 的值转换到目标尺度。

- `target_scale="1"`：除以 `scale_factor`。
- `target_scale="100"`：不缩放。
- `target_scale="reference"`：不缩放。

### `to_domain_degrees(value, source_scale="1", scale_factor=360.0, name="value")`

把角度类数值转换为 degrees。

- `source_scale="1"`：`1.0` 表示一整圈，乘以 `360`。
- `source_scale="100"`：`100` 表示一整圈，乘以 `360 / 100`。
- `source_scale="degrees"`：已经是角度，不缩放。
- `source_scale="reference"`：不缩放。

### `from_range_degrees(value, target_scale="1", scale_factor=360.0, name="value")`

把 degrees 转换到目标角度尺度。

- `target_scale="1"`：除以 `360`。
- `target_scale="100"`：乘以 `100 / 360`。
- `target_scale="degrees"`：不缩放。
- `target_scale="reference"`：不缩放。

## 使用建议

- 新模块如果只需要数组 shape / finite 校验，优先使用 `arrays.py`。
- 新模块如果有 `method=...`，优先使用 `methods.py`。
- 新的数据资源注册表如果需要宽松匹配名称，优先使用 `canonicalize_resource_name(...)`。
- 新模块如果出现显式 `[0, 1] <-> [0, 100]` 缩放，优先使用 `scale.py`。
- 如果校验逻辑包含领域含义，例如“白点必须为正”“波长必须递增”“CCT 必须在范围内”，应留在对应模块中。
