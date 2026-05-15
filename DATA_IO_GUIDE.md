# 数据加载脚本编写指南

> 在新 session 中提供数据文件夹，按照本指南执行即可生成完整的 datasets 加载层。

---

## 一、你需要准备什么

### 1. 将数据文件夹放到项目目录下

建议结构（或类似结构，不必完全一致）：

```
h:\Pycharm_projects\colour_develop\
└── data/                          # 你的原始数据
    ├── illuminants/
    │   ├── D65.csv
    │   ├── A.csv
    │   └── ...
    ├── cmfs/
    │   ├── CIE_1931_2deg.csv
    │   └── ...
    ├── colour_checkers/
    │   ├── xrite_classic.xlsx
    │   └── ...
    └── ...
```

### 2. 确认每个文件的格式

对每个文件，确认以下信息：

- **分隔符**：逗号 `,`、制表符 `\t`、还是其他
- **是否有表头**：第一行是列名还是数据
- **列的含义**：每列代表什么（波长、功率、X/Y/Z、x/y/Y 等）
- **数值范围**：波长单位（nm）、功率是否归一化、色度坐标是 0-1 还是 0-100

### 3. 准备一个文件清单

用以下格式整理你的数据文件，新 session 中直接粘贴即可：

```
文件路径 | 数据类型 | 分隔符 | 有表头 | 列含义 | 备注
--------|---------|--------|--------|--------|-----
data/illuminants/D65.csv | 光谱功率分布 | 逗号 | 是 | wavelength,power | 300-830nm, 5nm间隔
data/illuminants/A.csv | 光谱功率分布 | 逗号 | 是 | wavelength,power | 同上
data/cmfs/CIE_1931_2deg.csv | 色匹配函数 | 逗号 | 是 | wavelength,X,Y,Z | 360-830nm, 1nm间隔
data/colour_checkers/xrite_classic.xlsx | 色卡 | - | 是 | name,x,y,Y | 24色块
...
```

---

## 二、新 session 中怎么和我说

直接复制以下模板，填入你的信息：

```
我需要你为我的颜色科学库编写数据加载脚本。

## 数据文件夹位置
h:\Pycharm_projects\colour_develop\data\

## 文件清单
（粘贴上面的表格）

## 期望的输出
1. datasets/ 目录下的加载模块
2. 每种数据类型一个文件（illuminants.py, cmfs.py 等）
3. 一个 __init__.py 聚合导出

## 额外要求
- 我的库名是 xxx（你的包名）
- 数据读取用 pandas / numpy（选一个）
- 需要懒加载 / 直接加载（选一个）
- （其他你想说的话）
```

---

## 三、我会为你生成什么

### 目标目录结构

```
your_package/
├── data/                           # 你的原始数据（不动）
│   ├── illuminants/
│   ├── cmfs/
│   └── ...
└── datasets/                       # 我生成的加载脚本
    ├── __init__.py                 # 聚合导出
    ├── _utils.py                   # 通用加载工具函数
    ├── illuminants.py              # 光源加载
    ├── cmfs.py                     # CMF 加载
    ├── colour_checkers.py          # 色卡加载
    └── ...
```

### 每个加载模块的模式

```python
# datasets/illuminants.py 示例

from pathlib import Path
import numpy as np
import pandas as pd

_DATA_DIR = Path(__file__).parent.parent / "data" / "illuminants"

def _load_csv(name: str) -> dict[str, np.ndarray]:
    """从 CSV 加载光谱数据"""
    path = _DATA_DIR / f"{name}.csv"
    df = pd.read_csv(path)
    return {
        "wavelength": df["wavelength"].to_numpy(),
        "power": df["power"].to_numpy(),
    }

# 缓存
_CACHE: dict[str, dict] = {}

def get_illuminant(name: str) -> dict[str, np.ndarray]:
    """获取光源光谱数据（懒加载 + 缓存）"""
    if name not in _CACHE:
        _CACHE[name] = _load_csv(name)
    return _CACHE[name]

def list_illuminants() -> list[str]:
    """列出所有可用的光源"""
    return [p.stem for p in _DATA_DIR.glob("*.csv")]

# __init__.py 中导出
__all__ = ["get_illuminant", "list_illuminants"]
```

### 你会得到的产物

1. **每个数据类型的加载模块** — 包含 `get_xxx()` 和 `list_xxx()` 函数
2. **`_utils.py`** — 通用 CSV/Excel 读取、缓存、路径处理
3. **`__init__.py`** — 统一导出入口
4. **适配你已有代码的接口** — 如果你已有 `SpectralDistribution` 等类，加载函数可以直接返回实例

---

## 四、注意事项

- **不要在新 session 中上传整个 `colour/` 目录**，只需提供 `data/` 文件夹和你的包名
- **如果文件格式不一致**（有的 CSV 用逗号，有的用制表符），在清单中注明
- **如果数据量极大**（单个文件 >100MB），告诉我，我会用内存映射或分块读取
- **如果你已有部分 datasets 代码**，在新 session 中一起提供，我会基于现有代码扩展
