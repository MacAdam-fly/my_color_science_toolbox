# color.plot API 使用指南

本文档说明 `color.plot` 顶层 API 的推荐用法。`color.plot` 只负责绘制已经计算好的数据

## 顶层 API 总览

| API | 功能 | 推荐场景 |
| --- | --- | --- |
| `get_figure_axes` | 创建或复用二维 axes | 自定义组合图入口 |
| `finish_figure` | figure 收尾布局 | example 或脚本末尾统一整理 |
| `plot_lines` | 二维曲线 | 光谱曲线、轨迹、误差曲线 |
| `plot_points` | 二维散点 | 色品点、二维投影点 |
| `plot_segments` | 二维线段 | 主波长方向、辅助连接线 |
| `plot_labels` | 点文字标签 | 分离控制点和标签 |
| `plot_polygons` | 二维多边形 | RGB gamut、xy 边界 |
| `plot_arrows` | 二维箭头 | 方向、位移、色适应前后 |
| `plot_image` | 标量图像或 RGB(A) 图像 | 矩阵、图片、背景图 |
| `plot_bars` | 柱状图 | 指标对比、覆盖率对比 |
| `set_axis_limits_from_data` | 根据数据设置二维坐标范围 | 组合图统一范围 |
| `style_2d_axis` | 设置二维 axes 样式 | 已有 axes 的收尾 |
| `get_3d_figure_axes` | 创建或复用三维 axes | 三维色立体 |
| `plot_3d_points` | 三维散点 | 颜色空间点云 |
| `plot_3d_lines` | 三维曲线 | 三维轨迹 |
| `plot_3d_surface` | 三维曲面 | gamut boundary surface |
| `plot_3d_wireframe` | 三维线框 | 曲面辅助线框 |
| `set_3d_axis_limits_from_data` | 根据数据设置三维坐标范围 | 三维组合图统一范围 |
| `style_3d_axis` | 设置三维 axes 样式 | 三维图收尾 |
| `plot_cie1931_diagram` | CIE 1931 xy 色品图 | xy 色品位置展示 |
| `plot_cie1960_ucs_diagram` | CIE 1960 uv 色度图 | CCT / Duv 可视化 |
| `plot_cie1976_ucs_diagram` | CIE 1976 u'v' 色度图 | Luv 相关色度图 |
| `chromaticity_background_image` | 色品图背景图像数据 | 自定义背景组合 |
| `plot_chromaticity_background` | 色品图背景 | 底层背景绘制 |
| `plot_chromaticity_points` | 色度点绘制 | 色品图上添加点和标签 |
| `plot_locus_wavelength_labels` | 光谱轨迹波长标注 | 自定义波长标签 |
| `palette` | 有限颜色组 | 一次性指定多组颜色 |
| `colour_cycle` | 无限颜色循环 | 逐个分配颜色 |
| `available_styles` | 可用风格名称 | 查询 style |
| `available_palettes` | 可用调色板名称 | 查询 palette |
| `plot_style` | 临时应用 style | 推荐用法 |
| `set_plot_style` | 修改全局 style | notebook/session 级别 |
| `style_rcparams` | 获取 style 参数副本 | 外部集成或检查 |
| `despine` | 隐藏 axes spines | 局部修饰 |
| `mm_to_inches` / `cm_to_inches` | 尺寸单位换算 | 论文图尺寸 |
| `panel_label` | 单 axes 标签 | 单图 panel label |
| `add_panel_labels` | 批量 panel labels | 多面板论文图 |
| `available_cjk_fonts` | 检查 CJK 字体 | 中文标签诊断 |
| `use_cjk_font` | 启用 CJK 字体栈 | 中文图形入口 |
| `preview_sRGB_from_XYZ` | XYZ 到 clipped sRGB 预览 | 仅绘图预览 |
| `plot_swatch_strip` | 一行色块 | 少量颜色对比 |
| `plot_swatch_grid` | 多行色块 | 多组颜色对比 |

## 基础 figure / axes

