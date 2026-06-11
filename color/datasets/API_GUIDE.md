# color.datasets API 使用指南

本文档按 `color.datasets.__all__` 覆盖顶层 API。这里写最小使用案例；
模块边界、数据组织和读取约定见 [`README_DETAILS.md`](README_DETAILS.md)。

## 顶层 API 总览

| API | 功能 | 推荐场景 |
| --- | --- | --- |
| `DatasetEntry` | 描述一个注册数据集 | 注册自定义静态数据 |
| `get` | 通用数据读取入口 | 已知 category 和 name |
| `describe` | 查看注册信息 | 检查来源、列名、metadata |
| `clear_cache` | 清除读取缓存 | 文件修改后强制重读 |
| `list_categories` | 列出类别 | 探索数据目录 |
| `list_datasets` | 列出数据集 | 探索某一类别 |
| `register` | 注册数据集 | 添加临时或项目内静态文件 |
| `search` | 搜索注册表 | 不确定名称时查找 |
| `get_illuminant` | 读取静态光源 | D65、A、F 系列等 |
| `list_illuminants` | 列出静态光源 | 查看可用光源 |
| `get_color_card` | 读取色卡数据 | Macbeth、PMC、BCRA |
| `list_color_cards` | 列出色卡 | 查看可用色卡 |
| `get_standard_observer` | 读取标准观察者数据 | CMFs、LMS、光视效率等 |
| `list_standard_observers` | 列出某个标准观察者子类 | 查看 CMFs 或 LMS 文件 |
| `list_standard_observer_categories` | 列出标准观察者子类 | 查看可用子类别 |
| `describe_standard_observer` | 查看标准观察者注册信息 | 检查文件来源和 metadata |
| `get_gamut_data` | 读取色域参考数据 | Pointer、MacAdam |
| `list_gamut_data` | 列出色域数据 | 查看可用色域参考 |
| `get_color_system` | 读取颜色系统数据 | Munsell sRGB |
| `list_color_systems` | 列出颜色系统 | 查看可用颜色系统 |
| `get_reflectance_spectrum` | 读取 UEF 反射谱 | Munsell、Agfa、Paper、Forest |
| `list_reflectance_spectra` | 列出 UEF 反射谱 | 查看可用反射谱 |

## 核心读取与发现

### `get(category, name, **kwargs)`

用途：按注册表类别和名称读取原始数组字典。

输入：`category`、`name` 和可选读取参数。  
返回：`dict[str, numpy.ndarray]`，数组只读。

普通静态数据：

```python
from color.datasets import get

d65 = get("illuminants", "D65")
print(d65.keys())  # wavelength, spd
```

标准观察者 category alias：

```python
from color.datasets import get

xyz = get("standard_observers.cmf", "cie1931 xyz_1nm")
print(xyz["wavelength"], xyz["X"], xyz["Y"], xyz["Z"])
```

带参数的特殊数据：

```python
from color.datasets import get

pointer_l50 = get("gamut_data", "pointer", L=50)
```

注意：`get(...)` 返回的是原始数据，不做光谱包装、不插值、不转换单位。

### `describe(category, name)`

用途：查看注册信息，不加载数据文件。

输入：`category`、`name`。  
返回：`DatasetEntry`。

```python
from color.datasets import describe

entry = describe("illuminants", "D65")
print(entry.description)
print(entry.metadata)
```

注意：适合检查数据来源、列名、读取参数和 metadata。

### `clear_cache(category=None, name=None)`

用途：清除 `get(...)` 的缓存结果。

输入：可选 category 和 name。  
返回：被清除的缓存项数量。

清空全部：

```python
from color.datasets import clear_cache

removed = clear_cache()
```

按 category 清理：

```python
from color.datasets import clear_cache

removed = clear_cache("illuminants")
```

按 category + name 清理：

```python
from color.datasets import clear_cache

removed = clear_cache("illuminants", "D65")
```

注意：只传 `name` 不传 `category` 不允许，因为不同类别可以有同名数据。

### `list_categories()` / `list_datasets(category=None)`

用途：探索注册表。

输入：`list_categories()` 无参数；`list_datasets(...)` 可传 category。  
返回：字符串列表。

```python
from color.datasets import list_categories, list_datasets

categories = list_categories()
illuminants = list_datasets("illuminants")
all_names = list_datasets()
```

注意：`list_datasets()` 不传 category 时返回所有类别中的数据名。

### `search(keyword)`

用途：按名称和描述搜索数据集。

输入：搜索关键词。  
返回：`list[DatasetEntry]`。

