# color.plot 详细说明

## AI Usage Notes

- Use this module when drawing already-computed curves, points, chromaticity diagrams, gamut surfaces, swatches, images, bars, and publication-style figures.
- Do not use this module to compute colorimetric values, save files directly, load data, or mutate scientific meaning; route those to `colorimetry`, `io`, or the relevant computation module.
- Key assumptions: plot functions return Matplotlib figure/axes objects; they do not call `show()` or save by default; `plot_style(...)` sets defaults but explicit arguments still win.
- Common mistakes: using raw Matplotlib kwargs that conflict with semantic parameters; relying on titles in journal figures instead of panel labels; treating chromaticity background plotting as data computation.
- Related modules: use `io.save_figure` for export, `gamut`/`colorimetry` for computed data, and `spaces` for coordinate conversion.

`color.plot` 是项目的基础绘图组件层。它只负责把已经计算好的数据画出来，不负责生成数据，也不负责改变数据的科学语义。

逐项 API 用法见 [`API_GUIDE.md`](API_GUIDE.md)。本文件只记录设计边界、风格约定和使用注意。

## 模块边界

推荐的数据流是：

```text
datasets / generators -> spectra / colorimetry / spaces / difference / quality -> plot
```

如果需要光谱积分、颜色空间转换、色适应、色貌模型、色域分析或色差计算，应先调用对应模块，再把结果交给 `color.plot`。

`color.plot` 不负责：

- 读取或保存科学数据。
- 执行颜色科学计算。
- 进行色彩管理或 gamut mapping。
- 自动调用 `plt.show()`。
- 自动保存图片。

保存 Matplotlib figure 属于 IO 行为，使用 `color.io.save_figure(...)`。

## 顶层 API 原则

`color.plot` 顶层只保留常用绘图积木和稳定入口，包括：

- 二维线、点、线段、多边形、箭头、图像、柱状图。
- 三维点、线、曲面、线框。
- CIE 1931 xy、CIE 1960 uv、CIE 1976 u'v' 色品图底座。
- style、palette、font 和 panel label 工具。
- sRGB 预览色块。

以下内容不进入顶层：

- 底层 locus loader。
- D65 plotting constants。
- shape / RGB 校验 helper。
- raw `PLOT_STYLE_PRESETS`。
- 兼容包装，例如 `plot_xy_points(...)`。

这些内容仍可留在对应子模块中，但不作为普通用户主入口推荐。

## 低阶组件理念

`color.plot` 不提供高层组合图函数。原因是很多领域图本质上只是低阶组件组合：

- 光谱图是 `plot_lines(...)`。
- 色温图是色品图底座 + 曲线 + 散点。
- RGB gamut 图是色品图底座 + 多边形 + 点。
- 主波长图是色品图底座 + 点 + 线段。
- 色域立体是三维 surface / wireframe。

这种设计能避免 plot 模块重复实现领域逻辑。领域模块或 examples 应该负责计算数据，`color.plot` 只负责绘制。

## Journal Style 约定

`journal` 相关预设面向论文图，而不是官方期刊模板。参数参考常见出版方对图宽、字号、线宽和分辨率的通用要求：

- 单栏宽约 89-90 mm。
- 双栏宽约 180-183 mm。
- 最终图中文字通常需要保持可读。
- 彩色或灰度位图通常至少 300 dpi。

当前公共 style 只保留四个明确目标：

```text
journal
journal_double
presentation
monochrome
```

`journal` 是默认单栏论文图。宽图或多面板图使用 `journal_double`。汇报图使用 `presentation`，黑白打印或灰度论文图使用 `monochrome`。

推荐写法：

```python
from color.plot import plot_lines, plot_style

with plot_style("journal"):
    fig, ax = plot_lines((x, y), xlabel="x", ylabel="value")
```

`plot_style(...)` 是上下文管理器，不会永久污染 Matplotlib 全局设置。`set_plot_style(...)` 会修改全局 `rcParams`，只建议在 notebook 或整份报告统一风格时使用。

