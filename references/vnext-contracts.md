# VNext Contracts

仅在对应能力真实存在时使用本文件中的模板。删除不影响执行的字段，不创建空结构。

## 目录

1. Runtime 选择
2. Task Contract
3. Stage Contract
4. Atomic Action Contract
5. Gate 与 Judgment Routing
6. External Cognition Contract
7. Loop Contract
8. State、Commit 与 Recovery
9. Validation Design
10. Evolution Gate
11. Skill 文件治理契约
12. 主线与渠道差异层契约
13. 代码工程纪律契约
14. 校验器的逐字措辞要求

## 1. Runtime 选择

按实际运行风险选择最低可用等级。

### 选择 R0

- 单次执行即可交付；
- 不需要跨阶段保存进度；
- 失败可以安全重做；
- 没有异步等待和版本竞争。

### 升级到 R1

出现以下任一情况时考虑：

- 固定多步且中间结果会影响下一步；
- 阶段间需要 Gate；
- 存在有限的局部修复循环；
- 不同分支会产生不同后续动作。

### 升级到 R2

出现以下任一情况时考虑：

- 跨窗口、跨天或中断后恢复；
- 外部任务需要等待或轮询；
- 多个候选并存且必须区分生效版本；
- 工具超时后结果可能未知；
- 重复执行可能造成重复提交或不可逆影响；
- 多个并行分支需要汇合。

## 2. Task Contract

```markdown
## Task Contract

- Objective: <最终必须完成的结果>
- Authoritative Inputs: <允许依赖的材料及事实优先级>
- Deliverables: <完成时必须存在的成果>
- Invariants: <全过程不能破坏的条件>
- Authority:
  - Primary: <允许执行和决定的范围>
  - External: <如有，允许评审或决定的范围>
  - User: <必须由用户决定的事项>
- Workspace: <项目目录与新任务文件夹规则>
- Completion: <整个任务完成条件>
```

Authority 与 Autonomy 分开。某个参与者可以自主执行，不代表它拥有业务终审权。

## 3. Stage Contract

多阶段任务按自然边界定义，不为 R0 强行增加 Stage。

```markdown
## Stage: <名称>

- Goal: <本阶段目标>
- Inputs: <阶段输入>
- Boundaries: <本阶段允许看到、修改和决定什么>
- Capabilities: <可用工具、脚本、模型或人员>
- Key Decisions: <需要经过 Gate 的判断>
- Exit: <进入下一阶段的条件>
```

Stage 负责边界与退出，Atomic Action 负责具体动作。

## 4. Atomic Action Contract

### 核心字段

```markdown
### Atomic Action: <名称>

- Input: <当前动作需要的输入>
- Action: <只描述一个可完成动作>
- Output: <产生或更新什么>
- Mutation Scope: <最多允许改变什么>
- Acceptance: <结果合格的可检查条件>
- Failure Route: <retry / repair / fallback / rollback / escalate / ask user / skip / abort>
```

### 按需字段

```markdown
- Context Scope: <本步允许装配的最小上下文>
- Tools: <允许调用的能力>
- Autonomy: <A0 / A1 / A2>
- Evidence: <保留什么评价证据>
- Version Dependency: <本动作依赖哪个输入或候选版本>
```

Mutation Scope 控制影响半径。Acceptance 区分“动作完成”和“结果合格”。Failure Route 必须指向一个真实出口，不能只写“检查失败”。

## 5. Gate 与 Judgment Routing

### Gate Contract

```markdown
### Gate: <名称>

- Subject: <正在判断的候选或状态>
- Criteria: <通过标准>
- Evidence: <依据什么事实或验证结果>
- Judge: <脚本 / Primary / External / User>
- Decision Owner: <谁拥有最终决定权>
- Pass Route: <通过后去哪>
- Fail Route: <失败后去哪>
```

### 判断路由顺序

1. 能否由文件、schema、脚本、编译、测试或 API 结果决定？
2. 若需要语义判断，Primary 按明确标准自检是否足够？
3. 第二认知源能否显著降低路径依赖或补充真实能力？
4. 该判断对下游的影响是否值得额外 Token、延迟和协调成本？
5. 最终决定权属于谁？

