---
name: workflow-skill-builder
description: Use when creating, restructuring, or improving Codex skills and repeatable AI workflows for a personal studio. Turns recurring tasks, creator methods, scripts, prompts, and delivery processes into lean Skills with explicit contracts, atomic actions, validation, runtime complexity, judgment routing, recovery, evidence-driven evolution, and governed file architecture. Triggers on: create or upgrade a Skill, deterministic/agent/repeatable workflow, 确定性工作流, 工作流 skill, 可复用工作流, 文件结构/文件治理, 踩坑经验沉淀, test 代码转正, 给 skill 加 README 或技术文档, or simplifying an overbuilt process.
---

# Workflow Skill Builder VNext

把可复用能力设计成复杂度合适、能够稳定执行、**文件结构可长期维护**的 Skill。

确定性主要约束输入、事实版本、修改边界、验收条件、流转规则和正式生效结果；不承诺模型生成内容或主观判断完全一致。

## Load First

创建或重度修改 Skill 前，完整读取：

1. `references/personal-studio-standard.md`
2. `references/vnext-contracts.md` 中与当前 Runtime 和判断节点有关的部分
3. `references/file-governance.md` —— **只要产出物超过一个文件，就必须读**
4. `references/multi-platform-routing.md` —— **只要这件事有多个平台 / 多个版本能干，就必须读**
5. `references/code-engineering.md` —— **只要产出物里包含代码，就必须读**

三层架构（Design 定义能力边界与判断分工 / Runtime 执行·验证·路由·提交·恢复 / Evolution 用真实证据增删规则）
只作为思考视角，不作为强制文件结构。基础 Primitive 只保留六个：
`Contract + Atomic Action + Gate + State + Loop + Commit`，按需组合，不要求全部实现。

## 工作区硬规则

本 Skill 只提供可复用能力，不是任务工作区。升级其他 Skill 时，其 `SKILL.md` 必须明确写入同样的行为：

- 先识别目标项目目录（输入文件父目录明确就是它时可直接用），并在其中创建名称清晰的新任务文件夹；
  无法可靠判断时再询问用户。
- 所有输入引用、中间产物、状态、评审、预览、日志和最终交付物都写入该任务文件夹。
- Skill 目录只保存可复用能力，绝不承载 live task 的运行数据。
- 任何脚本都接收显式输出路径，不能默认写入 Skill 目录。

即使目标 Skill 当前不生成文件，也要保留这条规则，避免未来扩展后污染 Skill 目录。

## Step 0｜判断复用价值与 Runtime

把**三个**问题分开判断：① **是否值得 Skill 化** —— 有稳定触发 / 输入 / 输出 / 方法或长期复用价值
（一次 Prompt 能完成也可以是轻量 Skill）；② **要多复杂的 Runtime** —— 由真实执行难度决定，
**不因「未来可能需要」提前搭架构**；③ **是不是多平台 / 多版本任务** —— 是 → **拆成中控 + 渠道线**，
不要塞进一个 skill（见「多平台与多版本」节）。

| Profile | 适用情况 | 最小运行结构 |
|---|---|---|
| R0 Single-pass | 一次生成、简单转换、规则清楚 | Input → Execute → Validate → Deliver |
| R1 Structured | 固定多步、阶段 Gate、局部修复 | Stage → Atomic Actions → Gate → Next |
| R2 Stateful | 长任务、跨窗口、外部等待、多版本、中断恢复 | Restore → Resolve → Execute → Validate → Route → Commit → Persist |

## VNext 九步创建法

### 0. 判断复用价值与 Runtime

即上方「Step 0」的三问 + Profile 表：确定是否 Skill 化、选 R0 / R1 / R2，**只启用确有用途的能力**。

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

### 7. 归档文件架构

**一个 Skill 是否会长寿，取决于第 7 步，而不是前三步。**
落盘前必须给每个文件定层、给每个会长大的目录定索引。见下一节与 `references/file-governance.md`。

### 8. Evidence-driven Evolution

把任务要求、关键输入与输出、验证结果、用户修正、通过或失败原因保存在任务目录。原始聊天记录不作为默认数据集。

流程统一为：

`Evidence → Classify → Root Cause → Smallest Change → Regression → Held-out → Promote / Reject / Prune`

## 文件分层

使用最小必要结构：

```text
skill-name/
├── SKILL.md              # H｜触发 + 主流程 + Gate + 输出 + 通用避坑（唯一必读）
├── README.md             # H｜人看的定位与上手；AI 也读它的速览段
├── ARCHITECTURE.md       # W｜文件地图 + 排障定位表 + 改动影响面
├── references/           # W｜稳定方法、字段和评价规则，按需
├── scripts/              # W｜转正后的确定性动作，按需
├── config/               # W｜项目差异与参数模板，按需
├── templates/            # W｜产出物骨架，按需
├── assets/               # W｜可复用输出资源，按需
├── tests/                # C｜仍在跑的回归测试，按需
├── pitfalls/             # C｜踩坑治理：INDEX.md 是唯一默认可读项
├── logs/                 # C｜跨任务复用的运行日志，按需
└── _归档/                # D｜死稿层：禁止读取
```

