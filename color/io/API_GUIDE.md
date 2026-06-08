# color.io API 使用说明

本文档覆盖 `color.io` 顶层导出的 API。设计说明见 `README_DETAILS.md`。

## save_figure

用途：保存 Matplotlib figure。

输入：输出路径，和可选 `fig`。如果不传 `fig`，保存当前 figure。

返回：输出 `Path`，或传入的 file-like 对象。

```python
import matplotlib.pyplot as plt
from color.io import save_figure

fig, ax = plt.subplots()
ax.plot([400, 500, 600], [0.1, 0.8, 0.2])

save_figure("output/spectrum.png", fig=fig, dpi=300)
```

注意：`save_figure(...)` 默认使用 tight bbox。它不属于 `color.plot`，因为保存文件是 IO 行为。

## spectral_to_dataframe

用途：把 `SpectralDistribution` 或 `MultiSpectralDistribution` 转为 pandas DataFrame。

```python
from color.io import spectral_to_dataframe
from color.spectra import SpectralDistribution

sd = SpectralDistribution([400, 500, 600], [0.1, 0.8, 0.2])
frame = spectral_to_dataframe(sd)
```

多通道对象会生成 `wavelength` 加多个通道列。

```python
from color.spectra import MultiSpectralDistribution

msd = MultiSpectralDistribution(
    [400, 500, 600],
    [[0.1, 0.0], [0.8, 0.4], [0.2, 0.9]],
    ("A", "B"),
)
frame = spectral_to_dataframe(msd)
```

## spectral_from_dataframe

用途：从列式 DataFrame 创建 spectral 对象。

单通道示例：

```python
from color.io import spectral_from_dataframe

sd = spectral_from_dataframe(frame, x="wavelength", y="reflectance")
```

多通道示例：

```python
msd = spectral_from_dataframe(frame, x="wavelength", ys=("X", "Y", "Z"))
```

自动推断示例：

```python
obj = spectral_from_dataframe(frame)
```

如果除 `wavelength` 外只有一个数值列，返回 `SpectralDistribution`；如果有多个数值列，返回 `MultiSpectralDistribution`。

## read_spectral_csv / write_spectral_csv

用途：读写列式 spectral CSV。

写出单通道：

```python
from color.io import write_spectral_csv

write_spectral_csv("sample.csv", sd)
```

读回单通道：

```python
from color.io import read_spectral_csv

sd = read_spectral_csv("sample.csv")
```

读指定列：

```python
sd = read_spectral_csv("patches.csv", x="wavelength", y="Blue Sky")
```

读多通道：

```python
msd = read_spectral_csv("cmfs.csv", ys=("X", "Y", "Z"))
```

注意：CSV 不保存对象级 metadata。需要完整对象序列化时使用 JSON。

## read_spectral_excel / write_spectral_excel

用途：读写 Excel workbook 中的一个 spectral sheet。

写出：

```python
from color.io import write_spectral_excel

write_spectral_excel("sample.xlsx", msd, sheet_name="spectra")
```

读回：

```python
from color.io import read_spectral_excel

msd = read_spectral_excel("sample.xlsx", sheet_name="spectra")
```

指定通道：

```python
sd = read_spectral_excel("uef.xlsx", sheet_name="reflectance_0_1", y="Blue Sky")
```

注意：写出时可以生成一个简单的 metadata sheet；读取时默认只读取一个数值 sheet。

## read_spectral_json / write_spectral_json

用途：对象级 spectral JSON 序列化，保留 `name`、`metadata` 和多通道 labels。

单通道：

```python
from color.io import read_spectral_json, write_spectral_json

write_spectral_json("sample.json", sd)
sd2 = read_spectral_json("sample.json")
```

多通道：

```python
write_spectral_json("multi.json", msd)
msd2 = read_spectral_json("multi.json")
```

覆盖读回名称：

```python
sd = read_spectral_json("sample.json", name="renamed sample")
```

## read_sRGB_image

用途：把图像读取为 encoded sRGB 浮点数组。

返回：

```text
(height, width, 3), float64, [0, 1]
```

```python
from color.io import read_sRGB_image

image = read_sRGB_image("input.jpg")
```

注意：函数会应用 EXIF orientation，并转换为 RGB；不执行 ICC profile 色彩管理。

## write_sRGB_image

用途：把 encoded sRGB 浮点数组写为 8-bit 图像。

```python
from color.io import write_sRGB_image

write_sRGB_image("preview.png", image)
```

严格检查越界：

```python
write_sRGB_image("preview.png", image, clip=False)
```

JPEG 写出：

```python
write_sRGB_image("preview.jpg", image, quality=95)
```

注意：输入必须是 shape `(height, width, 3)` 的有限浮点数组，语义是 encoded sRGB，而不是线性 RGB。
