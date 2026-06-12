# CIE S 026 alpha-opic Toolbox 中文使用指南

本文说明同目录下官方文件：

- `CIE S 026 alpha-opic Toolbox.xlsx`
- `CIE S 026 alpha-opic Toolbox User Guide.pdf`

适用目标：

- 理解 CIE S 026 alpha-opic Toolbox 的 workbook 结构。
- 正确输入内置光源或用户自定义光谱。
- 读取 alpha-opic 输出量，例如 melanopic irradiance、melanopic EDI、alpha-opic ELR。
- 理解 `Action spectra` sheet 中五条 alpha-opic action spectra 的含义。
- 明确它和本项目 `color.datasets` 后续注册 melanopic / ipRGC 数据之间的关系。

## 1. 文件定位

`CIE S 026 alpha-opic Toolbox.xlsx` 是 CIE Division 6 发布的 alpha-opic 计算工具，版本信息在 workbook 的 `Disclaimer` sheet 中：

```text
CIE S 026 alpha-opic Toolbox - v1.049a - 2020/11/16
```

它用于辅助实现 CIE S 026:2018 中与 ipRGC-influenced responses to light 相关的 alpha-opic 计量计算。官方 User Guide 明确说明：Toolbox 支持 CIE S 026 的使用，但它本身不是标准正文的一部分。实际严肃使用时，应对关键结果做人工复核。

本项目当前只把该 workbook 放在 `docs/` 下作为参考和数据来源审查材料；它还不是运行时 dataset。

## 2. Workbook 总体结构

workbook 包含以下 sheet：

| Sheet | 用途 |
| --- | --- |
| `Maintenance` | 维护日志和内部配置，通常不需要使用 |
| `Disclaimer` | 版本、版权、免责声明 |
| `Inputs` | 主输入界面，日常计算主要在这里输入 |
| `Outputs` | 主输出界面，显示标准 CIE S 026 结果 |
| `Spectra` | 内置光源、参考光谱等内部数据 |
| `Physics` | SI、辐射量、光度量、光子量换算常量 |
| `Photobiology` | alpha-opic action spectra、D65 ELR 等内部表 |
| `Calculations` | 计算中间过程 |
| `Charts` | 测试光谱和参考光谱的可视化 |
| `Action spectra` | 五条 alpha-opic action spectra 的公开表 |
| `Glossary` | CIE S 026 相关术语和符号 |
| `Advanced Inputs` | 高级输入：参考光源、旧 Lucas 模式等 |
| `Advanced Outputs` | 高级输出：DER、参考光源匹配结果等 |
| `Transmittance` | 年龄相关透射率说明；该版本标注为不可用功能 |

日常使用只需要关注：

```text
Inputs -> Outputs
```

查看 action spectra 或提取数据时关注：

```text
Action spectra
```

高级研究或旧论文复核时再查看：

```text
Advanced Inputs -> Advanced Outputs
```

## 3. Alpha-opic 五个通道

CIE S 026 中的 `alpha` 可以代表五类光生物学通道：

| 缩写 | 名称 |
| --- | --- |
| `sc` | S-cone-opic |
| `mc` | M-cone-opic |
| `lc` | L-cone-opic |
| `rh` | Rhodopic |
| `mel` | Melanopic |

这些通道分别对应 S 锥体、M 锥体、L 锥体、杆体和 melanopsin / ipRGC 相关响应。

`Action spectra` sheet 中有两套 action spectra：

| 区域 | 含义 |
| --- | --- |
| 左侧 Radiometric system | `s_alpha(lambda) = se,alpha(lambda)`，用于辐射量系统 |
| 右侧 Photon system | `sp,alpha(lambda)`，用于光子量系统 |

本项目已经提取了左侧 radiometric action spectra：

```text
docs/cie_s026_alpha_opic_action_spectra_extracted.csv
```

字段为：

```text
wavelength, sc, mc, lc, rh, mel
```

范围为：

```text
380-780 nm, 1 nm
```

## 4. 内置光源快速计算

如果只想用 workbook 计算一个内置光源，例如 D65、A、E、FL11 或 LED-B3，使用 `Inputs` sheet。

### 4.1 推荐输入步骤

1. 在 `B5` 输入标题，例如：

   ```text
   D65 test
   ```

2. 在 `C8` 选择内置光源：

   ```text
   A
   D65
   E
   FL11
   LED-B3
   ```

3. 在 `C11` 选择基本量：

   ```text
   photon radiance
   photon irradiance
   radiance
   irradiance
   luminance
   illuminance
   ```

4. 在 `C12` / `C13` 选择 SI prefix 和面积 prefix。

