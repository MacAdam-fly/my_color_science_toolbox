# CVRL Color Science Data Collection

**Source:** [Colour & Vision Research Laboratory](http://www.cvrl.org/) — Institute of Ophthalmology, UCL
**Downloaded:** 2026-05-09
**Total:** 106 CSV files across 6 categories

All data is in plain CSV format (comma-separated values). Column headers are not included in most files — the first column is wavelength (nm), followed by the function values. Step sizes are 5nm unless otherwise noted.

---

## Directory Structure

```
cvrl_data/
├── cmfs/                        # Colour Matching Functions (15 files)
├── cone_fundamentals/           # Cone Spectral Sensitivities (27 files)
├── luminous_efficiency/         # Luminous Efficiency Functions (29 files)
├── prereceptoral_filters/       # Macular Pigment & Lens Density (11 files)
├── chromaticity_coordinates/    # Chromaticity Diagram Coordinates (16 files)
├── photopigments/               # Photopigment Absorption Spectra (8 files)
└── README.md                    # This file
```

---

## 1. Colour Matching Functions (`cmfs/`)

These functions describe how the standard human observer matches colors by mixing three primaries.

| File | Description | Range | Step |
| --- | --- | --- | --- |
| `cie1931_xyz_5nm.csv` | **CIE 1931 2° XYZ CMFs** — the fundamental standard observer | 360–830nm | 5nm |
| `cie1931_xyz_1nm.csv` | Same as above at 1nm resolution | 360–830nm | 1nm |
| `cie1964_xyz_5nm.csv` | **CIE 1964 10° XYZ CMFs** — supplementary observer | 360–830nm | 5nm |
| `cie1964_xyz_1nm.csv` | Same as above at 1nm resolution | 360–830nm | 1nm |
| `ciexyz_judd.csv` | CIE 1931 modified by Judd (1951) | 360–830nm | 5nm |
| `ciexyz_judd_vos.csv` | CIE 1931 modified by Judd (1951) and Vos (1978) | 360–830nm | 5nm |
| `sbrgb2.csv` | Stiles & Burch (1955) 2° RGB CMFs | 390–830nm | 5nm |
| `sbrgb10_5nm.csv` | Stiles & Burch (1959) 10° RGB CMFs | 390–830nm | 5nm |
| `sbrgb10_1nm.csv` | Same at 1nm resolution | 390–830nm | 1nm |
| `cie2012_xyz2_5nm.csv` | **CIE 2012 2° XYZ** — from CIE 2006 LMS (proposed) | 390–830nm | 5nm |
| `cie2012_xyz2_1nm.csv` | Same at 1nm resolution | 390–830nm | 1nm |
| `cie2012_xyz2_0p1nm.csv` | Same at 0.1nm resolution | 390–830nm | 0.1nm |
| `cie2012_xyz10_5nm.csv` | **CIE 2012 10° XYZ** — from CIE 2006 LMS (proposed) | 390–830nm | 5nm |
| `cie2012_xyz10_1nm.csv` | Same at 1nm resolution | 390–830nm | 1nm |
| `cie2012_xyz10_0p1nm.csv` | Same at 0.1nm resolution | 390–830nm | 0.1nm |

**Columns:** `wavelength, x_bar, y_bar, z_bar` (or `r_bar, g_bar, b_bar` for Stiles-Burch)

**Key references:**
- CIE 1931: CIE (1932). Commission Internationale de l'Eclairage Proceedings, 1931. Cambridge: Cambridge University Press.
- CIE 1964: CIE (1964). CIE 1964 supplementary standard colorimetric observer.
- CIE 2012: Derived from Stockman & Sharpe (2000) LMS cone fundamentals via CIE Technical Report 170-1.

---

## 2. Cone Fundamentals (`cone_fundamentals/`)

Human cone photoreceptor spectral sensitivities (L, M, S cones). Provided in three unit systems.

CIE 2006 LMS cone fundamentals are based on Stockman & Sharpe (2000) data. The original `ss*.csv` files (5nm only) were removed as they are identical to the `cie2006_lms*_5nm.csv` versions.

| File | Description | Units |
| --- | --- | --- |
| `cie2006_lms2_logE_5nm.csv` | CIE 2006 2° LMS, log energy (5nm) | log₁₀(energy) |
| `cie2006_lms2_logE_1nm.csv` | Same at 1nm resolution | log₁₀(energy) |
| `cie2006_lms2_logE_0p1nm.csv` | Same at 0.1nm resolution | log₁₀(energy) |
| `cie2006_lms2_logQ_5nm.csv` | CIE 2006 2° LMS, log quantal (5nm) | log₁₀(quanta) |
| `cie2006_lms2_logQ_1nm.csv` | Same at 1nm resolution | log₁₀(quanta) |
| `cie2006_lms2_logQ_0p1nm.csv` | Same at 0.1nm resolution | log₁₀(quanta) |
| `cie2006_lms2_linE_5nm.csv` | CIE 2006 2° LMS, linear energy (5nm) | linear |
| `cie2006_lms2_linE_1nm.csv` | Same at 1nm resolution | linear |
| `cie2006_lms2_linE_0p1nm.csv` | Same at 0.1nm resolution | linear |
| `cie2006_lms10_logE_5nm.csv` | CIE 2006 10° LMS, log energy (5nm) | log₁₀(energy) |
| `cie2006_lms10_logE_1nm.csv` | Same at 1nm resolution | log₁₀(energy) |
| `cie2006_lms10_logE_0p1nm.csv` | Same at 0.1nm resolution | log₁₀(energy) |
| `cie2006_lms10_logQ_5nm.csv` | CIE 2006 10° LMS, log quantal (5nm) | log₁₀(quanta) |
| `cie2006_lms10_logQ_1nm.csv` | Same at 1nm resolution | log₁₀(quanta) |
| `cie2006_lms10_logQ_0p1nm.csv` | Same at 0.1nm resolution | log₁₀(quanta) |
| `cie2006_lms10_linE_5nm.csv` | CIE 2006 10° LMS, linear energy (5nm) | linear |
| `cie2006_lms10_linE_1nm.csv` | Same at 1nm resolution | linear |
| `cie2006_lms10_linE_0p1nm.csv` | Same at 0.1nm resolution | linear |
| `smj2_logE.csv` | Stockman, MacLeod & Johnson (1993) 2° | log₁₀(energy) |
| `smj2_logQ.csv` | Same, log quantal | log₁₀(quanta) |
| `smj10_logE.csv` | Stockman, MacLeod & Johnson (1993) 10° | log₁₀(energy) |
| `smj10_logQ.csv` | Same, log quantal | log₁₀(quanta) |
| `vew_logE.csv` | Vos, Estevez & Walraven (1990) 2° | log₁₀(energy) |
| `vew_logQ.csv` | Same, log quantal | log₁₀(quanta) |
| `sp_logE.csv` | Smith & Pokorny (1975) 2° | log₁₀(energy) |
| `sp_logQ.csv` | Same, log quantal | log₁₀(quanta) |
| `dpse_logE.csv` | DeMarco, Pokorny & Smith (1992) | log₁₀(energy) |

**Columns:** `wavelength, L, M, S` (or `l, m, s`)

**Key references:**
- Stockman & Sharpe (2000) — endorsed by CIE as CIE 2006 (Technical Report 170-1)
- Smith & Pokorny (1975) — widely used in clinical vision science

---

## 3. Luminous Efficiency Functions (`luminous_efficiency/`)

Spectral sensitivity of the human visual system for brightness/luminance perception.

| File | Description | Units |
| --- | --- | --- |
| `cie2008_v2_linE_5nm.csv` | **CIE 2008 2° V(λ)** — physiologically-relevant, linear energy | energy |
| `cie2008_v2_linE_1nm.csv` | Same at 1nm resolution | energy |
| `cie2008_v2_linE_0p1nm.csv` | Same at 0.1nm resolution | energy |
| `cie2008_v2_logE_5nm.csv` | Same, log energy | log₁₀(energy) |
| `cie2008_v2_logE_1nm.csv` | Same at 1nm resolution | log₁₀(energy) |
| `cie2008_v2_logE_0P1nm.csv` | Same at 0.1nm resolution | log₁₀(energy) |
| `cie2008_v2_logQ_5nm.csv` | Same, log quantal | log₁₀(quanta) |
| `cie2008_v2_logQ_1nm.csv` | Same at 1nm resolution | log₁₀(quanta) |
| `cie2008_v2_logQ_0p1nm.csv` | Same at 0.1nm resolution | log₁₀(quanta) |
| `cie2008_v10_linE_5nm.csv` | **CIE 2008 10° V(λ)** — linear energy | energy |
| `cie2008_v10_linE_1nm.csv` | Same at 1nm resolution | energy |
| `cie2008_v10_linE_0p1nm.csv` | Same at 0.1nm resolution | energy |
| `cie2008_v10_logE_5nm.csv` | Same, log energy | log₁₀(energy) |
| `cie2008_v10_logE_1nm.csv` | Same at 1nm resolution | log₁₀(energy) |
| `cie2008_v10_logE_0P1nm.csv` | Same at 0.1nm resolution | log₁₀(energy) |
| `cie2008_v10_logQ_5nm.csv` | Same, log quantal | log₁₀(quanta) |
| `cie2008_v10_logQ_1nm.csv` | Same at 1nm resolution | log₁₀(quanta) |
| `cie2008_v10_logQ_0p1nm.csv` | Same at 0.1nm resolution | log₁₀(quanta) |
| `vl1924_5nm.csv` | CIE 1924 Photopic V(λ) | energy |
| `vl1924_1nm.csv` | Same at 1nm | energy |
| `vl1924_logE.csv` | Same, log energy | log₁₀(energy) |
| `vl1924_logQ.csv` | Same, log quantal | log₁₀(quanta) |
| `vl_judd_logE.csv` | V(λ) modified by Judd (1951) | log₁₀(energy) |
| `vl_judd_vos_5nm.csv` | V(λ) modified by Judd (1951) & Vos (1978) | energy |
| `vl_judd_vos_1nm.csv` | Same at 1nm | energy |
| `scotopic_v_5nm.csv` | CIE 1951 Scotopic V'(λ) | energy |
| `scotopic_v_1nm.csv` | Same at 1nm | energy |
| `scotopic_v_logE.csv` | Same, log energy | log₁₀(energy) |
| `scotopic_v_logQ.csv` | Same, log quantal | log₁₀(quanta) |

**Columns:** `wavelength, V(λ)` (single value per wavelength)

**Key references:**
- CIE 1924 V(λ): the original photopic luminous efficiency function
- CIE 2008: Sharpe et al. (2011) — consistent with Stockman & Sharpe cone fundamentals
- Scotopic V'(λ): CIE (1951) — sensitivity of rod vision under dim conditions

---

## 4. Prereceptoral Filters (`prereceptoral_filters/`)

Optical filtering by the eye's media before light reaches the photoreceptors.

### Macular Pigment
Absorbs short-wavelength light in the foveal retina. Peak absorption ~460nm.

| File | Description |
| --- | --- |
| `macular_ss_5nm.csv` | CVRL macular pigment optical density (Stockman & Sharpe) |
| `macular_ss_1nm.csv` | Same at 1nm |
| `macular_ss_0p1nm.csv` | Same at 0.1nm |
| `macular_vos.csv` | Vos (1972) macular pigment density |
| `macular_ws.csv` | Wyszecki & Stiles (1967/1982) macular pigment density |

### Lens Density
Absorbs UV and short-wavelength light in the crystalline lens. Increases with age.

| File | Description |
| --- | --- |
| `lens_ss_5nm.csv` | CVRL lens density spectrum (Stockman & Sharpe) |
| `lens_ss_1nm.csv` | Same at 1nm |
| `lens_ss_0p1nm.csv` | Same at 0.1nm |
| `lens_ciepo06_components_5nm.csv` | CIEPO06 ocular media components `D_ocul,1`, `D_ocul,2`, and their age-32 sum |
| `lens_smj.csv` | Stockman, MacLeod & Johnson (1993) lens density |
| `lens_vnv.csv` | van Norren & Vos (1974) lens density |
| `lens_ws.csv` | Wyszecki & Stiles (1967/1982) lens density |

**Columns:** `wavelength, optical_density`

---

## 5. Chromaticity Coordinates (`chromaticity_coordinates/`)

Planimetric coordinates for plotting chromaticity diagrams.

| File | Description |
| --- | --- |
| `cie1931_chro_5nm.csv` | CIE 1931 2° x,y chromaticity coordinates |
| `cie1931_chro_1nm.csv` | Same at 1nm |
| `cie1964_chro_5nm.csv` | CIE 1964 10° x,y chromaticity coordinates |
| `cie1964_chro_1nm.csv` | Same at 1nm |
| `cie2012_chro2_5nm.csv` | CIE 2012 2° x,y,z chromaticity coordinates |
| `cie2012_chro2_1nm.csv` | Same at 1nm |
| `cie2012_chro2_0p1nm.csv` | Same at 0.1nm |
| `cie2012_chro10_5nm.csv` | CIE 2012 10° x,y,z chromaticity coordinates |
| `cie2012_chro10_1nm.csv` | Same at 1nm |
| `cie2012_chro10_0p1nm.csv` | Same at 0.1nm |
| `mb2_chro2_5nm.csv` | MacLeod-Boynton 2° chromaticity (l, s, B) |
| `mb2_chro2_1nm.csv` | Same at 1nm |
| `mb2_chro2_0p1nm.csv` | Same at 0.1nm |
| `mb_chro10_5nm.csv` | MacLeod-Boynton 10° chromaticity (l, s, B) |
| `mb_chro10_1nm.csv` | Same at 1nm |
| `mb_chro10_0p1nm.csv` | Same at 0.1nm |

**Columns:** `wavelength, x, y, z` (for CIE) or `wavelength, l, s, B` (for MacLeod-Boynton)

**MacLeod-Boynton coordinates** are based on cone fundamentals and are widely used in color vision research to plot chromaticity in a cone-excitation space.

---

## 6. 光色素吸收光谱 (`photopigments/`)

人眼视网膜感光细胞中光色素（photopigment）对不同波长光的吸收光谱。光色素是视觉转导的第一步——它们吸收光子后发生构象变化，触发神经信号。

| 文件 | 测量对象 | 方法 | 数据特征 |
| --- | --- | --- | --- |
|                     |                                |            |                              |
| `sucrodsh.csv` | 人视杆细胞（rods） | 吸入电极 | 31 点，379–760 nm，单色素 |
| `sucrodsm.csv` | 猴视杆细胞（rods） | 吸入电极 | 17 点，398–720 nm，单色素 |
| `succones.csv` | 猴锥体细胞（L, M, S cones） | 吸入电极 | 24 点，381–830 nm，3 列 |
| `msprhes.csv` | 恒河猴锥体细胞 | 显微光谱法 | 25 点，410–650 nm，稀疏填充 |
| `msphum.csv` | 人锥体细胞（rod + L, M, S） | 显微光谱法 | 29 点，370–650 nm，5 列稀疏 |
| `ss_psycho_5nm.csv` | Stockman & Sharpe 模板锥体曲线 | 心理物理学 | 89 点，390–830 nm，3 列 |
| `merbnath.csv` | 人锥体色素基因表达产物 | 分子遗传学 | 401 点，300–700 nm，5 种色素 |

**数据格式：**

- 单色素文件（2 列）：`wavelength, absorption`（对数吸收率，负值）
- 多色素文件（4–5 列）：`wavelength, L, M, S` 或 `wavelength, rod, L, M, S`
- `msprhes`/`msphum`/`succones` 中部分单元格为空，因为不同锥体类型在不同波长范围内才有有效测量
- `merbnath` 为空格分隔格式（非逗号分隔）

**测量方法说明：**

| 方法 | 全称 | 原理 |
| --- | --- | --- |
| 吸入电极 | Suction electrode | 从单个感光细胞直接记录光电流响应，精度高但样本量少 |
| 显微光谱法 | MSP (Microspectrophotometry) | 用显微光度计测量单个细胞的吸收光谱，可测更多细胞类型 |
| 心理物理学 | Psychophysics | 通过人类视觉行为实验反推锥体灵敏度，非直接细胞测量 |
| 分子遗传学 | Molecular genetics | 从视蛋白基因表达产物测量吸收光谱（Merbs & Nathans, 1992） |
|            |                              |                                                           |

**参考文献：**

- Baylor, Nunn & Schnapf (1984, 1987) — 猴视杆/锥体吸入电极测量
- Kraft, Schneeweis & Schnapf (1993) — 人视杆吸入电极测量
- Bowmaker et al. (1978) — 恒河猴显微光谱法
- Dartnall, Bowmaker & Mollon (1983) — 人显微光谱法
- Stockman & Sharpe (2000) — 心理物理学锥体模板
- Merbs & Nathans (1992) — 分子遗传学人锥体色素

---

## Unit Conversions

| From | To | Formula |
| --- |----|---------|
| log₁₀(energy) | linear energy | `10^x` |
| log₁₀(quanta) | linear quanta | `10^x` |
| energy → quanta | — | multiply by λ (proportional) |
| quanta → energy | — | divide by λ (proportional) |

---

## Quick Usage Example (Python)

```python
import numpy as np

# Load CIE 1931 2° XYZ at 5nm steps
data = np.loadtxt('cmfs/cie1931_xyz_5nm.csv', delimiter=',')
wavelength = data[:, 0]
x_bar = data[:, 1]
y_bar = data[:, 2]
z_bar = data[:, 3]

# Load CIE 2006 2° LMS cone fundamentals (linear energy)
data = np.loadtxt('cone_fundamentals/ss2_linE.csv', delimiter=',')
l_cone = data[:, 1]
m_cone = data[:, 2]
s_cone = data[:, 3]
```

---

## License & Citation

Data from CVRL is provided for research and educational purposes. When using this data, please cite:

> Colour & Vision Research Laboratory, Institute of Ophthalmology, University College London. http://www.cvrl.org/

For specific datasets, cite the original authors as noted in each section above.

---

## Notes

- The CIE 2012 XYZ functions (from CIE 2006 LMS) are proposals that were not yet fully ratified at time of download.
- The "physiologically-relevant" CIE 2008 V(λ) functions are consistent with the Stockman & Sharpe cone fundamentals and should be preferred over the older CIE 1924 V(λ) for new work.
- Wavelength ranges vary by dataset: CIE standards typically cover 360–830nm, while specialized datasets may have narrower ranges.
- For the highest precision calculations, use the 1nm or 0.1nm versions; 5nm versions are sufficient for most applications.
