# 编码规范手册

> 从 colour-science 项目中提取的编码规范，每条配有实例代码。标注了哪些值得借鉴、哪些可跳过。

---

## 目录

1. [文件结构规范](#1-文件结构规范)
2. [Python 语言特性详解](#2-python-语言特性详解)
3. [类型注解规范](#3-类型注解规范)
4. [函数设计规范](#4-函数设计规范)
5. [数据结构设计规范](#5-数据结构设计规范)
6. [测试规范](#6-测试规范)
7. [可选依赖处理规范](#7-可选依赖处理规范)

---

## 1. 文件结构规范

### 1.1 标准文件头顺序 ✅ 强烈推荐

每个 Python 源文件严格遵循以下顺序：

```python
# ① 模块文档字符串（可选，推荐有）
"""
CIE L*a*b* Colourspace
======================

Define the *CIE L\*a\*b\** colourspace transformations.
"""

# ② __future__ 导入（必须是第一行代码）
from __future__ import annotations

# ③ 标准库导入
import typing
import numpy as np

# ④ TYPE_CHECKING 守卫下的类型导入（运行时不加载）
if typing.TYPE_CHECKING:
    from colour.hints import Domain1, Domain100, NDArrayFloat

# ⑤ 第三方库导入
from colour.utilities import as_float_array, attest, tsplit, tstack

# ⑥ 项目内部导入

# ⑦ 模块元数据（个人项目可省略）
__author__ = "Your Name"
__copyright__ = "Copyright 2024 Your Name"
__license__ = "BSD-3-Clause"
__maintainer__ = "Your Name"
__email__ = "your@email.com"
__status__ = "Production"

# ⑧ __all__ 声明
__all__ = [
    "XYZ_to_Lab",
    "Lab_to_XYZ",
]

# ⑨ 代码
```

**为什么这个顺序重要**：
- `from __future__ import annotations` 必须在最前，否则类型注解会被当作运行时表达式求值
- `TYPE_CHECKING` 守卫避免运行时导入仅用于类型检查的模块，减少启动时间和循环导入风险
- `__all__` 在代码之前，明确声明公共 API 边界

### 1.2 `__all__` 显式声明 ✅ 必须

```python
# 正确：显式列出所有公共名称
__all__ = [
    "XYZ_to_Lab",
    "Lab_to_XYZ",
]

# 错误：不声明 __all__，导致 import * 导入所有非下划线名称
```

**作用**：控制 `from module import *` 的行为。没有 `__all__` 时，`import *` 会导入所有不以 `_` 开头的名称，容易污染命名空间。

**增量拼接模式**（用于 `__init__.py` 聚合器）：

```python
# colour/models/__init__.py
from .cie_lab import XYZ_to_Lab, Lab_to_XYZ
from .cie_luv import XYZ_to_Luv, Luv_to_XYZ

__all__ = ["XYZ_to_Lab", "Lab_to_XYZ"]
__all__ += ["XYZ_to_Luv", "Luv_to_XYZ"]  # 每个源模块一组 +=
```

### 1.3 `# isort: split` 注释 ⚠️ 按需

```python
from colour.colorimetry import CCS_ILLUMINANTS
# isort: split
from colour.models import xy_to_xyY, xyY_to_XYZ
```

控制 isort 工具的导入分组。只有在你使用 isort 且有严格分组需求时才需要。

---

## 2. Python 语言特性详解

### 2.1 `@dataclass` 装饰器 ✅ 推荐

`@dataclass` 是 Python 3.7+ 的标准库装饰器，自动为类生成 `__init__`、`__repr__`、`__eq__` 等方法，替代手写样板代码。

**基础用法**：

```python
from dataclasses import dataclass, field

@dataclass
class Image_Specification_Attribute:
    """图像规格属性"""

    name: str                                          # 必填字段
    value: Any                                         # 必填字段
    type_: str | None = None                           # 可选字段，有默认值

# 自动生成的 __init__ 等价于：
# def __init__(self, name: str, value: Any, type_: str | None = None):
#     self.name = name
#     self.value = value
#     self.type_ = type_

attr = Image_Specification_Attribute("dpi", 300)
print(attr.name)    # "dpi"
print(attr)          # Image_Specification_Attribute(name='dpi', value=300, type_=None)
```

**`frozen=True`（不可变数据类）**：

```python
@dataclass(frozen=True)
class Image_Specification_BitDepth:
    """位深规格——创建后不可修改"""

    name: str
    numpy: type
    openimageio: object

bit_depth = Image_Specification_BitDepth("uint8", np.uint8, UINT8)
bit_depth.name = "uint16"  # ❌ 报错：FrozenInstanceError
```

**`field(default_factory=...)`（可变默认值）**：

```python
@dataclass
class DeltaE_Specification_CIE1976:
    """色差计算结果——用 None 作为默认值"""

    dE: np.ndarray | None = field(default_factory=lambda: None)
    dL: np.ndarray | None = field(default_factory=lambda: None)
    da: np.ndarray | None = field(default_factory=lambda: None)
    db: np.ndarray | None = field(default_factory=lambda: None)

# 为什么用 field(default_factory=lambda: None) 而不是直接 = None？
# 因为 dataclass 要求可变默认值必须用 factory，None 虽然不可变，
# 但项目统一使用 field() 风格保持一致性。
```

**`field()` 的其他常用参数**：

```python
@dataclass
class Config:
    # 不在 __repr__ 中显示
    internal: list = field(default_factory=list, repr=False)

    # 不参与 __eq__ 比较
    id: int = field(default=0, compare=False)

    # 不在 __init__ 中出现（需要在 __post_init__ 中赋值）
    computed: float = field(init=False, default=0.0)

    def __post_init__(self):
        self.computed = self.id * 2.5
```

**colour-science 中的典型用途**：

```python
# 用途1：返回多个值的结构化结果
@dataclass
class DeltaE_Specification_CIE2000:
    dE: NDArrayFloat | None = field(default_factory=lambda: None)
    dL: NDArrayFloat | None = field(default_factory=lambda: None)
    da: NDArrayFloat | None = field(default_factory=lambda: None)
    db: NDArrayFloat | None = field(default_factory=lambda: None)

# 用途2：不可变的规格/配置常量
@dataclass(frozen=True)
class Image_Specification_BitDepth:
    name: str
    numpy: type

# 用途3：配合 Mixin 获得迭代和算术能力
@dataclass
class DeltaE_Specification_CIE1976(MixinDataclassArithmetic):
    dE: NDArrayFloat | None = field(default_factory=lambda: None)
    # 现在可以：result * 2, result + other_result, dict(result), for v in result
```

### 2.2 `@property` 装饰器 ✅ 推荐

将方法伪装为属性访问，用于计算属性或受控访问：

```python
class Signal:
    def __init__(self, domain, range_):
        self._domain = domain
        self._range = range_

    @property
    def function(self):
        """返回一个可调用对象，组合了插值器和外推器"""
        return self._extrapolator(self._interpolator)

    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, value):
        self._domain = value
        self._invalidate_cache()  # 赋值时触发缓存清理

# 使用
sig = Signal(domain, range_)
sig.function(x)      # 调用计算
sig.domain = new_arr  # 赋值触发缓存更新
```

### 2.3 `@staticmethod` 和 `@classmethod` ⚠️ 按需

```python
class CacheRegistry:
    _instance = None

    @classmethod
    def get_instance(cls):
        """类方法：作为替代构造器或访问类级别状态"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @staticmethod
    def is_valid_key(key):
        """静态方法：不需要 self 或 cls 的工具函数"""
        return isinstance(key, str) and len(key) > 0
```

### 2.4 `@typing.overload` ✅ 按需

当函数的返回类型取决于参数值时，用 `@overload` 让类型检查器正确推断：

```python
from typing import overload

# 声明1：additional_data=False 时返回 ndarray
@overload
def delta_E_CIE1976(
    Lab_1: Domain100,
    Lab_2: Domain100,
    *,
    additional_data: Literal[False] = False,
) -> NDArrayFloat: ...

# 声明2：additional_data=True 时返回结构化结果
@overload
def delta_E_CIE1976(
    Lab_1: Domain100,
    Lab_2: Domain100,
    *,
    additional_data: Literal[True],
) -> DeltaE_Specification_CIE1976: ...

# 实际实现
def delta_E_CIE1976(
    Lab_1: Domain100,
    Lab_2: Domain100,
    additional_data: bool = False,
) -> NDArrayFloat | DeltaE_Specification_CIE1976:
    # ... 实现 ...
    pass
```

**使用场景**：函数有 `return_details: bool` 这类开关，不同值返回不同类型。

### 2.5 `@functools.cache` / `@functools.lru_cache` ✅ 推荐

```python
import functools

@functools.cache
def validate_method(method, valid_methods, ...):
    """校验结果被缓存，相同参数不重复计算"""
    ...

# 实际效果：
validate_method("sRGB", ("sRGB", "BT.709"))  # 计算并缓存
validate_method("sRGB", ("sRGB", "BT.709"))  # 直接返回缓存结果
```

### 2.6 `@contextmanager` — 上下文管理器 ✅ 推荐

```python
from contextlib import contextmanager

@contextmanager
def domain_range_scale(scale):
    """临时改变全局缩放设置"""
    old_scale = get_domain_range_scale()
    set_domain_range_scale(scale)
    try:
        yield  # with 块内的代码在此执行
    finally:
        set_domain_range_scale(old_scale)  # 恢复原设置

# 使用
with domain_range_scale("100"):
    result = XYZ_to_Lab(XYZ)  # 在 0-100 域中计算
# 离开 with 块后自动恢复
```

### 2.7 双重用途模式：上下文管理器 + 装饰器 ✅ 推荐

colour-science 中多个类同时支持 `with` 块和 `@` 装饰器两种用法：

```python
class _caching_enable:
    """同时支持 with 块和 @装饰器"""

    def __init__(self, enable=True):
        self._enable = enable

    # 上下文管理器协议
    def __enter__(self):
        self._old = is_caching_enabled()
        set_caching_enable(self._enable)
        return self

    def __exit__(self, *args):
        set_caching_enable(self._old)

    # 装饰器协议
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return wrapper

caching_enable = _caching_enable

# 用法1：with 块
with caching_enable(False):
    result = expensive_computation()

# 用法2：@装饰器
@caching_enable(False)
def expensive_computation():
    ...
```

### 2.8 `@dataclass` vs `NamedTuple` vs 普通类

| 特性 | `@dataclass` | `NamedTuple` | 普通 `class` |
|------|-------------|-------------|-------------|
| 自动生成 `__init__` | ✅ | ✅ | ❌ |
| 自动生成 `__repr__` | ✅ | ✅ | ❌ |
| 自动生成 `__eq__` | ✅ | ✅ | ❌ |
| 可变性 | 可变（除非 `frozen=True`） | 不可变 | 可变 |
| 可以有方法 | ✅ | ✅ | ✅ |
| 继承 Mixin | ✅ | 有限 | ✅ |
| 类型提示 | ✅ | ✅ | 手动 |

**colour-science 的选择**：数据容器用 `@dataclass`，配置常量用 `@dataclass(frozen=True)`，纯函数模块不需要类。

---

## 3. 类型注解规范

### 3.1 `from __future__ import annotations` ✅ 必须

```python
from __future__ import annotations

# 这些注解在运行时是字符串，不会被求值
# 避免了循环导入问题，也提升了启动速度
def XYZ_to_Lab(XYZ: Domain1, illuminant: ArrayLike = ...) -> Range100:
    ...
```

**没有这行时**：Python 会在函数定义时尝试求值每个注解表达式，如果 `Domain1` 尚未导入就会报错。

### 3.2 `TYPE_CHECKING` 守卫 ✅ 推荐

```python
import typing

# 这些导入只在 mypy/pyright 类型检查时生效，运行时不加载
if typing.TYPE_CHECKING:
    from colour.hints import Domain1, Domain100, NDArrayFloat, Literal

# 运行时用的导入放在守卫外面
from colour.hints import NDArrayReal, cast
```

**为什么区分**：
- `Domain1`, `Literal` 等只用于注解，运行时不需要
- `NDArrayReal`, `cast` 在运行时代码中实际使用

### 3.3 集中式类型别名 ✅ 推荐

```python
# colour/hints/__init__.py — 所有类型别名集中定义

import numpy as np
from typing import Annotated, Literal

# NumPy 数组别名
NDArrayFloat = np.ndarray[Any, np.dtype[np.floating[Any]]]
NDArrayInt = np.ndarray[Any, np.dtype[np.integer[Any]]]

# 域/范围标注类型
Domain1 = Annotated[ArrayLike, "Domain1"]       # 期望 0-1 输入
Domain100 = Annotated[ArrayLike, "Domain100"]   # 期望 0-100 输入
Range1 = Annotated[NDArrayFloat, "Range1"]       # 输出 0-1
Range100 = Annotated[NDArrayFloat, "Range100"]   # 输出 0-100

# Literal 类型（枚举所有合法字符串参数）
LiteralDeltaEMethod = Literal["CIE 1976", "CIE 1994", "CIE 2000", "CMC"]
LiteralRGBColourspace = Literal["sRGB", "Adobe RGB", "DCI-P3", ...]
```

**使用**：

```python
from colour.hints import Domain1, Domain100, Range1, ArrayLike, NDArrayFloat

def XYZ_to_Lab(
    XYZ: Domain1,                    # 函数签名中直接用别名
    illuminant: ArrayLike = ...,
) -> Range100:
    ...
```

### 3.4 `typing.Annotated` — 在类型中嵌入元数据 ⚠️ 高级

```python
from typing import Annotated

# Annotated[实际类型, 元数据1, 元数据2, ...]
Domain100 = Annotated[ArrayLike, "Domain100"]
Range100 = Annotated[NDArrayFloat, "Range100"]

# 元数据不影响运行时行为，仅供类型检查器和工具链使用
# colour-science 用它来标注域/范围缩放语义
```

### 3.5 `Protocol` — 结构化子类型 ✅ 按需

```python
from typing import Protocol, runtime_checkable

# Protocol 定义接口（鸭子类型，不需要继承）
@runtime_checkable
class ProtocolInterpolator(Protocol):
    """任何有 x, y 属性且可调用的对象都是合法的插值器"""
    x: NDArrayFloat
    y: NDArrayFloat
    def __call__(self, x: ArrayLike) -> NDArrayFloat: ...

# 任何满足接口的对象都可以使用，无需显式继承
class MyInterpolator:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __call__(self, x):
        return np.interp(x, self.x, self.y)

# 类型检查器会接受 MyInterpolator 作为 ProtocolInterpolator
```

**vs ABC 继承**：Protocol 不需要被实现类显式继承，更适合插件式设计。

---

## 4. 函数设计规范

### 4.1 `attest()` 替代 `assert` ✅ 强烈推荐

```python
def attest(condition: bool, message: str = "") -> None:
    """提供 assert 功能，但不会被 python -O 优化掉"""
    if not condition:
        raise AssertionError(message)

# 用法
def XYZ_to_Lab(XYZ, illuminant):
    attest(XYZ.ndim >= 1, '"XYZ" array must have at least 1 dimension')
    attest(
        XYZ.shape[-1] == 3,
        f'"XYZ" array must have 3 channels, got {XYZ.shape[-1]}',
    )
    ...

# ❌ 错误：assert 会被 python -O 删除
assert XYZ.ndim >= 1

# ✅ 正确：attest 始终执行
attest(XYZ.ndim >= 1, '"XYZ" array must have at least 1 dimension')
```

**为什么重要**：数学计算库的用户可能用 `python -O` 运行，如果输入验证被删除，会导致难以调试的错误。

### 4.2 `validate_method()` — 方法名校验 ✅ 推荐

```python
import functools

@functools.cache
def validate_method(method, valid_methods, message=..., as_lowercase=True):
    """校验方法名是否在合法列表中（大小写不敏感）"""
    if as_lowercase:
        method = method.lower()
        valid_methods = tuple(m.lower() for m in valid_methods)
    if method not in valid_methods:
        raise ValueError(message.format(method, valid_methods))
    return method

# 用法
def chromatic_adaptation(XYZ, method="Von Kries", **kwargs):
    method = validate_method(
        method,
        ("Von Kries", "CIE 1994", "Fairchild 1990"),
    )
    ...

# 效果：
chromatic_adaptation(XYZ, "von kries")     # ✅ 通过，返回 "von kries"
chromatic_adaptation(XYZ, "VON KRIES")     # ✅ 通过
chromatic_adaptation(XYZ, "invalid")       # ❌ ValueError
```

### 4.3 `filter_kwargs()` — 安全的 kwargs 转发 ✅ 推荐

```python
def filter_kwargs(function, **kwargs):
    """只保留函数签名接受的 kwargs，丢弃不兼容的"""
    params = inspect.signature(function).parameters
    valid = {k for k, v in params.items() if v.kind not in (
        inspect.Parameter.VAR_POSITIONAL,
        inspect.Parameter.VAR_KEYWORD,
    )}
    return {k: v for k, v in kwargs.items() if k in valid}

# 场景：统一接口转发到不同实现
def delta_E(Lab_1, Lab_2, method="CIE 2000", **kwargs):
    method = validate_method(method, ("CIE 1976", "CIE 1994", "CIE 2000"))
    function = METHODS[method]

    # 不同方法的参数不同，filter_kwargs 自动过滤不兼容的
    return function(Lab_1, Lab_2, **filter_kwargs(function, **kwargs))

# delta_E(Lab_1, Lab_2, "CIE 2000", kL=2, kH=1, extra_param="ignored")
# → delta_E_CIE2000(Lab_1, Lab_2, kL=2, kH=1)  # extra_param 被过滤
```

### 4.4 `to_domain_*` / `from_range_*` 边界缩放 ✅ 推荐（简化版）

```python
_DOMAIN_RANGE_SCALE = "reference"

def to_domain_1(a):
    """将输入归一化到 0-1 域"""
    if _DOMAIN_RANGE_SCALE == "100":
        return a / 100
    return a  # "reference" 或 "1" 时直接透传

def from_range_100(a):
    """将输出从 0-100 缩放到用户期望的范围"""
    if _DOMAIN_RANGE_SCALE == "100":
        return a * 100
    return a

# 在函数中使用
def XYZ_to_Lab(XYZ, illuminant=...):
    XYZ = to_domain_1(XYZ)       # 入口：归一化
    # ... 内部统一用 0-1 计算 ...
    Lab = from_range_100(Lab)    # 出口：缩放回用户约定
    return Lab
```

**简化建议**：如果你的库只支持一种约定（如 0-1），可以完全去掉这套机制，直接在文档中说明。

### 4.5 函数命名：`X_to_Y` 双向对称 ✅ 推荐

```python
# 正向转换
def XYZ_to_Lab(XYZ, illuminant=...): ...

# 逆向转换
def Lab_to_XYZ(Lab, illuminant=...): ...

# 色适应
def chromatic_adaptation_VonKries(XYZ, XYZ_w, XYZ_wr, **kwargs): ...

# 色差
def delta_E_CIE2000(Lab_1, Lab_2, **kwargs): ...
```

**命名规则**：
- 转换函数：`源_to_目标`
- 色差计算：`delta_E_方法名`
- 传递函数：`eotf_色彩空间名` / `oetf_色彩空间名`

### 4.6 NumpyDoc 文档字符串 ✅ 推荐

```python
def XYZ_to_Lab(
    XYZ: Domain1,
    illuminant: ArrayLike = ...,
) -> Range100:
    """
    Convert from *CIE XYZ* tristimulus values to *CIE L\*a\*b\** colourspace.

    Parameters
    ----------
    XYZ
        *CIE XYZ* tristimulus values.
    illuminant
        Reference *illuminant* *CIE xy* chromaticity coordinates.

    Returns
    -------
    :class:`numpy.ndarray`
        *CIE L\*a\*b\** colourspace array.

    Notes
    -----
    +----------------+-----------------------+-----------------+
    | **Domain**     | **Scale - Reference** | **Scale - 1**   |
    +================+=======================+=================+
    | ``XYZ``        | 1                     | 1               |
    +----------------+-----------------------+-----------------+

    +----------------+-----------------------+-----------------+
    | **Range**      | **Scale - Reference** | **Scale - 1**   |
    +================+=======================+=================+
    | ``Lab``        | 100                   | 1               |
    +----------------+-----------------------+-----------------+

    References
    ----------
    :cite:`CIETC1-482004m`

    Examples
    --------
    >>> import numpy as np
    >>> XYZ = np.array([0.20654008, 0.12197225, 0.05136952])
    >>> XYZ_to_Lab(XYZ)  # doctest: +ELLIPSIS
    array([41.5278752..., 52.6385830..., 26.9231792...])
    """

    XYZ = to_domain_1(XYZ)
    # ...
```

**关键部分**：
- **Parameters / Returns**：参数和返回值说明
- **Notes 中的 Domain/Range 表**：颜色科学库特有，说明数值范围约定
- **References**：学术引用
- **Examples**：可执行的 doctest（`# doctest: +ELLIPSIS` 允许浮点数省略）

### 4.7 `as_float_array()` 统一类型转换 ✅ 推荐

```python
def as_float_array(a):
    """将输入安全转换为 float64 ndarray"""
    return np.asarray(a, dtype=np.float64)

# 在每个函数入口统一调用
def delta_E_CIE1976(Lab_1, Lab_2):
    Lab_1 = as_float_array(Lab_1)
    Lab_2 = as_float_array(Lab_2)
    # ... 后续代码保证是 ndarray ...
```

**好处**：接受 list、tuple、单个数字、任意 dtype 的 ndarray，统一转为 `float64`。

### 4.8 `tsplit` / `tstack` — 通道拆分/堆叠 ✅ 推荐

```python
def tsplit(a):
    """沿最后一个轴拆分：(N, 3) → [x, y, z]"""
    return np.split(a, a.shape[-1], axis=-1)

def tstack(a):
    """沿最后一个轴堆叠：[x, y, z] → (N, 3)"""
    return np.concatenate(a, axis=-1)

# 用法
X, Y, Z = tsplit(XYZ)       # 拆分三通道
Lab = tstack([L, a, b])     # 合并三通道
```

**好处**：比 `a[:, 0], a[:, 1], a[:, 2]` 更简洁，且支持任意维度。

---

## 5. 数据结构设计规范

### 5.1 `CanonicalMapping` — 模糊键注册表 ✅ 核心模式

```python
from collections.abc import MutableMapping

class CanonicalMapping(MutableMapping):
    """大小写不敏感、分隔符不敏感的 dict"""

    def __init__(self, data=None, **kwargs):
        self._data = dict(data or {}, **kwargs)
        self._lower_to_original = {}
        for key in self._data:
            self._lower_to_original[key.lower()] = key

    def _canonical_key(self, key):
        """四级查找：原始 → 小写 → slug → 规范"""
        # 1. 原始键
        if key in self._data:
            return key
        # 2. 小写键
        lower = key.lower()
        if lower in self._lower_to_original:
            return self._lower_to_original[lower]
        # 3. slug 化（去空格和连字符）
        slug = lower.replace(" ", "").replace("-", "")
        for k in self._data:
            if k.lower().replace(" ", "").replace("-", "") == slug:
                return k
        raise KeyError(key)

    def __getitem__(self, key):
        return self._data[self._canonical_key(key)]

    def __setitem__(self, key, value):
        self._data[key] = value
        self._lower_to_original[key.lower()] = key

    def __delitem__(self, key):
        canonical = self._canonical_key(key)
        del self._data[canonical]
        del self._lower_to_original[canonical.lower()]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

# 用法
METHODS = CanonicalMapping({
    "Von Kries": von_kries_func,
    "CIE 1994": cie1994_func,
})

# 以下全部命中 "Von Kries"
METHODS["Von Kries"]      # 原始键
METHODS["von kries"]      # 小写
METHODS["von-kries"]      # 连字符
METHODS["vonkries"]       # 无分隔符
METHODS["VON KRIES"]      # 全大写
```

### 5.2 `LazyCanonicalMapping` — 延迟求值 ✅ 按需

```python
class LazyCanonicalMapping(CanonicalMapping):
    """值如果是 callable，首次访问时才求值并缓存"""

    def __getitem__(self, key):
        value = super().__getitem__(key)
        if callable(value):
            value = value()           # 首次访问：执行
            self._data[self._canonical_key(key)] = value  # 缓存结果
        return value

# 用法：避免导入时加载所有实现
METHODS = LazyCanonicalMapping({
    "CIE 1994": lambda: __import__("my_lib.adaptation.cie1994", ...).func,
    "Fairchild 1990": lambda: __import__(...).func,
})
# "CIE 1994" 的模块只在用户实际调用时才被导入
```

### 5.3 `Structure` — 属性风格访问 ⚠️ 按需

```python
class Structure(dict):
    """支持 obj.key 访问的 dict"""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

# 用法：嵌套配置
STYLE = Structure({
    "colour": Structure({
        "darkest": "#1a1a2e",
        "brightest": "#e0e0ff",
    }),
    "font_size": 12,
})

print(STYLE.colour.darkest)  # "#1a1a2e" — 比 STYLE["colour"]["darkest"] 更可读
```

---

## 6. 测试规范

### 6.1 测试类命名 ✅ 推荐

```python
class TestXYZ_to_Lab:
    """测试 XYZ_to_Lab 函数"""

    def test_XYZ_to_Lab(self):
        """基本功能测试"""
        XYZ = np.array([0.20654008, 0.12197225, 0.05136952])
        Lab = XYZ_to_Lab(XYZ)
        np.testing.assert_allclose(Lab, [41.52787529, 52.63858304, 26.92317922], atol=1e-7)

    def test_n_dimensional_XYZ_to_Lab(self):
        """N维数组兼容性测试"""
        XYZ = np.array([0.20654008, 0.12197225, 0.05136952])
        Lab = XYZ_to_Lab(XYZ)

        # 测试 (3,) 形状
        np.testing.assert_allclose(XYZ_to_Lab(XYZ), Lab, atol=1e-7)

        # 测试 (4, 3) 形状
        XYZ_4d = np.tile(XYZ, (4, 1))
        np.testing.assert_allclose(XYZ_to_Lab(XYZ_4d), np.tile(Lab, (4, 1)), atol=1e-7)

    def test_domain_range_scale_XYZ_to_Lab(self):
        """Domain-Range 缩放一致性测试"""
        XYZ = np.array([0.20654008, 0.12197225, 0.05136952])

        # scale="1" 时，输入 0-1，输出 0-100
        Lab_i = XYZ_to_Lab(XYZ)

        # scale="100" 时，输入 0-100，输出 0-100
        with domain_range_scale("100"):
            Lab_100 = XYZ_to_Lab(XYZ * 100)
            np.testing.assert_allclose(Lab_100, Lab_i, atol=1e-7)
```

### 6.2 测试命名约定

| 方法名 | 测试内容 |
|--------|---------|
| `test_function_name` | 基本功能：给定输入，验证输出 |
| `test_n_dimensional_function_name` | N维兼容：1D、2D、高维数组都能工作 |
| `test_domain_range_scale_function_name` | 缩放一致性：不同 scale 设置下结果一致 |

### 6.3 测试导入方式 ✅ 必须

```python
# ✅ 正确：从公共 API 导入
from colour.models import XYZ_to_Lab

# ❌ 错误：从内部模块导入
from colour.models.cie_lab import XYZ_to_Lab
```

**原因**：测试应该验证公共 API 的可达性。如果内部重构导致模块移动，但 `__init__.py` 重导出正确，测试不应失败。

---

## 7. 可选依赖处理规范

### 7.1 运行时检测函数 ✅ 推荐

```python
# colour/utilities/requirements.py
def is_scipy_installed():
    try:
        import scipy
        return True
    except ImportError:
        return False

# 在需要时使用
if is_scipy_installed():
    from scipy.interpolate import interp1d
else:
    raise ImportError("scipy is required for this feature")
```

### 7.2 `@required` 装饰器 ✅ 按需

```python
def required(*modules):
    """装饰器：函数调用时检查依赖是否可用"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for mod in modules:
                if not is_installed(mod):
                    raise ImportError(f"{mod} is required for {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@required("scipy")
def interpolate_spectrum(wavelengths, values):
    from scipy.interpolate import interp1d
    ...
```

### 7.3 Mock 降级 ⚠️ 按需

```python
# 在包的 __init__.py 中
try:
    import matplotlib
except ImportError:
    from unittest.mock import MagicMock
    sys.modules["matplotlib"] = MagicMock()
    sys.modules["matplotlib.pyplot"] = MagicMock()
    # 用户 import 不会报错，但调用时会得到 Mock 行为
```

**简化建议**：对轻量库，直接在文档中说明可选依赖即可，不需要 Mock 降级。

---

## 快速参考表

| 规范 | 优先级 | 一句话说明 |
|------|--------|-----------|
| `from __future__ import annotations` | **必须** | 文件第一行，避免注解被运行时求值 |
| `__all__` 显式声明 | **必须** | 控制公共 API 边界 |
| `attest()` 替代 `assert` | **强烈推荐** | 数学库的输入验证不能被 `-O` 删除 |
| `@dataclass` | **推荐** | 自动生成 `__init__`/`__repr__`/`__eq__` |
| `@dataclass(frozen=True)` | **推荐** | 不可变的配置/常量数据类 |
| `field(default_factory=...)` | **推荐** | 可变默认值的正确写法 |
| `TYPE_CHECKING` 守卫 | **推荐** | 运行时跳过仅类型检查的导入 |
| 集中式 `hints.py` | **推荐** | 类型别名统一管理 |
| `CanonicalMapping` | **推荐** | 大小写不敏感的方法注册表 |
| `validate_method()` | **推荐** | 校验方法名 + 缓存 |
| `filter_kwargs()` | **推荐** | 安全转发 kwargs |
| `as_float_array()` | **推荐** | 函数入口统一类型转换 |
| `tsplit()` / `tstack()` | **推荐** | 通道拆分/堆叠 |
| NumpyDoc + Domain/Range 表 | **推荐** | 颜色科学函数的文档标准 |
| `@typing.overload` | **按需** | 返回类型依赖参数值时使用 |
| `@functools.cache` | **按需** | 避免重复计算 |
| `@contextmanager` | **按需** | 临时改变全局状态 |
| `Protocol` 接口 | **按需** | 鸭子类型的正式约束 |
| 六行元数据头 | **跳过** | 开源项目惯例，个人项目不需要 |
| `isort: split` | **跳过** | linter 配置相关 |