只有第 3、4 项都有明确肯定答案时，才启用 External Cognition。

## 6. External Cognition Contract

```markdown
### External Cognition: <Gate 名称>

- Trigger: <何时调用>
- Role: <Challenger / Evaluator / Alternative Generator / Specialist>
- Context Policy: <提供哪些共同事实、成果、标准与历史决定>
- Decision Owner: <Primary / External / User / Eval>
- Dependency Mode: <Optional Consultation / Required Review / Deferred Async Review>
- Cognitive Budget:
  - Max Calls: <总调用次数>
  - Max Rounds: <该 Gate 的讨论轮次>
  - Max Wait: <允许等待时间，如适用>
  - Repeat Same Model: <yes/no>
- Material Version: <意见绑定的材料版本>
- Fallback: <不可用、超时或冲突时的处理>
- Acceptance: <外部意见如何改变或不改变后续行动>
```

### Role 对应上下文

| Role | 应提供 | 可省略 |
|---|---|---|
| Challenger / Alternative Generator | 原始事实、目标、约束、评价标准 | 第一轮的 Primary 结论和自我辩护 |
| Evaluator | 当前成果、权威材料、验收标准 | 与验收无关的过程讨论 |
| Specialist | 专业判断所需材料、接口和限制 | 无关项目历史 |
| 持续讨论 | 已确认决定、当前分歧、变化事实、最新版本 | 已失效旧版本全文 |

Dependency Mode：

- **Optional Consultation**：失败后按预设替代方式继续。
- **Required Review**：未取得评审前，相关候选不能 Commit；其他独立工作可以继续。
- **Deferred Async Review**：先推进独立工作；返回后先核对材料版本，再决定是否采用。

外部意见不同只是新信息，不自动等于质量更高。

## 7. Loop Contract

```markdown
### Loop: <名称>

- Goal: <循环要解决的问题>
- Entry: <进入条件>
- Body: <循环内的 Atomic Actions>
- Evaluator: <谁或什么负责评价>
- Acceptance: <退出并通过的条件>
- Budget: <最大轮次、调用或成本>
- Progress Check: <怎样判断有可验证改善，质量循环必填>
- Plateau: <怎样判断继续已无收益，质量循环必填>
- Best-known Result: <如何保留最好候选，质量循环必填>
- Failure Exit: <预算耗尽、不可修复或无收益时去哪>
```

```text
Execute → Evaluate → Pass?
                     ├─ Yes → Commit / Continue
                     └─ No  → Repairable?
                              ├─ Yes → Repair → Evaluate
                              └─ No  → Fallback / Escalate / End
```

Budget 是保险，不是验收条件。达到 Acceptance 立即退出；Plateau 触发时保留最好结果并停止优化。

## 8. State、Commit 与 Recovery

### 最小 State

R2 只保存继续执行需要的字段：

```json
{
  "task_status": "running",
  "current_stage": "stage-id",
  "current_step": "step-id",
  "authoritative_inputs": [],
  "current_accepted_output": null,
  "open_issues": [],
  "pending_dependencies": [],
  "decisions": [],
  "attempt_count": {},
  "last_safe_checkpoint": null
}
```

不要复制全部聊天记录。State 文件属于任务目录。

### Commit

只需区分：

- `Working / Candidate`
- `Current Accepted`
- `History`

Commit 最少记录：

```markdown
- Accepted Output: <路径或标识>
- Input Version: <对应输入版本>
- Acceptance Evidence: <验证结果>
- Decision: <关键判断及负责人>
- Committed At: <时间或顺序标识>
```

### Recovery

```markdown
## Recovery

- Last Safe Checkpoint: <最后安全位置>
- Uncommitted Work: <尚未生效的候选>
- Resume Point: <从哪里继续>
- Retry Policy: <何时可重试及次数>
- Rollback Target: <回退位置>
- Pending Dependency: <仍在等待什么及其版本>
- Outcome Status: <success / failed / unknown>
```

当 Outcome 为 `unknown`：

```text
核实外部真实状态 → 已成功则同步 State → 确认未执行才 Retry → 仍未知则等待或升级
```

## 9. Validation Design

