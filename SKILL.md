---
name: workflow-skill-builder
description: Use when creating, restructuring, or improving Codex skills and repeatable AI workflows for a personal studio. Turns recurring tasks, creator methods, scripts, prompts, and delivery processes into lean Skills with explicit contracts, atomic actions, validation, runtime complexity, judgment routing, recovery when needed, and evidence-driven evolution. Triggers on requests to create or upgrade a Skill, deterministic workflow, agent workflow, repeatable workflow, or to simplify an overbuilt process.
---

# Workflow Skill Builder VNext

把可复用能力设计成复杂度合适、能够稳定执行和持续改进的 Skill。

确定性主要约束输入、事实版本、修改边界、验收条件、流转规则和正式生效结果；不承诺模型生成内容或主观判断完全一致。

## Load First

创建或重度修改 Skill 前，完整读取：

1. `references/personal-studio-standard.md`
2. `references/vnext-contracts.md` 中与当前 Runtime 和判断节点有关的部分

三层架构只作为思考视角，不作为强制文件结构：

- **Design**：定义能力、边界、流程和判断分工。
- **Runtime**：执行、验证、路由、提交，必要时保存与恢复。
- **Evolution**：用真实证据增加、修改或删除规则。

基础 Primitive 只保留六个：`Contract + Atomic Action + Gate + State + Loop + Commit`。按需组合，不要求每个 Skill 全部实现。

## 工作区硬规则

本 Skill 只提供可复用能力，不是任务工作区。升级其他 Skill 时，其 `SKILL.md` 必须明确写入同样的行为：

- 先识别目标项目目录，并在其中创建名称清晰的新任务文件夹。
- 所有输入引用、中间产物、状态、评审、预览、日志和最终交付物都写入该任务文件夹。
- Skill 目录只保存可复用能力，绝不承载 live task 的运行数据。
- 输入文件父目录明确就是目标项目时可以使用；无法可靠判断目标目录时再询问用户。
- 任何脚本都接收显式输出路径，不能默认写入 Skill 目录。

即使目标 Skill 当前不生成文件，也要保留这条规则，避免未来扩展后污染 Skill 目录。

## Step 0｜判断复用价值与 Runtime

把两个问题分开判断：

1. **是否值得 Skill 化**：是否存在稳定触发、输入、输出、方法或长期复用价值。一次 Prompt 能完成，也可以是轻量 Skill。
2. **需要多复杂的 Runtime**：由真实执行难度决定，不因未来可能需要而提前搭架构。

| Profile | 适用情况 | 最小运行结构 |
|---|---|---|
| R0 Single-pass | 一次生成、简单转换、规则清楚 | Input → Execute → Validate → Deliver |
| R1 Structured | 固定多步、阶段 Gate、局部修复 | Stage → Atomic Actions → Gate → Next |
| R2 Stateful | 长任务、跨窗口、外部等待、多版本、中断恢复 | Restore → Resolve → Execute → Validate → Route → Commit → Persist |

## VNext 八步创建法

### 0. 判断复用价值与 Runtime

确定是否 Skill 化、选择 R0 / R1 / R2，只启用确有用途的能力。

### 1. 建立 Task Contract

明确：

- **Objective**：最终必须完成什么。
- **Inputs**：允许依赖什么，哪个是权威事实源。
- **Deliverables**：什么结果意味着任务真正完成。
- **Invariants**：全过程不能破坏什么。
- **Authority**：谁可以修改、判断和正式批准什么。

### 2. 萃取 Experience Model

在工程化之前先确认要稳定复现的能力：

- 用户通常先检查什么；
- 哪些变量真正影响结果；
- 常见失败和“看似完成但不可用”的情况；
- 用户认可的质量、格式和执行标准；
- 已验证有效、无效和可自由变化的部分。

只保留能改变执行结果的经验。一次事故先局部修复，不直接升级为永久规则。

### 3. 设计 Stage + Atomic Graph

按任务自然边界组织阶段，再拆成原子动作、分支、循环和 Gate。R0 不强制设置多个 Stage。

每个需要明确描述的 Atomic Action 至少回答：

`Input / Action / Output / Mutation Scope / Acceptance / Failure Route`

只有实际影响执行时再加入：

`Context Scope / Tools / Autonomy / Evidence / Version Dependency`

同步识别后续执行真正需要保存的 State，不为格式完整创建空状态。

### 4. 配置 Judgment Routing

流程拆清后，再逐个处理关键 Decision Gate：

- 谁参与判断；
- 使用脚本、测试、自检、独立评审还是外部模型；
- 谁拥有最终决定权。

默认单 Agent。只有判断高度主观、路径依赖明显、下游影响大、缺少客观验证器，并且第二认知源可能改变后续行动时，才在该 Gate 启用外部模型。

外部调用必须明确：`Role / Context Policy / Decision Owner / Dependency Mode / Cognitive Budget / Material Version`。不使用“再帮我看看”这类无职责调用。