`plot_style(...)` 的优先级低于显式绘图参数。它设置的是 Matplotlib 默认
`rcParams`，如果调用方在绘图函数中显式传入 `color`、`colors`、`cmap`、
`fontsize`、`linewidth` 等参数，这些显式参数会覆盖 style：

```python
with plot_style("monochrome"):
    # 仍然会画成红色，因为显式 color 优先于 monochrome 的默认色序。
    fig, ax = plot_lines((x, y), colors=("tab:red",))
```

因此，如果希望 `monochrome` 真正控制线条颜色，不要在调用处显式传彩色
`colors`；或者显式使用 `palette("monochrome")`。

旧别名和细分预设不再保留，例如 `paper`、`journal_single`、`journal_compact`、`bw`、`slide`。细微的字号或线宽变化应通过 `font_scale`、`line_scale` 和 `rc` 表达：

```python
with plot_style("journal", font_scale=1.08, line_scale=1.1):
    fig, ax = plot_lines((x, y), xlabel="x", ylabel="value")
```

## Title 与 Panel Label

科研论文图通常不建议把解释性文字写成 axes title。多面板图应使用：

- panel label，例如 `a / b / c`；
- caption；
- 图外说明。

因此 `journal` 相关预设默认抑制 axes title：

```text
axes.titlesize = 0
axes.titlepad = 0
```

这不是鼓励“先写 title 再隐藏”，而是防止旧脚本或无意设置的 title 挤占论文图空间。确实需要 title 时，可以在 `plot_style(..., rc={...})` 中显式覆盖。

Panel label 使用 `panel_label(...)` 和 `add_panel_labels(...)`，详见 [`API_GUIDE.md`](API_GUIDE.md)。

## Palette 与颜色使用

当前公共 palette 只保留：

```text
journal
presentation
monochrome
```

默认 `journal` palette 使用色盲友好的分类色序。论文图不应只依赖颜色区分数据系列，推荐同时使用：

- 线型；
- marker；
- 直接标签；
- 清晰图例；
- panel label 和 caption。

`palette(...)` 返回有限颜色组；`colour_cycle(...)` 返回无限循环。二者都只负责颜色选择，不改变图形语义。

## CJK 字体

`color.plot` 提供 `available_cjk_fonts(...)` 和 `use_cjk_font(...)`，用于中文、日文或其他 CJK 字符图形。

注意：

- `use_cjk_font(...)` 会修改当前 Matplotlib session 的字体栈。
- 库函数内部不应隐式调用它。
- 若图用于英文论文，应确认 CJK 字体不会影响 Latin 字体外观。

## 色品图背景

`plot_cie1931_diagram(...)`、`plot_cie1960_ucs_diagram(...)` 和 `plot_cie1976_ucs_diagram(...)` 可以绘制近似背景色。

背景色生成流程是：

```text
diagram coordinates -> xy -> xyY(Y=1) -> XYZ -> sRGB preview -> normalise/clip
```

因此背景色只是视觉辅助，不代表严格色彩管理结果。很多色品坐标无法被 sRGB 真实显示，必须经过裁剪或归一化。

## 波长标注

色品图上的波长标注默认关闭。需要时使用：

```python
plot_cie1931_diagram(show_wavelength_labels=True)
```

默认标注波长采用手选列表，而不是固定波长间隔。原因是光谱轨迹在红端、绿端和蓝紫端的几何密度差异很大，固定间隔容易造成局部拥挤或稀疏。

## 子模块高级入口

少数底层 helper 不在顶层导出，但高级用户可从子模块使用：

```python
from color.plot.chromaticity import load_cie1931_locus_xy
from color.plot.chromaticity import plot_xy_points
from color.plot.common import as_2d_points
from color.plot.style import PLOT_STYLE_PRESETS
```

这些入口通常用于测试、自定义扩展或兼容旧代码；普通绘图建议优先使用顶层 API。
