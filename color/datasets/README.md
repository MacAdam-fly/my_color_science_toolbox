# datasets — 色彩科学数据集加载模块

统一加载 `color/data/` 下所有静态参考数据和公式计算数据集。

---

## 目录

- [datasets — 色彩科学数据集加载模块](#datasets--色彩科学数据集加载模块)
  - [目录](#目录)
  - [快速上手](#快速上手)
  - [模块架构](#模块架构)
  - [核心 API](#核心-api)
    - [统一入口函数](#统一入口函数)
    - [类别便捷函数](#类别便捷函数)
    - [返回格式](#返回格式)
  - [数据类别](#数据类别)
    - [illuminants — 光源](#illuminants--光源)
    - [color\_cards — 色卡](#color_cards--色卡)
    - [standard\_observers — 标准观察者](#standard_observers--标准观察者)
    - [gamut\_data — 色域数据](#gamut_data--色域数据)
    - [color\_systems — 色彩体系](#color_systems--色彩体系)
  - [注册表系统](#注册表系统)
    - [DatasetEntry](#datasetentry)
    - [注册模式速查](#注册模式速查)
    - [缓存机制](#缓存机制)
    - [计算数据集注册](#计算数据集注册)
  - [文件读取工具](#文件读取工具)
  - [添加新数据](#添加新数据)
    - [场景一：添加 standard\_observer 数据](#场景一添加-standard_observer-数据)
    - [场景二：添加到已有类别（illuminants、color\_cards 等）](#场景二添加到已有类别illuminantscolor_cards-等)
    - [场景三：添加全新类别](#场景三添加全新类别)
  - [测试](#测试)
  - [数据来源](#数据来源)

---

## 快速上手

```python
from color.datasets import (
    get_illuminant, get_color_card, get_standard_observer,
    get_gamut_data, get_color_system,
)

# 加载 CIE D65 光源
d65 = get_illuminant("D65")
# d65["wavelength"] → array([300., 301., ..., 830.])
# d65["spd"]        → array([0.0, 3.2, ..., 56.1])

# 计算 6500K 黑体辐射（公式生成，无需文件）
bb = get_illuminant("blackbody", temperature=6500)

# 计算任意色温的 CIE D 系列日光
daylight = get_illuminant("daylight", cct=5000)

# 加载 Macbeth ColorChecker 24 色卡
macbeth = get_color_card("macbeth")
# macbeth["Dark Skin"] → array([0.12, 0.13, ..., 0.11])

# 加载 CIE 1931 2° XYZ 颜色匹配函数
xyz = get_standard_observer("cmfs", "cie1931_xyz_1nm")
# 别名也可以
lms = get_standard_observer("lms", "cie2006_lms2_logE_5nm")

# 加载 Pointer 色域数据
pointer = get_gamut_data("pointer")
# 加载 某个L平面的 Pointer 色域数据
p50 = get_gamut_data("pointer", L=50)

# 加载munsell色卡数据
munsell = get_color_system("munsell_srgb")
```

---

## 模块架构

```text
color/datasets/
├── __init__.py              # 统一入口，re-export 所有公开 API
├── _registry.py             # 核心注册表（DatasetEntry, register, get, search）
├── _utils.py                # 文件读取工具（read_csv, read_xlsx, read_xls）
├── illuminants.py           # 光源数据 + 黑体/日光公式计算
├── color_cards.py           # 色卡光谱反射率数据
├── standard_observers.py    # CVRL 标准观察者数据（自动发现 106 个 CSV）
├── gamut_data.py            # 色域边界数据
├── color_systems.py         # 色彩体系数据
└── tests/                   # 测试套件
```

**数据流：**

```text
用户调用 → 便捷函数 (get_xxx) → 注册表 (_registry.get)
                                      │
                        ┌──────────────┼──────────────┐
                        ▼              ▼              ▼
                   文件数据集      计算数据集      缓存命中
                   (read_csv/     (compute_fn)    (直接返回)
                    read_xlsx/
                    read_xls)
```

---

## 核心 API

### 统一入口函数

所有类别共享同一套注册表，可通过统一函数或类别便捷函数访问：

| 函数 | 说明 |
| ---- | ---- |
| `get(category, name, **kwargs)` | 统一加载，适用于任意类别 |
| `describe(category, name)` | 查看元数据，不加载数据 |
| `list_datasets(category=None)` | 列出某类别下所有数据集名称 |
| `list_categories()` | 列出所有已注册类别 |
| `search(keyword)` | 按关键词搜索名称和描述 |

### 类别便捷函数

每个类别提供专用的便捷函数，内部调用统一注册表：

| 类别 | 加载函数 | 列表函数 |
| ---- | -------- | -------- |
| 光源 | `get_illuminant(name, **kwargs)` | `list_illuminants()` |
| 色卡 | `get_color_card(name, **kwargs)` | `list_color_cards()` |
| 标准观察者 | `get_standard_observer(category, name, **kwargs)` | `list_standard_observers(category)` |
| 色域 | `get_gamut_data(name, **kwargs)` | `list_gamut_data()` |
| 色彩体系 | `get_color_system(name, **kwargs)` | `list_color_systems()` |

### 返回格式

所有数据集返回 `Dict[str, np.ndarray]`（类型别名 `SpectralDict`），键为列名，值为 numpy 数组。

```python
# cmf,chro,xyz等得到的类似如下
{
    "wavelength": array([360., 361., ...]),   # 总是第一列
    "x":      array([0.00013, ...]),      # 其余键取决于数据集
    "y":      array([3.9e-6, ...]),
}
```

---

## 数据类别

### illuminants — 光源

CIE 标准光源光谱功率分布。

**文件数据集（3 个）：**

| 名称 | 描述 | 波长范围 |
| --- | ---- | ------- |
| `"A"` | CIE 光源 A（~2856 K） | 300–830 nm, 1 nm |
| `"D65"` | CIE 光源 D65（~6504 K） | 300–830 nm, 1 nm |
| `"fluorescents"` | CIE F1–F12 荧光灯光谱 | 380–780 nm, 5 nm |

**计算数据集（2 个）：**

| 名称 | 参数 | 描述 |
| ---- | ---- | ---- |
| `"blackbody"` | `temperature: float`, `wavelength_nm: ndarray (可选)` | 任意温度的 Planck 黑体辐射。默认 300–830 nm, 1 nm |
| `"daylight"` | `cct: float`, `wavelength_nm: ndarray (可选)` | 任意色温的 CIE D 系列日光（4000–25000 K）。基于 S0/S1/S2 基函数 |

**计算原理：**

- 黑体辐射：Planck 公式 `L(λ) = c₁ / (λ⁵ (exp(c₂/λT) - 1))`
- 日光：色温 → 色度坐标 → M1/M2 乘数 → `S0 + S1·M1 + S2·M2`

```python
# 不同温度的黑体辐射
bb_3000 = get_illuminant("blackbody", temperature=3000)
bb_6500 = get_illuminant("blackbody", temperature=6500)

# 自定义波长范围
import numpy as np
wl = np.arange(400, 700, 1)
bb = get_illuminant("blackbody", temperature=5500, wavelength_nm=wl)
```

---

### color_cards — 色卡

标准色卡的光谱反射率数据。

| 名称 | 描述 | 色块数 | 波长范围 |
| ---- | ---- | -------- | -------- |
| `"macbeth"` | Macbeth ColorChecker Classic | 24 | 380–780 nm, 5 nm |
| `"pmc"` | Preferred Memory Color 色卡 | 31 | 400–700 nm, 10 nm |
| `"bcra"` | BCRA CERAM Series II 校准色块 | 12 | 380–730 nm, 10 nm |

**命名常量：**

```python
from color.datasets.color_cards import MACBETH_PATCH_NAMES, BCRA_TILE_NAMES

# MACBETH_PATCH_NAMES = ("Dark Skin", "Light Skin", "Blue Sky", ..., "Black")
# BCRA_TILE_NAMES = ("Black", "Deep Grey", ..., "Red")
```

```python
macbeth = get_color_card("macbeth")
skin_reflectance = macbeth["Dark Skin"]   # 按色名索引
```

---

### standard_observers — 标准观察者

CVRL（伦敦大学学院色彩与视觉研究实验室）人类视觉系统基础数据。**106 个 CSV 文件自动发现**，无需手动注册。

**六个子类别：**

| 类别 | 别名 | 文件数 | 内容 |
| ---- | ---- | -------- | ---- |
| `cmfs` | `cmf`, `xyz` | 15 | CIE 1931/1964/2012 XYZ 颜色匹配函数 |
| `cone_fundamentals` | `cone`, `lms`, `fundamentals` | 27 | 锥体光谱灵敏度（CIE 2006 LMS, Smith-Pokorny 等） |
| `luminous_efficiency` | `luminous`, `v_lambda`, `vl`, `efficiency` | 29 | 光视效率函数 V(λ) |
| `prereceptoral_filters` | `filter`, `macular`, `lens` | 11 | 黄斑色素 & 晶状体密度 |
| `chromaticity_coordinates` | `chromaticity`, `chroma`, `xy` | 16 | CIE & MacLeod-Boynton 色度坐标 |
| `photopigments` | `pigment`, `pigments` | 8 | 光色素吸收光谱 |

```python
# 使用类别别名
xyz = get_standard_observer("xyz", "cie1931_xyz_1nm")
lms = get_standard_observer("cone", "cie2006_lms2_logE_5nm")
v   = get_standard_observer("vl", "cie2008_v2_linE_1nm")

# 列出某类别下所有数据集
list_standard_observers("lms")
# → ['cie2006_lms10_linE_0p1nm', 'cie2006_lms10_linE_1nm', ..., 'vew_logQ']
```

**列名确定机制：**

`read_csv` 默认 `header=True`，自动检测首行是否为表头：

- 首行含非数值文本 → 当作表头，用其列名
- 首行全为数值 → 当作数据，列名从文件名模式推断（见下表）

优先级：**文件表头 > 文件名推断 > 通用默认名**

| 文件名包含 | 推断列名（无表头时的兜底） |
| ----------- | -------- |
| `xyz` | `wavelength, X, Y, Z` |
| `sbrgb` | `wavelength, R, G, B` |
| `lms`, `smj`, `sp_` | `wavelength, l, m, s` |
| `_v2_`, `_v10_`, `vl1924` | `wavelength, V` |
| `scotopic` | `wavelength, V_prime` |
| `mb` | `wavelength, l, s, B` |
| `chro` | `wavelength, x, y, z` |
| `macular`, `lens_` | `wavelength, optical_density` |
| `sucrodsh`, `sucrodsm` | `wavelength, absorption` |

无法匹配时回退到通用命名 `(wavelength, col1, col2, ...)`。

如果 CSV 有表头但想用自定义列名覆盖，在 `_CUSTOM_ENTRIES` 中设置 `columns` 即可（显式 `columns` 优先级最高）。

---

### gamut_data — 色域数据

真实表面色的色域边界。

| 名称 | 描述 | 数据来源 |
| ---- | ---- | -------- |
| `"pointer"` | Pointer (1980) Calculations sheet — 8 个 L\* 层级的色域边界 | 计算解析 |
| `"pointer_raw"` | Pointer XLS 原始多 sheet 数据（Data, SpecLoc, IllumDat） | 文件 |

```python
# Calculations sheet（默认）— 按 L* 层级的色域边界
pointer = get_gamut_data("pointer")           # 全部 8 级，296 行
pointer_50 = get_gamut_data("pointer", L=50)  # 仅 L*=50，37 行

pointer["hab"]  # 色相角 0°–360°
pointer["C"]    # 色度 C*
pointer["a"]    # a*
pointer["b"]    # b*
pointer["x"]    # 色度坐标 x

# 其他 sheet 通过 pointer_raw
specloc = get_gamut_data("pointer_raw", sheet="SpecLoc")
```

---

### color_systems — 色彩体系

色彩标注体系的参考数据。

| 名称 | 描述 | 样本数 |
| ---- | ---- | -------- |
| `"munsell_srgb"` | RIT Munsell 色度重命名数据 | 1625 |

```python
munsell = get_color_system("munsell_srgb")
```

---

## 注册表系统

### DatasetEntry

所有数据集通过 `DatasetEntry` 不可变数据类注册：

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class DatasetEntry:
    category: str                         # 类别: "illuminants", "standard_observers.cmfs", ...
    name: str                             # 唯一标识（通常是文件名去扩展名）
    description: str                      # 人类可读描述
    source: str = ""                      # 数据来源（论文、URL）
    file_path: Optional[str] = None       # 文件绝对路径，计算数据集为 None
    computed: bool = False                # 是否为公式计算生成
    compute_fn: Optional[Callable] = None # 计算函数，computed=True 时必填
    columns: Optional[Tuple[str, ...]] = None  # 列名，优先级最高
    metadata: Dict[str, Any] = {}         # 读取行为：header, skiprows, usecols, sheet
```

### metadata 字段详解

`metadata` 是注册时传给读取器的配置字典，控制文件如何被解析。`_registry.py` 的 `_read_file()` 会将其中的键分发给对应的 `read_csv` / `read_xlsx` / `read_xls`。

**所有读取器通用的键：**

| 键 | 类型 | 默认值 | 说明 |
| --- | ---- | ------ | ---- |
| `header` | `bool` / `int` / `str` | `False` | 表头设置。`False`=无表头，`True`/`"auto"`=自动检测，`int`=跳过 N 行用下一行做表头 |
| `usecols` | `list[int]` | `None` | 只读取指定列索引 |

> **列名**请使用 `DatasetEntry.columns` 字段指定，不要放在 `metadata` 中。`columns` 优先级最高，详见下方列名优先级说明。

**Excel 专用的键：**

| 键 | 类型 | 默认值 | 说明 |
| --- | ---- | ------ | ---- |
| `sheet` | `int` / `str` | `0` | 读取哪个 sheet（0-based 索引或名称） |

**`header` + `skiprows` 组合速查：**

```python
# 纯数据，无表头
metadata={"header": False}

# 首行是表头
metadata={"header": "auto"}

# 前 3 行是元数据，第 4 行是列名
metadata={"header": 3}

# 前 3 行是元数据，之后全是数据（无表头行）
metadata={"header": False}  # skiprows 不在 metadata 中，由 header=3 的语义处理
# 等价写法（在 _registry.py 中 skiprows 会从 metadata 读取）：
metadata={"header": 3}  # 整数 header = 跳过 N 行 + 用第 N+1 行做表头

# 跳过 5 行，无表头（用于 reference/ 下的复杂文件）
metadata={"header": False}
# 注意：这种场景需要在 _registry.py 中同时传递 skiprows
# 或直接在模块中用 read_xlsx(path, header=False, skiprows=5) 调用
```

**实际注册示例：**

```python
# CSV，自动检测表头
register(DatasetEntry(
    category="my_data",
    name="with_header",
    file_path="/path/to/data.csv",
    metadata={"header": "auto"},
))

# CSV，无表头，自定义列名
register(DatasetEntry(
    category="my_data",
    name="no_header",
    file_path="/path/to/data.csv",
    columns=("wavelength", "spd"),
))

# XLSX，指定 sheet，跳过 1 行用第 2 行做表头
register(DatasetEntry(
    category="my_data",
    name="my_excel",
    file_path="/path/to/data.xlsx",
    metadata={"sheet": "Sheet1", "header": 1},
))

# XLS，跳过 1 行元数据，无表头，自定义列名
register(DatasetEntry(
    category="my_data",
    name="my_xls",
    file_path="/path/to/data.xls",
    columns=("wavelength", "F1", "F2", "F3"),
    metadata={"header": 1},
))
```

### 注册模式速查

```text
场景                          做法                                        示例
─────────────────────────────────────────────────────────────────────────────────────────
普通 CSV/XLSX，列结构规整     register(file_path=...)                      get_illuminant("D65")
文件格式复杂，需自定义解析     register(computed=True, compute_fn=解析函数)   get_gamut_data("pointer", L=50)
运行时按公式生成数据           register_computed(compute_fn=公式函数)        get_illuminant("blackbody", temperature=6500)
```

三种方式都注册到同一个 `_REGISTRY`，`get()` 根据 `computed` 字段决定走文件读取还是函数调用。

```python
import numpy as np
from color.datasets._registry import DatasetEntry, register, register_computed, get

# ① 普通文件 — 直接给 file_path，自动按扩展名选择 read_csv/read_xlsx/read_xls
register(DatasetEntry(
    category="my_leds",
    name="rgb_model",
    description="RGB LED model",
    file_path="/path/to/led.csv",
    columns=("wavelength", "r", "g", "b"),
))
data = get("my_leds", "rgb_model")

# ② 复杂文件 — 用 compute_fn 自行解析，返回 SpectralDict
def _parse_my_xls(**kwargs):
    import xlrd
    wb = xlrd.open_workbook("/path/to/complex.xls")
    # ... 自定义解析逻辑 ...
    return {"wavelength": wl_array, "value": val_array}

register(DatasetEntry(
    category="my_data",
    name="complex_sheet",
    computed=True,
    compute_fn=_parse_my_xls,
))
data = get("my_data", "complex_sheet")

# ③ 公式生成 — 纯计算，无文件
def _blackbody(wavelength_nm=None, temperature=6500.0):
    if wavelength_nm is None:
        wavelength_nm = np.arange(300, 831, 1.0)
    # ... Planck 公式 ...
    return {"wavelength": wavelength_nm, "radiance": radiance}

register_computed(
    category="my_spds",
    name="blackbody",
    compute_fn=_blackbody,
    description="Planck blackbody radiation",
)
data = get("my_spds", "blackbody", temperature=5500)
```

### 缓存机制

- 文件数据集：首次 `get()` 时懒加载，结果缓存，后续调用直接返回
- 计算数据集：按参数缓存（numpy 数组转 bytes 做 hash key）

### 计算数据集注册

```python
from color.datasets._registry import register_computed

def my_compute(wavelength_nm=None, param=1.0):
    # 必须返回 SpectralDict
    return {"wavelength": wl, "value": result}

register_computed(
    category="my_category",
    name="my_dataset",
    compute_fn=my_compute,
    description="My computed dataset",
)
```

---

## 文件读取工具

`_utils.py` 提供三种文件格式的读取函数，基于 pandas 实现，统一返回 `Dict[str, np.ndarray]`：

| 函数 | 格式 | 引擎 |
| ---- | ---- | ---- |
| `read_csv(path, *, header, skiprows, usecols, names)` | CSV | pandas `read_csv` |
| `read_xlsx(path, *, sheet, header, skiprows, usecols, names)` | XLSX | pandas + openpyxl |
| `read_xls(path, *, sheet, header, skiprows, usecols, names)` | XLS | pandas + xlrd |

所有参数均为 keyword-only（`*` 之后）。

**`header` 参数语义：**

| 值 | 行为 | pandas 映射 |
| -- | ---- | ----------- |
| `False` | 无表头，全部当数据 | `header=None` |
| `True` / `"auto"` | 自动检测首行是否为表头 | 先 `header=None`，再 `_auto_detect_header()` |
| `N`（整数） | 跳过 N 行，用第 N+1 行做表头 | `skiprows=N, header=0` |

**`skiprows` 参数：** 额外跳过行数，与 `header` 叠加。典型用法：

- `header=False, skiprows=3` — 跳过 3 行元数据，无表头
- `header=1` — 跳过 1 行，用第 2 行做表头（等价于 `skiprows=1, header=0`）

**`_auto_detect_header()` 逻辑（`header=True` 时）：**

1. 以 `header=None` 读取，检查首行
2. 首行含非数值文本 → 当作表头，用其列名，从数据中移除
3. 首行全为数值 → 当作数据，列名用默认值 `(wavelength, value)` 或 `(wavelength, col1, col2, ...)`

**其他特性：**

- 自动处理尾部逗号和空字段（CSV）
- 行长度不一致时用 NaN 填充（需通过 `columns` 指定列数）
- `skipinitialspace=True` 自动去除前导空格（CSV）
- 列名优先级：`DatasetEntry.columns` > 文件表头 > 文件名推断 > 默认值（`columns` 始终最高，即使文件有表头也会被覆盖）
- 注册时通过 `columns=` 指定列名，或 `metadata={"header": "auto"}` 启用自动检测

**`header` 默认值：**

| 调用方式 | 默认 |
| -------- | ---- |
| 直接调用 `read_csv` / `read_xlsx` / `read_xls` | `header=False`（向后兼容） |
| 通过注册表自动发现（standard_observers） | `header=True`（自动检测） |
| 通过注册表手动注册 | `header=False`（除非 metadata 中指定） |

**辅助函数：**

| 函数 | 说明 |
| ---- | ---- |
| `attest(condition, message)` | 类似 `assert` 但 `python -O` 下不可禁用 |
| `data_dir(*parts)` | 构建 `color/data/` 下的路径 |

---

## 添加新数据

根据数据所属类别，有三种添加场景：

### 场景一：添加 standard_observer 数据

标准观察者数据统一放在 `data/standard_observer_data/` 下，按子文件夹分类（cmfs、cone_fundamentals 等）。有两种方式：

**1.零配置 — 直接放文件**

往已有文件夹或新建文件夹放 CSV，import 时自动扫描注册。列名走通用回退。

```python
# 新建 data/standard_observer_data/mesopic/v_meso_5nm.csv，然后直接用：
get_standard_observer("mesopic", "v_meso_5nm")
# → {'wavelength': ..., 'col1': ...}
```

**2.`_CUSTOM_ENTRIES` — 指定列名和别名（推荐）**

在 `standard_observers.py` 顶部添加条目，可自定义列名、描述、类别别名：

```python
_CUSTOM_ENTRIES = [
    {
        "category": "mesopic",
        "stem": "v_meso_5nm",
        "columns": ("wavelength", "V_meso"),
        "description": "CIE 201x Mesopic V(λ) (5 nm)",
        "aliases": ["meso"],
    },
]
```

```python
get_standard_observer("meso", "v_meso_5nm")
# → {'wavelength': ..., 'V_meso': ...}
```

### 场景二：添加到已有类别（illuminants、color_cards 等）

在对应模块文件中调用 `register()`，数据自动归入该类别，用对应的 `get_xxx()` 访问。

```python
# 在 datasets/illuminants.py 中添加（文件型）：
from color.datasets._registry import DatasetEntry, register
from color.datasets._utils import data_dir

register(DatasetEntry(
    category="illuminants",
    name="my_led",
    description="Custom LED illuminant",
    file_path=str(data_dir("illuminants", "my_led.csv")),
    columns=("wavelength", "spd"),
))
# → get_illuminant("my_led")
```

### 场景三：添加全新类别

创建新模块 `datasets/mydata.py`，仿照已有模块编写注册和便捷函数：

```python
# datasets/mydata.py
from color.datasets._registry import DatasetEntry, register, SpectralDict
from color.datasets._utils import data_dir

register(DatasetEntry(
    category="my_category",
    name="my_data",
    description="My custom dataset",
    file_path=str(data_dir("my_category", "my_data.csv")),
    columns=("wavelength", "value"),
))

def get_my_data(name: str, **kwargs) -> SpectralDict:
    from color.datasets._registry import get
    return get("my_category", name, **kwargs)

def list_my_data():
    from color.datasets._registry import list_datasets
    return list_datasets("my_category")
```

临时使用（不创建模块）也可直接调用 `register()`：

```python
from color.datasets._registry import DatasetEntry, register, get

register(DatasetEntry(
    category="temp_analysis",
    name="experiment_01",
    description="Lab measurement 2026-05-14",
    file_path="/path/to/data.csv",
    columns=("wavelength", "R", "G", "B"),
))
data = get("temp_analysis", "experiment_01")
```

---

## 测试

测试位于 `color/datasets/tests/`，共 114 个测试用例。

```bash
# 运行全部测试
python -m pytest color/datasets/tests/ -v

# 运行单个模块测试
python -m pytest color/datasets/tests/test_illuminants.py -v
```

| 测试文件 | 覆盖内容 | 用例数 |
| -------- | -------- | -------- |
| `test_registry.py` | DatasetEntry、register、get、list、search、describe | 14 |
| `test_utils.py` | attest、data_dir、read_csv/xlsx/xls | 12 |
| `test_illuminants.py` | 文件光源 + 黑体/日光计算（Wien 位移律验证） | 22 |
| `test_color_cards.py` | macbeth、pmc、bcra 加载与内容验证 | 13 |
| `test_standard_observers.py` | 6 类别 + 别名 + 列名推断 + 描述 | 34 |
| `test_gamut_data.py` | pointer 多 sheet 加载 | 4 |
| `test_color_systems.py` | munsell_srgb 加载 | 4 |

---

## 数据来源

| 来源 | URL |
| ---- | ----- |
| CVRL（伦敦大学学院） | http://www.cvrl.org/ |
| RIT Munsell 色彩科学实验室 | https://www.rit.edu/science/munsell-color-science-lab-educational-resources |
| RIT Munsell 色度重命名 | http://www.rit-mcsl.org/MunsellRenotation/ |
