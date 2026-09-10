# Deterministic Agent Workflow

确定性 Agent 工作流设计与 Skill 构建方法。把重复工作变成复杂度合适、能够稳定执行和持续改进的 AI Agent Skill。

## 这是什么

一套面向个人工作室与 AI Agent 的方法论 + 可直接安装的 Skill（`workflow-skill-builder`）：

- **确定性约束执行过程**：输入与事实源、修改边界、验收条件、流转规则、失败出口和生效版本必须明确。
- **不承诺生成内容完全一致**：模型输出和主观判断仍可能变化，因此按风险配置验证方式。
- **三个设计视角**：Design（能力与边界）、Runtime（R0/R1/R2 执行结构）、Evolution（证据驱动增删规则）。
- **六个基础 Primitive**：`Contract + Atomic Action + Gate + State + Loop + Commit`，按需组合，不要求全部实现。
- **判断路由**：能脚本验证的不进 LLM；外部模型必须绑定具体 Gate、职责、上下文策略和预算。
- **工作区硬规则**：Skill 目录只存可复用能力，一切任务产物写入目标项目中的新任务文件夹。

## 仓库结构

```text
deterministic-agent-workflow/
├── SKILL.md                              # 主方法文档（可直接作为 Codex Skill 安装）
├── references/
│   ├── personal-studio-standard.md       # 工作室工作流标准（Runtime 分级、验证分层、进化门禁）
│   └── vnext-contracts.md                # 各类契约模板（Task/Stage/Action/Gate/Loop/State/Commit/Recovery）
├── scripts/
│   └── validate-skill.py                 # 零依赖 SKILL.md 机械校验脚本
├── LICENSE                               # MIT
├── CONTRIBUTING.md                       # 贡献说明
└── AGENTS.md                             # 面向 AI Agent 的项目速览
```

## 快速开始

### 方式一：作为 Codex / Agent Skill 安装

```bash
git clone https://github.com/Zeno-Zhu/deterministic-agent-workflow.git \
  ~/.codex/skills/deterministic-agent-workflow
```

之后对 Agent 说"用 workflow-skill-builder 创建/优化一个 Skill"即可触发。

### 方式二：仅当方法论阅读

直接阅读 [SKILL.md](SKILL.md)，需要细节时再查 `references/` 下的两份文档。

### 校验你产出的 Skill

```bash
python3 scripts/validate-skill.py /absolute/path/to/your/SKILL.md
```

脚本为纯标准库实现（Python 3.9+），检查：

- YAML frontmatter 有效性（`name` 格式、`description` 非空）；
- 工作区隔离规则（任务产物不写入 Skill 目录、脚本使用显式输出路径）；
- 受控迭代规则（复盘与迭代、暂存后审阅再采用、held-out 门禁提示）。

## 适用与不适用

| ✅ 适用 | ❌ 不适用 |
|---|---|
| 重复触发的创作 / 数据 / 编码 / 文档工作流 | 一次性问题（直接问即可） |
| 需要跨会话恢复、多版本候选的长任务 | 需要多 Agent 委员会投票的场景 |
| 想让 Skill 按证据增删规则而非只增不减 | 试图用固定轮数替代验收条件 |

## License

[MIT](LICENSE) © 2026 Zeno-Zhu
