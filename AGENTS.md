# AGENTS.md — AI Agent 项目速览

## 项目定位

「确定性 Agent 工作流设计与 Skill 构建方法」的公开仓库。仓库根目录本身就是一个可安装的 Codex Skill：`workflow-skill-builder`。

## 关键文件

- `SKILL.md`：主方法（VNext 八步创建法、R0/R1/R2 Runtime、判断路由、验证分层、证据驱动进化）。
- `references/personal-studio-standard.md`：完整标准（六 Primitive、Runtime 分级、验证矩阵、Protected Rules）。
- `references/vnext-contracts.md`：契约模板库，仅在对应能力真实存在时引用。
- `scripts/validate-skill.py`：零依赖校验脚本，`python3 scripts/validate-skill.py SKILL.md` 返回 0 即通过。

## Agent 修改本仓库时的硬规则

1. 本仓库是 Skill 目录，不是任务工作区：任何任务产物、临时文件、日志一律写入目标项目的任务文件夹，绝不写入本仓库。
2. 修改 `SKILL.md` 后必须运行校验脚本并通过。
3. 不得移除工作区隔离规则与受控迭代规则（脚本会检查）。
4. 不得引入第三方依赖、个人绝对路径或 `.DS_Store`。

## 验证

```bash
python3 scripts/validate-skill.py SKILL.md
grep -RInE '/Users/|laozhu|\.trae|\.codex' . || echo clean
```
