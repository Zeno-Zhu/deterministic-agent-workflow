# ARCHITECTURE — workflow-skill-builder

> 后续 AI 的**排障地图**。只在出问题、要改造、要回推公开仓库时读。
> **不要放进 `SKILL.md` 的 Load First** —— 它的位置在 README 的目录导航里。

## 1. 文件地图

| 路径 | 层 | 是什么 | 权威性 | AI 读取策略 |
|---|---|---|---|---|
| `SKILL.md` | H | 主方法：九步创建法、Runtime、Autonomy、文件治理、多平台路由 | **方法的唯一权威** | 每次必读 |
| `README.md` | H | 人的定位与上手 | 说明性 | 初识时读 |
| `ARCHITECTURE.md` | W | 本文件 | 结构说明 | 排障 / 回推时读 |
| `references/personal-studio-standard.md` | W | 标准：三维度、六 Primitive、验证矩阵、Protected Rules | **标准层唯一权威** | 建/重改时读 |
| `references/vnext-contracts.md` | W | 契约模板库（§1–§10 能力，§11 文件治理，§12 中控与渠道线） | **契约层唯一权威** | 按需 |
| `references/file-governance.md` | W | 文件分层 / 踩坑三级治理 / test 毕业制 / 日志 / 文档三件套 / 读取预算 / 重构触发 | **文件层唯一权威** | 产出物 >1 文件时必读 |
| `references/multi-platform-routing.md` | W | 拆分判据 / 中控 + 渠道线 / 多版本 / API 中控三件套 / 调度纪律 | **多平台层唯一权威** | 多平台或多版本时必读 |
| `references/code-engineering.md` | W | 问题分类 A–J / 复用优先 / 分层与公共模块 / 提示词文件 / JSON 契约 / 任务生命周期与对账 / 日志内容 / 测试 / 输出协议 / 禁止事项 | **代码层唯一权威** | 产出物含代码时必读 |
| `scripts/validate-skill.py` | W | CLI 入口（`argparse` + `validate()` + 报告）；**入口** | 实现权威 | 每次产出后跑 |
| `scripts/wfsb_check/constants.py` | W | 全部阈值、正则、通用工具；**改阈值只改这里** | 实现权威 | 改检查规则时读 |
| `scripts/wfsb_check/checks_core.py` | W | 组 1–3：frontmatter / workspace / iteration | 实现权威 | 同上 |
| `scripts/wfsb_check/checks_layout.py` | W | 组 4 前半 4.1–4.8：残留 / 产物 / 未毕业 test / 草稿名 / tests / 冷存层 / 索引 / Load First | 实现权威 | 同上 |
| `scripts/wfsb_check/checks_quality.py` | W | 组 4 后半 4.9–4.14：文档三件套 / 读取预算 / 路由与内联参数 / 单文件行数 / 密钥 | 实现权威 | 同上 |
| `tests/test_validator_negative.py` | C | 校验器的**反面样本**回归（20 项必须全触发）+ 空壳样本 | 实现保护 | **不读**；改校验器后手动跑 |
| `pitfalls/INDEX.md` | C | 本 skill 自己的踩坑索引（一行一坑，唯一默认可读项） | 本 skill 踩坑权威 | **默认不读**；现象命中某一行才读 |
| `pitfalls/README.md` | C | 冷存层自声明（`⚠ 默认不读`） | 说明性 | 不读 |
| `templates/README.template.md` | W | 产出 skill 的 README 骨架 | 骨架权威 | 产出时按需读 |
| `templates/ARCHITECTURE.template.md` | W | 产出 skill 的技术文档骨架 | 骨架权威 | 产出时按需读 |
| `templates/PITFALLS-INDEX.template.md` | W | 踩坑索引骨架（冷存唯一入口） | 骨架权威 | 有坑时读 |
| `templates/PITFALL-CARD.template.md` | W | 单条坑的正文骨架（冷存） | 骨架权威 | 索引命中时读 |
| `templates/COLD-DIR-README.template.md` | W | 冷存/死稿目录的自声明 README 骨架 | 骨架权威 | 建冷存层时读 |
| `templates/ROUTER-SKILL.template.md` | W | **中控 skill** 骨架 | 骨架权威 | 建中控时读 |
| `templates/ROUTING-TABLE.template.md` | W | **路由表**骨架（固定列） | 骨架权威 | 建中控时读 |
| `templates/CHANNEL-CONTRACT.template.md` | W | **渠道线 skill** 契约骨架 | 骨架权威 | 建渠道线时读 |
| `templates/RESOURCE-REGISTRY.template.json` | W | **API 中控 registry** 骨架 | 骨架权威 | 建 API 中控时读 |
| `_user_meta.json` | D | 宿主写入的安装元数据 | 宿主所有 | **禁止读、禁止改、禁止删** |

