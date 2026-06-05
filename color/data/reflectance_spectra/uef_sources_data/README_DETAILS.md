# UEF 反射光谱源数据说明

本文档说明 `color/data/reflectance_spectra/uef_sources_data/` 中保存的 UEF 反射光谱源数据工作簿。这里的 `.xlsx` 文件是人工查阅和审计用数据源；程序运行时默认读取同级目录 `../uef_csv/` 中导出的 CSV。

## 数据来源

这些数据来自 University of Eastern Finland Computational Spectral Imaging 组公开的 spectral databases。当前纳入工程的数据主要服务于颜色科学中的表面反射率、光谱重建、色卡验证和材料泛化测试。

原始 UEF 数据通常以 ASCII 或 MATLAB `.mat` 文件发布。为了让工程内数据更容易审查，本项目先把每组数据转换为独立 workbook，并保留：

- `metadata`：数据来源、样本数、波长范围、转换规则和特殊处理说明。
- `audit`：每个数值 sheet 的 shape、最小值、最大值、均值、NaN 数、负值数等审计信息。
- `samples`：样本列名。
- 数值 sheet：统一采用 `wavelength, sample_1, sample_2, ...` 格式。

## 与运行时 CSV 的关系

`uef_sources_data/` 中的 workbook 用于人工核查，不是 `color.datasets` 的直接读取源。正式注册的数据从 `color/data/reflectance_spectra/uef_csv/` 读取，以减少 Excel 解析开销并保持运行时行为稳定。

导出规则如下：

| 数据组 | workbook sheet | 运行时 CSV |
|---|---|---|
| Munsell matt | `reflectance_0_1` | `munsell_matt.csv` |
| Munsell glossy all | `reflectance_0_1` | `munsell_glossy_all.csv` |
| Agfa IT8.7/2 | `reflectance_0_1` | `agfa_it872.csv` |
| Paper spectra | `reflectance_0_1` | 对应 `paper_*.csv` |
| Forest colors | `corrected_reflectance_0_1` | 对应 `forest_*.csv` |

Natural colors 暂不进入 `uef_sources_data/` 和运行时 CSV。原因是该数据为 AOTF 12-bit A/D 原始输出，严格转换成反射率需要白板和暗电流参考，即类似 `(DN_sample - DN_dark) / (DN_white - DN_dark)` 的校正信息；当前公开文件不足以支持这个转换。

## 已保存工作簿

| 文件 | 内容 | 样本数 | 波长范围 | 间隔 | 运行时采用 |
|---|---:|---:|---:|---:|---|
| `munsell_matt.xlsx` | Munsell 哑光色卡反射率 | 1269 | 380-800 nm | 1 nm | 是 |
| `munsell_glossy_all.xlsx` | Munsell 高光色卡，specular excluded | 1600 | 380-780 nm | 1 nm | 是 |
| `agfa_it872.xlsx` | Agfa IT8.7/2 扫描仪校准色靶 | 288 | 400-700 nm | 10 nm | 是 |
| `paper_cardboardsce.xlsx` | 纸板，SCE | 140 | 400-700 nm | 10 nm | 是 |
| `paper_cardboardsci.xlsx` | 纸板，SCI | 210 | 400-700 nm | 10 nm | 是 |
| `paper_newsprintsce.xlsx` | 新闻纸，SCE | 36 | 400-700 nm | 10 nm | 是 |
| `paper_newsprintsci.xlsx` | 新闻纸，SCI | 54 | 400-700 nm | 10 nm | 是 |
| `paper_papersce.xlsx` | 纸张，SCE | 144 | 400-700 nm | 10 nm | 是 |
| `paper_papersci.xlsx` | 纸张，SCI | 216 | 400-700 nm | 10 nm | 是 |
| `forest_spruce.xlsx` | 云杉针叶反射光谱 | 349 | 390-850 nm | 5 nm | 是，使用修正 sheet |
| `forest_birch.xlsx` | 桦树叶片反射光谱 | 337 | 390-850 nm | 5 nm | 是，使用修正 sheet |
| `forest_pine.xlsx` | 松树针叶反射光谱 | 370 | 390-850 nm | 5 nm | 是，使用修正 sheet |

## 各数据组说明

### Munsell Matt

