# Personal Studio Workflow Standard VNext

## 目标

把重复工作变成稳定能力，同时保持个人工作室的流程轻、短、可维护。

确定性约束执行过程：输入与事实源、修改范围、验收条件、流转规则、失败出口和生效版本必须明确。模型内容和主观判断仍可能变化，因此需要按风险配置验证方式。

## 三个设计维度

不要把所有复杂度压成一条“简单到高级”的轴线。分别判断：

| 维度 | 核心问题 | 决定什么 |
|---|---|---|
| 能力设计 | 要稳定复现什么经验与判断？ | Task Contract、Experience Model、references |
| 执行复杂度 | 一次任务如何运行、等待、恢复？ | R0 / R1 / R2 与 Runtime |
| 认知复杂度 | 哪些节点需要谁判断？ | Validator、自检、外部模型、用户决策 |

Design、Runtime、Evolution 是方法论视角。它们不要求三个文件夹，也不要求每个 Skill 实现全部机制。

## 基线模板

设计新 Skill 时先回答：

| Item | Decision |
|---|---|
| Reuse value | 为什么值得封装为 Skill？ |
| Runtime | R0、R1 还是 R2？ |
| Objective | 最终必须完成什么？ |
| Inputs | 需要什么，哪个是权威事实源？ |
| Deliverables | 哪些成果意味着真正完成？ |
| Invariants | 全程不能破坏什么？ |
| Authority | 谁能执行、修改和最终决定什么？ |
| Workspace | 哪个项目目录承载新的任务文件夹？ |
| Experience | 要稳定复现哪些业务经验和质量判断？ |
| Must-not-fail | 哪些失败会让结果不可用？ |
| Flexible parts | 哪些部分允许变化？ |
| Validation | L1 / L2 / L3 如何组合？ |
| Evidence | 哪些结果与修正支持未来迭代？ |

## Runtime Profile

### R0｜Single-pass

用于一次生成、简单转换和确定规则执行。

```text
Input → Execute → Validate → Deliver
```

不建立持久 State、Checkpoint 或复杂循环。

### R1｜Structured Workflow

用于固定多步、阶段 Gate 和局部修复。

```text
Stage → Atomic Actions → Gate → Next Stage
```

可以有局部循环，一般不需要跨会话恢复。

### R2｜Stateful Agent Workflow

用于长任务、多阶段、多工具、跨窗口、外部等待、多版本候选和中断恢复。

```text
Restore → Resolve → Context → Execute → Validate → Route → Commit → Persist
```

正式定义 State、Checkpoint、Version Binding、Commit、Recovery 和 Unknown Outcome。

Skill 是否存在由复用价值决定，Runtime 有多复杂由任务复杂度决定。

## Experience Model

工作流首先要复现正确的能力，再考虑工程结构。优先提取：

- 用户先看什么，再看什么；
- 哪些变量真正改变结论或成品；
- 常见失败、返工和假完成；
- 用户认可的质量阈值；
- 已验证的有效做法与无效做法；
- 哪些格式、字段和顺序必须稳定；
- 哪些内容允许模型自由发挥。

经验进入系统的条件是重复出现、能够改变执行结果。一次失败先局部修复并记录证据。

## 六个 Primitive

### Contract

定义任务、输入、交付、边界、权限与不变量。

### Atomic Action

执行一个边界明确、可完成、可检查的动作。

### Gate

根据验收条件决定继续、修复、等待、返回、升级或终止。

### State

保存未来恢复和继续执行真正需要知道的当前事实。聊天记录不能成为 R2 的唯一状态。

### Loop

在明确目标、评价方式、进展判断和退出条件下重复动作。

### Commit

把通过 Gate 的候选结果升级为当前生效版本，并绑定输入版本与验证证据。

## Judgment Routing

流程拆解完成后，对关键 Decision Gate 分别确定：

1. 谁参与判断；
2. 如何验证；
3. 谁拥有最终决定权。

优先级不是固定流水线。客观检查优先使用脚本、schema、测试、文件系统或 API 结果。标准明确且风险中等时可以由 Primary 自检。只有第二认知源可能显著改变高主观、高杠杆、低可验证节点的行动时，才启用外部模型。

外部模型必须绑定具体 Gate，说明职责、上下文、决策权、依赖模式、预算和材料版本。外部意见若针对旧版本，不能直接修改最新成果。

## 文件边界

### Skill 目录

只保存可复用能力。**完整骨架与 H/W/C/D 分层见 `references/file-governance.md` §1–§2**，此处不复述。
一句话：`SKILL.md` + `README.md` + `ARCHITECTURE.md` + `references/` + `scripts/` + `config/` + `templates/` + `assets/`
＋ 冷存层（`tests/`、`pitfalls/`、`logs/`）＋ 死稿层（`_归档/`），按需创建，**禁止为结构完整建空目录**。

### 多平台时的边界

同一件事有多个平台 / 版本能干时，**不把它们塞进一个 Skill**，也**不把全流程抄 N 遍**：
拆成「**一条主线 + N 个渠道差异层**」—— 每条差异层是**独立 Skill**，只写"相对主线不同在哪"；

- **主线承载全流程**（阶段 / 产出物 / 闸门 / 交付规范），**不内联任何渠道的参数、计费、字段名、模型名、报错特征**；
- ★ 主线**不得被掏空成"只做路由"**（那会把共性推给渠道，造成流程漂移）；
- ★ 差异层**不得复述主线**，且**必须声明锚定的主线版本**，供主线改版后对账。

