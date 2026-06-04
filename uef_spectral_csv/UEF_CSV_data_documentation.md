# UEF 光谱 CSV 数据说明与使用注意事项

> 适用对象：已经使用 `download_uef_spectral_reconstruction.py` 下载，并用 `convert_uef_spectra_to_csv.py v1.4.1` 解析得到的 UEF/University of Kuopio 光谱 CSV 数据。   
> 当前日志对应总样本数：**5232 条光谱**，**13 个解析表**。  
> 生成日期：2026-06-04

---

## 1. 文档目的

这份文档用于说明当前已经转换好的 CSV 数据，尤其是后续做颜色科学中的光谱重建任务时容易产生歧义的地方，包括：

- 每个数据集的样本数量为什么是当前日志中的数值；
- `sample`、`spectrum`、`physical sample` 三者并不总是同义；
- 反射率数值可能是 `0–1`、`0–100`，或 Natural colors 中的 AOTF 12-bit 原始计数；
- `Munsell glossy` 虽然是高光色卡，但该数据测量时排除了镜面反射，不等于真实图像中的高光亮斑；
- Agfa 数据中为什么是 289 条，而不是 288 条；
- Paper spectra 为什么会有 800 条，而不是 18 + 72 + 70 = 160 条；
- 建模前应该做哪些检查，避免把不同尺度的数据直接混合训练。

这份文档建议和 CSV 文件、下载脚本、转换脚本放在同一个项目仓库中，作为数据说明和实验复现说明。

---

## 2. 当前 CSV 输出概览

根据你当前成功运行的日志，转换结果如下：

```text
[ok] munsell_matt_spectrophotometer/munsell_matt: 1269 spectra x 421 bands
[ok] munsell_glossy_all_spectrophotometer/munsell_glossy_all: 1600 spectra x 401 bands
[info] optional dataset not present: munsell_glossy_subset_spectrophotometer (munsell400_700_10.asc)
[ok] agfa_it872/agfa_it872: 289 spectra x 31 bands
[info] natural_colors: parsed 219 candidate rows; kept 218 documented spectra
[ok] natural_colors/natural_colors: 218 spectra x 61 bands
[ok] forest_colors/spruce: 349 spectra x 93 bands
[ok] forest_colors/birch: 337 spectra x 93 bands
[ok] forest_colors/pine: 370 spectra x 93 bands
[ok] paper_spectra/cardboardsce: 140 spectra x 31 bands
[ok] paper_spectra/cardboardsci: 210 spectra x 31 bands
[ok] paper_spectra/newsprintsce: 36 spectra x 31 bands
[ok] paper_spectra/newsprintsci: 54 spectra x 31 bands
[ok] paper_spectra/papersce: 144 spectra x 31 bands
[ok] paper_spectra/papersci: 216 spectra x 31 bands

Done.
Parsed tables: 13
Total spectra: 5232
```

---

## 3. 生成的 CSV 文件说明

默认转换后通常会得到这些文件：

```text
uef_spectral_csv_v4/
  summary.csv
  all_spectra_wide_raw.csv
  all_spectra_wide_400_700_10.csv
  all_spectra_long_400_700_10.csv
  per_dataset_wide/
    *.csv
```

### 3.1 `summary.csv`

用于快速查看每个解析子表的信息，包括：

- `dataset`
- `subdataset`
- `n_samples`
- `wavelength_start_nm`
- `wavelength_end_nm`
- `n_wavelengths`
- `source_file`
- `notes`

建议每次转换后首先打开 `summary.csv`，确认样本数、波段范围、解析文件路径是否符合预期。

### 3.2 `all_spectra_wide_400_700_10.csv`

这是当前最推荐用于建模的文件。它的典型列结构如下：

```text
sample_id,dataset,subdataset,label,source_file,nm_400,nm_410,...,nm_700
```

含义：

| 列名 | 含义 |
|---|---|
| `sample_id` | 转换脚本生成的唯一行 ID，格式通常为 `dataset__subdataset__0001` |
| `dataset` | 数据集名称，例如 `munsell_matt_spectrophotometer` |
| `subdataset` | 子数据集名称，例如 `spruce`、`papersci`、`cardboardsce` |
| `label` | 原始或脚本生成的样本标签；Munsell 当前多为编号标签，Agfa 含 A1、A2、neutral、black、white、calibration 等标签 |
| `source_file` | 原始解析文件路径 |
| `nm_400` 到 `nm_700` | 400–700 nm、10 nm 间隔的光谱数值 |

