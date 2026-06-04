# color.plot 详细说明

`color.plot` 是项目的基础绘图组件层。它只负责把已经计算好的数据画出来，不负责生成数据，也不负责改变数据的科学语义。

## 模块边界

推荐的数据流是：

```text
datasets / generators -> spectra / colorimetry / spaces / difference / quality -> plot
```

如果需要这些计算，应先调用对应模块，再把结果交给 `color.plot`。

## 当前核心组件

| API | 功能 |
| --- | --- |
| `plot_lines` | 绘制一条或多条二维连续曲线 |
| `plot_points` | 绘制一组或多组二维散点 |
| `plot_segments` | 绘制一组或多组二维线段 |
| `plot_labels` | 给二维点添加文字标注 |
| `plot_polygons` | 绘制一个或多个二维多边形 |
| `plot_arrows` | 绘制二维箭头 |
| `plot_image` | 绘制二维标量图像或 RGB(A) 图像 |
| `plot_bars` | 绘制单组或多组柱状图 |
| `set_axis_limits_from_data` | 根据二维数据自动设置坐标范围 |
| `style_2d_axis` | 设置标题、坐标轴、网格和等比例坐标 |
| `plot_3d_points` | 绘制一组或多组三维散点 |
| `plot_3d_lines` | 绘制一条或多条三维曲线 |
| `plot_3d_surface` | 绘制三维曲面网格 |
| `plot_3d_wireframe` | 绘制三维线框网格 |
| `set_3d_axis_limits_from_data` | 根据三维数据自动设置坐标范围 |
| `style_3d_axis` | 设置三维坐标轴标题、标签、视角和网格 |
| `get_figure_axes` | 创建或复用 matplotlib axes |
| `finish_figure` | 统一执行 figure 收尾布局 |
| `colour_cycle` | 返回论文图常用颜色循环 |
| `plot_style` | 临时应用绘图风格，不永久修改全局设置 |
| `set_plot_style` | 显式修改全局 matplotlib 绘图风格 |
| `chromaticity_background_image` | 生成色品图背景的近似 sRGB 图像 |
| `plot_cie1931_diagram` | 绘制 CIE 1931 xy 色品图 |
| `plot_cie1960_ucs_diagram` | 绘制 CIE 1960 UCS uv 色度图 |
| `plot_cie1976_ucs_diagram` | 绘制 CIE 1976 UCS u'v' 色度图 |
| `plot_locus_wavelength_labels` | 沿光谱轨迹标注波长 |
| `plot_chromaticity_points` | 在色品图或普通二维图上标注色度点 |
| `preview_sRGB_from_XYZ` | 把 XYZ 转为仅供显示的 clipped sRGB |
| `plot_swatch_strip` | 绘制一行 sRGB 预览色块 |
| `plot_swatch_grid` | 绘制多行 sRGB 预览色块 |

`plot_xy_points` 暂时保留为兼容包装，新的代码推荐使用 `plot_chromaticity_points`。

## 基础曲线与散点

`plot_lines(...)` 和 `plot_points(...)` 是从旧 `tools` 模板中提炼出来的正式接口。它们保留了“多组数据一次绘制”和“统一风格”的优点，但去掉了不适合库函数的行为：

- 不强制 matplotlib backend。
- 不修改全局 `rcParams`。
- 不调用 `plt.show()`。
- 不在函数内部保存文件。
- 不使用 `zip` 静默截断不匹配的数据。

保存图像、展示窗口和项目级绘图风格应由 example 或调用方决定。

### `plot_lines(...)`

适合光谱曲线、色温轨迹、响应函数、误差曲线等连续二维数据：

```python
import numpy as np
from color.plot import plot_lines

wavelengths = np.linspace(380, 780, 200)
spd = np.exp(-0.5 * ((wavelengths - 560) / 35) ** 2)

fig, ax = plot_lines(
    (wavelengths, spd),
    xlabel="Wavelength (nm)",
    ylabel="Relative power",
)
```

