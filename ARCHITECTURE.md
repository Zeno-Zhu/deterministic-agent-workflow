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
| `references/vnext-contracts.md` | W | 契约模板库（§1–§10 能力，§11 文件治理，§12 主线与渠道差异层，§13 代码工程） | **契约层唯一权威** | 按需 |
| `references/file-governance.md` | W | 文件分层 / 踩坑三级治理 / test 毕业制 / 日志 / 文档三件套 / 规模口径（**文档字数不设门槛、代码按行数**）/ 重构触发 | **文件层唯一权威** | 产出物 >1 文件时必读 |
| `references/multi-platform-routing.md` | W | 主线 + 渠道差异层 / 只写差异与差异三类型 / **主线阶段五要素下限** / **「换渠道还成立吗」切分线** / 锚点与对账 / 拆分判据 / 多版本 / 代码侧三件套 / 调度纪律 | **多平台层唯一权威** | 多平台或多版本时必读 |
| `references/experience-distillation.md` | W | **经验的三问萃取（换渠道→换项目→换域）** / 四层归属 ＋ 环境事实 / 写法三条纪律 / **上浮·下沉·出域三向复核** / 跨域方法论样例 | **经验归属唯一权威** | 要沉淀坑 / 判据 / 教训时必读 |
| `references/code-engineering.md` | W | 问题分类 A–J / 调试四阶段 / 复用优先 / 分层与公共模块 / 提示词与模型版本化 / JSON 契约 / 任务生命周期·幂等·可续跑·降级梯 / 日志内容 / 测试·RED 先行·黄金集 / 输出协议 / 改动边界 / 版本门 / 禁止事项 / **来源与取舍附录** | **代码层唯一权威** | 产出物含代码时必读 |
| `scripts/validate-skill.py` | W | CLI 入口（`argparse` + `validate()` + 报告）；**入口** | 实现权威 | 每次产出后跑 |
| `scripts/wfsb_check/constants.py` | W | 全部阈值、正则、通用工具（含 `estimate_tokens`）；**改阈值只改这里** | 实现权威 | 改检查规则时读 |
| `scripts/wfsb_check/checks_core.py` | W | 组 1–3：frontmatter / workspace / iteration | 实现权威 | 同上 |
| `scripts/wfsb_check/checks_layout.py` | W | 组 4 前半 4.1–4.8：残留 / 产物 / 未毕业 test / 草稿名 / tests / 冷存层 / 索引 / Load First | 实现权威 | 同上 |
| `scripts/wfsb_check/checks_quality.py` | W | 组 4 后半 4.9–4.16：文档三件套 / 主线路由死路由 / 内联渠道参数 / 单文件行数 / 密钥 / **主线总览表带「进入·跳过条件」列**（4.10、4.15 已废除） | 实现权威 | 同上 |
| `scripts/audit-experience-loss.py` | W | **经验流失审计**：拿重构前快照 vs 当前 skill 全集，抽可辨识事实逐条比对，列「找不到」的（**判读三类：刻意丢弃 / 写法差异 / 真缺口**） | 实现权威 | ★ **拆分·搬迁·瘦身类改动收尾必跑** |
| `tests/test_validator_negative.py` | C | 校验器的**反面样本**回归（21 项必须全触发）+ 反向样本 + 空壳样本 | 实现保护 | **不读**；改校验器后手动跑 |
| `pitfalls/INDEX.md` | C | 本 skill 自己的踩坑索引（一行一坑，唯一默认可读项） | 本 skill 踩坑权威 | **默认不读**；现象命中某一行才读 |
| `pitfalls/README.md` | C | 冷存层自声明（`⚠ 默认不读`） | 说明性 | 不读 |
| `templates/README.template.md` | W | 产出 skill 的 README 骨架 | 骨架权威 | 产出时按需读 |
| `templates/ARCHITECTURE.template.md` | W | 产出 skill 的技术文档骨架 | 骨架权威 | 产出时按需读 |
| `templates/PITFALLS-INDEX.template.md` | W | 踩坑索引骨架（冷存唯一入口） | 骨架权威 | 有坑时读 |
| `templates/PITFALL-CARD.template.md` | W | 单条坑的正文骨架（冷存） | 骨架权威 | 索引命中时读 |
| `templates/COLD-DIR-README.template.md` | W | 冷存/死稿目录的自声明 README 骨架 | 骨架权威 | 建冷存层时读 |
| `templates/MAINLINE-SKILL.template.md` | W | **主线 skill** 骨架（全流程 + 分叉点 + 路由） | 骨架权威 | 建主线时读 |
| `templates/ROUTING-TABLE.template.md` | W | **路由表**骨架（固定列；归主线所有） | 骨架权威 | 建主线时读 |
| `templates/CHANNEL-CONTRACT.template.md` | W | **渠道差异层**契约骨架（差异三类型 + 锚点） | 骨架权威 | 建差异层时读 |
| `templates/RESOURCE-REGISTRY.template.json` | W | **API registry** 骨架 | 骨架权威 | 建 API 层时读 |
| `_user_meta.json` | D | 宿主写入的安装元数据 | 宿主所有 | **禁止读、禁止改、禁止删** |