宽表格式适合机器学习建模：

```text
一行 = 一条光谱
一列 = 一个波长
```

### 3.3 `all_spectra_wide_raw.csv`

该文件保留所有数据集的原始波长列的并集。例如：

- Munsell matt 原始为 380–800 nm、1 nm；
- Munsell glossy all 原始为 380–780 nm、1 nm；
- Natural colors 原始为 400–700 nm、5 nm；
- Forest colors 原始为 390–850 nm、5 nm；
- Agfa 和 Paper 原始为 400–700 nm、10 nm。

不同数据集没有覆盖的波长列会是空值。该文件适合检查原始数据，但不如 `all_spectra_wide_400_700_10.csv` 适合直接建模。

### 3.4 `all_spectra_long_400_700_10.csv`

长表格式：

```text
sample_id,dataset,subdataset,label,wavelength_nm,value,source_file
```

适合作图、抽样检查、画单条光谱曲线或按数据集统计波段分布。

### 3.5 `per_dataset_wide/*.csv`

每个数据集或子数据集一个宽表，保留该子数据集的原始波长采样。适合做单数据集实验或检查原始波段。

---

## 4. 当前样本数量解释

当前总光谱数为：

```text
1269 + 1600 + 289 + 218 + 1056 + 800 = 5232
```

详细如下：

| 数据集 | 子数据集 | 当前 CSV 光谱数 | 原始波段 | 原始波段数 | 说明 |
|---|---|---:|---|---:|---|
| Munsell matt spectrophotometer | `munsell_matt` | 1269 | 380–800 nm, 1 nm | 421 | 哑光 Munsell 色片；适合作为主训练/基准数据 |
| Munsell glossy all spectrophotometer | `munsell_glossy_all` | 1600 | 380–780 nm, 1 nm | 401 | 高光 Munsell 色片；原始测量为 specular excluded |
| Agfa IT8.7/2 | `agfa_it872` | 289 | 400–700 nm, 10 nm | 31 | 288 个色卡 patch + 1 个 Minolta white calibration sample |
| Natural colors | `natural_colors` | 218 | 400–700 nm, 5 nm | 61 | 自然样本；AOTF 12-bit 原始 A/D 输出，不是普通 0–1 反射率 |
| Forest colors | `spruce` | 349 | 390–850 nm, 5 nm | 93 | 云杉针叶光谱 |
| Forest colors | `birch` | 337 | 390–850 nm, 5 nm | 93 | 桦树叶光谱 |
| Forest colors | `pine` | 370 | 390–850 nm, 5 nm | 93 | 松树针叶光谱 |
| Paper spectra | `cardboardsce` | 140 | 400–700 nm, 10 nm | 31 | 纸板，SCE 测量，含不同背景/条件 |
| Paper spectra | `cardboardsci` | 210 | 400–700 nm, 10 nm | 31 | 纸板，SCI 测量，含不同背景/条件 |
| Paper spectra | `newsprintsce` | 36 | 400–700 nm, 10 nm | 31 | 新闻纸，SCE 测量，含不同背景/条件 |
| Paper spectra | `newsprintsci` | 54 | 400–700 nm, 10 nm | 31 | 新闻纸，SCI 测量，含不同背景/条件 |
| Paper spectra | `papersce` | 144 | 400–700 nm, 10 nm | 31 | 彩色纸，SCE 测量，含不同背景/条件 |
| Paper spectra | `papersci` | 216 | 400–700 nm, 10 nm | 31 | 彩色纸，SCI 测量，含不同背景/条件 |

---

## 5. 关于 `sample` 数量的关键说明

### 5.1 CSV 中的一行是“一条光谱”，不一定是“一个独立物理样本”

在当前 CSV 中：

```text
1 row = 1 spectrum
```

但这并不总是等于：

```text
1 row = 1 unique physical object
```

尤其是 Paper spectra，一个物理纸张样本可能在不同测量条件下有多条光谱，例如：

- SCI / SCE；
- 黑色背景；
- 白色背景；
- 不透明纸堆条件。

因此，Paper spectra 的 800 条光谱不是 800 个完全独立的纸张材料，而是多个物理样本在不同测量设置下展开后的光谱集合。

### 5.2 Agfa 的 289 条不是错误

