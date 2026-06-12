# datasets - 静态数据集加载模块详细说明

`color.datasets` 是 `color/data/` 的公共读取层，负责静态数据注册、懒加载、缓存、通用 CSV/XLS/XLSX 解析，以及少量特殊静态文件的自定义解析。

逐项 API 的最小用法见 [`API_GUIDE.md`](API_GUIDE.md)。本文件保留更完整的模块说明、数据清单、设计边界和使用注意。

公式或程序生成的数据不属于 `datasets`，例如黑体辐射、CIE D-series daylight、LED、理想光谱和个体化 cone fundamentals，应使用 `color.generators` 或对应计算模块。

`datasets` 也不负责把数据包装成光谱对象。需要插值、重采样、外推、算术、通道访问或只读对象封装时，应使用 `color.spectra`。

## 快速使用

```python
from color.datasets import (
    get,
    get_color_card,
    get_color_system,
    get_gamut_data,
    get_illuminant,
    get_reflectance_spectrum,
    get_standard_observer,
)

d65 = get_illuminant("D65")
xyz = get_standard_observer("cmfs", "cie1931_xyz_1nm")
macbeth = get_color_card("macbeth")
uef_munsell = get_reflectance_spectrum("munsell_matt")
pointer = get_gamut_data("pointer", L=50)
munsell_srgb = get_color_system("munsell_srgb")

# 通用入口也始终可用。
same = get("reflectance_spectra.uef", "munsell_matt")
```

所有加载函数返回 `dict[str, numpy.ndarray]`。通常第一列为 `wavelength`，其他键取决于数据集，例如 `spd`、`X/Y/Z`、`l/m/s`、色卡 patch 名或反射谱样本名。

返回数组是只读的缓存结果。需要修改时必须先 `.copy()`，避免误改缓存中的数据视图。

## 模块结构

```text
color/datasets/
|-- __init__.py              # 统一导出公共 API，并导入类别模块触发注册
|-- _registry.py             # DatasetEntry、注册表、懒加载和缓存
|-- _utils.py                # CSV/XLSX/XLS 读取工具
|-- illuminants.py           # 静态标准光源
|-- color_cards.py           # Macbeth、PMC、BCRA 色卡
|-- standard_observers.py    # CVRL 标准观察者数据自动发现
|-- reflectance_spectra.py   # UEF 反射谱数据
|-- gamut_data.py            # Pointer 和 MacAdam 色域数据
|-- color_systems.py         # Munsell sRGB 数据
`-- tests/
```

数据流：

```text
用户调用 get_xxx(...) 或 get(category, name)
        |
        v
类别模块确定 category/name
        |
        v
_registry.get(category, name, **kwargs)
        |
        |-- 通用静态文件：read_csv/read_xlsx/read_xls
        `-- 特殊静态文件：parser_fn(file_path, **kwargs)
        |
        v
返回只读 dict[str, ndarray]
```

类别模块在 `color.datasets.__init__` 中导入，以触发注册。注册阶段只创建 `DatasetEntry`，记录路径、读取参数和 metadata；不会读取完整数据文件。顶层 API 只导出稳定的读取、列举、注册和搜索入口；标准观察者的高频语义函数保留在 `color.datasets.standard_observers` 子模块中，避免顶层变重。

## 公共 API

### 通用入口

| 函数 | 说明 |
| --- | --- |
| `get(category, name, **kwargs)` | 按注册表类别和名称加载数据 |
| `describe(category, name)` | 返回 `DatasetEntry`，不加载数据 |
| `clear_cache(category=None, name=None)` | 清除缓存数据 |
| `list_datasets(category=None)` | 列出数据集名称 |
| `list_categories()` | 列出已注册类别 |
| `search(keyword)` | 在名称和描述中搜索数据集 |

类别名和数据集名称支持 canonical 匹配。大小写、空格、下划线、连字符、斜杠和括号等分隔符不会影响查找；资源名中的小数点会规范化为 `p`。

### 类别入口

