# UEF 光谱数据库整理与颜色科学光谱重建数据选择说明

整理日期：2026-06-04  
来源网站：[University of Eastern Finland Computational Spectral Imaging — Databases & Software](https://sites.uef.fi/spectral/databases-software/)

> 1. UEF 数据集总览

UEF Computational Spectral Imaging 组的 Databases & Software 页面收录了若干光谱数据集和光谱图像数据集，页面说明这些数据主要供研究使用。如果某个数据库页面没有单独指定引用论文，UEF 建议引用该研究组和数据库主页本身。网站还维护了 Zenodo community 页面，部分数据在 Zenodo 有镜像。

从使用方式看，这些数据可以分为两大类：

| 类别 | 含义 | 适合用途 |
|---|---|---|
| 光谱图像库 | 每个像素都有一条光谱，通常是 hyperspectral / multispectral image cube | 光谱图像处理、RGB 图像到光谱图像重建、材质识别、纹理分析、医学/文物/木材/眼部图像研究 |
| 非成像光谱库 | 每个样本是一条或多条光谱曲线，通常是 ASCII / MATLAB 文件 | 颜色科学、反射率建模、相机/扫描仪校准、光谱重建、训练基础光谱字典 |

---

## 2. 光谱图像库整理

这些数据集适合研究“图像级”或“像素级”光谱估计，例如 `RGB image → spectral image cube`。如果你的阶段还只是研究颜色科学中的一维反射谱重建，优先级可以低于 Munsell、Agfa、Natural、Paper 等非成像反射谱。

| 数据集 | 对象/场景 | 规模与波段 | 获取与格式 | 适合用途 |
|---|---|---|---|---|
| [ODSI-DB – Oral and Dental Spectral Image Database](https://sites.uef.fi/spectral/databases-software/odsi-db/) | 人体口腔、牙齿、口腔黏膜、嘴部周围面部；由牙科专家做了标注 | 完整数据库约 34 GB；页面未直接列出通用可见光波段范围 | 多页 TIFF：第一页 RGB preview，后续为 16-bit 灰度光谱 band；带 TIFF tag 存波长和元数据；另有 annotation TIFF 与 Python 读写函数；Zenodo 有镜像压缩包 | 牙齿/口腔组织识别、医学光谱图像、标注分割、反射谱分析 |
| [SIDRI – Spectral Image Dataset of Religious Icons](https://sites.uef.fi/spectral/databases-software/sidri-spectral-image-dataset-of-religious-icons/) | 6 幅 19 世纪末至 20 世纪初的俄罗斯东正教圣像画 | 多相机：RGB、7-band MSBS、LCTF-VIS、LCTF-NIR、Specim V10；VIS 为 400–720 nm / 10 nm，NIR 为 450–950 nm / 10 nm，V10 为 400–1000 nm / 5 nm；发布版约 640×480，完整下载约 1.7 GB | TIFF-stack，多相机配准到 LCTF-VIS；可单 ZIP 下载 | 文物/绘画光谱估计、多相机配准、相机质量评价、空间图像质量分析 |
| [SpecTex – HyperSpectral Texture Image Database](https://sites.uef.fi/spectral/databases-software/spectex-hyperspectral-texture-image-database/) | 60 个纹理样本，主要是织物；T10、T14 为塑料 | 400–780 nm；提供 5 nm 与 10 nm 版本；10 nm 版本为 640×640×39；5 nm 包约 3.3 GB，10 nm 包约 1.7 GB | TIFF hyperspectral cubes；另有 representative spectral signatures 和 MATLAB 工具函数 | 光谱纹理分析、材质分类、光谱图像处理、reflectance endmember / 字典构建 |
| [Spectral Image Database of Nordic Sawn Timbers](https://sites.uef.fi/spectral/databases-software/spectral-image-database-of-nordic-sawn-timbers/) | 芬兰重要木材：桦木、挪威云杉、欧洲赤松；包含心材、边材、腐朽、蓝变、霉菌、树脂、节疤、裂纹、树皮等 | 107 幅光谱图像；300–2500 nm，5 nm 采样；还测了 UV-B 激发下的光致发光；总数据约 500 GiB，约 4400 万条光谱 | 自定义二进制文件；含结构说明、MATLAB 程序和 viewer；因数据大，页面称通过实体硬盘分发，线上分发仍在考虑 | 木材质量检测、水分/木质素/缺陷空间分布、VIS-NIR-SWIR 材料识别 |
| [SPEED – SPectral Eye vidEo Database](https://sites.uef.fi/spectral/databases-software/speed-spectral-eye-video-database/) | 30 名志愿者左眼的光谱静态图像与眼动光谱视频；包含眼镜反射、极端角度、化妆等不利条件 | 180 个 7 通道眼动视频，380–1000 nm；30 张 51 通道静态眼图，450–950 nm；总约 293 GB | 51 通道静态图像为 TIFF；7 通道图像/视频为 MATLAB matrix；页面称线上分发仍在考虑，需要联系作者 | 眼部/虹膜/眼动视频、多光谱视频、复杂反射条件下的视觉研究 |

---

## 3. 非成像光谱库整理

这些数据集更适合颜色科学中的基础光谱重建，因为每个样本通常是一条表面反射率曲线。对于 `XYZ / RGB / camera responses → reflectance spectrum`，应优先从这些数据入手。

| 数据集 | 样本/对象 | 光谱类型与范围 | 数据量/格式 | 备注 |
|---|---|---|---|---|
| [Munsell colors matt – AOTF measured](https://sites.uef.fi/spectral/databases-software/munsell-colors-matt-aotf-measured/) | 1250 个哑光 Munsell 色片 | 反射率；400–700 nm，5 nm；61 个元素；AOTF 12-bit 原始输出 | ASCII、MATLAB | 蓝端有噪声说明；部分值大于 4096 时应修正为 4096；不建议作为主训练集，但可做鲁棒性测试 |
| [Munsell colors matt – Spectrophotometer measured](https://sites.uef.fi/spectral/databases-software/munsell-colors-matt-spectrofotometer-measured/) | 1269 个哑光 Munsell 色片 | 反射率；380–800 nm，1 nm；Perkin-Elmer Lambda 9 | ASCII、MATLAB | 最适合作为颜色科学光谱重建的主基准数据之一 |
| [Munsell colors glossy – Spectrophotometer measured](https://sites.uef.fi/spectral/databases-software/munsell-colors-glossy-spectrofotometer-measured/) | 32 个高光 Munsell 色片 | 反射率；400–700 nm，10 nm；Minolta CM-2002 | ASCII、MATLAB | 小规模高光 Munsell 子集 |
| [Munsell colors glossy all – Spectrophotometer measured](https://sites.uef.fi/spectral/databases-software/munsell-colors-glossy-all-spectrofotometer-measured/) | 1600 个高光 Munsell 色片 | 反射率；380–780 nm，1 nm；Perkin-Elmer Lambda 18，specular excluded | ASCII、MATLAB，另有 Excel 标签 | 高光 Munsell 全量版本，适合做 glossy 样本泛化测试；注意测量时排除了镜面反射 |
| [Agfa IT8.7/2 set](https://sites.uef.fi/spectral/databases-software/agfa-it8-7-2-set/) | Agfa ColorReference / IT8.7 输入校准靶，288 patches | 反射率；400–700 nm，10 nm；Minolta CM-2002，SCE，d/8 几何 | ASCII、MATLAB | 主要用于扫描仪/摄影介质校准、色彩管理基准；适合作为外部测试集 |
| [Candy colors](https://sites.uef.fi/spectral/databases-software/candy-colors/) | 10 种糖果染料，2 种浓度 | 吸收光谱；190–820 nm，2 nm；HP 8452A diode array spectrophotometer | ASCII、MATLAB | 不是物体表面反射率，而是染料溶液吸收光谱；不适合作为常规反射谱重建主数据 |
| [Daylight spectra](https://sites.uef.fi/spectral/databases-software/daylight-spectra/) | 不同日光照明下的白参考、约 100 m 外云杉、镜面反射天空 | 光谱辐射/照明测量；390–1070 nm，4 nm | ASCII、MATLAB | 更偏照明/场景光谱，不是标准物体反射率库 |
| [Forest colors](https://sites.uef.fi/spectral/databases-software/forest-colors/) | 苏格兰松、挪威云杉针叶，桦树叶；芬兰/瑞典采集 | 反射率；390–850 nm，5 nm；PR 713/702 AM | ASCII、MATLAB | 每次测量代表生长树木上大量叶片的平均光谱；适合植被/林业颜色研究和自然材料泛化测试 |
| [Natural colors](https://sites.uef.fi/spectral/databases-software/natural-colors/) | 218 个自然界彩色样本：花、叶、其他植物等 | 反射率；400–700 nm，5 nm；AOTF 12-bit 原始输出 | ASCII | 自然颜色样本库；部分值大于 4096 时应修正为 4096；适合真实材料泛化测试 |
| [Lumber spectra](https://sites.uef.fi/spectral/databases-software/lumber-spectra/) | 锯材枝节与无枝节纯木材 | 相对反射率；380–2700 nm，1 nm；Perkin-Elmer Lambda 9 | ASCII、MATLAB | 波段覆盖 VIS-NIR-SWIR，适合木材近红外/短波红外材料分析 |
| [Paper spectra](https://sites.uef.fi/spectral/databases-software/paper-spectra/) | 彩色纸与纸板；单张纸黑/白背景、以及不透明纸堆 | 反射率；400–700 nm，10 nm；Minolta CM-2002 | ASCII、MATLAB | 适合打印、纸张颜色、背景透射/遮盖影响分析；可作为跨材料测试集 |
| [Smooth spectra](https://sites.uef.fi/spectral/databases-software/smooth-spectra/) | 用 MATLAB 程序生成 716,784 条平滑非荧光反射谱 | 合成反射谱；页面未列具体波段采样细节 | MATLAB m-file | 是生成器/软件，不是实测物体数据；适合理论实验、同色异谱样本生成、数据增强 |

---

## 4. 面向颜色科学光谱重建的数据选择

### 4.1 任务定义

颜色科学中的光谱重建可以写成：

```text
CIE XYZ / linear RGB / camera responses  →  estimated reflectance spectrum R(λ)
```

其中 `R(λ)` 是物体表面反射率。这个问题与普通计算机视觉中“从 RGB 生成好看的高光谱图像”不同，目标应是恢复物理上和色度学上合理的反射谱。理想的数据应满足：

1. 是表面反射率，而不是吸收谱、照明谱或辐射亮度；
2. 波长范围覆盖可见光，例如 400–700 nm、380–780 nm 或 380–800 nm；
3. 样本颜色覆盖足够广，方便测试同色异谱、跨材料泛化和不同光源下的颜色误差；
4. 格式简单，便于转换为统一波长采样。

### 4.2 最优先使用的数据集

| 优先级 | 数据集 | 推荐角色 | 原因 |
|---|---|---|---|
| 1 | Munsell colors matt – Spectrophotometer measured | 主训练集 / 主基准 | 1269 个哑光 Munsell 色片，380–800 nm，1 nm；干净、标准、颜色科学相关性强 |
| 2 | Munsell colors glossy all – Spectrophotometer measured | glossy 泛化测试 / 扩展训练 | 1600 个高光 Munsell 色片，380–780 nm，1 nm；specular excluded；适合测试模型是否只适合哑光色片 |
| 3 | Agfa IT8.7/2 set | 外部测试集 | 288 个校准靶色块，400–700 nm，10 nm；适合设备校准和色彩管理场景 |
| 4 | Natural colors | 自然材料泛化测试 | 218 个花、叶等自然样本，400–700 nm，5 nm；适合测试真实自然颜色 |
| 5 | Paper spectra | 纸张/打印材料泛化测试 | 彩色纸、纸板、新闻纸，400–700 nm，10 nm；适合研究背景、遮盖、纸张材料影响 |
| 6 | Forest colors | 植被材料泛化测试 | 390–850 nm，5 nm；颜色类别集中，但适合植被/林业颜色研究 |
| 7 | SpecTex | 后续图像级重建 | 每个像素都有反射谱，400–780 nm；适合 `RGB image → spectral image cube` |
| 8 | SIDRI | 后续多相机/文物图像重建 | 含 RGB、多光谱、近红外和高光谱模态；适合多相机配准和文物光谱估计 |

### 4.3 不建议作为主数据的数据集

| 数据集 | 原因 |
|---|---|
| Candy colors | 是糖果染料的吸收光谱，不是表面反射率 |
| Daylight spectra | 更偏光源/照明/场景光谱，不是标准物体反射率库 |
| Smooth spectra | 是合成平滑反射谱生成程序，适合理论实验或数据增强，但不能替代实测数据 |
| ODSI-DB | 偏口腔医学光谱图像，对一般颜色科学重建不是第一优先 |
| SPEED | 偏眼部/虹膜/眼动多光谱视频，对一般颜色科学重建不是第一优先 |
| Nordic Sawn Timbers / Lumber spectra | 适合木材与 VIS-NIR-SWIR 材料分析；如果只做可见光颜色科学，优先级较低 |

---

## 5. 推荐实验路线

### 5.1 第一个可复现实验

建议先把所有数据统一到：

```text
400 nm – 700 nm, 10 nm interval
```

这样可以得到 31 个波段。这个范围的好处是：Agfa 与 Paper 本身就是 10 nm；Munsell 的 1 nm 数据可以重采样；Natural 与 Forest 的 5 nm 数据可以降采样。虽然 Munsell 覆盖到 780/800 nm，但为了跨数据集对齐，第一阶段用 400–700 nm 最稳。

| 用途 | 数据集 |
|---|---|
| Train | 80% Munsell matt spectrophotometer |
| Validation | 20% Munsell matt spectrophotometer |
| Test A | Munsell glossy all |
| Test B | Agfa IT8.7/2 |
| Test C | Natural colors |
| Test D | Paper spectra |
| Test E | Forest colors，可选 |

### 5.2 输入形式

可以设置三类重建任务：

| 任务 | 输入 | 输出 | 说明 |
|---|---|---|---|
| Task 1 | CIE XYZ | R(λ) | 最颜色科学，适合讨论同色异谱和基本可恢复性 |
| Task 2 | linear RGB | R(λ) | 更接近图像应用；注意不要直接使用 gamma-compressed sRGB |
| Task 3 | camera RGB responses | R(λ) | 最接近真实拍摄；需要相机光谱响应函数和光源 SPD |

### 5.3 建议基线模型

| 方法 | 说明 | 为什么需要 |
|---|---|---|
| PCA + linear regression | 先对反射谱做 PCA，再从 RGB/XYZ 预测 PCA 系数 | 传统、可解释，是颜色科学中常见基线 |
| Wiener estimation | 根据训练集统计关系建立输入到反射率的线性估计 | 相机响应到光谱估计常用 |
| kNN / local weighted reconstruction | 在颜色空间中找相近样本，用邻域光谱加权重建 | 对色卡数据自然，能体现局部先验 |
| 小型 MLP | 输入 RGB/XYZ，输出 31 维或 61 维反射谱 | 现代机器学习对照；不建议一开始用过大模型 |

### 5.4 评价指标

不要只报告 spectral RMSE。颜色科学方向最好同时报告光谱误差和色度误差。

| 指标 | 用途 |
|---|---|
| RMSE | 逐波段反射率误差 |
| GFC / goodness-of-fit coefficient | 光谱形状相似度 |
| SAM / spectral angle mapper | 光谱方向误差 |
| ΔE\*ab 或 CIEDE2000 | 感知颜色误差 |
| ΔXYZ / Δxy | 色度学误差 |
| 多光源下 ΔE | 在 D65、A、F11 等光源下检查重建谱是否稳定 |

特别重要的是：如果某个模型在 D65 下颜色误差很小，但换到 A 光源或荧光光源后误差明显变大，说明它可能只是在拟合某个光源下的颜色，而不是真正恢复了合理的反射谱。

---

## 6. 哑光色卡与高光色卡的区别

### 6.1 物理反射差异

| 类型 | 表面特征 | 主要反射形式 | 视觉效果 |
|---|---|---|---|
| 哑光色卡 matte | 表面微观粗糙 | 以漫反射 diffuse reflection 为主 | 从不同角度看颜色相对稳定，不容易出现亮斑 |
| 高光/光泽色卡 glossy | 表面更平滑、有涂层或光泽层 | 漫反射 + 镜面反射 specular reflection | 某些角度会看到高光、反光、亮斑，颜色外观随角度变化更明显 |

对于哑光表面，一个简化模型是：

```text
C(λ) ≈ E(λ) R(λ)
```

其中 `E(λ)` 是光源光谱，`R(λ)` 是材料表面反射率。

对于高光表面，观测光谱更接近：

```text
C(λ) ≈ E(λ) R_d(λ) + k_s E(λ)
```

第一项是材料本体的漫反射颜色，第二项是镜面高光。对很多非金属材料来说，镜面高光常常更接近光源颜色，而不完全是颜料本身的颜色。

### 6.2 SCI 与 SCE 测量模式

测量高光样品时，仪器常见两种模式：

| 模式 | 英文 | 含义 | 结果倾向 |
|---|---|---|---|
| SCI | Specular Component Included | 包含镜面反射和漫反射 | 更接近材料“本体/总反射”颜色，较少受表面光泽影响 |
| SCE | Specular Component Excluded | 排除镜面反射，主要测漫反射 | 更接近人眼观察到的外观，光泽样品可能测得更暗 |

Konica Minolta 的说明中也提到：光滑表面镜面反射较强，粗糙/哑光表面漫反射较强；SCI 包含镜面和漫反射，SCE 排除镜面反射，更接近视觉评价。参考：[Konica Minolta — SCI vs SCE](https://sensing.konicaminolta.us/us/blog/specular-component-included-sci-vs-specular-component-excluded-sce/)。

### 6.3 UEF 数据中的具体含义

在 UEF 数据库中：

- `Munsell colors matt – Spectrophotometer measured` 是 1269 个哑光 Munsell 色片，380–800 nm，1 nm。
- `Munsell colors glossy all – Spectrophotometer measured` 是 1600 个高光 Munsell 色片，380–780 nm，1 nm，并且页面明确写了测量设备为 `Perkin-Elmer Lambda 18 UV/VIS spectrofotometer (specular excluded)`。

所以 UEF 的 glossy all 数据并不是“带高光亮斑的照片数据”，而是：

```text
高光材料色卡在排除镜面反射后的反射率曲线
```

也就是说，它更接近 glossy 色卡的本体漫反射颜色，而不是真实拍照时看到的强反光外观。

### 6.4 对光谱重建的影响

| 使用方式 | 目的 |
|---|---|
| 先用 Munsell matt 训练 | 建立干净、稳定、可解释的基础反射谱重建模型 |
| 用 Munsell glossy all 测试 | 检查模型是否能从哑光样本泛化到高光材料样本 |
| matte + glossy all 混合训练 | 扩大颜色覆盖和表面类型覆盖，但要单独报告不同测试集结果 |
| 真实图像中处理高光 | 需要额外考虑高光检测、去高光、偏振、多角度或漫反射/镜面反射分离 |

不要一开始就把 matte 和 glossy 混在一起训练后只报告一个平均误差。更好的做法是分开报告：

```text
Train matte → Test matte
Train matte → Test glossy
Train matte + glossy → Test external datasets
```

这样可以清楚看出模型对表面光泽、材料集合和颜色分布的敏感性。

---

## 7. 最简结论

如果研究重点是颜色科学中的光谱重建，建议按以下顺序整理和使用 UEF 数据：

1. **Munsell matt spectrophotometer**：主训练/主基准。
2. **Munsell glossy all spectrophotometer**：高光色卡泛化测试；注意该数据是 specular excluded。
3. **Agfa IT8.7/2**：设备校准靶外部测试。
4. **Natural colors + Paper spectra + Forest colors**：真实材料/自然材料泛化测试。
5. **SpecTex**：后续做 RGB 图像到光谱图像重建。
6. **SIDRI**：后续研究多相机、多光谱/RGB 对比和文物图像光谱估计。

---

## 9. 参考链接

- UEF Databases & Software: https://sites.uef.fi/spectral/databases-software/
- ODSI-DB: https://sites.uef.fi/spectral/databases-software/odsi-db/
- SIDRI: https://sites.uef.fi/spectral/databases-software/sidri-spectral-image-dataset-of-religious-icons/
- SpecTex: https://sites.uef.fi/spectral/databases-software/spectex-hyperspectral-texture-image-database/
- Nordic Sawn Timbers: https://sites.uef.fi/spectral/databases-software/spectral-image-database-of-nordic-sawn-timbers/
- SPEED: https://sites.uef.fi/spectral/databases-software/speed-spectral-eye-video-database/
- Munsell matt AOTF: https://sites.uef.fi/spectral/databases-software/munsell-colors-matt-aotf-measured/
- Munsell matt spectrophotometer: https://sites.uef.fi/spectral/databases-software/munsell-colors-matt-spectrofotometer-measured/
- Munsell glossy: https://sites.uef.fi/spectral/databases-software/munsell-colors-glossy-spectrofotometer-measured/
- Munsell glossy all: https://sites.uef.fi/spectral/databases-software/munsell-colors-glossy-all-spectrofotometer-measured/
- Agfa IT8.7/2: https://sites.uef.fi/spectral/databases-software/agfa-it8-7-2-set/
- Candy colors: https://sites.uef.fi/spectral/databases-software/candy-colors/
- Daylight spectra: https://sites.uef.fi/spectral/databases-software/daylight-spectra/
- Forest colors: https://sites.uef.fi/spectral/databases-software/forest-colors/
- Natural colors: https://sites.uef.fi/spectral/databases-software/natural-colors/
- Lumber spectra: https://sites.uef.fi/spectral/databases-software/lumber-spectra/
- Paper spectra: https://sites.uef.fi/spectral/databases-software/paper-spectra/
- Smooth spectra: https://sites.uef.fi/spectral/databases-software/smooth-spectra/
- Konica Minolta — SCI vs SCE: https://sensing.konicaminolta.us/us/blog/specular-component-included-sci-vs-specular-component-excluded-sce/