Agfa IT8.7/2 色卡本身有 288 个 patch，但原始 ASCII 文件还包含第 289 个样本，即 Minolta white calibration sample。因此转换结果中：

```text
agfa_it872 = 289 spectra
```

是合理的。

做建模时有两种选择：

1. **归档/完整保留：** 保留 289 条；
2. **严格色卡实验：** 排除第 289 条 calibration sample，只保留 288 个真实 target patch。

可用如下代码排除 Agfa calibration 行：

```python
import pandas as pd

csv_path = r"E:\Python projects\spetrum_data_from_uef\uef_spectral_csv_v4\all_spectra_wide_400_700_10.csv"
df = pd.read_csv(csv_path)

df_no_agfa_cal = df[~((df["dataset"] == "agfa_it872") & (df["label"] == "minolta_white_calibration"))].copy()
print(df.shape, df_no_agfa_cal.shape)
```

如果某次转换中 `label` 没有正确写成 `minolta_white_calibration`，也可以检查 Agfa 的最后一行：

```python
agfa = df[df["dataset"] == "agfa_it872"]
print(agfa.tail())
```

### 5.3 Natural colors 的 218 条是按 README 保留的数量

Natural colors 的本地文件曾解析出 219 个候选 61-band 行，但 README 标称为 218 条光谱。当前 v1.4.1 解析结果保留了 218 条 documented spectra，因此：

```text
natural_colors = 218 spectra
```

这是当前项目中建议采用的版本，便于和 UEF 官方说明保持一致。

### 5.4 Forest colors 的一行通常是大量叶片的平均光谱

Forest colors 中的每个测量不是单片叶子的微观光谱，而是生长树木上大量叶片/针叶的平均光谱。因此它适合做植被类外部测试，但不应该解释为“单片叶子级别”的样本。

### 5.5 Paper spectra 的 800 条是测量条件展开后的数量

Paper spectra 原始物理样本数为：

```text
newsprint: 18
paper:     72
cardboard: 70
```

但数据同时包含 SCI/SCE，以及不同背景/纸堆测量条件，所以 CSV 中会展开为：

```text
cardboardsce: 140
cardboardsci: 210
newsprintsce: 36
newsprintsci: 54
papersce: 144
papersci: 216
Total paper spectra: 800
```

建模时要特别注意：如果用 Paper spectra 做 train/test 随机拆分，同一个物理纸样的不同测量条件可能被分到训练集和测试集，从而造成数据泄漏。更严格的评估应按材料类别、原始物理样本编号或测量组进行分组划分。

---

## 6. 波段与重采样说明

当前推荐建模文件 `all_spectra_wide_400_700_10.csv` 统一到：

```text
400, 410, 420, ..., 700 nm
```

也就是 31 维输出：

```text
R_400, R_410, ..., R_700
```

不同数据集到统一网格的处理逻辑如下：

| 原始数据 | 原始波段 | 到 400–700/10 nm 的处理 |
|---|---|---|
| Munsell matt | 380–800 nm, 1 nm | 选取/插值到 10 nm 网格；目标波长都存在 |
| Munsell glossy all | 380–780 nm, 1 nm | 选取/插值到 10 nm 网格；目标波长都存在 |
| Agfa IT8.7/2 | 400–700 nm, 10 nm | 原生匹配，无需插值 |
| Natural colors | 400–700 nm, 5 nm | 选取/插值到 10 nm 网格；目标波长都存在 |
| Forest colors | 390–850 nm, 5 nm | 截取可见光 400–700 nm 子区间 |
| Paper spectra | 400–700 nm, 10 nm | 原生匹配，无需插值 |

注意：

- 如果你的研究需要 1 nm 分辨率，应使用 `per_dataset_wide` 中的 Munsell 原始宽表，而不是统一 31 维文件；
- 如果你的研究要覆盖 700 nm 以上的近红外，则不应使用 `all_spectra_wide_400_700_10.csv`，因为它只保留了 400–700 nm；
- 对颜色科学中的 CIE XYZ / RGB 到可见光反射谱重建，400–700 nm、10 nm 是一个比较稳妥、兼容性强的初始设置。

---

## 7. 数值尺度：0–1、0–100 与 AOTF 12-bit 的区别

这是后续使用中最容易出错的地方。

### 7.1 不是所有 `nm_*` 数值都一定在 0–1

UEF 页面通常描述这些数据为 reflectance spectra，但不同历史数据文件未必都明确说明 ASCII 中的反射率是：

