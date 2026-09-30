"""workflow-skill-builder 的机械校验实现包。

`scripts/validate-skill.py` 是唯一 CLI 入口；本包只提供检查逻辑。
按「常量 → 核心 → 布局 → 规则」四层拆开，保证单文件 ≤ 300 行
（纪律见 references/code-engineering.md §0 第 7 条）。
"""