State、checkpoint、评审、trace 和本次输出属于任务目录。不要因为方法论里存在这些概念就在 Skill 中创建空目录。

★ 若这件事**有多个平台 / 多个版本能干** → **不要把分支塞进上面这个骨架**，
而是拆成「中控 + N 条渠道线」（见下一节的「多平台与多版本」）。

## 文件架构与知识治理

完整规范（阈值、模板、落地清单）见 `references/file-governance.md`。落盘前必须过这五条。

### 7.1 每个文件先定层：H / W / C / D

**H** 每次必读（`SKILL.md`、README 速览段）｜**W** 触发才读（`references/`、`templates/`、`ARCHITECTURE.md`）｜**C** 默认不读，只有索引命中才读指向的那一份（`pitfalls/` 正文、`logs/`）｜**D** 禁止读（废案、旧版）。

总原则：**能被「按需读」的东西，永远不要放进「每次必读」的地方。**
推论：`SKILL.md` 的 `Load First` **只允许引用 H / W 层**；引用 C / D 层 = 结构错误。

### 7.2 会长大的目录必须有索引 + 自声明

冷存 / 死稿目录内放 `README.md`，**第一段第一句**写 `⚠ 默认不读：<什么条件下才读>`。
没有索引的冷存层等于不可用 —— AI 要么通读（烧 token），要么永远不读（等于没记）。

### 7.3 踩坑：备案 → 命中计数 → ≥3 次晋升

`pitfalls/INDEX.md` 一行一坑，**命中次数是唯一量化依据**：1–2 次**备案**（详情进 `pitfalls/PNNN-*.md`，默认不读）；≥3 次且**通用**且**可执行** → **晋升**进 `SKILL.md`；不可通用 → **降级移出 Skill**，写进项目自己的文档。

**反污染红线**：单项目 / 单次操作的经验**绝不允许**直接写进 `SKILL.md`。晋升前先做一次「换个项目还成立吗」自检，答不上来就不晋升。每晋升一条，同时找一条能删的旧条目。

### 7.4 test 毕业制

`tests/` 放开发期测试；`scripts/` 下**永远不该出现** `test_*` / `*_test.*`。
**有用 → 转正**：移到 `scripts/`，**文件名去掉 `test_` / `_test` / `try_` / `tmp_` / `skill` 等草稿标记**，改成语义化能力名（`test_parse_groups.py` → `parse_groups.py`），并在 `ARCHITECTURE.md` 登记。
**废掉 / 失败 → 直接删除**：不进 `tests/`、不进 `SKILL.md`、不进冷存。
判据：**`scripts/` 里的文件必须「产品要它」；`tests/` 里的文件必须「我还在跑它」。两个都不满足 → 删。**

### 7.5 文档三件套

`SKILL.md`（AI 执行，**永不可省**）/ `README.md`（人 + AI 速览，单文件且 ≤2400 字符时可省）/ `ARCHITECTURE.md`（后续 AI 的排障地图：文件地图 + 现象→查哪里 + 改动影响面 + 校验重建；有 `scripts/` 或 ≥2 份 `references/` 时**必须有**）。模板见 `templates/`。★ 规模口径：**文档按字符、代码按行数**（细则见 `references/file-governance.md` §7）。

## 多平台与多版本

完整规范见 `references/multi-platform-routing.md`。硬规则四条。

### 8.1 满足任一就拆成独立渠道 skill

**模型名不同 / 参数约束不同 / 计费模型不同 / 调用协议不同 / 流程步骤不同 / 资源生命周期不同 / 失败模式不同。**
**反判据（不该拆）**：只是同一协议下的参数取值不同（换分辨率、换画幅、换语气档）→ 那是 `config/`，不是新 skill。

### 8.2 结构：一个中控 + N 条渠道线（互不嵌套）

```text
skills/
├── <domain>-creation        # ★ 中控（router）：只做路由
├── <domain>-<channel-a>     # 渠道线：自包含
└── <domain>-<channel-b>     # 渠道线：自包含
```

渠道线是**独立 skill，不嵌进中控目录** —— 只有被路由到的那一条会进上下文，**其余一个字都不读**。
这就是省 token 的全部机制，也是拆分的全部理由。

### 8.3 中控只做三件事

**辨识渠道 → 只加载那一条 → 声明用了哪条。**（未点名时走默认渠道，并**显式说出**走了哪条）