```markdown
## Validation

- L1 Mechanical: <脚本、schema、测试或文件检查>
- L2 Semantic: <要求、事实、遗漏、边界检查>
- L3 Quality: <业务质量和候选选择，仅在需要时>
- Gate Owner: <谁根据验证结果决定流转>
- Evidence Output: <验证结果写入任务目录的位置>
```

优先把可机械判断的内容移出 LLM。主观评分器本身也需要用真实案例校准，不能因为是独立模型就默认可靠。

## 10. Evolution Gate

### Quality Improvement

```markdown
- Target Metric: <需要改善的质量>
- Regression Set: <历史失败和成功样本>
- Held-out Set: <未用于修改的样本>
- Pass: <目标质量改善，关键质量无不可接受退步>
```

### Simplification / Pruning

```markdown
- Candidate Rule: <准备删除或简化的经验性规则>
- Protected Check: <确认不是用户约束、契约、权限或外部硬约束>
- Regression Set: <历史依赖该规则的样本>
- Held-out Set: <未用于修改的样本>
- Quality Floor: <关键质量不得下降>
- Cost Metric: <Token、延迟、调用、维护或结构复杂度>
- Pass: <质量达标且成本指标真实改善>
```

不能删除 Protected Rules。没有可检查信号时，不运行自动进化。

## 11. Skill 文件治理契约

完整规则见 `references/file-governance.md`。新建或升级 Skill 时，至少填这张表并写进目标 Skill 的 `ARCHITECTURE.md`：

> ★ 规模口径：**只有代码按行数，文档字数不设门槛（2026-10-02 起）**。
> `SKILL.md` / `references/` / README / ARCHITECTURE 的字符数与行数**只进 INFO 行、
> 不判不提示**；唯一的规模门槛是 `scripts/` 单文件行数（细则见 `file-governance.md` §7）。

```markdown
## 文件治理

- 分层：<每个目录属于 H / W / C / D 哪一层>
- 冷存索引：<pitfalls/INDEX.md、logs/README.md 等索引文件位置；无则写 none>
- 默认不读声明：<哪些目录含 `⚠ 默认不读` 自声明 README>
- 测试归属：tests/ 放什么；scripts/ 里有没有未毕业的 test（必须为 none）
- 日志归属：任务目录 or Skill 目录；保留策略
- 文档三件套：SKILL.md（必）/ README.md（有 / 省，原因）/ ARCHITECTURE.md（有 / 省，原因）
- 文档分层：<SKILL.md 只放触发 + 主干 + Gate + 硬规则；细节下沉到哪些 references/ —— ★ 文档字数不设门槛，此处不填数字>
- 重构触发器：<当前是否已接近 §7 任一阈值；代码阈值才有数字>
```

### 踩坑条目契约

`pitfalls/INDEX.md` 的每一行对应一条坑：

```markdown
| ID | 一句话现象 | 命中 | 处置 | 详情 | 通用化 |
|---|---|---|---|---|---|
```

- `命中`：同一坑再次出现就 +1，是唯一的量化依据。
- `处置`：`备案`（1–2 次）/ `已晋升`（≥3 次且通用且可执行）/ `降级`（不可通用 → 移出 Skill）。
- `通用化`：`✅ 一类操作` / `❌ 项目或本机专属`。
- 晋升三条件必须**同时**满足：频次 ≥3、通用、可执行。**单项目 / 单次经验禁止进 `SKILL.md`。**

### 冷存层访问契约

```markdown
### Cold Store Access: <目录名>

- Index: <索引文件路径>
- Read Trigger: <AI 在什么条件下才允许读正文>
- Read Scope: <只读索引命中的那一份，还是允许通读（通读=设计失败）>
- Declared In: <该目录的自声明 README 路径>
- Never Read By: <SKILL.md 的 Load First 明确不引用本目录>
```

## 12. 主线与渠道差异层契约

完整规则见 `references/multi-platform-routing.md`。
**多平台 / 多版本任务必须填两类契约：主线一份、每个渠道差异层一份。**

### 12.1 主线契约（Mainline）