### `get_figure_axes(...)`

用途：创建新 figure/axes，或复用已有 axes。

输入：可选 `ax`、`figsize`、`projection` 等参数。  
返回：`(fig, ax)`。

```python
from color.plot import get_figure_axes

fig, ax = get_figure_axes(figsize=(3.5, 2.5))
ax.plot([0, 1], [0, 1])
```

注意：普通绘图函数内部也会自动创建 axes；只有需要手动组合图时才需要直接调用。

### `finish_figure(...)`

用途：对 figure 执行统一收尾布局。

输入：`fig`。  
返回：`fig`。

```python
from color.plot import finish_figure

finish_figure(fig)
```

注意：保存文件不属于 `color.plot`；请使用 `color.io.save_figure(...)`。

## 二维绘图组件

### `plot_lines(...)`

用途：绘制一条或多条二维曲线。

输入：单条 `(x, y)` 或多条 `[(x1, y1), (x2, y2)]`。  
返回：`(fig, ax)`。

```python
import numpy as np
from color.plot import plot_lines

x = np.linspace(380, 780, 200)
y = np.exp(-0.5 * ((x - 560) / 35) ** 2)
fig, ax = plot_lines((x, y), xlabel="Wavelength (nm)", ylabel="Value")
```

注意：多曲线可传 `labels` 自动生成图例；长度不匹配会抛出 `ValueError`。

### `plot_points(...)`

用途：绘制一组或多组二维散点。

输入：`(n, 2)` 点数组，或多组点。  
返回：`(fig, ax)`。

```python
from color.plot import plot_points

fig, ax = plot_points(
    [[0.3127, 0.3290], [0.3457, 0.3585]],
    labels=("D65", "D50"),
    annotate=True,
    xlabel="x",
    ylabel="y",
)
```

注意：`annotate=True` 会把 `labels` 当作逐点文字；多组散点的 `labels` 则用于图例。

### `plot_segments(...)`

用途：绘制二维线段集合。

输入：形如 `(n, 2, 2)` 的线段数组。  
返回：`(fig, ax)`。

```python
from color.plot import plot_segments

segments = [[[0.3127, 0.3290], [0.65, 0.30]]]
fig, ax = plot_segments(segments, colors="tab:red")
```

注意：适合主波长方向、辅助连接线、Duv 偏移线。

### `plot_labels(...)`

用途：只给二维点添加文字标签。

输入：点数组和同长度标签。  
返回：`(fig, ax)`。

```python
from color.plot import plot_labels, plot_points

points = [[0.3127, 0.3290], [0.3457, 0.3585]]
fig, ax = plot_points(points, colors="tab:blue", legend=False)
plot_labels(points, ("D65", "D50"), ax=ax, offset=(4, 4))
```

注意：推荐和 `plot_points(...)` 分开使用，便于独立控制点和文字。

### `plot_polygons(...)`

用途：绘制一个或多个二维多边形。

输入：单个 `(n, 2)` 多边形或多个多边形。  
返回：`(fig, ax)`。

```python
from color.plot import plot_polygons

triangle = [[0.64, 0.33], [0.30, 0.60], [0.15, 0.06]]
fig, ax = plot_polygons([triangle], labels=("sRGB",), fill=False)
```

注意：RGB gamut 三角形、xy hull、二维边界都适合用它。

### `plot_arrows(...)`

用途：绘制二维箭头。

输入：起点数组和终点数组。  
返回：`(fig, ax)`。

```python
from color.plot import plot_arrows

fig, ax = plot_arrows([[0.3, 0.3]], [[0.4, 0.35]], colors="tab:orange")
```

注意：适合展示坐标变化方向，不适合替代线段或数据曲线。

### `plot_image(...)`

用途：绘制二维标量图像或 RGB(A) 图像。

输入：二维数组，或最后一维为 3/4 的图像数组。  
返回：`(fig, ax)`。

```python
import numpy as np
from color.plot import plot_image

image = np.random.random((64, 64))
fig, ax = plot_image(image, colorbar=True, cmap="viridis")
```