**严禁内联**任何渠道的：参数上限、计费、字段名、模型名、报错特征、坑。
中控的 `Load First` **只列路由表，不列各渠道 skill**。
路由表的「子 skill」列必须是真实存在的同级 skill —— **死路由会被校验脚本判错**。

### 8.4 多版本 = 多个渠道 skill，不用 if/else

同一平台不同版本各建一个 skill（`...-jimeng20` / `...-jimeng25`），弃用版本标 `历史`、默认不被选中。
★ **加新版本 = 加一个 skill + 路由表加一行，不动任何存量 skill** —— 这是拆分最大的收益。

### 8.5 代码侧同步拆：registry / client / scheduler

```
registry（模型名、端点、鉴权、计费、上限、能力开关、失败信号）
client（每个平台一个，只认自己那套字段）
scheduler（选路 + 限流 + 重试 + 计费闸）
```

★ **业务代码里禁止出现模型名字符串**；能力查询走 registry，不写 `if 平台 == X`。
选路顺序固定：`能力是否满足 → 成本 → 可用性`（能力不满足直接淘汰，**不参与比价**）。
**协议文档按渠道分割，禁止一份文档写多个平台** —— 混装是参数串味的头号来源。

## 代码工程纪律

完整规范见 `references/code-engineering.md`（含**规则来源与明确不吸收的部分**）。
**产出物里只要包含代码，就按这六条走。**

### 9.1 先分类，再决定力度

`A` 语法报错 ｜ `B` 局部逻辑 ｜ `C` 跨文件不一致 ｜ `D` API·异步·轮询·重试·恢复 ｜
`E` 架构整理·抽公共模块 ｜ `F` 配置·项目隔离·日志体系 ｜ `G` 性能并发 ｜
`H` 结果缺失·任务与文件不一致 ｜ `I` 提示词读取与格式兼容 ｜ `J` 其他

**默认局部修复**（拼写、单个参数、单个判断、单函数返回值）。
★ **必须系统性处理**（任一命中）：数据结构 / 任务状态 / 配置格式变了 ｜ 一个问题可能波及多个文件 ｜
涉及提交·轮询·下载·重试·恢复·去重·对账 ｜ 多能力混合调度 ｜ **「提交成功但结果没落盘」** ｜
**「表面报错只是后续表现，根因在前面的状态或流程」** ｜ 提示词输出结构变更影响下游。

★ **改一个文件不等于改完** —— 必须同步调用链、常量、配置、类型、日志、测试入口。

### 9.2 复用优先，公共模块必须抽

先问已有稳定流程「**它为什么稳**」，选择顺序固定：**直接复用 → 同模式复写 → 小范围抽象 → 局部修改**。
**禁止为「更优雅 / 更统一」推翻稳定方案**；真要重构必须写明：原方案哪里不够 / 为什么抽象 /
怎么兼容旧流程 / 风险在哪。

**≥2 条流程会复用的能力必须抽公共模块**（API 调用、响应解析、JSON 清洗、下载、日志、提示词读取与填充、
状态更新、对账恢复）。★ **业务代码单文件 ≤ 300 行**（硬线 600，例外在 `ARCHITECTURE.md` 逐文件声明）；
配置与代码分离，**密钥绝不硬编码**。

### 9.3 改动边界：只碰必须碰的

★ **每一行改动都要能直接追溯到需求。** 禁止顺手「改进」相邻代码、注释、格式；禁止重构没坏的东西；
**匹配既有风格**（哪怕你更喜欢另一种）；发现无关死代码**只说、不删**；
**只清理自己这次改动造成的孤儿**（失效的 import / 变量 / 函数）。
交付前自问「这个 diff 为什么这么大」—— 答不上来的那些行就是越界。

### 9.4 任务生命周期、幂等与可续跑

涉及 API / 异步任务时**不要只有两态**：`pending → submitted → queued → running → success →
download_pending → downloaded`，以及 `failed / rejected / insufficient_balance / timeout / lost_result`。

- **失败分型，不统一重试**：仍在生成→等 ｜ 无余额→停并告知用户（**不硬重试烧钱**）｜
  审核失败→记因不重试 ｜ 网络超时→按策略重试 ｜ **提交成功但文件没落地→补查→补下载→对账**。
- ★ **幂等 + 可续跑**：重跑不得产生重复副作用（重复扣费 / 下载 / 写台账）→ 用**稳定任务指纹**做幂等键；
  第 N 步失败不得从第 1 步重来 → 状态落盘、断点继续。
- ★ **降级梯**：强模型 → 便宜模型 → 确定性默认；上一版永远**一开关之隔**；新方案先小样本 canary。
- 所有任务记 `task_id` / 项目归属 / 时间 / 状态变化 / 结果路径 / 失败原因 / **成本**；
  **重跑前先读历史记录去重**。★ **成本突增是配置问题的第一信号**，不是账单问题。