```markdown
## Mainline Contract

- Domain: <这个域是什么>
- Version: <主线版本标记；改版递增，供差异层锚定>
- Full Flow: <全流程阶段清单：阶段名 → 产出物 → 闸门>
- Fork Points: <哪些阶段会因渠道而异（每处对应一段分叉声明）>
- Default Channel: <未点名时走哪条>
- Declare On Use: yes｜未点名时必须显式声明走了哪条
- Routing Table: <references/routing-table.md 路径>
- Load Policy: <只加载被路由到的那一条差异层，其余不读>
- Forbidden In This Skill:
  - <渠道> 的参数上限 / 计费 / 字段名 / 模型名 / 报错特征 / 坑
  - 各差异层 skill 的引用写进 Load First
- Channels: <渠道 A → 差异层 skill 名；渠道 B → 差异层 skill 名；…>
- Switch Checklist: <换渠道时读哪个协议 + 加载哪个差异层>
- Reconciliation: <主线改版后如何逐条对账差异层>
```

### 12.2 渠道差异层契约（Channel Overlay）

```markdown
## Channel Overlay Contract

- Channel: <渠道名>
- Skill Name: <domain>-<channel>
- Anchored To: <锚定主线版本 —— 必填；与主线当前版本不一致 = 待对账>
- Status: active / legacy（legacy 默认不被主线选中）
- Deltas: <按主线阶段逐个列；每项标类型；与主线相同的阶段**不列**>
  - Phase N：<append 追加了什么 / replace 替换了什么 / forbid 禁止了什么>
- Identity: <模型标识逐字符照抄 / 端点 / 鉴权>
- Hard Limits: <参考图上限 / 时长 / 画幅 / 音频 / 必填字段 / 资源 TTL>
- Billing: <model + unit price + 一次典型任务成本 + 提交前成本闸怎么算>
- Failure Signals: <信号 → 真/假 → 处置>
- Own Pitfalls: <只记本渠道的；跨渠道共性归主线或域级 skill>
- No Cross-Reference: <确认没有引用其他渠道的结论；引用主线是允许且必须的>
- No Restatement: <确认没有复述主线的阶段 / 闸门 / 交付规范>
```

### 12.3 拆分判据

```markdown
## Split Decision

- 模型名不同：<是 / 否>
- 参数约束不同：<是 / 否>
- 计费模型不同：<是 / 否>
- 调用协议不同：<是 / 否>
- 流程步骤不同：<是 / 否>
- 资源生命周期不同：<是 / 否>
- 失败模式不同：<是 / 否>
⇒ <任一为「是」→ 拆成渠道 skill；全为「否」→ 应做成 config/，不是新 skill>
```

### 12.4 代码侧 API 契约

```markdown
## API Hub Contract

- Registry: <平台/版本一行：模型名、端点、鉴权、计费、上限、能力开关、失败信号>
- Clients: <每个平台一个 client 的文件名>
- Scheduler: <选路 + 限流 + 重试 + 计费闸的实现位置>
- Routing Order: capability → cost → availability（固定，勿改序）
- Model Name Policy: <确认业务代码里没有模型名字符串>
- Cost Gate: <提交前如何算预估成本；算不出时的行为>
- Docs Split: <一渠道一份协议文档的路径清单>
```

## 13. 代码工程纪律契约

完整规则见 `references/code-engineering.md`。
**产出物里只要包含代码，就要填这四张表，并把结论写进目标 Skill 的 `ARCHITECTURE.md`。**

### 13.1 分层与规模契约

```markdown
## Code Layout

- Layers: <路由接口层 / 业务流程层 / 第三方调用层 / 数据结构层 / 提示词层 / 日志层 / 配置层 / 工具层，各自放哪>
- Shared Modules: <≥2 条流程会复用的能力抽到了哪几个模块>
- Single-File Limit: 300 行（软）/ 600 行（硬）
- Declared Exceptions: 单文件行数例外：<相对路径> —— <理由>；无则 none
- Config Split: <路径 / 模型名 / 端点 / 并发 / 轮询间隔 / 下载目录 / 日志级别 是否已配置化>
- Secret Policy: <敏感配置走环境变量或独立配置文件；确认业务代码里没有密钥字面量>
```

### 13.2 问题处理契约