**唯一权威原则**：同一件事只有一个权威文件。
「标准」问 `personal-studio-standard.md`；「契约长什么样」问 `vnext-contracts.md`；
「文件怎么放 / 多大算大」问 `file-governance.md`；「多平台怎么拆 / 主线写到多细」问 `multi-platform-routing.md`；
「这条经验该写进哪一层」问 `experience-distillation.md`；
「代码怎么写」问 `code-engineering.md`；「主流程」问 `SKILL.md`。
**七者不互相复述细节，只互相指路。**

## 2. 现象 → 查哪里

| 现象 | 先看 | 常见根因 |
|---|---|---|
| 触发不了（AI 不加载这个 skill） | `SKILL.md` frontmatter 的 `description` | 触发词没覆盖用户的实际说法（中文口语、旧叫法） |
| AI 没读治理规范就产出 skill | `SKILL.md` 的 `Load First` 第 3、4 条 | 把"必须读"写成了"建议读" |
| 产出的 skill 把坑故事写进 `SKILL.md` | `SKILL.md` §7.3 反污染红线 | 没做"换个项目还成立吗"自检 |
| 产出的 skill 参数串味（A 平台经验套 B 平台） | `references/multi-platform-routing.md` §0 §2 | 该拆的没拆，塞进了一个 skill 的 if/else |
| 主线里长出渠道数值 / 计费 / 报错特征 | 同文件 §2 | 主线在替差异层执行，而不是承载流程 |
| ★ 每条渠道 skill 都把全流程重写了一遍 | 同文件 §1.2 | **流程漂移**的根源：改一处要改 N 份，加新渠道要抄一遍 |
| ★ 主线被掏空成「只做路由」 | 同文件 §1.1 | 共性被推给渠道；读者看完主线不知道整体要做哪几步 |
| ★ 改了主线，渠道没跟着动 | 同文件 §4 | 缺锚点 / 对账：差异层锚定的版本 ≠ 主线当前版本 |
| 路由表的子 skill 找不到（死路由） | `references/routing-table.md` | 差异层 skill 改名 / 没装；校验脚本会报 |
| 加了新平台要回去改老 skill | 同文件 §6 | 结构错了：加平台应该只加 skill + 路由表一行 |
| 校验脚本对正确的 skill 报 FAIL | `scripts/wfsb_check/` 里对应的检查函数 | 正则匹配的是措辞而不是语义；改措辞没同步改正则 |
| 校验脚本漏报（该报没报） | 同上 | 检查项没写进代码 / 目录扫描白名单；**跑 ② 反面样本确认** |
| 校验报「存在运行产物目录 …`__pycache__`」 | `scripts/validate-skill.py` 顶部的 `sys.dont_write_bytecode` | 入口忘了在任何子包 import 之前关掉字节码写入（坑 P001） |
| 某个 skill 明明空壳却全项通过 | `checks_core.check_frontmatter` 的返回值语义 | 「正文为空」与「frontmatter 不合法」共用了一个哨兵值（坑 P002） |
| 密钥检查把展示文本 / 日志文案判成密钥 | `constants.SECRET_ASSIGN_RE` 的边界与取值形态 | 正则跨了字符串边界；见坑 P003 与 `code-engineering.md` 的宽正则纪律 |
| 产出的 skill 代码越写越乱 / 单文件几百行 | `references/code-engineering.md` §0、§3 | 没定分层、没抽公共模块；**代码**单文件超 300 行（校验器 4.13 会报） |
| 某份 `references/` 越写越长、翻起来找不到东西 | `references/file-governance.md` §7.1 | 两个主题挤在一份；**按主题拆**（不按字数拆） |
| 有人拿「文档超 N 字符」当理由去砍内容 | 同文件 §7「规模口径」 | **文档字数不设门槛**：字符数与行数只进 INFO 行，不判不提示；唯一规模门槛是**代码**行数 |
| 「提交成功但结果没落盘」反复出现 | `references/code-engineering.md` §6 | 缺状态机与对账流程，只做了「提交 + 等」 |
| 一次修复的 diff 大得没法审 / 夹带无关改动 | 同文件 §10「改动边界」 | 顺手改了相邻代码或「顺便重构」 |
| 同一批任务跑两遍，账单 / 产物不一样 | 同文件 §6.6「幂等」 | 没有稳定任务指纹，重试整段重来 |
| 改了个提示词，某几组突然变差 | 同文件 §8.4、§11 | 缺黄金集门；改动直接放量，没先跑样本 |
| 「以前能跑现在不行」，但提示词没动 | 同文件 §4.4 | 模型浮动别名被上游静默升级；报错常伪装成限流 / 余额 / 审核 |
| 花的钱莫名变多 | 同文件 §7、`.workbuddy` 台账 | 成本是配置问题的第一信号：先查重复提交 / 提示词变长，别先怪涨价 |
| 两个现象都指向同一条坑 | `pitfalls/INDEX.md` | 命中数该 +1 了；**别新建文件，改计数** |
| 两份 references 说法冲突 | `ARCHITECTURE.md` §1 唯一权威列 | 新内容写进了错的层 |
| 产出 skill 的 `scripts/` 单文件报「超过软线 300 行」WARN | `references/code-engineering.md` §0 第 7 条 | 代码按**行数**判；确实不该拆就在 `ARCHITECTURE.md` 写 `单文件行数例外：<相对路径> —— <理由>` |
| 有人问「文档多长算超」 | `references/file-governance.md` §7「规模口径」 | **文档字数不设门槛**（2026-10-02 起）：不判、不提示，只进 INFO 行 |
| 公开仓库与本地不一致 | `ARCHITECTURE.md` §3 影响面 | 只改了 `SKILL.md`，没同步 references / scripts / templates |
| `_user_meta.json` 被当成垃圾想删 | 本表 | 它是宿主安装元数据，**删了会掉注册** |

