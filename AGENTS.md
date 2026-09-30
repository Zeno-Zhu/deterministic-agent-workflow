# AGENTS.md — AI Agent 项目速览

## 项目定位

「确定性 Agent 工作流设计与 Skill 构建方法」的公开仓库。仓库根目录本身就是一个可安装的 Codex / Agent Skill：**`workflow-skill-builder`**。

它管四件事：

- **能力设计** —— 契约、Runtime（R0/R1/R2）、Atomic Action、Gate、判断路由、证据驱动进化；
- **文件治理** —— H/W/C/D 四层、踩坑三级晋升、test 毕业制、日志归属、文档三件套；
- **多平台 / 多版本** —— 一个中控 + N 条渠道线、API 中控三件套（registry / client / scheduler）；
- **代码工程纪律** —— 先分类再定力度、复用优先与公共模块、任务生命周期与对账、输出协议。

## 关键文件

| 路径 | 作用 |
|---|---|
| `SKILL.md` | 主方法：九步创建法 + 文件治理四条 + 多平台四条 + 代码工程四条 |
| `ARCHITECTURE.md` | 文件地图、现象 → 查哪里、改动影响面、校验命令 |
| `references/personal-studio-standard.md` | 标准层：三维度、六 Primitive、验证矩阵、Protected Rules |
| `references/vnext-contracts.md` | 契约模板库（§11 文件治理、§12 中控与渠道线、§13 代码工程） |
| `references/file-governance.md` | **文件层唯一权威**：分层、踩坑治理、test 毕业制、读取预算分档 |
| `references/multi-platform-routing.md` | **多平台层唯一权威**：拆分判据、中控硬规则、多版本、调度纪律 |
| `references/code-engineering.md` | **代码层唯一权威**：问题分类 A–J、公共模块、JSON 契约、任务生命周期与对账、输出协议 |
| `scripts/validate-skill.py` | 零依赖校验入口（四组；实现拆在 `scripts/wfsb_check/`），返回 0 即通过 |
| `scripts/wfsb_check/*.py` | 校验实现：`constants` / `checks_core` / `checks_layout` / `checks_quality`（每个 ≤300 行） |
| `tests/test_validator_negative.py` | 反面样本回归（20 项必须全触发）+ 空壳样本（2 项断言） |
| `pitfalls/` | 本 skill 自己的踩坑冷存层（`INDEX.md` 一行一坑，**默认不读**） |
| `templates/` | 9 份产出物骨架（README / ARCHITECTURE / 坑索引 / 坑卡 / 冷存声明 / 中控 / 渠道线契约 / 路由表 / registry） |

## Agent 修改本仓库时的硬规则

1. 本仓库是 **Skill 目录，不是任务工作区**：任何任务产物、临时文件、日志一律写入目标项目的任务文件夹，绝不写入本仓库。
2. 修改 `SKILL.md` 后必须运行校验脚本并通过：
   `python3 scripts/validate-skill.py .`
3. **改了任何检查规则，必须同时跑 `tests/test_validator_negative.py`。**
   只跑自检 `PASS` 不能证明检查有效 —— 把检查全删了它也会 PASS。
4. **不得移除**工作区隔离规则、受控迭代规则（脚本会检查）。
5. **不回推 `_user_meta.json`**（宿主安装元数据，已在 `.gitignore`）。
6. 不得引入第三方依赖、个人绝对路径或 `.DS_Store`。
7. 新增检查项时，`tests/` 的 `EXPECTED_ERRORS` / `EXPECTED_WARNINGS` 必须同步加一条，否则等于没有测试。
8. 改任何规则时，按 `ARCHITECTURE.md` §3「改动影响面」同步全部受影响文件 —— **只改一处 = 制造矛盾**。
9. **单文件 ≤300 行**（硬线 600）。`scripts/` 里任何文件超软线必须在 `ARCHITECTURE.md` §5 逐文件声明理由。
   入口脚本若要 import 同级子包，**必须**先 `sys.dont_write_bytecode = True`，否则会自造 `__pycache__` 让自己 FAIL。
10. **不得提交密钥 / 令牌字面量**（校验器 4.14 会扫；命中只说位置、不回显值）。
11. 踩到新坑 → 先写 `pitfalls/PNNN-*.md` + `pitfalls/INDEX.md` 加一行（命中 = 1）；
    **命中 ≥3 次且通用且可执行才准晋升进 `SKILL.md`**。单项目 / 单次的经验禁止进 `SKILL.md`。

## 验证

```bash
# 自检（应 PASS；若报 __pycache__ 见 pitfalls/P001）
python3 scripts/validate-skill.py .

# 反面样本回归（改过校验器才需要，但改了就必须跑）
python3 tests/test_validator_negative.py

# 无个人路径 / IDE 残留（说明类文件自身含这些检测模式，排除以免自匹配）
grep -RInE '/Users/|laozhu|\.trae|\.codex' \
  --exclude=AGENTS.md --exclude=CONTRIBUTING.md --exclude=README.md . || echo clean
```