```markdown
## Issue Triage

- Class: <A–J，可多选>
- Scope: 局部修复 / 系统性处理
- Reason: <为什么是这个力度；系统性时列出受影响文件、调用链、状态>
- Root Cause: <多维度根因；禁止只写表面报错>
- Synced: <同步改了哪些调用方 / 常量 / 配置 / 类型 / 日志 / 测试入口>
```

### 13.3 任务生命周期契约

```markdown
## Task Lifecycle

- States: <pending→submitted→queued→running→success→download_pending→downloaded；失败态清单>
- Ledger: <task_id / 项目归属 / 提交时间 / 状态变化 / 结果路径 / 失败原因的落盘位置>
- Failure Routing: <仍在生成 / 无余额 / 审核失败 / 网络超时 / 提交成功未落盘 各自的处置>
- Rerun Guard: <重跑前如何读历史记录去重，防跨项目交叉污染>
- Reconcile: <对账入口；无文件时的五态判定：未完成 / 未下载 / 下载失败 / 平台无结果 / 记录丢失>
```

### 13.4 输出协议

```markdown
## Output Protocol

代码类任务按 11 段输出：需求理解 → 问题分类 → 局部或系统性 → 根因 → 方案 →
改动文件与影响面 → 代码实现 → 测试步骤 → 测试结果 → 清理说明 → 后续可优化项。
不能真跑时必须照此顺序给出分析与实施方案，并写明缺的环境 / 依赖 / 密钥 / 权限。
```

### 13.5 改动边界契约

```markdown
## Change Boundary

- Scope: <本次只改这些文件 / 这些函数>
- Trace: <每一处改动对应的需求点；出现无法归属的改动 = 越界>
- Untouched: <明确不碰的相邻代码、格式、历史死代码（发现只说、不删）>
- Orphans: <本次改动造成的孤儿（失效 import / 变量），只清这些>
- Rollback Test: <单独回滚本次 diff 后，行为应恰好回到改动前>
```

### 13.6 版本门契约（产出物含模型 / 提示词时必填）

```markdown
## Version Gate

- Prompt Version: <提示词路径 + 版本 / 提交号>
- Model Id: <精确 id；确认没有 latest 或浮动别名>
- Params Snapshot: <关键参数快照路径>
- Golden Set: <黄金集文件路径 + 条数；覆盖正常 / 边界 / 已知易错>
- Golden Result: <通过率；与上一版的对比>
- Rollback: <上一版怎么一键切回>
- Canary: <先跑哪一个小样本；通过判据是什么>
```


---

## 14. 校验器的逐字措辞要求

`scripts/validate-skill.py` 的**组 2（工作区隔离）与组 3（受控迭代）是"逐字短语匹配"，不是语义判断**。
关键词不对就是 ERROR，哪怕意思写到了。落地前先读 `scripts/wfsb_check/checks_core.py` 拿准措辞，
比改一版跑一次快得多。常驻六条：

| 检查项 | `SKILL.md` 正文里必须出现的话 |
|---|---|
| 目标项目中的新任务文件夹 | 「目标项目」+「**新**…**任务文件夹**」（`目标项目…新的任务文件夹`） |
| 任务产物不得写入 Skill 目录 | 「绝不」+「写入」+「Skill 目录」 |
| 脚本使用显式输出路径 | 「脚本」+「显式输出路径」 |
| 复盘与迭代规则 | 一个标题就叫「**复盘与迭代**」的小节 |
| 暂存后审阅再采用 | 「候选…暂存…审阅…采用」这一整句 |
| held-out / dry-run（仅 WARN） | 正文出现 `held-out` 或 `留出`；出现 `dry-run` |

**另外三条最容易踩的结构坑**：

1. **`_` 前缀的目录**（如 `templates/_build/`）会被 `is_cold_dir()` 判成**死稿层**，
   于是要求它带一份第一句写「默认不读」的自声明 README —— 否则算结构错误。
   ⇒ **调试产物、构建中间件不要放在 skill 里**；工具一旦转正就搬进 `scripts/` 并去掉 `_`。
2. `scripts/` 下出现 `test_*` / `*_test.*` / `try_*` / `tmp_*` 一律判**未毕业 test**，直接 ERROR。
3. 文档里的示例命令写 `python3`；**Windows 上要换成实际解释器的完整路径**，否则照抄跑不通。
