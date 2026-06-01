# datasets - 色彩科学静态数据集加载模块详细说明

`color.datasets` 是 `color/data/` 的公共读取层，负责静态数据集注册、懒加载、缓存、文件解析和特殊静态文件解析。应用代码应优先使用这里的 API，而不是直接读取原始数据文件。

公式或程序生成的数据不属于 `datasets`，例如黑体辐射和 CIE D-series daylight 现在位于 `color.generators`。

## 快速上手

```python
from color.datasets import (
    get_color_card,
    get_color_system,
    get_gamut_data,
    get_illuminant,
    get_standard_observer,
)
from color.generators.blackbody import blackbody_spd
from color.generators.illuminants import daylight_spd

d65 = get_illuminant("D65")
bb = blackbody_spd(temperature=6500)
daylight = daylight_spd(cct=5000)

xyz = get_standard_observer("cmfs", "cie1931_xyz_1nm")
lms = get_standard_observer("lms", "cie2006_lms2_logE_5nm")

macbeth = get_color_card("macbeth")
pointer_50 = get_gamut_data("pointer", L=50)
munsell = get_color_system("munsell_srgb")
```

所有加载函数返回 `dict[str, numpy.ndarray]`。通常第一列为 `wavelength`，其余键取决于数据集，例如 `X/Y/Z`、`l/m/s`、`spd`、色卡色块名或 Munsell 字段名。

## 模块结构

```text
color/datasets/
├── __init__.py              # 统一导出公共 API
├── _registry.py             # DatasetEntry、注册表、懒加载和缓存
├── _utils.py                # CSV/XLSX/XLS 读取工具
├── illuminants.py           # 静态标准光源
├── color_cards.py           # Macbeth、PMC、BCRA 色卡
├── standard_observers.py    # CVRL 标准观察者数据自动发现
├── gamut_data.py            # Pointer 和 MacAdam 色域数据
├── color_systems.py         # Munsell sRGB 数据
└── tests/                   # pytest 测试
```

数据流：

```text
用户调用 get_xxx()
        │
        ▼
类别模块解析名称或别名
        │
        ▼
_registry.get(category, name, **kwargs)
        │
        ├── 通用静态文件：read_csv/read_xlsx/read_xls
        └── 特殊静态文件：parser_fn(file_path, **kwargs)
```

## 公共 API

### 统一入口

| 函数 | 说明 |
| --- | --- |
| `get(category, name, **kwargs)` | 按注册表类别和名称加载静态数据 |
| `describe(category, name)` | 返回 `DatasetEntry`，不加载数据内容 |
| `clear_cache(category=None, name=None)` | 清除缓存数据；可清全部、某类别或某个数据集 |
| `list_datasets(category=None)` | 列出某类别或全部类别的数据集名称 |
| `list_categories()` | 列出已注册类别 |
| `search(keyword)` | 在名称和描述中搜索数据集 |

类别名和数据集名称支持 canonical 匹配：大小写、空格、下划线、连字符、斜杠和括号等分隔符不会影响查找，数值中的小数点会规范化为 `p`。例如下面几种写法会访问同一个数据集：

```python
get("standard_observers.cmfs", "cie1931_xyz_1nm")
get("Standard Observers CMFS", "CIE 1931 XYZ 1 nm")
get("standard-observers/cmfs", "cie-1931-xyz-1nm")
```

### 类别入口

| 类别 | 加载函数 | 列表函数 |
| --- | --- | --- |
| 光源 | `get_illuminant(name, **kwargs)` | `list_illuminants()` |
| 色卡 | `get_color_card(name, **kwargs)` | `list_color_cards()` |
| 标准观察者 | `get_standard_observer(category, name, **kwargs)` | `list_standard_observers(category)` |
| 色域 | `get_gamut_data(name, **kwargs)` | `list_gamut_data()` |
| 色彩体系 | `get_color_system(name, **kwargs)` | `list_color_systems()` |

## 已注册数据

### Illuminants

| 名称 | 类型 | 内容 |
| --- | --- | --- |
| `A` | 文件 | CIE Illuminant A |
| `D65` | 文件 | CIE Illuminant D65 |
| `fluorescents` | 文件 | CIE F1-F12 fluorescent lamp SPDs |

黑体辐射和 CIE D-series daylight 不是静态数据集，使用 `color.generators`：

```python
from color.generators.blackbody import blackbody_spd
from color.generators.illuminants import daylight_spd

bb = blackbody_spd(temperature=5500)
d50 = daylight_spd(cct=5000)
```