| 类别 | 加载函数 | 列表函数 |
| --- | --- | --- |
| 光源 | `get_illuminant(name, **kwargs)` | `list_illuminants()` |
| 色卡 | `get_color_card(name, **kwargs)` | `list_color_cards()` |
| 标准观察者 | `get_standard_observer(category, name, **kwargs)` | `list_standard_observers(category)` |
| 反射谱 | `get_reflectance_spectrum(name, **kwargs)` | `list_reflectance_spectra()` |
| 色域数据 | `get_gamut_data(name, **kwargs)` | `list_gamut_data()` |
| 颜色系统 | `get_color_system(name, **kwargs)` | `list_color_systems()` |

这些函数的逐项输入、输出和最小案例集中放在 `API_GUIDE.md` 中。这里保留 API 分类，是为了帮助理解模块结构。

## 已注册数据

### Illuminants

| 名称 | 内容 |
| --- | --- |
| `A` | CIE Illuminant A |
| `D65` | CIE Illuminant D65 |
| `fluorescents` | CIE F1-F12 fluorescent lamp SPDs |

黑体辐射和 CIE D-series daylight 是公式生成数据，应使用 `color.generators`。

### Color Cards

| 名称 | 内容 | 色块数 |
| --- | --- | ---: |
| `macbeth` | Macbeth ColorChecker Classic | 24 |
| `pmc` | Preferred Memory Color chart | 31 |
| `bcra` | BCRA CERAM Series II calibration tiles | 12 |

这些文件格式比较特殊，因此通过 `parser_fn` 解析。返回字典通常包含 `wavelength` 和每个 patch 的反射谱列。

### Standard Observers

标准观察者数据来自 `color/data/standard_observer_data/`，按子目录自动发现并注册。注册时只扫描目录和 CSV 文件名，不打开 CSV 首行；列名推断发生在第一次 `get(...)` 真正读取对应文件之后。

| 子类别 | 常用别名 | 内容 |
| --- | --- | --- |
| `cmfs` | `cmf`, `xyz` | CIE 1931/1964/2012 XYZ 与 RGB colour matching functions |
| `cone_fundamentals` | `cone`, `lms`, `fundamentals` | LMS cone fundamentals |
| `luminous_efficiency` | `luminous`, `v_lambda`, `vl`, `efficiency` | Photopic/scotopic luminous efficiency |
| `prereceptoral_filters` | `filter`, `macular`, `lens` | Macular pigment and lens density |
| `chromaticity_coordinates` | `chromaticity`, `chroma`, `xy` | CIE and MacLeod-Boynton chromaticity coordinates |
| `photopigments` | `pigment`, `pigments` | Photopigment absorption spectra |
| `iprgc` | `melanopic`, `melanopsin`, `mel` | CIE S 026 melanopic / ipRGC action spectrum |

常用文件也提供语义入口，例如 `get_cie1931_xyz_cmfs(...)` 和 `get_cie2006_lms_2degree_fundamentals(...)`。这些入口位于 `color.datasets.standard_observers`，不从 `color.datasets` 顶层导出。

示例：

```python
from color.datasets.standard_observers import (
    get_cie1931_xyz_cmfs,
    get_cie2006_lms_2degree_fundamentals,
)

cmfs = get_cie1931_xyz_cmfs(interval_nm=1)
lms = get_cie2006_lms_2degree_fundamentals(interval_nm=1, energy="linE")
mel = get_standard_observer("iprgc", "cie_s026_melanopic_1nm")
```

`interval_nm` 选择已有源文件采样间隔，不做插值；需要重采样时应进入 `color.spectra`。

`iprgc` 当前只注册 CIE S 026 melanopic 单曲线，不重复注册 `sc/mc/lc/rh`。完整五通道 alpha-opic action spectra 可在 `color.spectra.from_alpha_opic_action_spectra()` 中由已有标准数据组合得到。ipRGC 主要分布在外周，因此该数据按外周 ipRGC 激活语义使用，不提供 2° / 10° 两套视角区分。

