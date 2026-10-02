#!/usr/bin/env python3
"""回归测试：validate-skill.py 的反面样本。

用途：确认各项检查**真的会报错**。改了 validate-skill.py 的检查规则后必须跑它 ——
只对自身跑 `PASS` 不能证明检查有效（把检查全删了也会 PASS）。

四个样本：
  · 反面样本（case_messy）          —— 违规项塞满，逐条断言全部触发
  · 长文档零告警（case_long_but_light）—— 再长再大的文档都不许触发任何规模报错
  · 主线颗粒度（case_mainline_granularity）—— 总览表只有阶段名必须 WARN、带进入条件列不许 WARN
  · 空壳样本（case_empty_body）      —— 只有 frontmatter 的 skill 必须 FAIL，
                                       而不是被 `if not body` 提前放行

约定（见 references/file-governance.md §4）：
  - 测试代码只住 `tests/`，不进 `scripts/`；名字去掉 test 前缀才算转正。
  - 所有产物建在系统临时目录，**绝不在真实数据目录里建了再删**。
  - 跑完自清；不留中间物。

用法：
    python3 tests/test_validator_negative.py
退出码 0 = 全部检查项按预期触发。
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent          # <skill>/tests
SKILL_DIR = HERE.parent                          # <skill>
VALIDATOR = SKILL_DIR / "scripts" / "validate-skill.py"

#: 反面样本应当触发的全部检查项（出现即视为该检查有效）
EXPECTED_ERRORS = [
    "缺少：目标项目中的新任务文件夹",
    "缺少：任务产物不得写入 Skill 目录",
    "缺少：脚本使用显式输出路径",
    "缺少：复盘与迭代规则",
    "缺少：暂存后审阅再采用",
    "存在草稿/版本残留",
    "存在运行产物/依赖目录",
    "scripts/ 下存在未毕业的测试代码",
    "冷存/死稿目录 logs/ 缺少自声明 README.md",
    "冷存/死稿目录 pitfalls/ 缺少自声明 README.md",
    "存在 pitfalls/ 但没有 pitfalls/INDEX.md",
    "存在 logs/ 但没有 logs/README.md",
    "Load First 引用了冷存/死稿层路径",
    "必须有 README.md",
    "必须有 ARCHITECTURE.md",
    "路由表存在死路由",
    "疑似硬编码密钥",
    "超过硬线 600 行",
]

#: 预期只给 WARN 的项
EXPECTED_WARNINGS = [
    "疑似内联了渠道专属参数",
    "超过软线 300 行",
    "找不到「全流程总览」表",
]


def build_bad_skill(root: Path) -> Path:
    """故意塞满违规项，产出一个「该被 FAIL」的主线 skill。"""
    skill = root / "bad-skill"
    for sub in ("scripts", "references", "pitfalls", "logs", "node_modules/leftpad"):
        (skill / sub).mkdir(parents=True, exist_ok=True)

    # 字符数要越过 README 触发线（2400 字符）—— 这是**结构完备性**判定
    # （篇幅够大就该配 README），与已废除的「字数门槛」是两回事
    filler = "\n".join(
        f"第 {i} 行填充内容，用于触发三件套与规模检查。" for i in range(120)
    )
    (skill / "SKILL.md").write_text(
        "---\nname: bad-skill\ndescription: 反面样本\n---\n\n"
        "## Load First\n\n1. `pitfalls/INDEX.md`\n2. `logs/`\n\n"
        "## 路由\n\n"
        "参考图上限 10 张，按次计费，未命中触发词时走默认渠道。\n\n"
        "## 正文\n\n" + filler + "\n",
        encoding="utf-8",
    )
    (skill / "SKILL.md.bak-20260101-000000").write_text("旧版", encoding="utf-8")
    (skill / "scripts" / "test_parse_groups.py").write_text("print(1)\n", encoding="utf-8")
    (skill / "scripts" / "e2e-smoke.mjs").write_text("// smoke\n", encoding="utf-8")
    # 超软线（300）但不超硬线（600）→ WARN
    (skill / "scripts" / "big_module.py").write_text(
        "\n".join(f"step_{i} = {i}" for i in range(310)) + "\n", encoding="utf-8"
    )
    # 超硬线（600）→ ERROR
    (skill / "scripts" / "huge_module.py").write_text(
        "\n".join(f"step_{i} = {i}" for i in range(610)) + "\n", encoding="utf-8"
    )
    # 硬编码密钥 → ERROR。**运行时拼接**：字面写死会让本测试文件自己命中扫描。
    (skill / "scripts" / "config_sample.py").write_text(
        'API_KEY = "' + "sk-" + "a" * 26 + '"\n', encoding="utf-8"
    )
    (skill / "references" / "a.md").write_text("a\n", encoding="utf-8")
    (skill / "references" / "b.md").write_text("b\n", encoding="utf-8")
    (skill / "references" / "routing-table.md").write_text(
        "# 路由表\n\n"
        "| 渠道 | 触发词 | 子 skill | 关键差异（一句话） | 协议文档 |\n"
        "|---|---|---|---|---|\n"
        "| 真渠道 | real | `real-channel` | 按次计费 | `channels/real.md` |\n"
        "| 幽灵渠道 | ghost | `ghost-channel` | —— | `channels/ghost.md` |\n",
        encoding="utf-8",
    )
    (skill / "pitfalls" / "P001-note.md").write_text("坑\n", encoding="utf-8")
    (skill / "logs" / "run.log").write_text("log\n", encoding="utf-8")
    (skill / "node_modules" / "leftpad" / "index.js").write_text(
        "module.exports=1\n", encoding="utf-8"
    )

    # 同级必须存在至少一个真实 skill，死路由检查才会判 ERROR 而不是 WARN
    sibling = root / "real-channel"
    sibling.mkdir()
    (sibling / "SKILL.md").write_text(
        "---\nname: real-channel\ndescription: 占位渠道线\n---\n", encoding="utf-8"
    )
    return skill


def run_validator(skill: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(skill)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def case_messy(root: Path) -> list:
    """反面样本：违规项塞满，必须逐条命中且整体 FAIL。"""
    skill = build_bad_skill(root)
    proc = run_validator(skill)
    out = (proc.stdout or "") + (proc.stderr or "")

    failures = []
    if proc.returncode != 1:
        failures.append(f"期望退出码 1（FAIL），实际 {proc.returncode}")
    for needle in EXPECTED_ERRORS:
        if f"ERROR: {needle}" not in out and needle not in out:
            failures.append(f"未触发预期 ERROR：{needle}")
    for needle in EXPECTED_WARNINGS:
        if f"WARN: {needle}" not in out and needle not in out:
            failures.append(f"未触发预期 WARN：{needle}")
    if "PASS" in out:
        failures.append("反面样本竟然 PASS")

    print(out.rstrip())
    print(
        f"· 反面样本：期望 {len(EXPECTED_ERRORS) + len(EXPECTED_WARNINGS)} 项，"
        f"未达标 {len(failures)} 项"
    )
    return failures


def case_long_but_light(root: Path) -> list:
    """反向样本：**再长再大的文档都不许触发任何「规模」报错**。

    回归自一次真实争议：早年拿「行数」当硬线（SKILL.md 超 400 行即 FAIL），
    于是 500 行的短句清单被判违规，而 250 行的中文长文反而放行 —— 行数只反映
    换行习惯，不反映读取成本。之后改成「按字符设门槛」，但那些数字同样是
    **本规范自设、非平台限制**：域级 skill（提示词规范 / 渠道协议 / 母工作流）
    天然超出，一刀切只会逼人把内容切碎成难用的碎片。

    ★ 2026-10-02 起 **文档字数不设门槛**：`SKILL.md` / `references/` / `README.md`
      再长再大，都只进 INFO 行，**一律不许 ERROR、也不许 WARN**。
      规模口径只剩代码按行数（见 case_messy）。
    """
    skill = root / "long-light-skill"
    (skill / "references").mkdir(parents=True)
    # 500 行 SKILL.md（越过旧 400 行硬线）
    body = "\n".join(f"填充行 {i}" for i in range(500))
    (skill / "SKILL.md").write_text(
        "---\nname: long-light-skill\ndescription: 超长文档的反向样本\n---\n\n"
        "## Load First\n\n1. `references/huge.md`\n\n"
        "## 工作区硬规则\n\n"
        "- 任务产物落在目标项目中的新任务文件夹。\n"
        "- 绝不把任务产物写入 Skill 目录。\n"
        "- 脚本使用显式输出路径。\n\n"
        "## 复盘与迭代\n\n"
        "候选先暂存，经审阅后再采用。改共享件时先用一小批留出（held-out）组验证；\n"
        "批量前先跑 dry-run 预检。\n\n"
        "## 正文\n\n" + body + "\n",
        encoding="utf-8",
    )
    # README 越过旧 20000 字符提示线
    (skill / "README.md").write_text("填充段落。" * 4200 + "\n", encoding="utf-8")
    # 单份 references 越过旧 20000 字符硬线 —— 这是「字数门槛已废除」的核心回归点
    (skill / "references" / "huge.md").write_text(
        "填充段落。" * 4200 + "\n", encoding="utf-8"
    )

    proc = run_validator(skill)
    out = (proc.stdout or "") + (proc.stderr or "")

    failures = []
    if len((skill / "SKILL.md").read_text(encoding="utf-8").splitlines()) <= 400:
        failures.append("样本构造有误：行数没有超过旧的 400 行硬线，测不出回归")
    if len((skill / "references" / "huge.md").read_text(encoding="utf-8")) <= 20000:
        failures.append("样本构造有误：references 未超过旧的 20000 字符硬线，测不出回归")
    if len((skill / "README.md").read_text(encoding="utf-8")) <= 20000:
        failures.append("样本构造有误：README 未超过旧的 20000 字符提示线，测不出回归")

    # 已废除的规模报错文案：一个字都不许再出现
    retired = (
        "超出读取预算", "已超「每日多次」档", "超过人读文档提示线",
        "超过 references/ 单份硬线", "超过 references/ 单份软线",
        "超过读取预算硬线", "超过读取预算软线",
    )
    for needle in retired:
        if needle in out:
            failures.append(f"文档字数已不设门槛，却仍报出规模告警：{needle}")
    # 除了「文档太长」，样本其余部分都合规 —— 它必须整体 PASS
    if proc.returncode != 0:
        failures.append(f"超长但合规的 skill 应当 PASS，实际退出码 {proc.returncode}")

    print(out.rstrip())
    print(f"· 长文档零告警：未达标 {len(failures)} 项")
    return failures


def case_mainline_granularity(root: Path) -> list:
    """主线颗粒度样本：总览表**只有阶段名** → 必须 WARN；带「进入 / 跳过条件」列 → 不许 WARN。

    回归自一次真实事故：主线被掏成「一句话 + 一张表」，Phase 1/2/3 只剩"跑一条命令"，
    执行者**看不出"这步什么情况下不用做"** ⇒ 对已完成的步骤再跑一遍
    （重跑 = 白烧钱 / 覆盖已完成产物 / 全量重编号作废已交付物）。
    规范见 `references/multi-platform-routing.md` §1.1.1。
    """
    failures = []

    def build(name: str, header: str) -> Path:
        skill = root / name
        (skill / "references").mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: " + name + "\ndescription: 主线颗粒度样本\n---\n\n"
            "## 全流程总览\n\n" + header + "\n"
            "|---|---|---|---|\n"
            "| 0 | 初始化 | 配置文件 | — |\n"
            "| 1 | 剧本处理 | 分集剧本 | — |\n\n"
            "## 工作区硬规则\n\n"
            "- 任务产物落在目标项目中的新任务文件夹。\n"
            "- 绝不把任务产物写入 Skill 目录。\n"
            "- 脚本使用显式输出路径。\n\n"
            "## 复盘与迭代\n\n"
            "候选先暂存，经审阅后再采用。改共享件时先用一小批留出（held-out）组验证；\n"
            "批量前先跑 dry-run 预检。\n",
            encoding="utf-8",
        )
        (skill / "references" / "routing-table.md").write_text(
            "# 路由表\n\n"
            "| 渠道 | 触发词 | 子 skill | 关键差异（一句话） | 协议文档 |\n"
            "|---|---|---|---|---|\n"
            "| 真渠道 | real | `ml-real-channel` | 按次计费 | `channels/real.md` |\n",
            encoding="utf-8",
        )
        sibling = root / "ml-real-channel"
        if not sibling.exists():
            sibling.mkdir()
            (sibling / "SKILL.md").write_text(
                "---\nname: ml-real-channel\ndescription: 占位渠道线\n---\n",
                encoding="utf-8",
            )
        return skill

    needle = "缺少「进入 / 跳过条件」列"

    thin = build("ml-thin", "| Phase | 干什么 | 产出物 | 闸门 |")
    out_thin = _run(thin)
    if needle not in out_thin:
        failures.append("总览表只有阶段名（无进入条件列），却没报颗粒度不足")

    good = build("ml-good", "| Phase | 干什么 | 进入 / 跳过条件 | 产出物 | 闸门 |")
    out_good = _run(good)
    if needle in out_good:
        failures.append("总览表已带「进入 / 跳过条件」列，却被误报")

    print(out_thin.rstrip())
    print(f"· 主线颗粒度：未达标 {len(failures)} 项")
    return failures


def _run(skill: Path) -> str:
    proc = run_validator(skill)
    return (proc.stdout or "") + (proc.stderr or "")


def case_empty_body(root: Path) -> list:
    """空壳样本：只有 frontmatter、没有正文 —— 必须 FAIL，不能直接放行。

    回归自一次真实漏洞：`validate()` 曾用 `if not body` 判断，
    把「正文为空」误当成「frontmatter 不合法」，
    结果一个空壳 skill 会把全部治理检查整体跳过。
    """
    skill = root / "hollow-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: hollow-skill\ndescription: 空壳样本\n---\n", encoding="utf-8"
    )
    proc = run_validator(skill)
    out = (proc.stdout or "") + (proc.stderr or "")

    failures = []
    if "PASS" in out:
        failures.append("空壳 skill（无正文）竟然 PASS —— 治理检查被整体跳过了")
    if "缺少：复盘与迭代规则" not in out:
        failures.append("空壳 skill 未触发治理检查")

    print(out.rstrip())
    print(f"· 空壳样本：未达标 {len(failures)} 项")
    return failures


def main() -> int:
    if not VALIDATOR.is_file():
        print(f"找不到校验器：{VALIDATOR}")
        return 2

    root = Path(tempfile.mkdtemp(prefix="validate-skill-fixture-"))
    try:
        failures = (
            case_messy(root)
            + case_long_but_light(root)
            + case_mainline_granularity(root)
            + case_empty_body(root)
        )
        print("-" * 60)
        if failures:
            print(f"FAIL ｜ {len(failures)} 项未达预期：")
            for item in failures:
                print("  - " + item)
            return 1
        total = len(EXPECTED_ERRORS) + len(EXPECTED_WARNINGS)
        print(
            f"PASS ｜ 反面样本按预期触发 {total} 项检查，"
            "长文档样本（字数门槛已废）逐项断言，主线颗粒度样本双向断言，"
            "空壳样本 2 项断言，全部通过。"
        )
        return 0
    finally:
        shutil.rmtree(root, ignore_errors=True)
        print(f"fixture 已清理：{not root.exists()}")


if __name__ == "__main__":
    sys.exit(main())