### Color Cards

| 名称 | 内容 | 色块数 |
| --- | --- | ---: |
| `macbeth` | Macbeth ColorChecker Classic | 24 |
| `pmc` | Preferred Memory Color chart | 31 |
| `bcra` | BCRA CERAM Series II calibration tiles | 12 |

这些数据仍属于静态文件数据，只是文件格式比较特殊，因此通过 `parser_fn` 解析。

```python
from color.datasets.color_cards import MACBETH_PATCH_NAMES, BCRA_TILE_NAMES

macbeth = get_color_card("macbeth")
dark_skin = macbeth["Dark Skin"]
```

### Standard Observers

标准观察者数据来自 `color/data/standard_observer_data/`，主体数据共 106 个 CSV 文件，按子目录自动发现并注册。

| 子类别 | 别名 | 文件数 | 内容 |
| --- | --- | ---: | --- |
| `cmfs` | `cmf`, `xyz` | 15 | CIE 1931/1964/2012 XYZ 与 RGB colour matching functions |
| `cone_fundamentals` | `cone`, `lms`, `fundamentals` | 27 | LMS cone fundamentals |
| `luminous_efficiency` | `luminous`, `v_lambda`, `vl`, `efficiency` | 29 | Photopic/scotopic luminous efficiency |
| `prereceptoral_filters` | `filter`, `macular`, `lens` | 11 | Macular pigment and lens density |
| `chromaticity_coordinates` | `chromaticity`, `chroma`, `xy` | 16 | CIE and MacLeod-Boynton chromaticity coordinates |
| `photopigments` | `pigment`, `pigments` | 7 | Photopigment absorption spectra |

```python
xyz = get_standard_observer("xyz", "cie1931_xyz_1nm")
v_lambda = get_standard_observer("vl", "cie2008_v2_linE_1nm")
```

测试中的自定义数据会在运行时创建临时文件，不需要在 `color/data/` 中保留测试专用 CSV。

### Gamut Data

| 名称 | 内容 |
| --- | --- |
| `pointer` | Pointer Calculations sheet 解析后的 L\* 分层边界数据 |
| `pointer_raw` | PointerData.xls 的原始 sheet 读取入口 |
| `macadam_limits_A` | Illuminant A 下缓存的 MacAdam optimal colour stimuli |
| `macadam_limits_C` | Illuminant C 下缓存的 MacAdam optimal colour stimuli |
| `macadam_limits_D65` | Illuminant D65 下缓存的 MacAdam optimal colour stimuli |

```python
pointer = get_gamut_data("pointer")
pointer_50 = get_gamut_data("pointer", L=50)
specloc = get_gamut_data("pointer_raw", sheet="SpecLoc")
macadam = get_gamut_data("macadam_limits_D65")
```

MacAdam 数据字段为 `x, y, Y, X, Z, L, a, b, C, h`。其中 `x, y, Y`
是缓存的 xyY 数据，`X/Z` 和 Lab/LCHab 字段是为了后续 gamut 分析派生出来的。

### Color Systems

| 名称 | 内容 | 样本数 |
| --- | --- | ---: |
| `munsell_srgb` | RIT Munsell renotation / real sRGB data | 1625 |

## 列名规则

文件读取工具默认返回 `dict[str, np.ndarray]`。列名来源按以下优先级确定：

```text
DatasetEntry.columns > 显式 names > 文件表头 > 文件名模式推断 > 通用默认名
```

标准观察者 CSV 默认启用表头自动检测。若首行全为数值，则根据文件名推断列名：

| 文件名模式 | 推断列名 |
| --- | --- |
| `xyz` | `wavelength, X, Y, Z` |
| `sbrgb` | `wavelength, R, G, B` |
| `lms`, `smj`, `sp_` | `wavelength, l, m, s` |
| `_v2_`, `_v10_`, `vl1924` | `wavelength, V` |
| `scotopic` | `wavelength, V_prime` |
| `mb` | `wavelength, l, s, B` |
| `chro` | `wavelength, x, y, z` |
| `macular`, `lens_` | `wavelength, optical_density` |
| `sucrodsh`, `sucrodsm` | `wavelength, absorption` |

## 注册表系统

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
| `file_path` | 静态文件数据集路径 |
| `parser_fn` | 特殊静态文件解析函数；接收 `file_path` 作为第一个参数 |
| `columns` | 显式列名，优先级最高 |
| `read_options` | 文件读取控制字段，如 `header`、`skiprows`、`sheet` |
| `metadata` | 只描述数据本身；不会影响读取行为 |

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