### Reflectance Spectra

UEF 反射谱数据注册在：

```text
reflectance_spectra.uef
```

便捷入口：

```python
from color.datasets import get_reflectance_spectrum, list_reflectance_spectra

names = list_reflectance_spectra()
munsell = get_reflectance_spectrum("munsell_matt")
```

等价通用入口：

```python
from color.datasets import get

munsell = get("reflectance_spectra.uef", "munsell_matt")
```

数据目录分为两层：

| 目录 | 用途 |
| --- | --- |
| `color/data/reflectance_spectra/uef_csv/` | 程序运行时读取的 CSV |
| `color/data/reflectance_spectra/uef_sources_data/` | 人工审计和查阅用 workbook |

注册数据包括 Munsell matt、Munsell glossy all、Agfa IT8.7/2、Paper spectra 和 Forest spectra。Munsell、Agfa、Paper 使用 workbook 中的 `reflectance_0_1` sheet 导出 CSV；Forest 使用经过审查的 `corrected_reflectance_0_1` sheet 导出 CSV。

Natural colors 暂未注册。当前数据来自 AOTF 12-bit 数值，但缺少可用于严格转换的 dark/white calibration，即不能可靠执行：

```text
reflectance = (DN_sample - DN_dark) / (DN_white - DN_dark)
```

因此 Natural 数据保留在审计材料中，不作为运行时 reflectance factor 数据注册。

### Gamut Data

| 名称 | 内容 |
| --- | --- |
| `pointer` | Pointer Calculations sheet 解析后的 L\* 分层边界数据 |
| `pointer_raw` | PointerData.xls 的原始 sheet 读取入口 |
| `macadam_limits_A` | Illuminant A 下缓存的 MacAdam optimal colour stimuli |
| `macadam_limits_C` | Illuminant C 下缓存的 MacAdam optimal colour stimuli |
| `macadam_limits_D65` | Illuminant D65 下缓存的 MacAdam optimal colour stimuli |

`datasets` 只读取这些表；几何边界、覆盖率和 inside 判断属于 `color.gamut`。

### Color Systems

| 名称 | 内容 | 样本数 |
| --- | --- | ---: |
| `munsell_srgb` | RIT Munsell renotation / real sRGB data | 1625 |

这里读取的是静态表，不执行 Munsell 颜色系统转换算法。

## 列名规则

文件读取工具默认返回 `dict[str, np.ndarray]`。列名来源按以下优先级确定：

```text
DatasetEntry.columns > 显式 names > 文件表头 > 文件名模式推断 > 通用默认名
```

如果读取标准观察者 CSV 时没有显式列名且没有表头，系统会根据文件名推断常见列名，例如：

| 文件名模式 | 推断列名 |
| --- | --- |
| `xyz` | `wavelength, X, Y, Z` |
| `sbrgb` | `wavelength, R, G, B` |
| `lms`, `smj`, `sp_` | `wavelength, l, m, s` |
| `v2`, `v10`, `vl1924` | `wavelength, V` |
| `scotopic` | `wavelength, V_prime` |
| `macular`, `lens_` | `wavelength, optical_density` |

## 名称解析

`datasets` 使用资源名 canonicalization。大小写、空格、下划线、连字符、斜杠和括号等分隔符不会影响查找；资源名中的特殊符号会保留必要语义：

- `0.1 nm` 会规范化为 `0p1nm`，避免和 `01nm` 混淆。
- `V(lambda)` 和 `V(λ)` 可匹配到相同资源语义。
- `10 degree` 和 `10°` 可匹配到相同资源语义。

标准观察者还有 category alias，例如 `cmf` 可解析到 `cmfs`，`lms` 可解析到 `cone_fundamentals`。

## 注册表系统

所有数据集通过 `DatasetEntry` 注册：

```python
from color.datasets import DatasetEntry, register

register(DatasetEntry(
    category="illuminants",
    name="my_led",
    description="Custom LED illuminant",
    file_path="path/to/my_led.csv",
    columns=("wavelength", "spd"),
    read_options={"header": False},
    metadata={"quantity": "relative_spd", "wavelength_unit": "nm"},
))
```

