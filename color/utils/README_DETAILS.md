# color.utils - 详细说明

`color.utils` 是全库共享的底层工具层。它不实现颜色科学公式，也不表达具体科学对象，只处理多个模块反复遇到的基础机械问题：

- NumPy 输入如何统一转成 `float64`。
- 最后一维坐标通道数量如何校验。
- 单点和批量输入如何广播。
- 标量结果和数组结果如何保持 NumPy 风格返回。
- `method="..."` 这类参数如何做别名解析和函数分发。
- 普通名字、method 名字、数据资源名字如何 canonicalize。
- `[0, 1]`、`[0, 100]`、角度制这些纯数值尺度如何显式转换。

一句话边界：

```text
utils 只放通用工具，不放颜色科学含义。
```

## 模块结构

| 文件 | 职责 |
| --- | --- |
| `arrays.py` | 数组转换、shape 校验、广播、拆分最后一维 |
| `names.py` | 名称规范化：普通名、method 名、资源名 |
| `methods.py` | method 注册表、别名解析、dispatch、kwargs 过滤 |
| `scale.py` | 显式数值尺度转换 |

`utils` 是底层模块，不应该依赖 `spaces`、`colorimetry`、`appearance`、`difference`、`spectra`、`datasets` 等上层模块。

## 设计边界

适合放入 `utils`：

- 多个模块都会用到的小工具。
- 标准库和 NumPy 就能完成的基础逻辑。
- 不带明确颜色科学语义的输入处理。
- 名称 canonical、method dispatch、纯数值尺度转换。

不适合放入 `utils`：

- 颜色空间转换公式。
- 色差公式。
- 光谱积分公式。
- 色貌模型公式。
- 数据集业务注册逻辑。
- 只服务某一个模块、且带强领域语义的 helper。

例如：

```text
白点必须为正          -> 色适应 / 空间模块自己的语义
波长必须严格递增      -> spectra 自己的语义
CCT 必须在物理范围内  -> temperature 自己的语义
观察条件必须合法      -> appearance 自己的语义
```

这些虽然也是“校验”，但不是通用工具。

## arrays.py

`arrays.py` 负责数组输入的机械处理。

### as_float_array

```python
as_float_array(value, name="value", finite=True)
```

把输入转换为 `np.float64` 数组。

行为：

- 使用 `np.asarray(value, dtype=np.float64)`。
- `finite=True` 时要求所有元素有限。
- 遇到 `nan` 或 `inf` 时抛 `ValueError`。
- `name` 用于错误信息。

示例：

```python
XYZ = as_float_array(XYZ, name="XYZ")
```

它不检查 shape，也不检查正值或范围。

### as_float_result

```python
as_float_result(value)
```

把结果转换为 `np.float64`，并保留 NumPy 的标量/数组返回习惯。

示例：

```python
as_float_result(np.array(1.2))
# np.float64(1.2)

as_float_result(np.array([1.2, 3.4]))
# array([1.2, 3.4])
```

适合函数结尾使用，避免标量输入时返回奇怪的 0 维数组。

### as_last_axis

```python
as_last_axis(value, size, name="value", finite=True)
```

把输入转换为 float 数组，并要求最后一维长度为 `size`。

示例：

```python
xy = as_last_axis(xy, 2, name="xy")
XYZ = as_last_axis(XYZ, 3, name="XYZ")
```

合法输入：

```text
(3,)       单个三通道坐标
(n, 3)     一批三通道坐标
(h, w, 3)  图像式三通道坐标
```

非法输入：

```text
()       没有最后一维
(2,)    期待 3 通道时通道数不对
(n, 4)  期待 3 通道时通道数不对
```

### as_last_axis_triplets

```python
as_last_axis_triplets(value, name="value", finite=True)
```

等价于：

```python
as_last_axis(value, 3, name=name, finite=finite)
```

常用于：

```text
XYZ
RGB
Lab
Luv
Oklab
Jzazbz
CAM02-UCS / CAM16-UCS
```

### as_last_axis_pairs

```python
as_last_axis_pairs(value, name="value", finite=True)
```

等价于：

```python
as_last_axis(value, 2, name=name, finite=finite)
```

常用于：

```text
xy
uv
u'v'
二维几何点
```

### broadcast_last_axis

```python
broadcast_last_axis(
    value_1,
    value_2,
    size,
    name_1="value_1",
    name_2="value_2",
    finite=True,
)
```

先分别校验两个输入最后一维长度为 `size`，再用 NumPy 广播到共同形状。

适合两个同类坐标之间的运算，例如色差：

```python
Lab_1, Lab_2 = broadcast_last_axis(Lab_1, Lab_2, 3)
```