注意：RGB 图像应使用 `[0, 1]` 或 Matplotlib 可接受范围。

### `plot_bars(...)`

用途：绘制单组或多组柱状图。

输入：一维数组或二维分组数组。  
返回：`(fig, ax)`。

```python
from color.plot import plot_bars

fig, ax = plot_bars([0.72, 0.84, 0.91], labels=("sRGB", "P3", "Rec.2020"))
```

注意：覆盖率、误差、指标对比适合用柱状图。

### `set_axis_limits_from_data(...)`

用途：根据二维数据自动设置坐标范围。

输入：`ax` 和二维点/边界数据。  
返回：`ax`。

```python
from color.plot import set_axis_limits_from_data

set_axis_limits_from_data(ax, points, padding=0.08, equal_aspect=True)
```

注意：只处理几何范围，不理解颜色科学语义。

### `style_2d_axis(...)`

用途：对已有二维 axes 设置标题、标签、网格、等比例等。

输入：`ax` 和可选 `xlabel/ylabel/grid/equal_aspect`。  
返回：`ax`。

```python
from color.plot import style_2d_axis

style_2d_axis(ax, xlabel="x", ylabel="y", grid=True, equal_aspect=True)
```

注意：journal style 默认抑制 axes title；论文图推荐 panel label + caption。

## 三维绘图组件

### `get_3d_figure_axes(...)`

用途：创建或复用三维 axes。

输入：可选 `ax`、`figsize`。  
返回：`(fig, ax)`。

```python
from color.plot import get_3d_figure_axes

fig, ax = get_3d_figure_axes(figsize=(4.0, 3.2))
```

注意：传入非 3D axes 会抛出 `ValueError`。

### `plot_3d_points(...)`

用途：绘制三维点。

输入：`(n, 3)` 点数组，或多组点。  
返回：`(fig, ax)`。

```python
from color.plot import plot_3d_points

fig, ax = plot_3d_points([[0, 0, 50], [20, 10, 70]], xlabel="a*", ylabel="b*", zlabel="L*")
```

注意：适合 Lab/Oklab/Jzazbz 点云。

### `plot_3d_lines(...)`

用途：绘制三维曲线。

输入：单条 `(x, y, z)` 或多条曲线。  
返回：`(fig, ax)`。

```python
from color.plot import plot_3d_lines

fig, ax = plot_3d_lines((x, y, z), xlabel="a*", ylabel="b*", zlabel="L*")
```

### `plot_3d_surface(...)` / `plot_3d_wireframe(...)`

用途：绘制三维曲面和线框。

输入：形状一致的 `X, Y, Z` 网格。  
返回：`(fig, ax)`。

```python
from color.plot import plot_3d_surface, plot_3d_wireframe

fig, ax = plot_3d_surface(X, Y, Z, alpha=0.35)
plot_3d_wireframe(X, Y, Z, ax=ax, color="0.25", linewidth=0.4)
```

注意：色域立体边界通常用 surface + wireframe 组合。

### `set_3d_axis_limits_from_data(...)`

用途：根据三维点云设置坐标范围。

输入：`ax` 和三维数据。  
返回：`ax`。

```python
from color.plot import set_3d_axis_limits_from_data

set_3d_axis_limits_from_data(ax, points_3d, padding=0.08, equal_aspect=True)
```

### `style_3d_axis(...)`

用途：设置三维 axes 标签、视角、网格等。

输入：`ax` 和可选 `xlabel/ylabel/zlabel/view`。  
返回：`ax`。

```python
from color.plot import style_3d_axis

style_3d_axis(ax, xlabel="a*", ylabel="b*", zlabel="L*", view=(25, -45))
```

## 色品图组件

### `plot_cie1931_diagram(...)`

用途：绘制 CIE 1931 xy 色品图。

输入：可选 `show_background`、`show_wavelength_labels`、`whitepoint_xy`。  
返回：`(fig, ax)`。

