# 贡献指南

感谢关注本项目。这是一套方法论 + Skill，欢迎通过 Issue 讨论真实使用中的失败案例，或提交最小化的改进 PR。

## 改动原则

1. **最小改动**：一次 PR 只解决一个明确问题，不夹带格式化或顺手重构。
2. **证据优先**：新增规则必须对应真实失败场景；描述"什么失败会被这条规则阻止"。
3. **可以删，不只可以加**：删除不改变执行的说明同样是有效贡献。
4. **不扩展复杂度**：默认拒绝为"未来可能需要"引入 State、多 Agent、外部模型等机制。
5. **Protected Rules 不可移除**：工作区硬规则（任务产物不写入 Skill 目录、脚本显式输出路径）与权限边界条款不得删改。
6. **坑先备案，别急着晋升**：新踩的坑写进 `pitfalls/`（命中 = 1），**命中 ≥3 次且通用且可执行**才准进 `SKILL.md`。
   单项目 / 单次的具体经验禁止进 `SKILL.md` —— 那是 token 黑洞。
7. **规模红线**：`scripts/` 单文件 ≤300 行（硬线 600，例外须在 `ARCHITECTURE.md` §5 声明理由）；
   不提交密钥 / 令牌字面量。

## 提交前自查

```bash
# 1. 校验脚本仍然通过（应 PASS + 一行 INFO）
python3 scripts/validate-skill.py .

# 2. 改过任何检查规则 → 反面样本必须仍然真的会报错
python3 tests/test_validator_negative.py

# 3. 不引入个人环境信息（说明类文件与 .gitignore 自身含检测模式，需排除）
grep -RInE '/Users/|laozhu|\.trae|\.codex|\.DS_Store' --exclude=AGENTS.md --exclude=CONTRIBUTING.md --exclude=README.md --exclude=.gitignore . && echo "发现问题" || echo "clean"
```

## 约定

- 文档语言：中文为主，契约模板中的字段名保留英文（与脚本检查正则对应）。
- 目录命名 `kebab-case`，脚本仅使用 Python 标准库。
- 提交信息用英文祈使句，如 `fix: clarify loop plateau exit`。