多条曲线可以一次传入，并配合 `labels` 自动生成图例：

```python
fig, ax = plot_lines(
    [(x, y1), (x, y2)],
    labels=("sample A", "sample B"),
    xlabel="x",
    ylabel="value",
)
```

### `plot_points(...)`

适合色品坐标、二维颜色空间投影、实验散点等：

```python
from color.plot import plot_points

xy = [[0.3127, 0.3290], [0.3457, 0.3585], [0.2990, 0.3149]]

fig, ax = plot_points(
    xy,
    labels=("D65", "D50", "D75"),
    annotate=True,
    xlabel="x",
    ylabel="y",
)
```

多组散点可以使用不同颜色和图例：

```python
fig, ax = plot_points(
    (measured_xy, predicted_xy),
    labels=("measured", "predicted"),
    colors=("tab:blue", "tab:orange"),
)
```

`plot_segments(...)`、`plot_polygons(...)`、`plot_arrows(...)` 和 `plot_labels(...)`
继续补齐了常见二维几何元素。它们让领域图可以由更小的积木组成：

- 主波长方向可以用 `plot_segments(...)`。
- RGB 色域三角形可以用 `plot_polygons(...)`。
- 色适应或坐标迁移方向可以用 `plot_arrows(...)`。
- 点标签可以用 `plot_points(...) + plot_labels(...)` 分开控制。

`set_axis_limits_from_data(...)` 只根据传入数据设置坐标范围，不推断任何颜色科学语义。

### `plot_segments(...)`

适合画主波长方向、Duv 偏移线、样本点到参考点的连线：

```python
from color.plot import plot_segments

segments = [
    [[0.3127, 0.3290], [0.68, 0.32]],
    [[0.3127, 0.3290], [0.15, 0.06]],
]

fig, ax = plot_segments(
    segments,
    labels=("dominant direction", "complementary direction"),
    colors=("tab:red", "tab:purple"),
)
```

### `plot_polygons(...)`

适合画 RGB 色域三角形、容差区域、二维凸包：

```python
from color.plot import plot_cie1931_diagram, plot_polygons

srgb_triangle = [
    [0.6400, 0.3300],
    [0.3000, 0.6000],
    [0.1500, 0.0600],
]

fig, ax = plot_cie1931_diagram(show_background=True)
plot_polygons(
    srgb_triangle,
    ax=ax,
    labels=("sRGB",),
    edgecolors=("black",),
    fill=False,
)
```

### `plot_arrows(...)`

适合表达方向，例如白点到样本点、色适应前后位置变化：

```python
from color.plot import plot_arrows

fig, ax = plot_arrows(
    starts=[[0.3127, 0.3290]],
    ends=[[0.40, 0.36]],
    color="tab:orange",
    xlabel="x",
    ylabel="y",
)
```

### `plot_labels(...)`

推荐和 `plot_points(...)` 分开使用，这样点样式和文字样式可以独立控制：

```python
from color.plot import plot_labels, plot_points

fig, ax = plot_points(points, colors="tab:blue", legend=False)
plot_labels(
    points,
    labels=("A", "B", "C"),
    ax=ax,
    offset=(5, 5),
)
```

### `set_axis_limits_from_data(...)`

适合组合图最后统一设置坐标范围：

```python
from color.plot import set_axis_limits_from_data

all_points = np.concatenate([points, polygon_vertices], axis=0)
set_axis_limits_from_data(ax, all_points, padding=0.08, equal_aspect=True)
```

`plot_image(...)` 和 `plot_bars(...)` 用来覆盖两类非常常见的论文图：
前者适合显示图像、矩阵、热图结果或 RGB 数组；后者适合显示 XYZ/LMS/Lab
分量、色差指标、质量评价指标等一维或分组数据。它们仍然只是底层绘图组件，
不会解释数据的颜色科学含义。

### `plot_image(...)`

适合展示 RGB 图像、矩阵或二维标量场：