```text
0–1 fraction
```

还是：

```text
0–100 percent reflectance
```

因此，不能仅凭列名 `nm_400`、`nm_410` 判断单位。建模前必须检查数值范围。

检查代码：

```python
import pandas as pd
import numpy as np

csv_path = r"E:\Python projects\spetrum_data_from_uef\uef_spectral_csv_v4\all_spectra_wide_400_700_10.csv"
df = pd.read_csv(csv_path)
wl_cols = [c for c in df.columns if c.startswith("nm_")]

for name, g in df.groupby("dataset"):
    values = g[wl_cols].to_numpy(dtype=float)
    print(
        name,
        "n=", len(g),
        "min=", np.nanmin(values),
        "max=", np.nanmax(values),
        "mean=", np.nanmean(values)
    )
```

经验判断：

| 数值范围 | 可能含义 | 建议 |
|---|---|---|
| 大多数值在 `0–1` | 反射率 fraction | 可直接作为 `R(lambda)` 使用 |
| 大多数值在 `0–100` | 百分比反射率 | 建模前通常除以 100 |
| 大多数值在 `0–4096` 或更大 | AOTF 12-bit 原始计数 | 不应直接与普通反射率混合 |
| 有少量负值 | 仪器噪声、校正误差或解析问题 | 先定位来源，谨慎 clip |
| 大量大于 100 的非 Natural 数据 | 可能是解析/单位问题 | 暂停建模，回查原始文件 |

### 7.2 非 AOTF 数据的 0–100 可能性

Munsell、Agfa、Forest、Paper 等数据在 UEF 页面中被称为 reflectance spectra，但 ASCII 文件的尺度仍建议用代码确认。

如果某个非 AOTF 数据集最大值明显大于 1，例如接近 80、90、100，那么它很可能是百分比反射率。对于机器学习中的统一建模，通常建议转换到：

```text
0–1 reflectance factor
```

即：

```python
R_0_1 = R_percent / 100
```

转换脚本提供了一个辅助选项：

```bat
python convert_uef_spectra_to_csv.py ^
  --root "E:\Python projects\spetrum_data_from_uef\uef_spectral_data" ^
  --out "E:\Python projects\spetrum_data_from_uef\uef_spectral_csv_scaled" ^
  --scale-percent
```

该选项会对非 AOTF 数据做保守判断：如果某个表的最大值大于 1.5 且不超过 100，则除以 100。

注意：

- 不建议在没有检查数值范围的情况下盲目使用 `--scale-percent`；
- 如果某些数据本来就是 0–1，不能再除以 100；
- 如果某些数据是 Natural colors 的 AOTF 原始计数，不能用百分比反射率逻辑处理。

### 7.3 Natural colors 的 AOTF 12-bit 问题

Natural colors 是最特殊的数据集。UEF README 说明：

- 它包含 218 个自然样本；
- 每条光谱有 61 个元素；
- 波长为 400–700 nm、5 nm 间隔；
- 数值来自 AOTF color measuring equipment 的 12-bit A/D converter 原始输出；
- 理论范围应为 0–4096；
- 可能存在超过 4096 的值，超过者应修正为 4096。

因此，Natural colors 中的数值不是普通意义上已经归一化的 `0–1` 反射率。它更接近仪器原始响应或相对强度。

这意味着：

```text
Natural colors raw values 不应直接和 Munsell/Agfa/Paper/Forest 的反射率混合训练。
```

如果把 Natural raw 直接和 0–1 或 0–100 反射率混合，模型会严重受到尺度影响。例如 Natural 的某些波段值可能在几千量级，而普通反射率可能只有 0–1 或 0–100。

转换脚本中的 Natural 处理选项：

```text
--aotf raw        保持原始 AOTF 数值，默认方式
--aotf clip       clip 到 [0, 4096]
--aotf normalize 先 clip 到 [0, 4096]，再除以 4096
```

例如生成 Natural 归一化版本：

```bat
python convert_uef_spectra_to_csv.py ^
  --root "E:\Python projects\spetrum_data_from_uef\uef_spectral_data" ^
  --out "E:\Python projects\spetrum_data_from_uef\uef_spectral_csv_aotf_norm" ^
  --aotf normalize
```

但要注意：

```text
clip(value, 0, 4096) / 4096
```