核心字段：

| 字段 | 说明 |
| --- | --- |
| `category` | 注册类别，例如 `illuminants` 或 `standard_observers.cmfs` |
| `name` | 类别内唯一名称 |
| `description` | 人类可读描述 |
| `source` | 数据来源 |
| `file_path` | 静态文件路径 |
| `parser_fn` | 特殊静态文件解析函数；接收 `file_path` 作为第一个参数 |
| `columns` | 显式列名；优先级最高 |
| `read_options` | 文件读取控制字段，如 `header`、`skiprows`、`sheet`、`coerce_numeric` |
| `metadata` | 只描述数据本身；不会影响读取行为 |

`metadata` 不控制读取行为。读取行为应放在 `read_options` 中；特殊文件解析应放在 `parser_fn` 中。这个边界很重要：metadata 应服务科学复现和数据说明，不应改变同一文件的解析结果。

### read_options

| 键 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `header` | `False | True | "auto" | int` | `False` | 表头策略 |
| `skiprows` | `int` | `0` | 额外跳过行数 |
| `usecols` | `Sequence[int]` | `None` | 读取的列索引 |
| `sheet` | `int | str` | `0` | Excel sheet |
| `coerce_numeric` | `bool` | `False` | 将非数值单元格转换为 `NaN` |

`header=True` 和 `header="auto"` 会检测第一行是否为文本表头。`header=N` 表示跳过 `N` 行并把下一行当表头。如果只想跳过行而不使用表头，使用：

```python
read_options = {"skiprows": 3, "header": False}
```

如果文件有表头：

```python
read_options = {"header": True}
```

如果读取 Excel 指定 sheet：

```python
read_options = {"sheet": "SPD", "header": True}
```

### 自定义 parser

当静态文件无法通过通用 CSV/XLS/XLSX reader 正确解析时，使用 `parser_fn`：

```python
def parse_special_file(path: str, **kwargs):
    ...
    return {"wavelength": wavelength, "spd": spd}

register(DatasetEntry(
    category="example",
    name="special_spd",
    description="Special static SPD file",
    file_path="path/to/special.txt",
    parser_fn=parse_special_file,
))
```

`parser_fn` 只表示“特殊静态文件解析”，不表示“公式生成”。公式生成请放在 `color.generators`。

### metadata 字段约定

`metadata` 是普通 `dict`，但只用于描述数据本身。读取层不会消费 `metadata` 中的任何键；会影响读取行为的字段必须放在 `read_options` 中，例如 `header`、`skiprows`、`usecols`、`sheet`、`coerce_numeric`。

需要自定义解析的特殊文件不要把 callable 放入 `metadata`，而应使用 `DatasetEntry.parser_fn`。

推荐描述字段：

| 键                               | 说明                                                         |
| -------------------------------- | ------------------------------------------------------------ |
| `quantity`                       | 数据表达的物理量或表格类型，如 `spectral_reflectance`、`colour_matching_function`、`luminous_efficiency` |
| `value_unit`                     | 数值单位或归一化方式，如 `relative`、`dimensionless`、`reflectance_factor` |
| `wavelength_unit`                | 波长单位，当前光谱数据通常为 `nm`                            |
| `wavelength_range_nm`            | 波长范围，如 `(380, 780)`                                    |
| `sampling_interval_nm`           | 采样间隔                                                     |
| `observer_angle_deg`             | 标准观察者视场角，如 2 或 10                                 |
| `illuminant` / `reference_white` | 关联光源或参考白                                             |
| `color_space` / `color_spaces`   | 数据所在颜色空间                                             |
| `domain`                         | 数据域，如 `spectral`                                        |
| `source_collection`              | 数据集合来源，如 `CVRL`                                      |
| `patch_count` / `sample_count`   | 色卡、色彩体系等表格的样本数量                               |

