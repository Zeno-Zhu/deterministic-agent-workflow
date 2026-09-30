#!/usr/bin/env python3
"""回归测试：validate-skill.py 的反面样本。

用途：确认各项检查**真的会报错**。改了 validate-skill.py 的检查规则后必须跑它 ——
只对自身跑 `PASS` 不能证明检查有效（把检查全删了也会 PASS）。

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
]

#: 预期只给 WARN 的项
EXPECTED_WARNINGS = [
    "疑似内联了渠道专属参数",
]


def build_bad_skill(root: Path) -> Path:
    """故意塞满违规项，产出一个「该被 FAIL」的中控 skill。"""
    skill = root / "bad-skill"
    for sub in ("scripts", "references", "pitfalls", "logs", "node_modules/leftpad"):
        (skill / sub).mkdir(parents=True, exist_ok=True)

    filler = "\n".join(f"第 {i} 行填充" for i in range(120))
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


def main() -> int:
    if not VALIDATOR.is_file():
        print(f"找不到校验器：{VALIDATOR}")
        return 2

    root = Path(tempfile.mkdtemp(prefix="validate-skill-fixture-"))
    try:
        skill = build_bad_skill(root)
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(skill)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
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
        print("-" * 60)
        if failures:
            print(f"FAIL ｜ {len(failures)} 项未达预期：")
            for item in failures:
                print("  - " + item)
            return 1
        total = len(EXPECTED_ERRORS) + len(EXPECTED_WARNINGS)
        print(f"PASS ｜ 反面样本按预期触发 {total} 项检查，退出码 1。")
        return 0
    finally:
        shutil.rmtree(root, ignore_errors=True)
        print(f"fixture 已清理：{not root.exists()}")


if __name__ == "__main__":
    sys.exit(main())