只能把 AOTF 原始输出映射到 0–1 数值范围，不等价于严格校准后的物理反射率。除非你有该设备的白板/暗电流/系统响应校正信息，否则它仍然更适合作为“自然样本相对谱形”或外部泛化测试，而不是和 Munsell 反射率完全等价的数据。

---

## 8. 数据集逐项说明

### 8.1 Munsell matt spectrophotometer

CSV 信息：

```text
dataset:     munsell_matt_spectrophotometer
subdataset:  munsell_matt
n_spectra:   1269
raw bands:   380–800 nm, 1 nm, 421 bands
common grid: 400–700 nm, 10 nm, 31 bands
```

用途建议：

- 主训练集；
- PCA 基函数学习；
- Wiener estimation / linear regression 基准；
- `XYZ -> reflectance` 或 `RGB -> reflectance` 的基础实验。

注意事项：

- 哑光色卡更接近漫反射表面，适合作为颜色科学中的干净基准；
- 该数据集色卡本身是人工色彩样本，不等价于所有自然材料；
- 使用前仍要检查数值是 0–1 还是 0–100。

### 8.2 Munsell glossy all spectrophotometer

CSV 信息：

```text
dataset:     munsell_glossy_all_spectrophotometer
subdataset:  munsell_glossy_all
n_spectra:   1600
raw bands:   380–780 nm, 1 nm, 401 bands
common grid: 400–700 nm, 10 nm, 31 bands
```

用途建议：

- 作为 Munsell matt 的外部测试集；
- 测试模型是否能从哑光色卡泛化到高光色卡材料；
- 与 Munsell matt 合并训练以扩大色彩覆盖。

关键注意：

UEF 说明该数据是 glossy Munsell color chips，但测量条件为 `specular excluded`。因此它代表的是高光色卡在排除镜面反射后的光谱，不等于真实相机图像中带有高光亮斑的像素光谱。

简化理解：

```text
Munsell glossy all CSV = 光泽色卡材料的漫反射/排除镜面反射测量
真实高光图像像素 = 漫反射分量 + 镜面反射分量 + 几何/光源/曝光影响
```

所以不要用该数据直接声称已经解决了真实图像中的 specular highlight removal 问题。

### 8.3 Agfa IT8.7/2

CSV 信息：

```text
dataset:     agfa_it872
subdataset:  agfa_it872
n_spectra:   289
raw bands:   400–700 nm, 10 nm, 31 bands
common grid: 400–700 nm, 10 nm, 31 bands
```

用途建议：

- 外部测试集；
- 扫描仪/相机颜色校准相关实验；
- 测试 Munsell 训练模型在校准靶材料上的泛化。

关键注意：

- 色卡主体是 288 个 patch；
- 第 289 条是 Minolta white calibration sample；
- 做严格色卡误差统计时，建议报告是否排除了第 289 条。

建议报告格式：

```text
Agfa IT8.7/2 was evaluated on 288 target patches; the Minolta white calibration sample was excluded.
```

或者：

```text
Agfa IT8.7/2 was kept as 289 spectra including the Minolta white calibration sample for data completeness.
```

### 8.4 Natural colors

CSV 信息：

```text
dataset:     natural_colors
subdataset:  natural_colors
n_spectra:   218
raw bands:   400–700 nm, 5 nm, 61 bands
common grid: 400–700 nm, 10 nm, 31 bands
```

用途建议：

- 自然材料外部测试；
- 花、叶和植物颜色的谱形分析；
- 不建议在默认 raw 状态下直接和 Munsell/Agfa/Paper 混合训练。

关键注意：

Natural colors 的数值来自 AOTF 设备 12-bit A/D 原始输出。默认 `--aotf raw` 转换时，这些值仍然是原始计数。若要把它放进机器学习模型中，需要明确说明处理方式：

```text
raw AOTF counts
```

或：

```text
clipped to [0, 4096] and normalized by 4096
```

如果论文/报告中使用该数据，请不要简单写成 “reflectance values in [0, 1]”，除非你确实做了归一化，并且在方法中说明 Natural colors 只是基于 AOTF raw counts 的归一化值。

### 8.5 Forest colors

CSV 信息：

```text
dataset:     forest_colors
subdatasets: spruce, birch, pine
n_spectra:   349 + 337 + 370 = 1056
raw bands:   390–850 nm, 5 nm, 93 bands
common grid: 400–700 nm, 10 nm, 31 bands
```

用途建议：