5. 在 `C17` 输入该基本量的数值。

6. 清空 `C24:C424` 中的用户光谱数据区域。

7. 检查 `Inputs` 右侧错误提示区域，确认没有红色错误信息。

### 4.2 典型例子

官方 User Guide 给出的例子是：

```text
Spectrum: LED-B3
Quantity: illuminance
Prefix: k
Value: 0.10
```

也就是：

```text
0.10 klx = 100 lx
```

此时 workbook 会把 LED-B3 按 100 lx 标定后，输出对应的 alpha-opic 结果。

## 5. 用户自定义光谱输入

如果要输入自己的光谱数据，应在 `Inputs` sheet 中选择 `User`。

### 5.1 允许的 spectral quantity

用户光谱输入支持四类 spectral quantity：

```text
photon radiance
photon irradiance
radiance
irradiance
```

注意：

```text
luminance / illuminance 不能作为 spectral input。
```

它们是积分后的光度量，不是每个波长上的光谱分布。

### 5.2 输入区域

主要单元格如下：

| 单元格 | 用途 |
| --- | --- |
| `C8` | 选择 `User` |
| `C11` | 选择 spectral quantity |
| `C12` | 主 SI prefix |
| `C13` | 面积 prefix |
| `C17` | 用户光谱模式下应清空 |
| `C20` | 波长步长 |
| `B24:B424` | workbook 自动生成波长 |
| `C24:C424` | 用户输入光谱数值 |

### 5.3 波长范围和步长

Toolbox 的用户光谱范围固定为：

```text
380-780 nm
```

允许的步长为：

```text
1 nm, 2 nm, 4 nm, 5 nm
```

填写光谱后，要清空 780 nm 之后的多余单元格，否则可能触发错误提示。

## 6. Outputs sheet 如何读

`Outputs` 是标准结果主界面。核心输出按五个 alpha-opic 通道排列。

### 6.1 基本量

输出顶部会给出输入光谱对应的基本量，例如：

- unweighted irradiance / radiance
- photopic illuminance / luminance
- photon irradiance / photon radiance

具体单位取决于 `Inputs` 的 quantity 和 prefix。

### 6.2 Alpha-opic irradiance

alpha-opic irradiance 的概念是：

```text
E_alpha = integral spectral irradiance(lambda) * s_alpha(lambda) d lambda
```

其中 `s_alpha(lambda)` 是对应 alpha-opic action spectrum。

如果输入是 radiance，输出会是对应的 alpha-opic radiance。

### 6.3 Alpha-opic ELR

ELR 是 efficacy of luminous radiation：

```text
K_alpha,v = E_alpha / E_v
```

其中：

- `E_alpha` 是 alpha-opic irradiance。
- `E_v` 是 photopic illuminance 对应的光度量。

workbook 中常以 `mW.lm-1` 显示。

### 6.4 Alpha-opic EDI

EDI 是 equivalent daylight (D65) illuminance。

语义是：

```text
产生相同 alpha-opic irradiance 的 D65 日光照度
```

计算思路为：

```text
E_v,alpha^D65 = E_alpha / K_alpha,v^D65
```

其中 `K_alpha,v^D65` 是 D65 对应通道的固定 alpha-opic ELR。

`Action spectra` sheet 中列出了 D65 下五个通道的 ELR 值，workbook 计算使用未四舍五入的内部数值。

### 6.5 Alpha-opic photon irradiance

光子系统输出使用 photon-system action spectrum：

```text
sp,alpha(lambda)
```

输出通常以 `log10(Q / (1 s-1 m-2))` 形式显示。`Outputs` sheet 也给出 standard notation，便于把 log 形式还原为普通科学计数法。

## 7. Action spectra sheet 使用说明

`Action spectra` sheet 是提取五条 alpha-opic sensitivity curve 的主要位置。

### 7.1 Radiometric action spectra

左侧区域从 `B20:G421` 开始：

| 列 | 含义 |
| --- | --- |
| `B` | wavelength / nm |
| `C` | `sc` |
| `D` | `mc` |
| `E` | `lc` |
| `F` | `rh` |
| `G` | `mel` |

这些是 radiometric system 下的 action spectra：

```text
s_alpha(lambda) = se,alpha(lambda)
```

本项目提取的 CSV 正是这一区域。

### 7.2 Photon-system action spectra

右侧区域从 `J20:O421` 开始：

| 列 | 含义 |
| --- | --- |
| `J` | wavelength / nm |
| `K` | `sc` |
| `L` | `mc` |
| `M` | `lc` |
| `N` | `rh` |
| `O` | `mel` |

这些是 photon system 下的 action spectra：

