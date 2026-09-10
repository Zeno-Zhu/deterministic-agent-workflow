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