- 植被/自然材料泛化测试；
- 检查模型在叶片、针叶等绿色材料上的表现；
- 如果做可见光以外研究，可回到 raw CSV 使用 700–850 nm 近红外部分。

注意事项：

- 每条测量代表大量叶片/针叶的平均光谱；
- 颜色分布高度集中于植被，不适合作为通用颜色训练集；
- 当前推荐建模文件只保留 400–700 nm，舍弃了 Forest 的 700–850 nm 部分。

### 8.6 Paper spectra

CSV 信息：

```text
dataset: paper_spectra
subdatasets:
  cardboardsce  140
  cardboardsci  210
  newsprintsce   36
  newsprintsci   54
  papersce      144
  papersci      216
n_spectra total: 800
raw bands: 400–700 nm, 10 nm, 31 bands
```

用途建议：

- 纸张/纸板材料泛化测试；
- 打印、纸介质颜色复制、背景影响分析；
- SCI/SCE 比较。

关键注意：

- `sci` = specular component included；
- `sce` = specular component excluded；
- 同一类物理样本可能有多种背景/纸堆条件；
- `mirrorsci.asc` 是 surface mirror calibration spectra，当前脚本默认跳过，不作为材料样本纳入建模。

建模建议：

- 如果只是做通用光谱重建外部测试，可以把 Paper spectra 作为整体测试集；
- 如果研究表面光泽/背景影响，应分开分析 `sci` 和 `sce`；
- 不建议对 Paper 进行简单随机行划分后宣称“独立测试”，因为同一物理样本的不同测量条件可能同时出现在训练和测试中。

---

## 9. SCI、SCE 与高光/哑光的关系

### 9.1 SCI/SCE 定义

在 Paper 和 Agfa 中会遇到：

```text
SCI = Specular Component Included
SCE = Specular Component Excluded
```

通俗理解：

| 模式 | 含义 | 对光泽样本的影响 |
|---|---|---|
| SCI | 包含镜面反射分量 | 更接近“总反射”或材料整体反射能力 |
| SCE | 排除镜面反射分量 | 更接近不含高光的表面颜色外观 |

### 9.2 Munsell glossy all 的特殊点

Munsell glossy all 是“高光色卡”，但测量时 specular excluded。也就是说，CSV 中的 glossy 数据并不包含相机拍摄时看到的高光亮斑。

因此，在论文中更严谨的表述应该是：

```text
We evaluated on glossy Munsell chips measured with specular component excluded.
```

而不是：

```text
We evaluated on spectra with specular highlights.
```

### 9.3 哑光 vs 高光在本项目中的使用建议

| 数据 | 推荐用途 |
|---|---|
| Munsell matt | 主训练/基础基准 |
| Munsell glossy all | 表面类型泛化测试，或与 matt 合并扩大色彩覆盖 |
| Agfa SCE | 外部校准靶测试 |
| Paper SCI/SCE | 分析镜面分量包含/排除、背景条件和纸介质影响 |

---

## 10. 推荐建模前检查流程

### 10.1 检查总行数和各数据集数量

```python
import pandas as pd

csv_path = r"E:\Python projects\spetrum_data_from_uef\uef_spectral_csv_v4\all_spectra_wide_400_700_10.csv"
df = pd.read_csv(csv_path)

print("shape:", df.shape)
print(df["dataset"].value_counts())
print(df.groupby(["dataset", "subdataset"]).size())
```

预期：

```text
Total rows = 5232
```

### 10.2 检查是否有空值

```python
wl_cols = [c for c in df.columns if c.startswith("nm_")]

missing = df[wl_cols].isna().sum().sum()
print("missing spectral values:", missing)
```

对于 `all_spectra_wide_400_700_10.csv`，理论上不应有缺失，因为所有当前数据集都覆盖 400–700 nm。

### 10.3 检查每个数据集的数值范围

```python
import numpy as np

for (dataset, subdataset), g in df.groupby(["dataset", "subdataset"]):
    values = g[wl_cols].to_numpy(dtype=float)
    print(
        f"{dataset:40s} {subdataset:15s}",
        "n=", len(g),
        "min=", np.nanmin(values),
        "max=", np.nanmax(values),
        "mean=", np.nanmean(values)
    )
```

重点查看：

- Natural colors 是否是几千量级；
- Munsell/Agfa/Paper/Forest 是 0–1 还是 0–100；
- 是否有明显异常的负值或极端大值。