```python
from color.plot import plot_image

fig, ax = plot_image(
    rgb_image,
    title="Encoded sRGB preview",
    show_ticks=False,
)
```

二维标量图可以配合 colormap 和 colorbar：

```python
fig, ax = plot_image(
    error_map,
    cmap="viridis",
    colorbar=True,
    xlabel="x",
    ylabel="y",
)
```

### `plot_bars(...)`

适合比较多个指标或颜色分量：

```python
from color.plot import plot_bars

fig, ax = plot_bars(
    [2.1, 1.4, 3.0],
    labels=("CIE 1976", "CIE 2000", "CAM16-UCS"),
    ylabel="Delta E",
)
```

分组柱状图可以用于多个样本、多种方法的对比：

```python
fig, ax = plot_bars(
    [[2.1, 1.4, 3.0], [1.8, 1.2, 2.5]],
    labels=("CIE 1976", "CIE 2000", "CAM16-UCS"),
    group_labels=("sample A", "sample B"),
)
```

## 三维绘图组件

`plot_3d_points(...)`、`plot_3d_lines(...)`、`plot_3d_surface(...)` 和
`plot_3d_wireframe(...)` 是为三维色立体、Lab/LCH 边界、RGB cube 或
三维轨迹准备的底层组件。它们仍然不做任何颜色科学计算，只接受已经计算好的
三维点、曲线或网格。

### `plot_3d_surface(...)` / `plot_3d_wireframe(...)`

色域边界通常可以整理为 `L* / h / C_max` 网格，然后转换为
`a* = C_max cos(h)`、`b* = C_max sin(h)`、`L* = L` 后绘制：

```python
from color.plot import plot_3d_surface, plot_3d_wireframe

fig, ax = plot_3d_surface(
    a_grid,
    b_grid,
    L_grid,
    xlabel="a*",
    ylabel="b*",
    zlabel="L*",
    cmap="viridis",
)
plot_3d_wireframe(a_grid, b_grid, L_grid, ax=ax, color="0.25", linewidth=0.4)
```

### `plot_3d_points(...)` / `plot_3d_lines(...)`

三维样本点或轨迹可以单独绘制，也可以叠加到曲面上：

```python
from color.plot import plot_3d_lines, plot_3d_points

fig, ax = plot_3d_lines((x, y, z), xlabel="a*", ylabel="b*", zlabel="L*")
plot_3d_points(points_3d, ax=ax, colors="tab:orange")
```

### `set_3d_axis_limits_from_data(...)`

组合三维图时，推荐最后统一设置坐标范围：

```python
from color.plot import set_3d_axis_limits_from_data

set_3d_axis_limits_from_data(ax, xyz_points, padding=0.08, equal_aspect=True)
```

## 绘图风格

`colour_cycle(...)`、`plot_style(...)` 和 `set_plot_style(...)` 用来提供更稳定的
学术汇报/论文图风格。当前正式预设覆盖了论文、报告、笔记本、汇报和深色背景等
常见场景，具体是：

- `journal`：默认预设，等同于 `journal_single`。
- `journal_single`：约 3.5 inch / 89 mm 单栏宽，适合常规论文插图。
- `journal_compact`：更紧凑的单栏布局，适合空间更受限的图。
- `journal_double`：约 7.16 inch / 180-183 mm 双栏宽，适合宽图和多面板图。
- `journal_large`：更宽松的论文图尺寸，适合元素较多但仍需要学术风格的图。
- `journal_grid`：更偏网格化排版的论文风格，适合带子图或面板组合的图。
- `journal_bw` / `monochrome`：黑白风格，适合需要线型区分或灰度输出的图。
- `report` / `thesis`：适合长报告、论文草稿或学位论文的通用风格。
- `notebook`：更适合实验记录、数据探索和交互式笔记本。
- `presentation`：更大字号和线宽，适合汇报/PPT。
- `poster`：更醒目的展示风格，适合海报或演示大图。
- `dark`：深色背景风格，适合深色主题展示或截图。