## 3. 改动影响面

| 改这个 | 必须同步改 |
|---|---|
| `SKILL.md` 的九步法 | `references/personal-studio-standard.md` 对应节、`README.md` 的 30 秒上手 |
| `SKILL.md` 的文件治理四条 | `references/file-governance.md`（细则权威）、`references/vnext-contracts.md` §11 |
| `SKILL.md` 的多平台五条 | `references/multi-platform-routing.md`（细则权威）、`references/vnext-contracts.md` §12 |
| `SKILL.md` 的代码工程四条 | `references/code-engineering.md`（细则权威）、`references/vnext-contracts.md` §13 |
| `file-governance.md` 的阈值（索引 40 行 / 测试死化 30 天 / **代码**单文件 300·600 行） | `scripts/wfsb_check/constants.py` 的常量、`templates/ARCHITECTURE.template.md` §5、`vnext-contracts.md` §11、本文件 §5 |
| `code-engineering.md` 的代码规模与密钥纪律 | `scripts/wfsb_check/constants.py`（`CODE_FILE_*` / `SECRET_*`）、`SKILL.md` §9.2、本文件 §5 |
| `code-engineering.md` 新增/删改规则 | `SKILL.md` §9（要保持同步的**索引性**，不复制细节）、`vnext-contracts.md` §13、`file-governance.md` §6.1、本文件 §2／§3；**项目侧 `docs/工作室稳定型开发模式.md` 是它的「人读版」，两边必须一致** |
| `multi-platform-routing.md` 的拆分判据 / 术语 | `templates/ROUTING-TABLE.template.md` 的列定义、`templates/MAINLINE-SKILL.template.md`、`templates/CHANNEL-CONTRACT.template.md`、`scripts/wfsb_check/checks_quality.py` 的路由检查 |
| `multi-platform-routing.md` §1.1 的**五要素下限** / 切分线 | `templates/MAINLINE-SKILL.template.md`（阶段卡骨架）、`SKILL.md` §8.3、**目标域主线的阶段文件**（如 `manju-creation/references/phase-*.md`） |
| `experience-distillation.md` 的萃取判据 / 四层归属 | `SKILL.md` §8.4、`vnext-contracts.md` §12 的 `Own Pitfalls` / 主线域级坑节、`multi-platform-routing.md` §1.1.4 |
| `scripts/validate-skill.py` 新增检查项 | `SKILL.md`「输出与验证」的检查清单、`file-governance.md` §9 落地清单、**`tests/` 的 EXPECTED 列表**、本文件 §1 |
| 拆分 / 改名 `scripts/` 里的模块 | 本文件 §1、§5、`README.md` 目录导航、`SKILL.md`「输出与验证」里的路径 |
| ★ **拆分 / 搬迁 / 瘦身 skill 内容** | ★ **收尾跑 `scripts/audit-experience-loss.py`**，逐条判读「刻意丢弃 / 写法差异 / 真缺口」；★ **`validate-skill.py` 只管结构，不管有没有改丢东西** |
| 新增 / 改名 `templates/` | `README.md` 目录导航、本文件 §1 |
| 目录结构变化 | 本文件 §1、§3、`README.md` 目录导航 |
| 记录一次新踩的坑 | `pitfalls/INDEX.md` 加一行 + 新建 `pitfalls/PNNN-*.md`；**命中 ≥3 次且通用才改 `SKILL.md`** |
| 回推公开仓库 | 全部（`SKILL.md` + **6 份 references** + `scripts/` **7 个文件**（入口 1 + `wfsb_check/` 4 + **审计 1**） + `tests/` + `pitfalls/` 5 个文件 + 9 份 templates + `README.md` + 本文件） |