### 10.4 生成一个更安全的建模版本

如果你想先避开 AOTF 原始计数问题，可以排除 Natural colors：

```python
model_df = df[df["dataset"] != "natural_colors"].copy()
print(model_df.shape)
```

如果你想严格排除 Agfa calibration sample：

```python
model_df = model_df[~((model_df["dataset"] == "agfa_it872") & (model_df["label"] == "minolta_white_calibration"))].copy()
print(model_df.shape)
```

如果你确认某些非 AOTF 数据是百分比反射率，可以统一除以 100。但建议先按数据集检查，不要对所有行盲目处理。

示例：

```python
non_aotf = df[df["dataset"] != "natural_colors"].copy()
wl_cols = [c for c in non_aotf.columns if c.startswith("nm_")]

for dataset, idx in non_aotf.groupby("dataset").groups.items():
    vmax = non_aotf.loc[idx, wl_cols].to_numpy(dtype=float).max()
    if 1.5 < vmax <= 100:
        non_aotf.loc[idx, wl_cols] = non_aotf.loc[idx, wl_cols] / 100.0

non_aotf.to_csv("uef_model_ready_non_aotf_0_1.csv", index=False, encoding="utf-8-sig")
```

---

## 11. 推荐实验数据划分

对于颜色科学中的光谱重建，建议不要一开始把所有数据随机混合。更稳妥的路线是分数据集报告结果。

### 11.1 基础实验

```text
Train:      Munsell matt
Validation: Munsell matt 内部划分
Test A:     Munsell glossy all
Test B:     Agfa IT8.7/2
Test C:     Paper spectra
Test D:     Forest colors
Test E:     Natural colors，需注明 AOTF raw/normalized 处理方式
```

### 11.2 为什么不要只做随机划分

如果把 5232 条光谱全部随机划分，可能出现：

- Paper 同一个物理样本的不同测量条件进入 train 和 test；
- Munsell 色卡占比大，平均误差被 Munsell 主导；
- Natural colors 的 AOTF 数值尺度影响训练；
- 模型看起来整体误差低，但跨材料泛化并不好。

更推荐报告：

```text
Train Munsell matt -> Test Munsell glossy all
Train Munsell matt -> Test Agfa
Train Munsell matt -> Test Paper
Train Munsell matt -> Test Forest
Train Munsell matt -> Test Natural, with AOTF handling stated explicitly
```

---

## 12. 做 XYZ/RGB -> Reflectance 时的单位提醒

光谱重建常见流程：

```text
Reflectance R(lambda)
+ illuminant SPD E(lambda)
+ CIE CMF or camera spectral sensitivity
-> XYZ or camera RGB
```

如果 `R(lambda)` 使用 0–1，计算流程最清晰。

如果 `R(lambda)` 使用 0–100，则必须在积分前除以 100，或者在公式归一化中保持一致。为了避免混乱，建议建模文件最终统一为：

```text
R(lambda) in [0, 1]
```

Natural colors 不能简单认为是 `R(lambda)`，除非你已经明确做了设备响应校正或至少做了 AOTF 归一化，并在实验说明中单独标注。

另外，使用 RGB 输入时应区分：

```text
linear RGB
```

和：

```text
gamma-compressed sRGB
```

用于物理建模和光谱重建时，一般应使用 linear RGB 或相机原始线性响应，而不是直接使用 gamma 压缩后的 sRGB 值。

---

## 13. 常见错误与防错清单

### 13.1 最常见错误

| 错误 | 后果 | 建议 |
|---|---|---|
| 把 Natural raw AOTF counts 当成 0–1 反射率 | 模型被几千量级数据主导 | 排除 Natural，或 `--aotf normalize` 后单独测试 |
| 忽略 Agfa 第 289 条 calibration sample | Agfa 样本数解释不清 | 报告中说明保留或排除 |
| 把 Paper 800 条当成 800 个独立物理样本 | 评估可能数据泄漏 | 按 dataset/subdataset/条件分组分析 |
| 不检查 0–1/0–100 尺度 | XYZ/RGB 计算和损失函数错误 | 建模前打印 min/max |
| 把 Munsell glossy 解释为真实高光图像 | 研究结论夸大 | 说明它是 specular excluded 测量 |
| 随机混合所有数据集划分 train/test | 泛化能力被高估 | 分数据集报告结果 |
| 只报 RMSE，不报色差 | 难以评价颜色科学意义 | 同时报 RMSE、GFC、Delta E |