### 文件读取选项

| 键 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `header` | `False | True | "auto" | int` | `False` | 表头处理策略；`True` 与 `"auto"` 等价 |
| `skiprows` | `int` | `0` | 额外跳过的行数 |
| `usecols` | `Sequence[int]` | `None` | 按列索引筛选 |
| `sheet` | `int | str` | `0` | Excel sheet，仅 XLS/XLSX |
| `coerce_numeric` | `bool` | `False` | 将非数值单元格转为 `NaN`，用于少量混合内容的原始表 |

`header` 语义：

| 值 | 行为 |
| --- | --- |
| `False` | 文件无表头，所有行都作为数据 |
| `True` / `"auto"` | 自动检测首行：若首行含文本则作为列名；若首行全为数值则作为数据 |
| `N` | 跳过 N 行，并把下一行作为表头 |

如果只是跳过前 N 行但文件没有表头，请使用 `read_options={"skiprows": N, "header": False}`。不要用 `header=N` 表达这种场景，因为整数 `header` 的含义是“跳过 N 行后读取表头”。

### metadata 字段约定

`metadata` 是普通 `dict`，但只用于描述数据本身。读取层不会消费 `metadata` 中的任何键；会影响读取行为的字段必须放在 `read_options` 中，例如 `header`、`skiprows`、`usecols`、`sheet`、`coerce_numeric`。

需要自定义解析的特殊文件不要把 callable 放入 `metadata`，而应使用 `DatasetEntry.parser_fn`。

推荐描述字段：

| 键 | 说明 |
| --- | --- |
| `quantity` | 数据表达的物理量或表格类型，如 `spectral_reflectance`、`colour_matching_function`、`luminous_efficiency` |
| `value_unit` | 数值单位或归一化方式，如 `relative`、`dimensionless`、`reflectance_factor` |
| `wavelength_unit` | 波长单位，当前光谱数据通常为 `nm` |
| `wavelength_range_nm` | 波长范围，如 `(380, 780)` |
| `sampling_interval_nm` | 采样间隔 |
| `observer_angle_deg` | 标准观察者视场角，如 2 或 10 |
| `illuminant` / `reference_white` | 关联光源或参考白 |
| `color_space` / `color_spaces` | 数据所在颜色空间 |
| `domain` | 数据域，如 `spectral` |
| `source_collection` | 数据集合来源，如 `CVRL` |
| `patch_count` / `sample_count` | 色卡、色彩体系等表格的样本数量 |

这些描述字段已经覆盖了标准观察者、色卡、Pointer gamut 和 Munsell 数据；后续新增数据集可以继续补充同类字段。

## 生成数据

公式生成数据位于 `color.generators`，而不是 `color.datasets`：

```python
from color.generators import generate
from color.generators.blackbody import blackbody_spd
from color.generators.illuminants import daylight_spd

bb = generate("blackbody", "planck", temperature=6500)
d50 = daylight_spd(cct=5000)
```

这样可以保持边界清楚：

```text
datasets   = 静态数据读取
generators = 公式/程序生成数据
```

## 缓存和只读返回

静态文件和 parser 结果都会按调用参数缓存，因此同一 Excel 文件用不同 `sheet` 读取时不会互相污染。传入 numpy 数组时，缓存键使用数组 dtype、shape 和 bytes 表示。

`get()` 返回缓存数据的只读副本。调用方如果需要修改数组，应先显式复制：

```python
d65 = get_illuminant("D65")
spd = d65["spd"].copy()
spd *= 100
```

如果底层文件发生变化，或在 notebook 中反复调试自定义注册项，可以清除缓存后重新读取：

```python
from color.datasets import clear_cache

clear_cache()                         # 清除全部缓存
clear_cache("illuminants")            # 清除某个类别
clear_cache("gamut_data", "pointer")  # 清除某个数据集
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

## 测试

使用项目虚拟环境运行：

```powershell
.\.venv\Scripts\python.exe -m pytest color/datasets/tests -q --basetemp .pytest_tmp
```

如果系统临时目录权限受限，保留 `--basetemp .pytest_tmp` 可以让 pytest 在工作区内创建临时目录。

## 数据来源

| 来源 | URL |
| --- | --- |
| CVRL, UCL | http://www.cvrl.org/ |
| RIT Munsell Color Science Lab | https://www.rit.edu/science/munsell-color-science-lab-educational-resources |
| RIT Munsell Renotation | http://www.rit-mcsl.org/MunsellRenotation/ |