`munsell_matt.xlsx` 保存 1269 个 Munsell Book of Color matte finish 色片的光谱反射率。原始 README 说明测量设备为 Perkin-Elmer Lambda 9 UV/VIS/NIR spectrophotometer，波长范围为 380-800 nm，间隔 1 nm。

该数据适合作为光谱重建、反射率恢复和颜色科学算法验证的核心基准数据之一。workbook 中 `raw` 与 `reflectance_0_1` 数值一致，均为 0-1 反射率尺度。

### Munsell Glossy All

`munsell_glossy_all.xlsx` 保存 1600 个 Munsell glossy finish 色片的反射率。原始 README 说明测量设备为 Perkin-Elmer Lambda 18 UV/VIS spectrophotometer，并明确为 specular excluded。

这意味着该数据不是“带镜面高光的图像外观”，而是高光材料在排除镜面分量后的本体反射率。它适合用来测试从哑光色卡训练得到的模型能否泛化到 glossy 材料。

### Agfa IT8.7/2

`agfa_it872.xlsx` 保存 Agfa ColorReference / IT8.7/2 校准色靶的 288 个 patch。原始 README 中 `.mat` 文件包含 289 列，其中第 289 列是 Minolta white calibration sample；本项目注册数据只保留正式 288 个 patch。

原始数据为百分比反射率，`reflectance_0_1 = raw_percent / 100`。该数据适合作为外部色靶验证和扫描仪/摄影介质相关的测试集。

### Paper Spectra

Paper spectra 包含 coloured newsprint、paper 和 cardboard 样本，分别提供 SCI 和 SCE 两种测量模式：

- `SCI`：Specular Component Included，包含镜面分量。
- `SCE`：Specular Component Excluded，排除镜面分量。

原始 README 说明测量设备为 Minolta CM-2002 spectrophotometer，波长范围为 400-700 nm，间隔 10 nm。原始数据为百分比反射率，workbook 中 `reflectance_0_1 = raw_percent / 100`。

部分 paper 样本在除以 100 后会略大于 1，当前保留原值，不裁剪。这类值可能来自测量、校准或材料表面特性，不应在源数据阶段静默修改。

### Forest Colors

Forest colors 包含 Scots pine、Norway spruce 和 birch 的针叶/叶片反射光谱。原始 README 说明测量在 1992 年 6 月生长季晴天进行，每条光谱代表一棵生长树上大量叶片或针叶的平均光谱。测量设备为 PR 713/702 AM spectroradiometer，波长范围为 390-850 nm，间隔 5 nm。

MATLAB `.mat` 数据与原始解析结果一致，说明大于 1 的值不是 ASCII 解析错误。审计时发现每个 Forest 子集只有一个样本出现明显或轻微大于 1 的情况，因此 workbook 同时保留：

- `raw_relative`：UEF 原始相对数据，不做修改。
- `corrected_reflectance_0_1`：人工审查后的候选修正版，用于当前运行时 CSV。

当前修正规则为：

| 子集 | 修正样本 | 修正比例 |
|---|---|---:|
| spruce | `spruce_0016` | `0.1` |
| pine | `pine_0206` | `0.1` |
| birch | `birch_0262` | `1 / 1.4` |

这些修正是工程审计决策，不是 UEF 官方尺度声明。需要复核原始数据时应查看 `raw_relative`。

## 与 `color.datasets` 的对应关系

这些数据注册在：

```python
get("reflectance_spectra.uef", name)
```

便捷入口为：

```python
from color.datasets import get_reflectance_spectrum, list_reflectance_spectra

names = list_reflectance_spectra()
munsell = get_reflectance_spectrum("munsell_matt")
```

返回值是原始列字典，例如：

```python
munsell["wavelength"]
munsell["2.5_R_9_2"]
```

如果需要进行插值、积分或与 `color.colorimetry` 串联，建议再用 `color.spectra.from_columns(...)` 包装成 `SpectralDistribution` 或 `MultiSpectralDistribution`。

## 使用注意

- `uef_sources_data/` 是审计源，不是运行时读取源。
- `uef_csv/` 是 `datasets` 正式读取源。
- Munsell、Agfa、Paper 的运行时数据是 0-1 反射率。
- Forest 的运行时数据是人工审查后的 `corrected_reflectance_0_1`。
- Natural colors 当前不注册为反射率数据，因为缺少严格 AOTF DN 到反射率转换所需的暗电流和白板参考。