```text
sp,alpha(lambda)
```

如果计算 photon irradiance 或 photon radiance，应使用这套 photon-system 权重。

### 7.3 与本项目已有数据的核验结果

根据当前审计文件：

```text
docs/cie_s026_alpha_opic_extraction_audit.md
```

当前提取结果为：

| 通道 | 与本项目已有数据关系 |
| --- | --- |
| `sc` | 与 CIE 2006 10° S cone linear-energy fundamentals 一致 |
| `mc` | 与 CIE 2006 10° M cone linear-energy fundamentals 一致 |
| `lc` | 与 CIE 2006 10° L cone linear-energy fundamentals 一致 |
| `rh` | 与 scotopic `V_prime` 一致 |
| `mel` | 已作为 `standard_observers.iprgc / cie_s026_melanopic_1nm` 注册 |

重要结论：

```text
该 Toolbox 的 Action spectra sheet 提供的是标准五条 alpha-opic action spectra，
其中 L/M/S 对齐 10° CIE 2006 LMS。melanopic / ipRGC 曲线不做 2° / 10°
视角区分；ipRGC 主要分布在外周，通常按外周 ipRGC 激活语义使用。
```

因此，本项目只单独注册 `mel` 曲线；`sc/mc/lc/rh` 继续使用已有标准数据，
完整五通道组合由 `color.spectra.from_alpha_opic_action_spectra()` 提供。

## 8. Advanced Inputs / Advanced Outputs

日常标准计算不需要改 Advanced 输入。保持默认即可：

```text
Publication: CIE S 026
Reference: D65
```

高级区域主要用于：

- 对比旧的 Lucas et al. 2014 体系。
- 改变 reference spectrum。
- 查看 test source 和 reference source 的匹配结果。
- 查看 alpha-opic DER。
- 控制高级输出的 SI prefix。

### 8.1 DER

DER 是 daylight efficacy ratio。它用于把 photopic illuminance 转成 alpha-opic EDI：

```text
alpha-opic EDI = photopic illuminance * alpha-opic DER
```

其中 DER 本质上是测试光源和 D65 参考光源的 alpha-opic ELR 比值。

### 8.2 非标准组合

如果在 Advanced Inputs 中选择非 D65 reference 或旧 Lucas et al. 2014 模式，workbook 会给出 warning。

这些结果可以用于研究或旧结果复核，但不应混同为标准 CIE S 026 D65-reference 输出。

## 9. 常见错误和检查点

### 9.1 用户光谱输入后没有清空多余单元格

如果使用 `User` 光谱，并且步长不是 1 nm，`C24:C424` 中 780 nm 后的单元格必须清空。

否则 workbook 可能报：

```text
User spectral range mismatch
```

### 9.2 spectral input 误选 luminance / illuminance

用户光谱输入不能选择：

```text
luminance
illuminance
```

这两个是积分后的光度量，不是 spectral quantity。

### 9.3 光子系统 prefix

当选择 photon radiance / photon irradiance 时，某些 prefix 输入需要清空。以 workbook 右侧 error messages 为准。

### 9.4 小数点格式

Excel 会根据系统区域设置解析小数点。某些系统需要 `0,1`，某些系统需要 `0.1`。

### 9.5 不要复用被修改过的 workbook

官方指南建议使用干净 workbook，并对关键结果做人工 spot-check。该 workbook 无宏、无命名区域，便于集成到其它 spreadsheet，但也意味着用户手工修改后更容易留下隐藏错误。

## 10. 和本项目数据注册的关系

当前项目处理方式：

1. 不注册整个 `CIE S 026 alpha-opic Toolbox.xlsx`。
2. 只把运行时需要的 melanopic / ipRGC 曲线固化为标准 CSV：

   ```text
   color/data/standard_observer_data/iprgc/cie_s026_melanopic_1nm.csv
   ```

3. 该数据注册为：

   ```text
   standard_observers.iprgc / cie_s026_melanopic_1nm
   ```

4. 完整 alpha-opic 五通道体系不重复注册为一个 dataset，而是在 `color.spectra` 中组合：

   ```text
   sc, mc, lc, rh, mel
   ```

5. 注册 metadata 应明确：

   ```text
   source_standard = CIE S 026:2018
   source_file = CIE S 026 alpha-opic Toolbox.xlsx
   action_spectra_system = radiometric
   wavelength_range_nm = 380-780
   interval_nm = 1
   observer_basis = ipRGC peripheral activation; no 2/10 degree variant
   ```

6. melanopic / ipRGC 曲线不按 2° / 10° 拆分；文档和 metadata 应明确其外周 ipRGC 激活语义。