如果前置维度无法广播，会抛出包含两个 shape 的 `ValueError`。

### broadcast_triplets

```python
broadcast_triplets(value_1, value_2, name_1="value_1", name_2="value_2", finite=True)
```

三通道坐标广播便捷入口。常用于：

```text
Lab 色差
Oklab 色差
Jzazbz 色差
XYZ / RGB 批量比较
```

### broadcast_pairs

```python
broadcast_pairs(value_1, value_2, name_1="value_1", name_2="value_2", finite=True)
```

二维坐标广播便捷入口。常用于：

```text
xy 点比较
uv 点比较
二维几何计算
```

### split_last_axis

```python
split_last_axis(value)
```

把最后一维拆成多个通道数组：

```python
L, a, b = split_last_axis(Lab)
x, y = split_last_axis(xy)
```

它只做结构拆分，不做 float 转换和有限值检查。如果需要这些检查，应先调用 `as_last_axis_*`。

## names.py

`names.py` 是名字 canonicalization 的唯一规则来源。

### canonicalize_name

```python
canonicalize_name(value)
```

基础名字规范化，适合普通 alias、method、option、空间名等。

规则：

- `strip()` 去掉首尾空白。
- `casefold()` 忽略大小写。
- 只保留 ASCII 小写字母和数字。
- 空格、下划线、连字符、斜线、点号、括号等都会被移除。

示例：

```text
"CAM16-UCS"       -> "cam16ucs"
"CIE 2000"        -> "cie2000"
"Jz Az Bz"        -> "jzazbz"
"0.1 nm"          -> "01nm"
"V(λ)"            -> "v"
"10° observer"    -> "10observer"
```

注意最后三项：基础规则会丢失小数点、`λ`、`°` 的资源语义。因此它不应该直接用于 datasets/generators 的资源名。

### canonical_method_name

```python
canonical_method_name(value)
```

method/option/alias 的语义入口，内部直接调用 `canonicalize_name(...)`。

保留它的原因是可读性：

```python
key = canonical_method_name(method)
```

比直接写：

```python
key = canonicalize_name(method)
```

更能表达这是 method 分发语境。

### canonicalize_resource_name

```python
canonicalize_resource_name(value)
```

数据资源名规范化，适合：

```text
datasets category/name
generators category/name
standard_observers category aliases
```

它会先保留资源名中的重要科学语义，再调用基础规则：

- 数字之间的小数点 `.` 转成 `p`：`0.1 -> 0p1`。
- `°` 转成 `degree`。
- `λ` 转成 `lambda`。

示例：

```text
"0.1 nm"          -> "0p1nm"
"V(λ)"            -> "vlambda"
"10° observer"    -> "10degreeobserver"
"CIE 1931 XYZ 1 nm" -> "cie1931xyz1nm"
```

这个函数的目的不是“给所有数据集创建 alias”，而是让轻微的分隔符、大小写和常见符号差异能够稳定匹配。

## methods.py

`methods.py` 负责 `method="..."` 风格 API 的分发。

它不再定义自己的字符串规则，而是从 `names.py` 使用并 re-export `canonical_method_name(...)`。

### build_method_index

```python
build_method_index(method_aliases)
```

根据主方法名和 alias 表构建查找索引。

示例：

```python
ALIASES = {
    "CIE 2000": ("cie2000", "CIEDE2000"),
    "Oklab": ("OKLab", "OKLAB"),
}

index = build_method_index(ALIASES)
```

结果类似：

```python
index["cie2000"] == "CIE 2000"
index["ciede2000"] == "CIE 2000"
index["oklab"] == "Oklab"
```

主方法名本身也会被加入索引。

### resolve_method

```python
resolve_method(method, method_index, methods)
```

把用户传入的 method 解析成：

```python
canonical_name, function
```

示例：

```python
name, fn = resolve_method("CIEDE2000", METHOD_INDEX, METHODS)
```

未知 method 会抛 `ValueError`，并列出可用方法。

### filter_kwargs

```python
filter_kwargs(function, kwargs)
```

只保留目标函数签名中接受的关键字参数。

典型场景：一个 dispatch 入口接收了多个 kwargs，但不同 method 函数只接受其中一部分。

```python
kwargs = {"textiles": True, "unused": 1}
filtered = filter_kwargs(delta_E_CIE2000, kwargs)
```

如果 `delta_E_CIE2000` 接受 `textiles`，但不接受 `unused`，结果只保留：

```python
{"textiles": True}
```

注意：`filter_kwargs(...)` 是“静默过滤”。如果某个 API 希望未知参数直接报错，应在该 API 外层自己做严格校验。

## scale.py