```python
from color.plot import plot_cie1931_diagram

fig, ax = plot_cie1931_diagram(show_background=True)
```

注意：默认不设置 title；论文图推荐 panel label + caption。

### `plot_cie1960_ucs_diagram(...)`

用途：绘制 CIE 1960 UCS uv 图。

输入：可选背景、波长标签和白点。  
返回：`(fig, ax)`。

```python
from color.plot import plot_cie1960_ucs_diagram

fig, ax = plot_cie1960_ucs_diagram(show_background=True)
```

注意：uv1960 是 CCT / Duv 可视化的主要图面。

### `plot_cie1976_ucs_diagram(...)`

用途：绘制 CIE 1976 UCS u'v' 图。

输入：可选背景、波长标签和白点。  
返回：`(fig, ax)`。

```python
from color.plot import plot_cie1976_ucs_diagram

fig, ax = plot_cie1976_ucs_diagram(show_background=True)
```

注意：u'v'1976 常用于 Luv 相关色度展示。

### `chromaticity_background_image(...)`

用途：生成色品图背景的近似 sRGB 图像数组。

输入：`method`、`samples`、`normalise`。  
返回：形状为 `(samples, samples, 3)` 的 RGB 图像。

```python
from color.plot import chromaticity_background_image, plot_image

image = chromaticity_background_image(samples=128)
fig, ax = plot_image(image, show_ticks=False)
```

注意：背景经过归一化和裁剪，只是视觉辅助，不是严格色彩管理结果。

### `plot_chromaticity_background(...)`

用途：绘制色品图背景。

输入：色度图 method、samples、alpha。  
返回：`(fig, ax)`。

```python
from color.plot import plot_chromaticity_background

fig, ax = plot_chromaticity_background(method="CIE 1931", samples=128)
```

注意：通常更推荐直接用 `plot_cie1931_diagram(show_background=True)`。

### `plot_chromaticity_points(...)`

用途：在色品图或普通二维图上添加色度点和标签。

输入：`(n, 2)` 点数组、可选 labels。  
返回：`(fig, ax)`。

```python
from color.plot import plot_chromaticity_points, plot_cie1931_diagram

fig, ax = plot_cie1931_diagram(show_background=True)
plot_chromaticity_points([[0.3127, 0.3290]], ax=ax, labels=("D65",))
```

### `plot_locus_wavelength_labels(...)`

用途：沿已有光谱轨迹标注波长。

输入：wavelengths、coordinates、可选 label 列表或间隔。  
返回：文字 artist 列表。

```python
from color.plot import plot_locus_wavelength_labels

texts = plot_locus_wavelength_labels(wavelengths, xy_coordinates, ax=ax)
```

注意：通常不需要直接调用；`plot_cie1931_diagram(show_wavelength_labels=True)` 已封装常用场景。

## 风格、调色板和字体

### `plot_style(...)`

用途：临时应用绘图风格。

输入：style 名称，可选 `font_scale`、`line_scale`、`palette_name`、`rc`。  
返回：上下文管理器。

```python
from color.plot import plot_lines, plot_style

with plot_style("journal"):
    fig, ax = plot_lines((x, y), xlabel="x", ylabel="value")
```

当前支持的 style 只有 `journal`、`journal_double`、`presentation`、`monochrome`。细微字号/线宽变化使用 `font_scale` 和 `line_scale`：

```python
with plot_style("journal", font_scale=1.08, line_scale=1.1):
    fig, ax = plot_lines((x, y), xlabel="x", ylabel="value")
```

注意：推荐在脚本和 examples 中使用，不污染全局 Matplotlib 设置。旧别名如 `paper`、`journal_single`、`journal_compact`、`bw`、`slide` 不再支持。

### `set_plot_style(...)`

用途：修改全局 Matplotlib rcParams。

输入：style 名称和可选缩放/覆盖参数。  
返回：`None`。

```python
from color.plot import set_plot_style

set_plot_style("journal")
```

注意：适合 notebook 或整份报告统一风格；库函数内部不要调用。

