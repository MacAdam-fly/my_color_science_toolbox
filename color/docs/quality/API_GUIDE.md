# color.quality API 使用指南

本文档按 `color.quality.__all__` 覆盖顶层 API。模块边界和 SSI 计算流程见
[`README_DETAILS.md`](README_DETAILS.md)。

## 顶层 API 总览

| API | 功能 |
| --- | --- |
| `spectral_similarity_index` | 计算两条光谱的 Academy Spectral Similarity Index |

## `spectral_similarity_index(test, reference, round_result=True)`

用途：比较测试光源和参考光源的光谱形状相似度。

```python
from color.generators.leds import multi_led_spd
from color.quality import spectral_similarity_index
from color.spectra import from_D65_illuminant, from_columns

d65 = from_D65_illuminant()
raw_led = multi_led_spd(
    peak_wavelengths=(455, 535, 615),
    half_spectral_widths=(18, 28, 22),
    peak_power_ratios=(1.0, 0.8, 0.6),
)
led = from_columns(raw_led, y="spd", name="Example LED")

score = spectral_similarity_index(led, d65)
score_float = spectral_similarity_index(led, d65, round_result=False)
```

注意：

- 输入必须是 `SpectralDistribution`。
- `round_result=True` 返回 SSI 常见取整分数。
- SSI 比较的是 SPD 形状相似度，不是 CRI、TM-30 或 CQS。

## 高级子模块入口

SSI 的固定采样域常量不属于顶层 API。需要验证实现细节时：

```python
from color.quality.ssi import SPECTRAL_SHAPE_SSI

print(SPECTRAL_SHAPE_SSI)
```