`scale.py` 负责纯数值尺度转换。它不表达白点、不表达色适应、不表达积分归一化。

支持的普通尺度：

```text
"1"          [0, 1] 或相对 1 的数值域
"100"        [0, 100] 或 Y=100 的数值域
"reference"  保持当前参考域，不缩放
```

支持的角度尺度额外包括：

```text
"degrees"    角度制
```

常见 alias：

```text
"unit" / "normalised" / "normalized" / "0to1" -> "1"
"percent" / "percentage" / "0to100"          -> "100"
"ref"                                           -> "reference"
"deg" / "degree"                               -> "degrees"
```

### to_domain_1

```python
to_domain_1(value, source_scale="100", scale_factor=100.0, name="value")
```

把输入转换到 `[0, 1]` 数值域。

行为：

```text
source_scale="100"       -> value / scale_factor
source_scale="1"         -> 不缩放
source_scale="reference" -> 不缩放
```

示例：

```python
to_domain_1([0, 50, 100], source_scale="100")
# [0.0, 0.5, 1.0]
```

### to_domain_100

```python
to_domain_100(value, source_scale="1", scale_factor=100.0, name="value")
```

把输入转换到 `[0, 100]` 数值域。

行为：

```text
source_scale="1"         -> value * scale_factor
source_scale="100"       -> 不缩放
source_scale="reference" -> 不缩放
```

示例：

```python
to_domain_100([0, 0.5, 1], source_scale="1")
# [0.0, 50.0, 100.0]
```

### from_range_1

```python
from_range_1(value, target_scale="100", scale_factor=100.0, name="value")
```

把已经处于 `[0, 1]` range 的值转换到目标尺度。

行为：

```text
target_scale="100"       -> value * scale_factor
target_scale="1"         -> 不缩放
target_scale="reference" -> 不缩放
```

### from_range_100

```python
from_range_100(value, target_scale="1", scale_factor=100.0, name="value")
```

把已经处于 `[0, 100]` range 的值转换到目标尺度。

行为：

```text
target_scale="1"         -> value / scale_factor
target_scale="100"       -> 不缩放
target_scale="reference" -> 不缩放
```

### to_domain_degrees

```python
to_domain_degrees(value, source_scale="1", scale_factor=360.0, name="value")
```

把角度类输入转换为 degrees。

行为：

```text
source_scale="1"         -> value * scale_factor
source_scale="100"       -> value * scale_factor / 100
source_scale="degrees"   -> 不缩放
source_scale="reference" -> 不缩放
```

示例：

```python
to_domain_degrees(0.5, source_scale="1")
# 180.0
```

### from_range_degrees

```python
from_range_degrees(value, target_scale="1", scale_factor=360.0, name="value")
```

把 degrees 转换到目标角度尺度。

行为：

```text
target_scale="1"         -> value / scale_factor
target_scale="100"       -> value * 100 / scale_factor
target_scale="degrees"   -> 不缩放
target_scale="reference" -> 不缩放
```

示例：

```python
from_range_degrees(180, target_scale="1")
# 0.5
```

## scale.py 的边界

`scale.py` 只是缩放工具。

它可以表达：

```text
XYZ(Y=100) -> XYZ(Y=1)
relative RGB -> 0-100 range
normalized hue -> degrees
```

它不能表达：

```text
D50 -> D65 色适应
光谱积分归一化
反射率到 XYZ 的 k 因子
CIECAM02/CIECAM16 观察条件参考域
Oklab / IPT / Jzazbz 是否已经 D65-referred
```

这些需要由对应模块显式处理。

## 当前迁移状态

已经较明显使用 `utils` 的模块包括：

- `color.difference`：数组广播、method dispatch。
- `color.spaces`：部分注册表 canonical、部分三通道输入、D65-referred 空间的尺度转换。
- `color.adaptation`：部分 XYZ triplet 输入和 transform 名称 canonical。
- `color.datasets` / `color.generators`：资源名 canonical。

## 新代码使用建议

如果你在写新模块：

1. 需要三通道坐标输入：优先用 `as_last_axis_triplets(...)`。
2. 需要二维坐标输入：优先用 `as_last_axis_pairs(...)`。
3. 需要两个同类坐标做差：优先用 `broadcast_triplets(...)` 或 `broadcast_pairs(...)`。
4. 需要 method 分发：用 `build_method_index(...)`、`resolve_method(...)`。
5. 需要普通 alias 解析：用 `canonical_method_name(...)` 或 `canonicalize_name(...)`。
6. 需要 dataset/generator 资源名解析：用 `canonicalize_resource_name(...)`。
7. 需要 `[0, 1] <-> [0, 100]`：用 `to_domain_1(...)` / `to_domain_100(...)`。