- ★ **对账是正式流程**：核 `task_id` → 核本地文件 → 没有则判
  「未完成 / 未下载 / 下载失败 / 平台无结果 / 记录丢失」。

### 9.5 版本门：提示词与模型都是部署产物

★ **提示词与模型 id 一起版本化**：提示词进版本控制、不散写代码里；**锁定精确模型 id，禁用 `latest` /
浮动别名**（上游静默升级后，报错常伪装成限流 / 余额 / 审核）；每次运行都要能回答「哪版提示词 + 哪个模型」。
★ **黄金集门**：维护一小组代表性样本 + 期望结果；**改提示词 / 模型 / 参数后必须先跑它**，
通过率退化就拦住，不许直接放量。

### 9.6 输出协议与红线

代码类任务按 **11 段**输出：需求理解 → 分类 → 局部或系统性 → 根因 → 方案 → 改动文件与影响面 →
实现 → 测试步骤 → 测试结果 → 清理说明 → 后续可优化项。**不能真跑时必须照此顺序给方案并写明缺什么。**

红线：不分类就改 ｜ 只修表面报错 ｜ 只改当前文件 ｜ **顺手改无关代码** ｜ 过度设计 ｜ 重复造轮子 ｜
★ **假装测试过** ｜ ★ **新增检查不先拿坏样本证明它会报警** ｜ 提示词散写硬编码 ｜
**浮动模型别名 / 不记版本** ｜ 输出结构变了不同步下游 ｜ 多项目日志状态交叉污染 ｜
兜底当主流程 ｜ 密钥进代码 ｜ 单文件无限膨胀。

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

1. 在任务目录保存请求、关键输入与输出、验证结果、用户修正、通过或失败原因；**不默认收集整段原始会话**。
2. 一次只改一个目标 `SKILL.md`；先跑 `dry-run` 或等价无改动预检；真实候选最多四条编辑并保留 held-out 集；
   **候选只能暂存，审阅报告和候选之后才允许采用**，定时任务不能自动采用。
3. 保留接受**与拒绝**原因。重复且已验证的问题才变规则、重复人工动作才脚本化、重复项目差异才配置化；
   **踩坑先走 §7.3 的备案 → 晋升路径**，不要一次就写成永久规则。
4. Evolution 必须支持 Add / Modify / Remove。用户明确要求、任务契约、权限边界和外部硬约束属于
   Protected Rules，不得以"近期无退步"为理由删除。质量候选要「目标质量改善且关键指标无不可接受退步」；
   Pruning 候选可在关键质量不下降时，以 Token / 延迟 / 调用次数 / 维护负担的可验证下降通过。

没有可检查质量信号时，让迭代保持休眠，并先定义未来可收集的证据。不要伪造分数或建立自动自改循环。

## 输出与验证

创建或升级 Skill 时直接编辑实际文件，并运行：

```bash
python3 /path/to/workflow-skill-builder/scripts/validate-skill.py \
  /absolute/path/to/target/SKILL.md
```

脚本查四组共 18 项：frontmatter、工作区隔离、受控迭代，以及**治理组 4.1–4.14**
（草稿残留、运行产物、未毕业 test、草稿命名、tests 登记、冷存层自声明、索引缺失、
Load First 引用冷存层、文档三件套、读取预算、路由死路由、内联渠道参数、
**scripts 单文件行数、硬编码密钥**）。

★ **只对自身 `PASS` 不能证明检查有效**（把检查删了也会 PASS）：改过校验规则就必须
再跑 `tests/test_validator_negative.py`，确认 20 项反面断言仍然真的会报错。

再用至少一个真实请求走查 Runtime、Gate、任务目录和最终交付路径。

优化现有 Skill 固定输出三部分：

1. 原内容问题；
2. 修改原则；
3. 已完成的最终文件。

## Avoid

- 把简单 Skill 做成 Agent 平台；默认加入 State、Checkpoint、外部 LLM、多 Agent、异步评审或复杂版本管理。
- 用更多模型投票替代明确的判断职责和验证标准。
- 用固定轮数代替 Acceptance 或把预算耗尽当作通过。
- 把任务状态、评审、trace、预览和交付物写进 Skill 目录。
- 只有增加规则、不能删除规则的单向进化。
- 多层审批、企业流程语言和不改变执行的说明。
- **把踩坑故事、日志原文、测试残留、失败实验写进 `SKILL.md`** —— 它们是 token 黑洞。
- **为结构完整建空目录**（结构只在实际有东西要放时才长出来）；**用 `.bak` / `_v2` / `_final` / `副本` 管版本**（交给 git）。
- **顺手改与需求无关的代码** —— 出事后没人能定位（见「代码工程纪律」9.3）。
