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
| `scripts/validate-skill.py` | W | 零依赖机械校验（5 组共 22 项检查） | 实现权威 | 每次产出后跑 |
| `tests/test_validator_negative.py` | C | 校验器的**反面样本**回归（17 项必须全触发） | 实现保护 | **不读**；改校验器后手动跑 |
| `templates/README.template.md` | W | 产出 skill 的 README 骨架 | 骨架权威 | 产出时按需读 |
| `templates/ARCHITECTURE.template.md` | W | 产出 skill 的技术文档骨架 | 骨架权威 | 产出时按需读 |
| `templates/PITFALLS-INDEX.template.md` | W | 踩坑索引骨架（冷存唯一入口） | 骨架权威 | 有坑时读 |
| `templates/PITFALL-CARD.template.md` | W | 单条坑的正文骨架（冷存） | 骨架权威 | 索引命中时读 |
| `templates/COLD-DIR-README.template.md` | W | 冷存/死稿目录的自声明 README 骨架 | 骨架权威 | 建冷存层时读 |
| `templates/ROUTER-SKILL.template.md` | W | **中控 skill** 骨架 | 骨架权威 | 建中控时读 |
| `templates/ROUTING-TABLE.template.md` | W | **路由表**骨架（固定列） | 骨架权威 | 建中控时读 |
| `templates/RESOURCE-REGISTRY.template.json` | W | **API 中控 registry** 骨架 | 骨架权威 | 建 API 中控时读 |
| `_user_meta.json` | D | 宿主写入的安装元数据 | 宿主所有 | **禁止读、禁止改、禁止删** |

**唯一权威原则**：同一件事只有一个权威文件。
「标准」问 `personal-studio-standard.md`；「契约长什么样」问 `vnext-contracts.md`；
「文件怎么放」问 `file-governance.md`；「多平台怎么拆」问 `multi-platform-routing.md`；「主流程」问 `SKILL.md`。
**五者不互相复述细节，只互相指路。**

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
| 校验脚本对正确的 skill 报 FAIL | `scripts/validate-skill.py` 的对应检查项 | 正则匹配的是措辞而不是语义；改措辞没同步改正则 |
| 校验脚本漏报（该报没报） | 同上 | 检查项没写进代码 / 目录扫描白名单；**跑 ② 反面样本确认** |
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
| `file-governance.md` 的阈值（读取预算 / 40 行 / 30 天 / 500 行） | `scripts/validate-skill.py` 的常量、`templates/ARCHITECTURE.template.md` §5、本文件 §5 |
| `multi-platform-routing.md` 的拆分判据 | `templates/ROUTING-TABLE.template.md` 的列定义、`scripts/validate-skill.py` 的路由检查 |
| `scripts/validate-skill.py` 新增检查项 | `SKILL.md`「输出与验证」的检查清单、`file-governance.md` §9 落地清单、**`tests/` 的 EXPECTED 列表** |
| 新增 / 改名 `templates/` | `README.md` 目录导航、本文件 §1 |
| 目录结构变化 | 本文件 §1、§3、`README.md` 目录导航 |
| 回推公开仓库 | 全部（`SKILL.md` + 4 份 references + scripts + tests + 8 份 templates + `README.md` + 本文件） |

## 4. 校验与重建

```bash
# ① 自检（对本 skill 自身）
python3 scripts/validate-skill.py SKILL.md

# ② 反面样本回归（改过 validate-skill.py 就必须跑）
python3 tests/test_validator_negative.py

# ③ 校验任意产出 skill（可传目录或 SKILL.md）
python3 scripts/validate-skill.py /absolute/path/to/target-skill

# ④ 结构完整性：应列出 SKILL.md README.md ARCHITECTURE.md references scripts templates tests
ls -1
```

> ① 单独跑 `PASS` **不能**证明检查有效 —— 把检查全删了它也会 PASS。
> 所以改了校验规则一定要跑 ②，确认 **17 项**检查仍然真的会报错。

## 5. 文件治理

- **分层**：
  - H = `SKILL.md`、`README.md`
  - W = `references/`×4、`scripts/`、`templates/`×8、`ARCHITECTURE.md`
  - C = `tests/`（1 份回归测试，不读）
  - D = `_user_meta.json`（宿主所有）
- **读取预算档**：**每周数次或更少**（上限 12000 字符 / 400 行）
  —— 它是"产 skill 的 skill"，只在建/改 skill 时触发，不是每次任务都读。
- **冷存索引**：`tests/` 无索引需求（单文件、无增长）；本 skill 无 `pitfalls/`、无 `logs/`
- **默认不读声明**：`tests/` 属 C 层但只有一份文件，AI 默认不会触及；
  一旦 `tests/` 超过 3 份或开始增长，**必须补 `tests/README.md` 自声明**
- **测试归属**：`tests/test_validator_negative.py` —— 校验器的反面样本，证明检查项真的会报错。
  判据「我还在跑它」成立：**每次改 `validate-skill.py` 的检查规则都必须跑**。不是产品代码，不进 `scripts/`
- **日志归属**：无日志。本 skill 不产生运行日志
- **文档三件套**：`SKILL.md`（有）/ `README.md`（有）/ `ARCHITECTURE.md`（有，因为存在 `scripts/` 与 4 份 references）
- **重构触发器**：
  - `SKILL.md` 当前 **309 行 / 9120 字符** —— 已在「每日多次」档之上、「每周数次」档之内（已按 §5 声明档位）。
    **再加内容一律下沉到 `references/`，不要再往 SKILL.md 堆。**
  - `templates/` 8 份、`references/` 4 份 → 未触 15 个平铺的阈值，但已过半；下次加骨架优先考虑合并。
  - ✅ 用 `python3 scripts/validate-skill.py .` 一条命令即可核对以上全部项。