```python
from color.datasets import search

matches = search("MacAdam")
for entry in matches:
    print(entry.category, entry.name)
```

注意：搜索用于发现数据，不保证结果唯一；真正读取仍应使用明确的 category/name。

高级调试时，datasets 的资源名规范化函数保留在子模块 registry 中：

```python
from color.datasets._registry import canonicalize_name

print(canonicalize_name(" CIE 1931 XYZ 1 nm "))
print(canonicalize_name("0.1 nm"))
```

普通用户不需要直接调用它；优先使用 `get(...)`、`list_datasets(...)` 和 `search(...)`。

## 注册自定义静态数据

### `DatasetEntry`

用途：描述一个静态数据集。

输入：category、name、description、file path、columns、read options、metadata 等。  
返回：dataclass 实例，通常传给 `register(...)`。

```python
from color.datasets import DatasetEntry

entry = DatasetEntry(
    category="example_spds",
    name="led_450",
    description="Example LED SPD",
    file_path="led_450.csv",
    columns=("wavelength", "spd"),
    read_options={"header": False},
    metadata={"quantity": "relative_spd", "wavelength_unit": "nm"},
)
```

注意：`metadata` 只描述数据，不控制读取行为。

### `register(entry)`

用途：把 `DatasetEntry` 加入注册表。

输入：`DatasetEntry`。  
返回：`None`。

无表头 CSV：

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from color.datasets import DatasetEntry, get, register

with TemporaryDirectory() as tmp:
    path = Path(tmp) / "led.csv"
    path.write_text("400,0.0\n500,1.0\n600,0.2\n", encoding="utf-8")

    register(DatasetEntry(
        category="example_spds",
        name="led_no_header",
        description="No-header example",
        file_path=str(path),
        columns=("wavelength", "spd"),
        read_options={"header": False},
    ))

    data = get("example_spds", "led_no_header")
```

有表头 CSV：

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from color.datasets import DatasetEntry, get, register

with TemporaryDirectory() as tmp:
    path = Path(tmp) / "measured.csv"
    path.write_text("wavelength,spd\n400,0.1\n500,0.8\n", encoding="utf-8")

    register(DatasetEntry(
        category="example_spds",
        name="measured_with_header",
        description="Header example",
        file_path=str(path),
        read_options={"header": True},
    ))

    data = get("example_spds", "measured_with_header")
```

Excel sheet：

```python
from color.datasets import DatasetEntry, get, register

register(DatasetEntry(
    category="example_tables",
    name="vendor_excel",
    description="Named sheet example",
    file_path="vendor.xlsx",
    read_options={"sheet": "SPD", "header": True},
))

data = get("example_tables", "vendor_excel")
```

自定义 `parser_fn`：

```python
from color.datasets import DatasetEntry, get, register

def parse_semicolon_file(path, **kwargs):
    wavelength = []
    spd = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            wl, value = line.strip().split(";")
            wavelength.append(float(wl))
            spd.append(float(value))
    return {"wavelength": wavelength, "spd": spd}

register(DatasetEntry(
    category="example_spds",
    name="semicolon_file",
    description="Custom parser example",
    file_path="semicolon.txt",
    parser_fn=parse_semicolon_file,
))

data = get("example_spds", "semicolon_file")
```

注意：测试和示例应使用临时目录；不要把测试专用 CSV 放进 `color/data/`。

## Illuminants

### `get_illuminant(name, **kwargs)` / `list_illuminants()`

用途：读取或列出静态光源 SPD。

输入：光源名称。  
返回：`dict[str, ndarray]` 或名称列表。

```python
from color.datasets import get_illuminant, list_illuminants

print(list_illuminants())
d65 = get_illuminant("D65")
a = get_illuminant("A")
```

注意：这里是静态文件。黑体辐射和公式 daylight 使用 `color.generators`。

## Color Cards

### `get_color_card(name, **kwargs)` / `list_color_cards()`

用途：读取或列出静态色卡反射谱。

输入：色卡名称。  
返回：`dict[str, ndarray]` 或名称列表。

```python
from color.datasets import get_color_card, list_color_cards

print(list_color_cards())
pmc = get_color_card("pmc")
blue_sky = pmc["Blue Sky"]
```

注意：色卡列名通常是 patch 名；包装到 `color.spectra` 后可通过对应通道名访问。

## Standard Observers

### `get_standard_observer(category, name, **kwargs)`

用途：读取标准观察者子类别数据。

输入：标准观察者子类别和数据名。  
返回：`dict[str, ndarray]`。

CMFs：