## 4. 校验与重建

```bash
# ① 自检（对本 skill 自身，应 PASS + INFO 行；若报 __pycache__ 见坑 P001）
python3 scripts/validate-skill.py .

# ② 反面样本回归（改过任何检查规则就必须跑；应打印「20 项 + 长文档 11 项 + 空壳 2 项」全过）
python3 tests/test_validator_negative.py

# ③ 校验任意产出 skill（可传目录或 SKILL.md）
python3 scripts/validate-skill.py /absolute/path/to/target-skill

# ④ 结构完整性：应列出 SKILL.md README.md ARCHITECTURE.md references scripts templates tests pitfalls
ls -1

# ⑤ 经验流失审计（★ 拆分 / 搬迁 / 瘦身类改动后必跑；validate 只管结构，不管「有没有改丢东西」）
python3 scripts/audit-experience-loss.py \
  --archive "<重构前的快照目录>" --current "<skills 目录>" --only "manju-*"
#   逐条判读三类：A 刻意丢弃 / B 写法差异 / C 真缺口（C 才要补）
#   挂门：加 --fail-on-missing（有缺失即退出码 1）

# ⑥ 单文件规模（代码按行数；应全部 ≤300 行）
python -c "import glob,os;[print(len(open(p,encoding='utf-8').read().splitlines()),p) for p in sorted(glob.glob('scripts/**/*',recursive=True)) if os.path.isfile(p)]"
```

