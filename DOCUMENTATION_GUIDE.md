# Module Documentation And Public API Guide

本文档是项目后续整理各模块时的统一执行规范。目标是避免长流程开发后出现：

- 顶层 API 过多、别名过多、职责不清。
- `README_DETAILS.md` 同时承担设计说明和 API 手册，内容混杂。
- 文档和 `__all__` 不一致。
- examples、README、测试对旧 API 的引用没有同步清理。

后续修改 `color.*` 模块时，优先按本文档执行。

## 1. 文档分层

每个主要模块建议维护三层文档。

### `README.md`

英文快速入口。

应回答：

- 这个模块做什么。
- 推荐从哪里导入。
- 最核心的 3-8 个 API。
- 一个最短 Quick Start。

不应承担：

- 长篇设计论证。
- 每个 API 的完整示例。
- 历史迁移记录。

### `README_DETAILS.md`

中文设计说明。

应回答：

- 模块边界是什么。
- 为什么这样设计。
- 和其他模块如何串联。
- 重要约定，例如 XYZ 标度、白点、缓存、不可变对象、数值范围、警告策略。
- 算法限制和常见风险。

不应承担：

- 逐个 API 的使用手册。
- 大量重复的最小代码案例。
- 顶层 `__all__` 的逐项展开。

### `API_GUIDE.md`

中文 API 使用指南。

应回答：

- 顶层 API 有哪些。
- 每个顶层 API 的用途、输入、输出。
- 每个顶层 API 至少一个最小使用案例。
- 常见误用或注意事项。

建议结构：

```md
# color.module API 使用指南

## 顶层 API 总览

| API | 功能 | 推荐场景 |
| --- | --- | --- |

## API 分组一

### function_name(...)

用途：
输入：
返回：
最小示例：
注意：
```

## 2. 顶层 API 收口原则

顶层 `color.module` 只导出用户高频、语义稳定、推荐使用的 API。

### 应放顶层

- 模块的主要对象类型。
- 主要计算入口。
- 常用构造函数。
- 推荐用户直接调用的绘图、转换、分析、读取函数。

### 不应放顶层

- 兼容包装。
- 原始常量表。
- 底层校验函数。
- 数据加载 helper。
- 内部注册表细节。
- 只服务测试或 examples 的工具。
- 容易让用户绕开主语义入口的高级 helper。

这些内容可以留在子模块中，例如：

```python
from color.plot.chromaticity import load_cie1931_locus_xy
from color.plot.style import PLOT_STYLE_PRESETS
```

但不要进入：

```python
from color.plot import ...
```

## 3. `__all__` 编写规范

顶层 `__all__` 使用分组累加，并给每个 API 添加短说明：

```python
__all__: list[str] = []

__all__ += [
    "MainObject",  # short description
    "main_function",  # short description
]

__all__ += [
    "secondary_function",  # short description
]
```

要求：

- 每个顶层 API 都有注释。
- 同一功能组放在同一个 `__all__ += [...]` 中。
- 不把内部 helper 混入顶层。
- 不为同一功能保留多个同义别名，除非已有稳定外部依赖。

## 4. API 文档覆盖规则

整理模块时，以顶层 `__all__` 为准：

```powershell
.\.venv\Scripts\python.exe -c "import color.module as m; print('\n'.join(m.__all__))"
```

然后逐项检查：

- 是否真的应该是顶层 API。
- 是否在 `API_GUIDE.md` 中有小节。
- 是否有最小使用案例。
- 是否在 `README.md` 中出现核心入口。
- 是否在 `README_DETAILS.md` 中解释了必要的设计约定。

如果某个 API 不值得写进 `API_GUIDE.md`，通常说明它不应该在顶层。

## 5. Examples 与 API 文档的关系

`API_GUIDE.md` 写最小调用案例。

`examples/` 写完整工作流案例。

不要把完整 workflow 塞进 API 文档；也不要让 examples 承担基础 API 说明职责。

推荐：

- API guide：5-15 行小例子。
- examples：可视化、长链路、模块串联、真实数据演示。

## 6. 迁移流程

整理某个模块时按以下步骤执行：

1. 打印当前顶层 `__all__`。
2. 分类每个 API：保留顶层 / 下沉子模块 / 删除别名。
3. 修改 `__init__.py` 和相关子模块导出。
4. 搜索旧 API 引用：

   ```powershell
   rg -n "old_api_name" color examples
   ```

5. 更新 README / README_DETAILS / API_GUIDE。
6. 更新 examples 导入。
7. 更新测试导入。
8. 运行模块测试。
9. 运行相关 example 测试。

## 7. 命名与别名原则

优先一个概念一个推荐名字。

避免：

- `label_panel` / `panel_label` 同时顶层存在。
- `get_xxx` / `from_xxx` 混在同一层但语义不清。
- `computed_xxx` 和 `published_xxx` 同时暴露给普通用户，除非用户确实需要选择底层路线。

允许：

- 子模块中保留高级入口。
- 顶层提供统一分发入口。
- 兼容别名短期存在，但不推荐写入新文档。

## 8. 测试建议

每个模块建议至少有：

- public API 导入测试。
- 核心行为测试。
- example 集成测试。

对于 API 收口，额外检查：

```python
def test_public_api_has_no_internal_helpers():
    import color.module as module
    assert "some_internal_helper" not in module.__all__
```

如果某个 API 被移出顶层，应测试它仍可从子模块导入，或者确认它已完全删除。

## 9. 当前建议迁移顺序

已完成或正在整理：

1. `color.plot`

建议后续顺序：

1. `color.datasets`
2. `color.spectra`
3. `color.colorimetry`
4. `color.spaces`
5. `color.gamut`
6. `color.recovery`
7. `color.difference`
8. `color.generators`

顺序可以根据当前开发主线调整，但每个模块都应遵循同一套文档与 API 收口规则。
