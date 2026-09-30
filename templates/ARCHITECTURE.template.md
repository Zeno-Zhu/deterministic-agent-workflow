# ARCHITECTURE — <skill-name>

> 后续 AI 的**排障地图**。只在出问题、要改造、要交接时读 —— **不要放进 `SKILL.md` 的 Load First**。
> 写好这份文件的标准是：**一个从没看过这个 skill 的 AI，读完能在 1 分钟内定位到该改哪个文件。**

## 1. 文件地图

| 路径 | 层 | 是什么 | 权威性 | AI 读取策略 |
|---|---|---|---|---|
| `SKILL.md` | H | 触发、主流程、Gate | **唯一权威**的流程说明 | 每次必读 |
| `README.md` | H | 人的定位与上手 | 说明性 | 初识时读 |
| `ARCHITECTURE.md` | W | 本文件 | 结构说明 | 排障时读 |
| `references/<x>.md` | W | <主题> | 该主题**唯一权威** | 触发时读 |
| `scripts/<x>` | W | <能力> | 实现权威 | 按步骤调用 |
| `tests/<x>` | C | <回归对象> | - | 不读 |
| `pitfalls/INDEX.md` | C | 踩坑索引 | 坑的唯一入口 | 只在匹配现象时读 |
| `logs/` | C | 运行日志 | - | 默认不读 |

> 一句话原则：**同一件事只有一个权威文件。** 出现两个说法就先合并，别让 AI 猜。

## 2. 现象 → 查哪里

| 现象 | 先看 | 常见根因 |
|---|---|---|
| 触发不了（AI 不用它） | `SKILL.md` frontmatter 的 `description` | 触发词没覆盖用户的实际说法 |
| 流程走到一半错了 | `SKILL.md` 对应 Stage 的 Gate | Gate 的 Acceptance 写的是"完成"而不是"合格" |
| 输出格式/字段不对 | `references/<字段规范>` | 规范与脚本实现不一致 |
| 脚本报错 | `scripts/<x>` 的入参与 `ARCHITECTURE.md` §3 | 输出路径没显式传 |
| 输出落到了 skill 目录里 | `SKILL.md` 工作区硬规则 | 脚本默认写了相对路径 |
| 同一现象反复出现 | `pitfalls/INDEX.md` | 该坑命中 ≥3 次但没晋升 |
| 每次都要读一堆废话 | `references/file-governance.md` §7 | 没做分层，冷存混进了 H/W |
| 校验报「scripts/ 下 … 超过硬线 600 行」 | `scripts/` 对应文件的职责边界 | 没按职责拆模块（`code-engineering.md` §3） |
| 校验报「疑似硬编码密钥」 | `scripts/` 里被点名的行 | 敏感配置没走环境变量或独立配置文件 |
| 「提交成功但结果没落盘」 | 任务生命周期与对账实现 | 缺状态机 / 对账流程（`code-engineering.md` §6） |

## 3. 改动影响面

| 改这个 | 必须同步改 |
|---|---|
| `SKILL.md` 的流程 | 对应 `references/` 方法段、`README.md` 的 30 秒上手 |
| `scripts/` 的入参或输出字段 | `references/` 字段规范、`ARCHITECTURE.md` §1 与 §4 |
| 目录结构 | `ARCHITECTURE.md` §1、`README.md` 目录导航、本 skill 的 `Load First` |
| 新增 `references/` | `SKILL.md` 的 Load First 或触发条件 |

## 4. 校验与重建

```bash
# 自检（唯一入口）
<command>

# 从零重建产物
<command>
```

## 5. 文件治理

照 `references/vnext-contracts.md` §11 与 §13 的契约填写。
★ 规模口径：**文档按字符、代码按行数**（细则见 `references/file-governance.md` §7）。

- **分层**：<每个目录属于 H / W / C / D 哪一层>
- **冷存索引**：<pitfalls/INDEX.md、logs/README.md 等；无则 none>
- **默认不读声明**：<哪些目录含 `⚠ 默认不读` 自声明 README>
- **测试归属**：<tests/ 放什么；确认 scripts/ 里没有未毕业的 test>
- **单文件行数例外**：<`单文件行数例外：scripts/<x> —— <理由>`；无则 none>
- **日志归属**：<任务目录 or Skill 目录；保留策略>
- **文档三件套**：<SKILL.md（必）/ README.md（有 / 省，原因）/ ARCHITECTURE.md（有 / 省，原因）>
- **读取预算档**：<几乎每次任务 4000 ｜ 每日多次 8000 ｜ 每周数次或更少 12000；口径为**字符**>
  —— 这一行必须写：`SKILL.md` 超 8000 字符时校验器要看它才不报警。
- **文档规模**：<references/ 单份字符数；超 12000 软线 / 20000 硬线才需拆；README、ARCHITECTURE、pitfalls 超 20000 只提示、不判；无则 none>
- **重构触发器**：<当前是否已接近 `file-governance.md` §7 任一阈值>