这些描述字段已经覆盖了标准观察者、色卡、Pointer gamut 和 Munsell 数据；后续新增数据集可以继续补充同类字段。

## 缓存与只读数组

- `get()` 返回只读数组；需要修改时请先 `.copy()`。
- 静态文件和 `parser_fn` 结果都会按调用参数缓存，包括 Excel 的 `sheet`。
- `describe()`、`list_datasets()` 和注册阶段只访问注册表；第一次 `get(...)` 才会打开对应数据文件。
- 需要重读时可调用 `clear_cache()`。
- 测试和示例中的自定义文件应使用临时目录创建，不应把测试专用 CSV 常驻在 `color/data/` 中。

示例：

```python
from color.datasets import clear_cache, get_illuminant

d65 = get_illuminant("D65")
editable = d65["spd"].copy()

clear_cache("illuminants", "D65")
```

## 添加新数据

### 添加 standard observer CSV

把 CSV 放入 `color/data/standard_observer_data/<category>/`。导入 `color.datasets.standard_observers` 时会自动扫描并注册。

如需列名、描述或别名，在 `standard_observers.py` 的 `_CUSTOM_ENTRIES` 中添加条目：

```python
_CUSTOM_ENTRIES = [
    {
        "category": "mesopic",
        "stem": "v_meso_5nm",
        "columns": ("wavelength", "V_meso"),
        "description": "Mesopic luminous efficiency function",
        "aliases": ["meso"],
        "read_options": {"header": "auto"},
    },
]
```

### 添加已有类别的数据

在对应类别模块中注册：

```python
from color.datasets._registry import DatasetEntry, register
from color.datasets._utils import data_dir

register(DatasetEntry(
    category="illuminants",
    name="custom_led",
    description="Measured custom LED SPD",
    file_path=str(data_dir("illuminants", "custom_led.csv")),
    columns=("wavelength", "spd"),
))
```

### 添加全新类别

新建一个模块，例如 `color/datasets/mydata.py`，在模块导入时注册数据，并提供 `get_mydata()`、`list_mydata()` 这类便捷函数。若希望统一导出，还需要在 `color/datasets/__init__.py` 中导入该模块和公共函数。

## 行为约定

- `get()` 返回只读数组；需要修改时请先 `.copy()`。
- 静态文件和 parser 数据都按调用参数缓存，包括 Excel 的 `sheet`；需要重读时可调用 `clear_cache()`。
- 注册时会检查 canonical 名称冲突；例如 `my-data` 和 `My Data` 不能在同一规范类别下同时注册。
- 测试和示例中的自定义文件使用临时目录创建，不应把测试专用 CSV 常驻在 `color/data/` 中。
- 读取行为只放在 `DatasetEntry.read_options`；特殊解析放在 `DatasetEntry.parser_fn`；描述性信息只放在 `DatasetEntry.metadata`。

## 和其他模块的串联

`datasets` 返回原始字典；后续计算通常由其它模块承接。

包装为光谱对象：

```python
from color.datasets import get_reflectance_spectrum
from color.spectra import from_columns

raw = get_reflectance_spectrum("munsell_matt")
sample = from_columns(raw, y="sample_1", name="Munsell matt sample 1")
```

用于色度积分：

```python
from color.datasets import get_color_card
from color.spectra import from_columns
from color.colorimetry import reflectance_to_XYZ

raw = get_color_card("pmc")
patch = from_columns(raw, y="Blue Sky", name="PMC Blue Sky")
XYZ = reflectance_to_XYZ(patch, illuminant="D65")
```

如果需要公式数据：

```python
from color.generators import blackbody_spd

bb = blackbody_spd(6500)
```

## 测试与示例约定

测试和 examples 中需要注册临时数据时，应在临时目录里创建文件，不应把测试专用 CSV 常驻到 `color/data/` 中。`color/data/` 只保存真实静态参考数据或已审计运行时数据。

完整工作流示例放在 `examples/datasets/`；`API_GUIDE.md` 只保留最小调用案例。
