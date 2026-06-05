# datasets - 静态数据集加载模块详细说明

`color.datasets` 是 `color/data/` 的公共读取层，负责静态数据注册、懒加载、缓存、通用 CSV/XLS/XLSX 解析，以及少量特殊静态文件的自定义解析。

公式或程序生成的数据不属于 `datasets`，例如黑体辐射、CIE D-series daylight 和个体化 cone fundamentals，应使用 `color.generators` 或对应计算模块。

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
用户调用 get_xxx()
        |
        v
类别模块确定 category/name
        |
        v
_registry.get(category, name, **kwargs)
        |
        |-- 通用静态文件：read_csv/read_xlsx/read_xls
        `-- 特殊静态文件：parser_fn(file_path, **kwargs)
```

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

这些文件格式比较特殊，因此通过 `parser_fn` 解析。

### Standard Observers

标准观察者数据来自 `color/data/standard_observer_data/`，按子目录自动发现并注册。

| 子类别 | 常用别名 | 内容 |
| --- | --- | --- |
| `cmfs` | `cmf`, `xyz` | CIE 1931/1964/2012 XYZ 与 RGB colour matching functions |
| `cone_fundamentals` | `cone`, `lms`, `fundamentals` | LMS cone fundamentals |
| `luminous_efficiency` | `luminous`, `v_lambda`, `vl`, `efficiency` | Photopic/scotopic luminous efficiency |
| `prereceptoral_filters` | `filter`, `macular`, `lens` | Macular pigment and lens density |
| `chromaticity_coordinates` | `chromaticity`, `chroma`, `xy` | CIE and MacLeod-Boynton chromaticity coordinates |
| `photopigments` | `pigment`, `pigments` | Photopigment absorption spectra |

常用文件也提供语义入口，例如 `get_cie1931_xyz_cmfs(...)` 和 `get_cie2006_lms_2degree_fundamentals(...)`。这些入口位于 `color.datasets.standard_observers`，不从 `color.datasets` 顶层导出。

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

### Gamut Data

| 名称 | 内容 |
| --- | --- |
| `pointer` | Pointer Calculations sheet 解析后的 L\* 分层边界数据 |
| `pointer_raw` | PointerData.xls 的原始 sheet 读取入口 |
| `macadam_limits_A` | Illuminant A 下缓存的 MacAdam optimal colour stimuli |
| `macadam_limits_C` | Illuminant C 下缓存的 MacAdam optimal colour stimuli |
| `macadam_limits_D65` | Illuminant D65 下缓存的 MacAdam optimal colour stimuli |

### Color Systems

| 名称 | 内容 | 样本数 |
| --- | --- | ---: |
| `munsell_srgb` | RIT Munsell renotation / real sRGB data | 1625 |

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

## DatasetEntry

所有数据集通过 `DatasetEntry` 注册：

```python
from color.datasets._registry import DatasetEntry, register

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

### read_options

| 键 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `header` | `False | True | "auto" | int` | `False` | 表头策略 |
| `skiprows` | `int` | `0` | 额外跳过行数 |
| `usecols` | `Sequence[int]` | `None` | 读取的列索引 |
| `sheet` | `int | str` | `0` | Excel sheet |
| `coerce_numeric` | `bool` | `False` | 将非数值单元格转换为 `NaN` |

不要用 `metadata` 控制读取行为。读取行为应放在 `read_options` 中；特殊文件解析应放在 `parser_fn` 中。

## 缓存与只读数组

- `get()` 返回只读数组；需要修改时请先 `.copy()`。
- 静态文件和 parser 结果都会按调用参数缓存，包括 Excel 的 `sheet`。
- 需要重读时可调用 `clear_cache()`。
- 测试和示例中的自定义文件应使用临时目录创建，不应把测试专用 CSV 常驻在 `color/data/` 中。