判据与调度纪律见 `references/multi-platform-routing.md`。
一句话判据：模型名 / 参数约束 / 计费 / 协议 / 流程 / 资源生命周期 / 失败模式 —— **任一不同就拆**。
反判据：只是**流程骨架一样**（要做的事相同）→ 不是拆分理由，骨架本就该在主线里共用。

### Task 目录

本次任务产生的内容全部放入新任务文件夹：输入引用、候选成果、状态、评审、checkpoint、运行证据、预览、日志和最终交付物。

是否创建 `state/`、`reviews/`、`evidence/`、`outputs/` 由任务复杂度决定。禁止为了结构完整创建空目录。

## 每个产出 Skill 的强制工作区规则

Builder 必须把以下行为写入每个新建或升级 Skill 的核心说明，不能只留在本 Builder 或参考文件中：

- Skill 只提供可复用能力，不是任务工作区。
- 每次任务先定位目标项目目录，并在其中创建新的任务文件夹。
- 所有中间和最终产物都进入任务文件夹。
- Skill 目录不能接收任务输出、临时文件、预览、日志、草稿、状态或交付物。
- 脚本必须接收显式输出路径，不能默认写入 Skill 目录。
- 输入文件父目录明确是项目目录时可以直接使用；无法可靠判断时询问用户。

这条规则同样适用于当前不创建文件的 Skill。

## 内容归属

| 内容 | 位置 |
|---|---|
| 触发意图、短流程、默认行为、关键边界、停止条件 | `SKILL.md` |
| 稳定方法、字段定义、质量标准、示例 | `references/` |
| 重复解析、转换、验证、渲染、提取和格式化 | `scripts/` |
| 路径、字段映射、阈值、平台选项、风格变量 | `config/` |
| 当前状态、候选、评审、trace、checkpoint、交付物 | Task 目录 |

## Validation

验证按需组合，不是固定三步：

| Level | 检查内容 | 首选执行者 |
|---|---|---|
| L1 Mechanical | 文件、格式、字段、schema、路径、脚本、测试 | 脚本或工具 |
| L2 Semantic | 任务要求、事实、遗漏、修改边界 | Primary、独立 Validator 或外部模型 |
| L3 Quality | 业务质量、候选优劣、阶段准入 | 明确的评价者或用户 |

不同任务的最小验证：

| Workflow Type | Necessary Validation |
|---|---|
| 创作、提示词、剧本 | 结构、语气、完整性、用户约束，必要时 L3 |
| 文档与交付物 | 文件检查；版式重要时渲染或预览 |
| 数据处理 | 行数、必填字段、解析错误、输出格式 |
| 编码工作流 | 现有测试或最小相关命令 |
| Skill 创建 | frontmatter、工作区规则、迭代边界、真实请求走查 |

## Runtime 与恢复

所有工作流都执行 `Resolve → Context → Execute → Evaluate → Route → Commit` 的最小语义；R0 可以把它压缩成单次步骤。

只在有真实需要时加入 Loop、State、Checkpoint 与 Recovery：

- Loop 必须有 Acceptance、Budget、Plateau、Best-known Result 和 Failure Exit。
- State 只保存继续执行需要的事实，不复制全部对话。
- Commit 区分 working/candidate、current accepted、history。
- Recovery 记录 last safe checkpoint、uncommitted work、resume point、retry policy、rollback target 和 pending dependency。
- 超时、中断等 Unknown Outcome 先核实真实状态，确认未执行后再重试。

可靠恢复优先由脚本、执行环境或持久化系统承担，不能只依赖自然语言提醒。

## 询问用户的边界

只在继续执行很可能做错时询问：

- 核心输入缺失；
- 用户意图与文件冲突；
- 付费、公开、不可逆或账户级动作；
- 品牌敏感终审；
- 两条合理路线会产生明显不同的交付物。

小缺口做清晰假设并继续。外部模型参与不改变用户权限边界。

## 进化与删减

一次只优化一个 Skill。每次任务保留可比较证据，而不是记录一切。

```text
Observe → Classify → Root Cause → Smallest Change
        → Regression → Held-out → Promote / Reject / Prune
```

规则分两类：

- **Protected Rules**：用户明确要求、Task Contract、权限边界、数据格式契约和外部硬约束，不能根据短期样本自动删除。
- **Empirical Rules**：来自历史经验与失败修复，可以通过回归和 held-out 评价尝试修改或删除。

采用门禁分两类：

- **Quality Improvement**：目标质量显著改善，关键质量没有不可接受退步。
- **Simplification / Pruning**：关键质量不下降，且 Token、耗时、调用次数、维护负担或结构复杂度确实下降。

`skillopt-sleep` 是环境可用且有足够证据时启用的实现工具，不是每次任务的强制运行层。真实候选保持最多四条编辑，`run` 只暂存，人工审阅后才 `adopt`。环境未提供该工具时，在独立 evolution 任务目录手工执行同样的候选、回归、held-out 和明确采用边界。

## 最终审查六问

1. **能力**：是否提炼出真正值得复用的经验？
2. **权威**：哪些事实、版本和决定正在生效？
3. **边界**：每一步允许看到、修改和决定什么？
4. **流转**：什么条件继续、循环、返回、等待或终止？
5. **判断**：谁应该判断，第二认知源是否真的值得？
6. **进化**：什么证据支持增加、修改或删除规则？

## 常见删减目标

删除或避免：

- 模型已经知道的定义；
- 不改变执行的抽象说明；
- 为未来可能性建立的脚手架；
- 没有读者的日志和报告；
- 重复示例与重复规则；
- 外部模型委员会式投票；
- 固定轮数即通过；
- 复杂 Runtime 的空目录和占位状态。
