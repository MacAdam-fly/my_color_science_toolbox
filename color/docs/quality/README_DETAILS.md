# color.quality 详细说明

## AI Usage Notes

- Use this module only for the currently documented spectral similarity functionality.
- Do not claim stable support for CRI/Ra/R9, TM-30, CQS, or mature light-quality workflows unless they are explicitly implemented and documented later.
- Key assumptions: this module is not part of the current mature mainline API; treat it as limited and narrower than general lighting-quality evaluation.
- Common mistakes: mapping any light-quality request to `quality`; inventing CRI/TM-30 calculations from memory; treating SSI as a substitute for all rendering-quality metrics.
- Related modules: use `colorimetry` for spectral integration and `plot`/`io` for reporting; propose a scoped implementation plan for unsupported quality metrics.

`color.quality` 用来放置光源质量、显色质量和光谱相似度相关的指标。当前第一版只实现
Academy **Spectral Similarity Index (SSI)**。

## 模块边界

`quality` 是已有模块的下游应用层：

```text
datasets / generators -> spectra -> quality
```

SSI 的输入是已经包装好的 `SpectralDistribution`，因此来自 `datasets` 或
`generators` 的原始字典需要先用 `color.spectra.from_columns(...)` 包装。

```python
from color.generators.leds import multi_led_spd
from color.spectra import from_columns

raw = multi_led_spd()
sd = from_columns(raw, y="spd", name="Example LED")
```

## SSI 是什么

SSI 比较两个光源光谱形状的相似程度。它回答的问题是：

```text
这个测试光源的 SPD 和参考光源的 SPD 有多像？
```

常见用法包括把 LED、黑体、日光或电影灯光与某个参考光源比较。`100` 表示两条光谱在
SSI 规则下完全一致或非常接近。

## SSI 不是什么

SSI 不是 CRI、TM-30 或 CQS。

| 指标 | 比较对象 | 需要标准色样 |
| --- | --- | --- |
| SSI | 两条 SPD 本身 | 不需要 |
| CRI | 标准反射色样在测试光源和参考光源下的颜色差异 | 需要 |
| TM-30 | 大量标准色样的保真度、色域变化和色相分区 | 需要 |
| CQS | 标准色样下的颜色质量评分 | 需要 |

因此 SSI 适合作为 `quality` 第一版；CRI、TM-30、CQS 后续需要先整理标准测试色样数据。

## 当前 API

```python
from color.quality import spectral_similarity_index
```

| API | 作用 |
| --- | --- |
| `spectral_similarity_index(test, reference, round_result=True)` | 计算测试光源相对参考光源的 SSI |

SSI 固定采样域常量 `SPECTRAL_SHAPE_SSI` 属于高级实现细节；如需检查，
从 `color.quality.ssi` 导入。

## 计算流程

当前实现对齐 Academy SSI 参考流程：

1. 将测试光谱和参考光谱线性对齐到 `375-675 nm, 1 nm`。
2. 范围外光谱值使用 `0` 填充。
3. 用 10 nm 积分矩阵压缩到 `380-670 nm` 的 30 个采样块。
4. 分别归一化测试光谱和参考光谱。
5. 计算加权相对差异。
6. 用 `[0.22, 0.56, 0.22]` 平滑差异。
7. 返回：

```text
SSI = 100 - 32 * sqrt(sum(smoothed_difference^2))
```

`round_result=True` 时返回取整分数；`round_result=False` 时返回未取整浮点值。

## 使用示例

```python
from color.quality import spectral_similarity_index
from color.spectra import from_D65_illuminant, from_columns
from color.generators.blackbody import blackbody_spd

d65 = from_D65_illuminant()
raw = blackbody_spd(temperature=6500)
blackbody = from_columns(raw, y="radiance", name="Blackbody 6500 K")

score = spectral_similarity_index(blackbody, d65)
score_float = spectral_similarity_index(blackbody, d65, round_result=False)
```

## 注意事项

- SSI 只接受 `SpectralDistribution`，不直接接受原始字典。
- SSI 比较的是光谱相似度，不会计算物体颜色还原能力。
- 输入光谱的绝对幅度会被归一化，主要影响来自光谱形状。
- 范围外填充为 `0`，因此非常窄或范围不足的光谱会自然得到较低相似度。

## 后续方向

后续 `quality` 可以继续加入：

- `CRI / Ra / Ri`
- `TM-30 Rf / Rg / 色相分区数据`
- `CQS`

这些指标需要标准测试色样数据和更完整的色度流程，应单独规划。