```python
from color.datasets import get_standard_observer

xyz = get_standard_observer("cmfs", "cie1931_xyz_1nm")
```

LMS fundamentals：

```python
from color.datasets import get_standard_observer

lms = get_standard_observer("lms", "cie2006_lms2_linE_1nm")
```

光视效率：

```python
from color.datasets import get_standard_observer

photopic = get_standard_observer("luminous", "cie2008_v2_linE_1nm")
scotopic = get_standard_observer("luminous_efficiency", "scotopic_v_1nm")
```

category alias：

```python
from color.datasets import get_standard_observer

same = get_standard_observer("xyz", "cie1931 xyz 1 nm")
```

注意：常用 CMFs/LMS 的语义快捷入口在 `color.datasets.standard_observers` 子模块中，
不属于 `color.datasets` 顶层 API。

### `list_standard_observers(category)` / `list_standard_observer_categories()`

用途：探索标准观察者子类别和数据名。

输入：子类别名称或别名。  
返回：字符串列表。

```python
from color.datasets import (
    list_standard_observer_categories,
    list_standard_observers,
)

categories = list_standard_observer_categories()
cmfs = list_standard_observers("cmfs")
lms = list_standard_observers("lms")
```

### `describe_standard_observer(category, name)`

用途：查看标准观察者数据的注册信息。

输入：子类别和数据名。  
返回：`DatasetEntry`。

```python
from color.datasets import describe_standard_observer

entry = describe_standard_observer("cmfs", "cie1931_xyz_1nm")
print(entry.source)
print(entry.metadata)
```

## Gamut Data

### `get_gamut_data(name, **kwargs)` / `list_gamut_data()`

用途：读取或列出静态色域参考数据。

输入：数据名称和可选参数。  
返回：`dict[str, ndarray]` 或名称列表。

Pointer 全量数据：

```python
from color.datasets import get_gamut_data

pointer = get_gamut_data("pointer")
```

Pointer 某个 L* 切面：

```python
from color.datasets import get_gamut_data

pointer_l50 = get_gamut_data("pointer", L=50)
```

MacAdam 静态数据：

```python
from color.datasets import get_gamut_data, list_gamut_data

print(list_gamut_data())
macadam_d65 = get_gamut_data("macadam_limits_D65")
```

注意：色域几何、coverage 和 boundary 分析属于 `color.gamut`；这里仅读取静态表。

## Color Systems

### `get_color_system(name, **kwargs)` / `list_color_systems()`

用途：读取或列出颜色系统静态表。

输入：颜色系统名称。  
返回：`dict[str, ndarray]` 或名称列表。

```python
from color.datasets import get_color_system, list_color_systems

print(list_color_systems())
munsell = get_color_system("munsell_srgb")
```

注意：这里读取的是静态表，不执行 Munsell 转换算法。

## Reflectance Spectra

### `get_reflectance_spectrum(name, **kwargs)`

用途：读取 UEF spectral reflectance 数据集。

输入：数据集名称。  
返回：`dict[str, ndarray]`。

便捷入口：

```python
from color.datasets import get_reflectance_spectrum

munsell = get_reflectance_spectrum("munsell_matt")
print(munsell["wavelength"])
```

等价通用入口：

```python
from color.datasets import get

munsell = get("reflectance_spectra.uef", "munsell_matt")
```

读取另一个 UEF 数据集：

```python
from color.datasets import get_reflectance_spectrum

agfa = get_reflectance_spectrum("agfa_it872")
forest = get_reflectance_spectrum("forest_birch")
```

注意：当前只注册已审计的运行时 CSV。Natural colors 未注册。

### `list_reflectance_spectra()`

用途：列出当前 UEF reflectance spectra。

输入：无。  
返回：字符串列表。

```python
from color.datasets import list_reflectance_spectra

for name in list_reflectance_spectra():
    print(name)
```

## 常见串联

### datasets -> spectra

`datasets` 返回原始字典；需要重采样或通道对象时再包装。

```python
from color.datasets import get_reflectance_spectrum
from color.spectra import from_columns

raw = get_reflectance_spectrum("munsell_matt")
sample = from_columns(raw, y="sample_1", name="Munsell matt sample 1")
```

### datasets -> colorimetry

```python
from color.datasets import get_color_card
from color.spectra import from_columns
from color.colorimetry import reflectance_to_XYZ

raw = get_color_card("pmc")
patch = from_columns(raw, y="Blue Sky", name="PMC Blue Sky")
XYZ = reflectance_to_XYZ(patch, illuminant="D65")
```

注意：`datasets` 不做积分；积分属于 `color.colorimetry`。
