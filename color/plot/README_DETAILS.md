# color.plot 详细说明

`color.plot` 是项目的公共绘图层，用来沉淀 examples 中反复出现的可视化逻辑。它只负责把已有数据画出来，不负责改变计算结果。

## 模块边界

`color.plot` 位于计算模块之上：

```text
datasets / generators -> spectra / colorimetry / spaces -> plot
```

它不做光谱积分、不做色适应、不做颜色空间路由。需要这些计算时，应该先调用对应模块，再把结果交给 `color.plot`。

## 当前功能

| API | 用途 |
| --- | --- |
| `get_figure_axes` | 创建或复用 matplotlib axes |
| `finish_figure` | 统一执行图形收尾布局 |
| `as_2d_points` | 校验绘图用二维点数组 |
| `as_rgb_rows` | 校验并裁剪绘图用 RGB 行 |
| `chromaticity_background_image` | 生成色度图背景的 sRGB 图像 |
| `plot_chromaticity_background` | 绘制通用色度图背景 |
| `plot_xy_chromaticity_background` | 绘制 CIE 1931 xy 背景 |
| `plot_cie1960_ucs_diagram` | 绘制 CIE 1960 UCS uv 色度图 |
| `plot_cie1976_ucs_diagram` | 绘制 CIE 1976 UCS u'v' 色度图 |
| `plot_spectral_distribution` | 绘制单通道光谱 |
| `plot_multi_spectral_distribution` | 绘制多通道光谱，例如 CMFs |
| `style_spectral_axis` | 统一光谱图坐标轴样式 |
| `load_cie1931_locus_xy` | 读取 CIE 1931 xy 光谱轨迹 |
| `load_cie1931_locus_uv1960` | 读取 CIE 1931 光谱轨迹并转换到 uv1960 |
| `load_cie1931_locus_upvp1976` | 读取 CIE 1931 光谱轨迹并转换到 u'v'1976 |
| `plot_cie1931_diagram` | 绘制 CIE 1931 xy 色度图 |
| `plot_xy_points` | 在 xy 图上绘制点和标签 |
| `preview_sRGB_from_XYZ` | 把 XYZ 转成仅供显示的 clipped sRGB |
| `plot_swatch_strip` | 绘制一行色块 |
| `plot_swatch_grid` | 绘制多行色块网格 |
| `plot_rgb_gamuts` | 绘制 RGB 色域三角形 |
| `plot_conversion_path` | 绘制单条颜色空间转换路径 |
| `plot_conversion_graph` | 绘制当前注册的颜色空间转换图谱 |

## 返回值约定

所有绘图函数都接受 `ax=None`：

- 没有传入 `ax` 时，函数创建新的 figure 和 axes。
- 传入已有 `ax` 时，函数在该 axes 上绘制。
- 所有函数返回 `(fig, ax)`，方便 example 保存图片或继续叠加绘制。

## common 的边界

`color.plot.common` 只放绘图基础设施，例如 axes 创建、figure 收尾和绘图输入数组整理。
色品图背景填色、RGB 色域、光谱曲线这类有明确颜色科学语义的逻辑不放在
`common` 中，而是放在对应的主题模块中。

## 色品图背景填色

`plot_cie1931_diagram(show_background=True)`、`plot_cie1960_ucs_diagram(show_background=True)`
和 `plot_cie1976_ucs_diagram(show_background=True)` 都可以在光谱轨迹内部绘制近似
sRGB 背景色。背景计算先把当前图的坐标转换回 CIE xy，再进入统一流程：

```text
diagram 网格 -> xy -> xyY(Y=1) -> XYZ -> sRGB -> 按最大通道归一化 -> clip 到 [0, 1]
```

背景色只是可视化辅助。因为很多 xy 坐标不能被 sRGB 真实显示，所以图中的颜色经过
归一化和裁剪，不代表严格的显示色彩管理结果。

CIE 1960 `uv` 是 CCT / Duv 可视化更自然的图面，因为 Duv 本身就是相对普朗克轨迹
在 uv1960 中定义的偏离量。CIE 1976 `u'v'` 更常用于 Luv 相关的均匀色度图展示。
二者都只是二维色度坐标，不包含亮度信息，也不是完整的三维颜色空间。

旧名称 `plot_xy_locus(...)`、`plot_uv1960_locus(...)` 和
`plot_upvp1976_locus(...)` 仍作为兼容别名保留；新代码推荐使用
`plot_cie1931_diagram(...)` 这一组更明确的命名。

## sRGB 预览色块

`preview_sRGB_from_XYZ(...)` 是绘图辅助函数。它会把 `XYZ` 转换成 sRGB，并 clip 到 `[0, 1]` 以便显示。

这有两个重要限制：

- 它不是色域映射算法。
- 它不是严格的色貌再现。

因此它适合 example、调试图、概览图，不适合用于最终颜色管理结果。

## conversion path / graph

`plot_conversion_path(...)` 和 `plot_conversion_graph(...)` 的真实实现仍在 `color.spaces.plotting`，`color.plot` 只是提供统一绘图入口。这样可以保留原有导入路径，同时让用户从一个地方找到所有常用绘图函数。

## 示例

```python
from color.plot import plot_cie1931_diagram, plot_xy_points

fig, ax = plot_cie1931_diagram()
plot_xy_points([[0.3127, 0.3290]], ax=ax, labels=["D65"])
```

```python
from color.plot import preview_sRGB_from_XYZ, plot_swatch_strip

rgb = preview_sRGB_from_XYZ([[95.047, 100.0, 108.883]])
fig, ax = plot_swatch_strip(rgb, labels=["D65"])
```