### 5. 配置 Runtime

统一主循环：

`Resolve → Context → Execute → Evaluate → Route → Commit`

R2 在两端增加 `Restore` 与 `Persist`。Route 只进入已经定义的出口，例如：

`continue / repair / retry / loop / fallback / wait / rollback / escalate / ask user / end`

只有通过 Gate 的候选结果才能 Commit 为当前生效版本。Commit 至少绑定输入版本和验证结果，防止中间产物成为错误事实源。

出现循环时定义 `Acceptance / Budget / Plateau / Best-known Result / Failure Exit`。执行到轮次上限不等于通过；无可验证改善时停止，保留已验证的最好结果。

R2 的恢复必须区分失败与 `Unknown Outcome`。工具超时或中断后先核实真实状态，确认未执行后再重试，避免重复提交。

### 6. 配置 Validation 并跑通

按任务性质组合：

- **L1 Mechanical**：文件、格式、schema、路径、脚本、测试等确定性检查。
- **L2 Semantic**：要求、事实、遗漏、修改边界等语义检查。
- **L3 Quality**：是否真正达到业务质量、是否值得进入下一阶段。

优先把 L1 交给脚本或工具。至少完成一次真实运行，或对无法实跑的流程进行可验证的端到端走查。

### 7. Evidence-driven Evolution

把任务要求、关键输入与输出、验证结果、用户修正、通过或失败原因保存在任务目录。原始聊天记录不作为默认数据集。

流程统一为：

`Evidence → Classify → Root Cause → Smallest Change → Regression → Held-out → Promote / Reject / Prune`

## 文件分层

使用最小必要结构：

```text
skill-name/
├── SKILL.md
├── references/   # 稳定方法、字段和评价规则，按需
├── scripts/      # 重复且需要确定性的动作，按需
├── config/       # 项目差异与参数模板，按需
├── assets/       # 可复用输出资源，按需
└── evals/        # 真正独立且可复用的大型评测集，少数情况
```

State、checkpoint、评审、trace 和本次输出属于任务目录。不要因为方法论里存在这些概念就在 Skill 中创建空目录。

## Autonomy

只使用三档：

| Level | 含义 | 适用情况 |
|---|---|---|
| A0 | 先询问用户 | 缺少核心输入、不可逆动作、花费、账户权限、品牌敏感终审 |
| A1 | 默认执行，关键异常再询问 | 创作、数据、文档、编码和一般工作流任务 |
| A2 | 完全执行后汇报 | 低风险格式化、转换、本地验证和脚本化重复工作 |

Autonomy 只表示是否可自主执行，不等于拥有最终业务决策权。

## 复盘与迭代

每个新建或升级的 Skill 都必须在自己的 `SKILL.md` 中包含一段短而可执行的“复盘与迭代”规则：

1. 在任务目录保存请求、关键输入与输出、验证结果、用户修正，以及通过或失败原因；不要默认收集整段原始会话。
2. 一次只改一个目标 `SKILL.md`。积累足够同类证据后，新建 evolution 任务目录；环境提供 `skillopt-sleep` 时，用 `--project <task-dir> --target-skill-path <skill>` 处理，否则在该目录手工建立候选与对照验证。
3. 先执行 `dry-run` 或等价的无改动预检；真实候选最多四条编辑，保留 held-out 集。候选只能暂存，审阅报告和候选后才允许采用，定时任务不能自动采用。
4. 同时保留接受和拒绝原因。重复、已验证的问题才变成规则；重复人工动作才脚本化；重复项目差异才配置化。
5. Evolution 必须支持 Add、Modify、Remove。用户明确要求、任务契约、权限边界和外部硬约束属于 Protected Rules，不能因近期样本无退步而删除。
6. 质量候选需要目标质量改善且关键指标无不可接受退步；Pruning 候选可以在关键质量不下降时，以 Token、延迟、调用次数或维护负担的可验证下降通过。

没有可检查质量信号时，让迭代保持休眠，并先定义未来可收集的证据。不要伪造分数或建立自动自改循环。

## 输出与验证

创建或升级 Skill 时直接编辑实际文件，并运行：

```bash
python3 /path/to/workflow-skill-builder/scripts/validate-skill.py \
  /absolute/path/to/target/SKILL.md
```

再用至少一个真实请求走查 Runtime、Gate、任务目录和最终交付路径。

优化现有 Skill 固定输出三部分：

1. 原内容问题；
2. 修改原则；
3. 已完成的最终文件。

## Avoid

- 把简单 Skill 做成 Agent 平台。
- 默认加入 State、Checkpoint、外部 LLM、多 Agent、异步评审或复杂版本管理。
- 用更多模型投票替代明确的判断职责和验证标准。
- 用固定轮数代替 Acceptance 或把预算耗尽当作通过。
- 把任务状态、评审、trace、预览和交付物写进 Skill 目录。
- 只有增加规则、不能删除规则的单向进化。
- 多层审批、企业流程语言和不改变执行的说明。
