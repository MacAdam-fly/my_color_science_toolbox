# color.io 详细说明

`color.io` 是项目的文件读写层。它负责把已经定义好的对象写出到文件，或把文件读回为项目对象；它不负责数据注册、颜色空间转换、色适应、ICC 色彩管理或科学计算。

更完整的逐项 API 示例见 `API_GUIDE.md`。

## 模块边界

`color.io` 当前覆盖三类基础 IO：

- Matplotlib figure 保存。
- `SpectralDistribution` / `MultiSpectralDistribution` 的 CSV、Excel、JSON 读写。
- sRGB 图像作为 `[0, 1]` 浮点数组的读写。

`color.datasets` 负责静态数据注册和缓存；`color.spectra` 负责光谱对象包装和重采样；`color.io` 只处理文件输入输出。

## Spectral 表格约定

CSV 和 Excel 使用列式表格：

```text
wavelength, sample_1, sample_2, ...
```

如果只有一个数值列，读取结果是 `SpectralDistribution`。如果有多个数值列，读取结果是 `MultiSpectralDistribution`。调用者也可以通过 `y=` 或 `ys=` 显式指定通道。

CSV 和 Excel 适合和表格工具互通，但它们不是对象级序列化格式。对象的 `name`、`metadata`、多通道 `labels` 等信息不一定能从普通 CSV 中自然恢复。

## Spectral JSON 约定

JSON 是对象级导出格式，会保留：

- 对象类型。
- `name`。
- `metadata`。
- `wavelength`。
- 单通道 `value` 或多通道 `labels` / `values`。

因此，如果目标是保存一个 spectral 对象并在之后尽量完整地读回，优先使用 JSON。

## 图像 IO 约定

`read_image(...)` 是通用图像入口。默认 `as_float=True`，会把整数图像编码值归一化到 `[0, 1]`；如果需要保留原始 `uint8 / uint16` 编码值，使用：

```python
image_codes = read_image("input.png", as_float=False)
```

读取时可以用 `mode="RGB"`、`mode="RGBA"` 或 `mode="L"` 让 Pillow 先做基础通道转换。这里的 mode 转换只是图像格式层面的通道转换，不是 ICC/profile 色彩管理。

`write_image(...)` 是通用写入入口。浮点数组被解释为 `[0, 1]` 归一化图像，默认写成 8-bit；如果要从浮点写成 16-bit，可以显式传入：

```python
write_image("gray16.tiff", image, bit_depth=16)
```

整数数组在 `bit_depth=None` 时保留原始 dtype；如果显式传入 `bit_depth=8/16`，则按对应码值范围裁剪或检查。

`read_sRGB_image(...)` / `write_sRGB_image(...)` 是语义更窄的便利入口，固定用于 encoded sRGB RGB 图像。`read_sRGB_image(...)` 读取图像后返回浮点数组，shape 为：

```text
(height, width, 3)
```

数值范围是 `[0, 1]`。它会应用 EXIF orientation，并转换为 RGB。

`write_sRGB_image(...)` 接受同样的 `[0, 1]` encoded sRGB 数组，并写出为 8-bit 图像。默认 `clip=True`，越界值会裁剪到 `[0, 1]`；如果需要严格检查越界，使用 `clip=False`。

这些图像函数只做常规数组读写，不解析 ICC profile，也不执行显示 profile 之间的色彩管理。

## Figure 保存

`save_figure(...)` 放在 `color.io`，不是 `color.plot`。原因是保存文件属于 IO 操作，而不是绘图 primitive。`color.plot` 负责创建图形元素，`color.io.save_figure(...)` 负责输出文件。

## 后续方向

后续可以加入：

- ICC / profile 文件读写。
- 更通用的图像位深、alpha、灰度和浮点图像 IO。
- 光谱对象的压缩或批量容器格式。

这些扩展应保持同一原则：IO 只负责文件和对象之间的转换，不隐式改变颜色科学语义。