> ① 单独跑 `PASS` **不能**证明检查有效 —— 把检查全删了它也会 PASS。
> 所以改了校验规则一定要跑 ②，确认 **20 项反面断言 + 长文档样本 11 项断言 + 2 项空壳断言**仍然真的会报错 / 该不报的不报。
> ④ 跑完若多出 `scripts/wfsb_check/__pycache__` → 说明有人把入口顶部的
> `sys.dont_write_bytecode = True` 删了（坑 P001）。

## 5. 文件治理

- **分层**：
  - H = `SKILL.md`、`README.md`
  - W = `references/`×6、`scripts/`（入口 1 + `wfsb_check/` 4 模块 + **审计 1**）、`templates/`×9、`ARCHITECTURE.md`
  - C = `tests/`（1 份回归测试）、`pitfalls/`（索引 1 + 正文 3，**默认不读**）
  - D = `_user_meta.json`（宿主所有）
- **规模口径**：**文档字数不设门槛（2026-10-02 起）；唯一规模门槛是代码按行数**（`file-governance.md` §7）。
  本 skill 的文档（`SKILL.md` / 5 份 `references/` / `README` / 本文件）不论多长都**不判、不提示**；
  只有 `scripts/` 单文件行数参与判定（当前全部 ≤300 行，见 §1）。
- **冷存索引**：`pitfalls/INDEX.md`（固定列，一行一坑）；`tests/` 无索引需求（单文件、无增长）
- **默认不读声明**：`pitfalls/README.md` 首句为 `⚠ 默认不读：…`；
  `tests/` 属 C 层但只有一份文件，AI 默认不会触及 —— 一旦 `tests/` 超过 3 份或开始增长，
  **必须补 `tests/README.md` 自声明**
- **测试归属**：`tests/test_validator_negative.py` —— 反面样本 + 长文档样本 + 空壳样本，证明检查项真的会报错。
  判据「我还在跑它」成立：**每次改检查规则都必须跑**。不是产品代码，不进 `scripts/`
- **单文件行数例外**：无。全部 `scripts/` 文件均 ≤300 行；**将来要破这条，必须在本节逐文件写明理由**
- **日志归属**：无日志。本 skill 不产生运行日志
- **文档三件套**：`SKILL.md`（有）/ `README.md`（有）/ `ARCHITECTURE.md`（有，因为存在 `scripts/` 与 5 份 references）
- **重构触发器**：
  - ★ **文档侧不再有数字触发器**（2026-10-02 起字数门槛全部废除，见 `file-governance.md` §7）。
    文档该不该拆，只看**主题**：一份文件里挤了两个可独立命中的主题就拆，否则不拆。
  - `SKILL.md` 当前 **~11599 字符 / ~378 行**，全部 `references/` 均 ~10k 字符量级 ——
    历史上这曾超「每日多次 8000」档 / 「references 12000 软线」，**现在一律不判、不提示**。
    **仍建议下沉**：`SKILL.md` 是每次触发都要付的 token 成本 ——
    加内容前先问「这段该不该在 `references/`」，而不是问「超没超字数」。
  - `references/vnext-contracts.md` **496 行** —— 契约类文档天然行多而字疏（缩进 + 短行），
    行数不构成拆分理由；拆不拆只看它是否混装了两个主题。
  - `scripts/` 单文件行数：**唯一仍参与判定的规模口径**（软线 300 / 硬线 600），当前全部 ≤300 行。
  - `templates/` 9 份、`references/` 5 份 → 未触"单目录平铺 >15"阈值，但已过半；
    **下次加骨架优先考虑合并或改用索引**（暂时不加新模板，黄金集结构写在 `code-engineering.md` §8.4）。
  - `pitfalls/INDEX.md` 4 行 → 距 40 行归档阈值很远，可放心备案新坑。
  - ✅ 用 `python3 scripts/validate-skill.py .` 一条命令即可核对以上全部项。