这些风格是 journal-friendly 预设，不是 Nature、IEEE 或其他期刊的官方模板。
参数参考了常见出版方对最终图宽、字号、分辨率和可读性的要求：单栏约
89-90 mm，双栏约 180-183 mm，最终字号约 5-7 pt，彩色/灰度位图通常
至少 300 dpi。

主要参考：

- Nature figure guide / formatting guide：单栏、双栏尺寸和最终字号建议。
- IEEE graphics guidance：3.5 inch 单栏、7.16 inch 双栏，以及彩色/灰度位图
  至少 300 dpi 的常见要求。

推荐优先使用上下文形式：

```python
from color.plot import plot_lines, plot_style

with plot_style("journal"):
    fig, ax = plot_lines(...)
```

`plot_style(...)` 只在 `with` 代码块中临时应用 matplotlib `rcParams`，
不会永久污染调用方环境。`set_plot_style(...)` 会显式修改全局 `rcParams`，
适合 notebook 或整份报告都需要统一风格的场景。

多面板论文图通常建议把子图说明放到 panel label 和 caption 里，而不是把
`ax.set_title(...)` 当成子图标题使用。这个模块提供了 `panel_label(...)`、
`add_panel_labels(...)` 和 `move_titles_to_panel_labels(...)`，可以直接给现有
axes 加 `a / b / c ...` 标签，或者把旧脚本的标题式标签迁移过来。

配色默认使用色盲友好的分类色序。论文图不要只依赖颜色区分数据系列；
建议同时使用线型、marker、直接标签或图例说明。

### `plot_style(...)`

推荐使用临时上下文形式，不污染全局 matplotlib 设置：

```python
from color.plot import plot_lines, plot_style

with plot_style("journal"):
    fig, ax = plot_lines((x, y), xlabel="x", ylabel="value")
```

双栏或多面板图可以选择 `journal_double`：

```python
with plot_style("journal_double"):
    fig, ax = plot_lines([(x, y1), (x, y2)], labels=("A", "B"))
```

### `colour_cycle(...)`

当需要手动给不同对象分配一致颜色时，可以直接取颜色循环：

```python
from color.plot import colour_cycle, plot_bars

colours = colour_cycle("journal")
fig, ax = plot_bars(
    values,
    group_labels=("method A", "method B"),
    colors=(next(colours), next(colours)),
)
```

### `set_plot_style(...)`

`set_plot_style(...)` 会修改全局 `rcParams`，适合 notebook 或整份报告统一风格：

```python
from color.plot import set_plot_style

set_plot_style("journal")
```

库代码和可复用函数中更推荐 `plot_style(...)`，避免意外改变调用方环境。

## 色品图组件

`plot_cie1931_diagram(...)`、`plot_cie1960_ucs_diagram(...)` 和
`plot_cie1976_ucs_diagram(...)` 是当前最核心的领域绘图底座。它们负责：

- 读取 CIE 1931 光谱轨迹。
- 转换到 xy、uv1960 或 u'v'1976 图面。
- 可选绘制近似 sRGB 背景。
- 可选标注 D65 白点。
- 可选沿光谱轨迹标注波长。

背景色只用于视觉辅助。很多色品坐标无法被 sRGB 真实显示，所以背景经过归一化和裁剪，不代表严格色彩管理结果。

波长标注默认关闭。需要时可以使用：

```python
plot_cie1931_diagram(
    show_wavelength_labels=True,
)
```

默认标注波长参考 `colour.plotting` 的手选列表，而不是固定波长间隔。这样可以避免红端标签过密、绿端标签过疏的问题。

如果确实需要自定义，也可以传入 `wavelength_labels=(...)`；`wavelength_label_interval` 只作为手动等波长间隔模式保留。

`plot_locus_wavelength_labels(...)` 是更底层的 helper，也可以用于 CIE 1960 uv 和 CIE 1976 u'v' 图面。

### `plot_cie1931_diagram(...)`