### 13.2 建模前最小检查清单

在开始训练前，至少确认：

```text
[ ] all_spectra_wide_400_700_10.csv 行数为 5232
[ ] nm_400 到 nm_700 共 31 列
[ ] 没有缺失波段值
[ ] 已明确是否排除 Agfa calibration sample
[ ] 已明确 Natural colors 是 raw、clip 还是 normalized
[ ] 已明确非 AOTF 数据是 0–1 还是 0–100
[ ] Paper SCI/SCE 是否合并，是否单独分析
[ ] 训练/测试划分是否避免同类测量条件泄漏
[ ] RGB 输入是否为 linear RGB，而不是 gamma-compressed sRGB
```

---

## 14. 建议的项目记录方式

为了防止后续实验混乱，建议每次生成建模文件时同时记录这些信息：

```yaml
data_source: UEF / University of Kuopio spectral databases
converter_version: 1.4.1
csv_file: all_spectra_wide_400_700_10.csv
common_grid_nm: [400, 410, ..., 700]
total_spectra: 5232
include_natural_colors: true
natural_colors_handling: raw | clip | normalize
non_aotf_scale: unchecked | 0-1 | percent_divided_by_100
agfa_calibration_sample: included | excluded
paper_sci_sce: included_both | sci_only | sce_only
train_test_split: describe_here
```

如果后续生成多个版本，可以用文件名区分：

```text
uef_all_400_700_10_raw.csv
uef_all_400_700_10_no_natural.csv
uef_all_400_700_10_non_aotf_0_1.csv
uef_all_400_700_10_aotf_norm.csv
uef_all_400_700_10_agfa288.csv
```

---

## 15. 参考资料

以下为本项目中使用的 UEF 数据集页面和 README。建议在论文或报告中按实际使用的数据集引用对应页面。

- UEF Spectral databases & software:  
  https://sites.uef.fi/spectral/databases-software/

- Munsell colors matt spectrophotometer page:  
  https://sites.uef.fi/spectral/databases-software/munsell-colors-matt-spectrofotometer-measured/

- Munsell matt README:  
  https://cs.uef.fi/pub/color/spectra/mspec/README.txt

- Munsell glossy all page:  
  https://sites.uef.fi/spectral/databases-software/munsell-colors-glossy-all-spectrofotometer-measured/

- Munsell glossy all README:  
  https://cs.uef.fi/pub/color/spectra/mglossy_all/README.txt

- Agfa IT8.7/2 page:  
  https://sites.uef.fi/spectral/databases-software/agfa-it8-7-2-set/

- Agfa IT8.7/2 README:  
  https://cs.uef.fi/pub/color/spectra/agfait872/README.txt

- Natural colors page:  
  https://sites.uef.fi/spectral/databases-software/natural-colors/

- Natural colors README:  
  https://cs.uef.fi/pub/color/spectra/natural/README.txt

- Forest colors page:  
  https://sites.uef.fi/spectral/databases-software/forest-colors/

- Forest colors README:  
  https://cs.uef.fi/pub/color/spectra/forest/README.txt

- Paper spectra page:  
  https://sites.uef.fi/spectral/databases-software/paper-spectra/

- Paper spectra README:  
  https://cs.uef.fi/pub/color/spectra/paper/README.txt

---

## 16. 最终建议

如果你的目标是颜色科学中的光谱重建，建议先建立两个 CSV 版本：

### 版本 A：干净反射率建模版

```text
包含：Munsell matt, Munsell glossy all, Agfa, Paper, Forest
排除：Natural colors raw AOTF
Agfa：可选排除 Minolta white calibration sample
尺度：统一到 0–1 reflectance factor
```

适合主实验、PCA、Wiener estimation、MLP 等模型训练。

### 版本 B：完整归档版

```text
包含全部 5232 条光谱
Natural colors 保留 raw 或 normalize 方式明确记录
Agfa calibration sample 是否保留明确记录
Paper SCI/SCE 全部保留
```

适合数据备份、统计、画图和后续扩展实验。

最重要的是：

```text
不要在未检查数值范围和测量条件的情况下，把 5232 条光谱直接随机混合训练。
```

这样可以最大限度避免后续实验中出现单位混乱、样本数量解释不清、AOTF 数据误用、Paper 条件泄漏等问题。