**唯一权威原则**：同一件事只有一个权威文件。
「标准」问 `personal-studio-standard.md`；「契约长什么样」问 `vnext-contracts.md`；
「文件怎么放」问 `file-governance.md`；「多平台怎么拆」问 `multi-platform-routing.md`；
「代码怎么写」问 `code-engineering.md`；「主流程」问 `SKILL.md`。
**六者不互相复述细节，只互相指路。**

## 2. 现象 → 查哪里

| 现象 | 先看 | 常见根因 |
|---|---|---|
| 触发不了（AI 不加载这个 skill） | `SKILL.md` frontmatter 的 `description` | 触发词没覆盖用户的实际说法（中文口语、旧叫法） |
| AI 没读治理规范就产出 skill | `SKILL.md` 的 `Load First` 第 3、4 条 | 把"必须读"写成了"建议读" |
| 产出的 skill 把坑故事写进 `SKILL.md` | `SKILL.md` §7.3 反污染红线 | 没做"换个项目还成立吗"自检 |
| 产出的 skill 参数串味（A 平台经验套 B 平台） | `references/multi-platform-routing.md` §1 | 该拆的没拆，塞进了一个 skill 的 if/else |
| 中控里长出渠道数值 / 计费 / 报错特征 | 同文件 §3 | 中控在替渠道 skill 执行，而不只是路由 |
| 路由表的子 skill 找不到（死路由） | `references/routing-table.md` | 渠道 skill 改名 / 没装；校验脚本会报 |
| 加了新平台要回去改老 skill | 同文件 §5 | 结构错了：加平台应该只加 skill + 路由表一行 |
| 校验脚本对正确的 skill 报 FAIL | `scripts/wfsb_check/` 里对应的检查函数 | 正则匹配的是措辞而不是语义；改措辞没同步改正则 |
| 校验脚本漏报（该报没报） | 同上 | 检查项没写进代码 / 目录扫描白名单；**跑 ② 反面样本确认** |
| 校验报「存在运行产物目录 …`__pycache__`」 | `scripts/validate-skill.py` 顶部的 `sys.dont_write_bytecode` | 入口忘了在任何子包 import 之前关掉字节码写入（坑 P001） |
| 某个 skill 明明空壳却全项通过 | `checks_core.check_frontmatter` 的返回值语义 | 「正文为空」与「frontmatter 不合法」共用了一个哨兵值（坑 P002） |
| 密钥检查把展示文本 / 日志文案判成密钥 | `constants.SECRET_ASSIGN_RE` 的边界与取值形态 | 正则跨了字符串边界；见坑 P003 与 `code-engineering.md` 的宽正则纪律 |
| 产出的 skill 代码越写越乱 / 单文件几百行 | `references/code-engineering.md` §0、§3 | 没定分层、没抽公共模块；单文件超 300 行（校验器 4.13 会报） |
| 「提交成功但结果没落盘」反复出现 | `references/code-engineering.md` §6 | 缺状态机与对账流程，只做了「提交 + 等」 |
| 两个现象都指向同一条坑 | `pitfalls/INDEX.md` | 命中数该 +1 了；**别新建文件，改计数** |
| 两份 references 说法冲突 | `ARCHITECTURE.md` §1 唯一权威列 | 新内容写进了错的层 |
| SKILL.md 报「超读取预算」 | `references/file-governance.md` §7 分档表 | 没确认自己属于哪一档；确认后在 §5 写 `读取预算档` |
| 公开仓库与本地不一致 | `ARCHITECTURE.md` §3 影响面 | 只改了 `SKILL.md`，没同步 references / scripts / templates |
| `_user_meta.json` 被当成垃圾想删 | 本表 | 它是宿主安装元数据，**删了会掉注册** |

## 3. 改动影响面

| 改这个 | 必须同步改 |
|---|---|
| `SKILL.md` 的九步法 | `references/personal-studio-standard.md` 对应节、`README.md` 的 30 秒上手 |
| `SKILL.md` 的文件治理四条 | `references/file-governance.md`（细则权威）、`references/vnext-contracts.md` §11 |
| `SKILL.md` 的多平台四条 | `references/multi-platform-routing.md`（细则权威）、`references/vnext-contracts.md` §12 |
| `SKILL.md` 的代码工程四条 | `references/code-engineering.md`（细则权威）、`references/vnext-contracts.md` §13 |
| `file-governance.md` 的阈值（读取预算 / 索引 40 行 / 测试死化 30 天 / 单文件行数） | `scripts/wfsb_check/constants.py` 的常量、`templates/ARCHITECTURE.template.md` §5、本文件 §5 |
| `code-engineering.md` 的代码规模与密钥纪律 | `scripts/wfsb_check/constants.py`（`CODE_FILE_*` / `SECRET_*`）、`SKILL.md` §9.2、本文件 §5 |
| `multi-platform-routing.md` 的拆分判据 | `templates/ROUTING-TABLE.template.md` 的列定义、`scripts/wfsb_check/checks_quality.py` 的路由检查 |
| `scripts/validate-skill.py` 新增检查项 | `SKILL.md`「输出与验证」的检查清单、`file-governance.md` §9 落地清单、**`tests/` 的 EXPECTED 列表**、本文件 §1 |
| 拆分 / 改名 `scripts/` 里的模块 | 本文件 §1、§5、`README.md` 目录导航、`SKILL.md`「输出与验证」里的路径 |
| 新增 / 改名 `templates/` | `README.md` 目录导航、本文件 §1 |
| 目录结构变化 | 本文件 §1、§3、`README.md` 目录导航 |
| 记录一次新踩的坑 | `pitfalls/INDEX.md` 加一行 + 新建 `pitfalls/PNNN-*.md`；**命中 ≥3 次且通用才改 `SKILL.md`** |
| 回推公开仓库 | 全部（`SKILL.md` + 5 份 references + `scripts/` 6 个文件 + `tests/` + `pitfalls/` 5 个文件 + 9 份 templates + `README.md` + 本文件） |