用于 CIE 1931 xy 色品图底图，可以选择是否绘制背景和波长标签：

```python
from color.plot import plot_cie1931_diagram

fig, ax = plot_cie1931_diagram(show_background=True)
```

```python
fig, ax = plot_cie1931_diagram(
    show_background=True,
    show_wavelength_labels=True,
)
```

### `plot_cie1960_ucs_diagram(...)` / `plot_cie1976_ucs_diagram(...)`

`uv1960` 常用于色温与 Duv 可视化，`u'v'1976` 常用于 Luv 相关色度图：

```python
from color.plot import plot_cie1960_ucs_diagram, plot_cie1976_ucs_diagram

fig, ax = plot_cie1960_ucs_diagram(show_background=True)
fig, ax = plot_cie1976_ucs_diagram(show_background=True)
```

### `plot_chromaticity_points(...)`

色品图底图和散点标注可以组合使用：

```python
from color.plot import plot_chromaticity_points, plot_cie1931_diagram

fig, ax = plot_cie1931_diagram(show_background=True)
plot_chromaticity_points(
    [[0.3127, 0.3290], [0.3457, 0.3585]],
    ax=ax,
    labels=("D65", "D50"),
    color="black",
)
```

### `chromaticity_background_image(...)`

当需要自己控制图像显示方式时，可以先生成背景 RGB 数组：

```python
from color.plot import chromaticity_background_image, plot_image

image = chromaticity_background_image(samples=256)
fig, ax = plot_image(image, show_ticks=False)
```

## 为什么移除高层组合图

光谱曲线、色温轨迹、RGB 色域三角形和转换图谱都不是 `color.plot` 的底层职责：

- 光谱曲线本质上是曲线绘制。
- 色温轨迹本质上是色度图、曲线和散点的组合。
- RGB gamut 本质上是色度图、多边形和散点的组合。
- conversion path / graph 是 `color.spaces` 注册表的特殊可视化。

因此这些图不再从 `color.plot` 顶层导出。需要时应在对应 example 或领域模块中使用基础组件组合。

## 色块预览

`preview_sRGB_from_XYZ(...)`、`plot_swatch_strip(...)` 和 `plot_swatch_grid(...)`
只用于绘图预览。它们会把 RGB 裁剪到 `[0, 1]` 以便显示。

这不是色域映射，也不是严格的色貌再现。

### `preview_sRGB_from_XYZ(...)`

适合把 XYZ 结果快速变成可显示的近似色块：

```python
from color.plot import preview_sRGB_from_XYZ

preview = preview_sRGB_from_XYZ([[95.047, 100.0, 108.883]])
```

如果输入 XYZ 是 `Y=1` 标度，可以显式写明：

```python
preview = preview_sRGB_from_XYZ([[0.95047, 1.0, 1.08883]], white_Y=1.0)
```

### `plot_swatch_strip(...)`

适合少量颜色的横向比较：

```python
from color.plot import plot_swatch_strip

fig, ax = plot_swatch_strip(
    [[0.8, 0.2, 0.1], [0.1, 0.4, 0.9]],
    labels=("sample A", "sample B"),
)
```

### `plot_swatch_grid(...)`

适合展示多组颜色，例如不同转换方法或不同观察条件的结果：

```python
from color.plot import plot_swatch_grid

fig, ax = plot_swatch_grid(
    (
        ("method A", rgb_a),
        ("method B", rgb_b),
    ),
    title="Preview swatches",
)
```

## 示例

```python
import numpy as np
from color.plot import plot_cie1931_diagram, plot_chromaticity_points, plot_lines

x = np.linspace(380, 780, 100)
y = np.exp(-0.5 * ((x - 560) / 35) ** 2)
fig, ax = plot_lines((x, y), xlabel="Wavelength (nm)", ylabel="Value")

fig, ax = plot_cie1931_diagram(show_background=True)
plot_chromaticity_points([[0.3127, 0.3290]], ax=ax, labels=["D65"])
```
