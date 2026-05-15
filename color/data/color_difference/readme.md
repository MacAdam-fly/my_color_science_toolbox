# Color Difference Formula Data

**Folder:** `color/data/color_difference/`
**Purpose:** CIE recommended color difference formula implementation and validation data.

---

## Files

### 1. CIEDE2000.xls

**Source:** Dr. Klaus Witt, BAM, Germany

| Property | Value |
|----------|-------|
| Format | XLS |

**Sheets:**
- **Formulae** — Complete Excel implementation of CIEDE2000 color difference formula
- **Examples** — 10 pairs of calculation examples with full intermediate values for validation

CIEDE2000 is the latest CIE recommended color difference formula (CIE 142:2001), more accurately reflecting human perception of color differences than CIE94 and CMC.

---

## About CIEDE2000

CIEDE2000 improves upon previous color difference formulas by incorporating:
- Lightness weighting function (S_L)
- Chroma weighting function (S_C)
- Hue weighting function (S_H)
- Chroma rotation term (R_T) to deal with the problematic blue region

---

## CIEDE2000 Formula (Step by Step)

All angles are in **degree** units. For programmers: all trigonometric functions need conversion of angle to radian.

### Step 1: Calculate CIELAB values

Given two colors (standard `s` and batch `b`) in CIELAB: (L\*, a\*, b\*)

### Step 2: Calculate C'ab and h'ab

**Chroma:**
```
C*ab = sqrt(a*² + b*²)
```

**Hue angle:**
```
h'ab = tan⁻¹(b*/a')
```
> Add 360 to the smaller h' if absolute value of difference > 180°

### Step 3: Calculate G

```
G = 0.5 * (1 - sqrt(C*ab,m⁷ / (C*ab,m⁷ + 25⁷)))
```
where `C*ab,m = (C*ab,b + C*ab,s) / 2`

### Step 4: Calculate a', C', h'

```
L' = L*
a' = a* × (1 + G)
b' = b*
```

```
C' = sqrt(a'² + b'²)
```

```
h' = tan⁻¹(b'/a')
```
> Add 360 to the smaller h' if absolute value of difference > 180°

**Mean values:**
```
C'm = (C'b + C's) / 2
h'm = (h'b + h's) / 2
```

### Step 5: Calculate T

```
T = 1 - 0.17×cos(h'm - 30°) + 0.24×cos(2×h'm) + 0.32×cos(3×h'm + 6°) - 0.20×cos(4×h'm - 63°)
```

### Step 6: Calculate SL, SC, SH

```
L'm = (L'b + L's) / 2
```

```
S_L = 1 + 0.015×(L'm - 50)² / sqrt(20 + (L'm - 50)²)
S_C = 1 + 0.045×C'm
S_H = 1 + 0.015×C'm×T
```

### Step 7: Calculate ΔL', ΔC', ΔH'

```
ΔL' = L'b - L's
ΔC' = C'b - C's
Δh' = h'b - h's    (add 360 to smaller h' if |difference| > 180°)
ΔH' = 2×sqrt(C'b × C's) × sin(Δh'/2)
```

### Step 8: Calculate Δθ and RC

```
Δθ = 30×exp(-((h'm - 275°)/25°)²)
```

```
R_C = 2×sqrt(C'm⁷ / (C'm⁷ + 25⁷))
```

### Step 9: Calculate R_T

```
R_T = -sin(2×Δθ) × R_C
```

### Step 10: Calculate ΔE₀₀

```
ΔE₀₀ = sqrt(
    (ΔL'/(k_L×S_L))² +
    (ΔC'/(k_C×S_C))² +
    (ΔH'/(k_H×S_H))² +
    R_T × (ΔC'/(k_C×S_C)) × (ΔH'/(k_H×S_H))
)
```

where:
- `k_L, k_C, k_H` = parametric weighting factors (set to 1 for reference conditions)
- `D_V = ΔE₀₀ / k_E` (k_E = overall sensitivity factor)

---

## Validation Examples

The Examples sheet provides 10 pairs (s = standard, b = batch) of CIELAB colors with complete intermediate calculation values. Input data is in XYZ (CIE 10° observer, D65 illuminant).

**Reference white (10°):**
```
X₀,₁₀ = 94.811,  Y₀,₁₀ = 100,  Z₀,₁₀ = 107.304
```

| Pair | ΔE₀₀ | Description |
|------|-------|-------------|
| 1 | 1.2644 | |
| 2 | 1.2630 | |
| 3 | 1.8731 | |
| 4 | 1.8645 | |
| 5 | 2.0373 | |
| 6 | 1.4146 | |
| 7 | 1.4440 | |
| 8 | 1.5381 | |
| 9 | 0.6378 | |
| 10 | 0.9082 | |

### Detailed Intermediate Values (Pair 1)

**Standard (1s):**
| Parameter | Value |
|-----------|-------|
| X₁₀, Y₁₀, Z₁₀ | 19.41, 28.41, 11.5766 |
| L\* | 60.2574 |
| f(X/X₀) | 0.589371 |
| f(Y/Y₀) | 0.657391 |
| f(Z/Z₀) | 0.476053 |
| a\* | -34.0099 |
| b\* | 36.2677 |
| C\*ab | 49.7194 |
| a' | -34.0678 |
| C' | 49.7590 |
| h' | 133.2086° |

**Batch (1b):**
| Parameter | Value |
|-----------|-------|
| X₁₀, Y₁₀, Z₁₀ | 19.5525, 28.64, 10.5791 |
| L\* | 60.4626 |
| f(X/X₀) | 0.59081 |
| f(Y/Y₀) | 0.65916 |
| f(Z/Z₀) | 0.461967 |
| a\* | -34.1751 |
| b\* | 39.4387 |
| C\*ab | 52.1857 |
| a' | -34.2333 |
| C' | 52.2238 |
| h' | 130.9584° |

**Intermediate calculations:**
| Parameter | Value |
|-----------|-------|
| L'm | 60.3600 |
| C'm | 50.9914 |
| h'm | 132.0835° |
| T | 1.3010 |
| G | 0.001703 |
| ΔL' | -2.2501 |
| ΔC' | 0.2052 |
| Δh' | 2.4648° |
| ΔH' | -2.0018 |
| S_L | 1.1427 |
| S_C | 3.2946 |
| S_H | 1.9951 |
| Δθ | 0.0 |
| R_T | -0.0 |
| **ΔE₀₀** | **1.2644** |

---

## Usage

Open `CIEDE2000.xls` in Excel to:
1. Study the formula implementation step by step
2. Use the Examples sheet for validation (10 pairs with full intermediate values)
3. Adapt the formulas for your own calculations

> **Note:** For programmers working in English Excel, replace the German `WENN` function with `IF`.

---

## References

- CIE 142:2001. Improvement to Industrial Colour-Difference Evaluation.
- Sharma, G., Wu, W., & Dalal, E.N. (2005). The CIEDE2000 color-difference formula: Implementation notes, supplementary test data, mathematical observations. Color Research & Application, 30(1), 21-30.