## 4. 校验与重建

```bash
# ① 自检（对本 skill 自身，应 PASS + INFO 行；若报 __pycache__ 见坑 P001）
python3 scripts/validate-skill.py .

# ② 反面样本回归（改过任何检查规则就必须跑；应打印「20 项 + 空壳 2 项」全过）
python3 tests/test_validator_negative.py

# ③ 校验任意产出 skill（可传目录或 SKILL.md）
python3 scripts/validate-skill.py /absolute/path/to/target-skill

# ④ 结构完整性：应列出 SKILL.md README.md ARCHITECTURE.md references scripts templates tests pitfalls
ls -1

# ⑤ 单文件规模（应全部 ≤300 行）
python -c "import glob,os;[print(len(open(p,encoding='utf-8').read().splitlines()),p) for p in sorted(glob.glob('scripts/**/*',recursive=True)) if os.path.isfile(p)]"
```

> ① 单独跑 `PASS` **不能**证明检查有效 —— 把检查全删了它也会 PASS。
> 所以改了校验规则一定要跑 ②，确认 **20 项反面断言 + 2 项空壳断言**仍然真的会报错。
> ④ 跑完若多出 `scripts/wfsb_check/__pycache__` → 说明有人把入口顶部的
> `sys.dont_write_bytecode = True` 删了（坑 P001）。

## 5. 文件治理

- **分层**：
  - H = `SKILL.md`、`README.md`
  - W = `references/`×5、`scripts/`（入口 1 + `wfsb_check/` 4 模块）、`templates/`×9、`ARCHITECTURE.md`
  - C = `tests/`（1 份回归测试）、`pitfalls/`（索引 1 + 正文 3，**默认不读**）
  - D = `_user_meta.json`（宿主所有）
- **读取预算档**：**每周数次或更少**（上限 12000 字符 / 400 行）
  —— 它是"产 skill 的 skill"，只在建/改 skill 时触发，不是每次任务都读。
- **冷存索引**：`pitfalls/INDEX.md`（固定列，一行一坑）；`tests/` 无索引需求（单文件、无增长）
- **默认不读声明**：`pitfalls/README.md` 首句为 `⚠ 默认不读：…`；
  `tests/` 属 C 层但只有一份文件，AI 默认不会触及 —— 一旦 `tests/` 超过 3 份或开始增长，
  **必须补 `tests/README.md` 自声明**
- **测试归属**：`tests/test_validator_negative.py` —— 反面样本 + 空壳样本，证明检查项真的会报错。
  判据「我还在跑它」成立：**每次改检查规则都必须跑**。不是产品代码，不进 `scripts/`
- **单文件行数例外**：无。全部 `scripts/` 文件均 ≤300 行；**将来要破这条，必须在本节逐文件写明理由**
- **日志归属**：无日志。本 skill 不产生运行日志
- **文档三件套**：`SKILL.md`（有）/ `README.md`（有）/ `ARCHITECTURE.md`（有，因为存在 `scripts/` 与 5 份 references）
- **重构触发器**：
  - `SKILL.md` 当前 **363 行 / 10865 字符** —— 在「每周数次」档内，但**已用掉 91%**。
    **再从「每日多次」档的视角看它是超标的**，所以：**任何新增内容一律下沉到 `references/`，
    不要再往 `SKILL.md` 堆**；真要扩写，先删旧条目。
  - `templates/` 9 份、`references/` 5 份 → 未触"单目录平铺 >15"阈值，但已过半；
    下次加骨架优先考虑合并或改用索引。
  - `pitfalls/INDEX.md` 3 行 → 距 40 行归档阈值很远，可放心备案新坑。
  - ✅ 用 `python3 scripts/validate-skill.py .` 一条命令即可核对以上全部项。