### `style_rcparams(...)`

用途：获取某个 style 的 rcParams 副本。

输入：style 名称和可选覆盖参数。  
返回：`dict`。

```python
from color.plot import style_rcparams

params = style_rcparams("journal")
```

局部覆盖：

```python
params = style_rcparams("journal", rc={"axes.grid": True})
```

注意：不要直接修改 `color.plot.style.PLOT_STYLE_PRESETS`。

### `palette(...)`

用途：返回一组有限颜色。

输入：palette 名称。  
返回：颜色字符串 tuple。

```python
from color.plot import palette

colors = palette("journal")
```

当前支持的 palette 只有 `journal`、`presentation`、`monochrome`。

### `colour_cycle(...)`

用途：返回无限颜色循环。

输入：palette 名称。  
返回：迭代器。

```python
from color.plot import colour_cycle

colors = colour_cycle("journal")
first = next(colors)
```

### `available_styles(...)` / `available_palettes(...)`

用途：查看可用 style 和 palette 名称。

返回：字符串 tuple。

```python
from color.plot import available_palettes, available_styles

print(available_styles())
print(available_palettes())
```

当前结果应为：

```text
available_styles() -> ("journal", "journal_double", "presentation", "monochrome")
available_palettes() -> ("journal", "presentation", "monochrome")
```

### `despine(...)`

用途：隐藏指定 axes spines。

输入：`ax` 和 top/right/left/bottom 开关。  
返回：`ax`。

```python
from color.plot import despine

despine(ax, top=True, right=True)
```

### `mm_to_inches(...)` / `cm_to_inches(...)`

用途：论文图尺寸单位换算。

输入：毫米或厘米数值。  
返回：英寸数值。

```python
from color.plot import mm_to_inches

width = mm_to_inches(89)
```

### `available_cjk_fonts(...)` / `use_cjk_font(...)`

用途：检查并启用 CJK 字体。

返回：字体名称 tuple。

```python
from color.plot import available_cjk_fonts, use_cjk_font

print(available_cjk_fonts())
use_cjk_font()
```

注意：`use_cjk_font(...)` 会修改当前 Matplotlib session 的字体栈。

## Panel labels

### `panel_label(...)`

用途：给单个 axes 添加 panel label。

输入：`ax`、label、位置和字体参数。  
返回：text artist。

```python
from color.plot import panel_label

panel_label(ax, "a")
```

### `add_panel_labels(...)`

用途：给多个 axes 批量添加 panel labels。

输入：axes 序列、可选 labels。  
返回：text artist 列表。

```python
from color.plot import add_panel_labels

add_panel_labels(axes, labels=("a", "b", "c"))
```

注意：不传 labels 时自动使用 `a, b, c, ...`。

## 色块预览

### `preview_sRGB_from_XYZ(...)`

用途：把 XYZ 转成仅供绘图预览的 clipped sRGB。

输入：`XYZ`，可选 `white_Y`。  
返回：RGB 数组。

```python
from color.plot import preview_sRGB_from_XYZ

rgb = preview_sRGB_from_XYZ([[95.047, 100.0, 108.883]])
```

注意：这是显示预览，不是严格色貌再现；会裁剪到 `[0, 1]`。

### `plot_swatch_strip(...)`

用途：绘制一行 sRGB 色块。

输入：RGB 行数组和可选 labels。  
返回：`(fig, ax)`。

```python
from color.plot import plot_swatch_strip

fig, ax = plot_swatch_strip([[1, 0, 0], [0, 1, 0]], labels=("R", "G"))
```

### `plot_swatch_grid(...)`

用途：绘制多行 sRGB 色块。

输入：`[(row_label, rgb_rows), ...]`。  
返回：`(fig, ax)`。

```python
from color.plot import plot_swatch_grid

fig, ax = plot_swatch_grid([
    ("row 1", [[1, 0, 0], [0, 1, 0]]),
    ("row 2", [[0, 0, 1], [1, 1, 1]]),
])
```
