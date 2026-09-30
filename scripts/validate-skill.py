#!/usr/bin/env python3
"""Mechanical checks for a produced or upgraded Codex Skill. —— CLI 入口

四组检查，共 18 项（全部 L1 机械检查，无 LLM，仅标准库，Python 3.9+）：

  1. frontmatter   name / description 合法
  2. workspace     Skill 目录不承载任务产物；脚本用显式输出路径
  3. iteration     受控迭代：复盘与迭代 + 暂存后审阅再采用
  4. governance    4.1 草稿残留 / 4.2 运行产物 / 4.3 未毕业 test /
                   4.4 草稿命名 / 4.5 tests 登记 / 4.6 冷存层自声明 /
                   4.7 索引 / 4.8 Load First 不碰冷存层 /
                   4.9 文档三件套 / 4.10 SKILL.md 读取预算 /
                   4.11 中控路由死路由 / 4.12 内联渠道参数 /
                   4.13 scripts 单文件行数 / 4.14 硬编码密钥
   规则权威：references/file-governance.md、multi-platform-routing.md、
             code-engineering.md

实现拆在 `wfsb_check/` 包内（每个文件 ≤ 300 行，见 code-engineering §0 第 7 条）：
  constants.py       常量、正则、通用工具
  checks_core.py     组 1–3
  checks_layout.py   4.1–4.8
  checks_quality.py  4.9–4.14

Usage:
    python3 validate-skill.py <skill-dir | SKILL.md>

Exit code 0 = PASS, 1 = FAIL.
"""

from __future__ import annotations

import sys

# ★ 必须早于任何 wfsb_check 导入：否则解释器会写出
#   scripts/wfsb_check/__pycache__，而下一次运行就被 4.2「运行产物目录」判 FAIL。
sys.dont_write_bytecode = True

import argparse                    # noqa: E402
from pathlib import Path           # noqa: E402

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from wfsb_check.checks_core import (      # noqa: E402
    check_frontmatter,
    check_iteration,
    check_workspace,
)
from wfsb_check.checks_layout import check_files       # noqa: E402
from wfsb_check.checks_quality import check_quality    # noqa: E402
from wfsb_check.constants import read_text             # noqa: E402


def validate(target: Path) -> tuple:
    errors: list = []
    warnings: list = []
    summary: dict = {
        "files": 0, "cold_dirs": [], "tests": [], "scripts": [],
    }

    if target.is_dir():
        skill_dir, skill_md = target, target / "SKILL.md"
    else:
        skill_dir, skill_md = target.parent, target

    if not skill_md.is_file():
        return [f"文件不存在：{skill_md}"], warnings, summary

    body = check_frontmatter(read_text(skill_md), errors, warnings)
    if body is None:          # frontmatter 不合法：后续检查没有可靠上下文
        return errors, warnings, summary

    check_workspace(body, errors)
    check_iteration(body, errors, warnings)
    check_files(skill_dir, body, errors, warnings, summary)
    check_quality(skill_dir, skill_md, body, errors, warnings, summary)

    return errors, warnings, summary


def _report(summary: dict) -> None:
    cold = summary.get("cold_dirs") or []
    routes = summary.get("routes") or []
    print(
        "INFO: 文件 {files} 个｜references {ref} 份｜scripts {sc} 个｜"
        "tests {ts} 个｜冷存层 {cold}｜路由 {rt}｜README {r}｜ARCHITECTURE {a}｜"
        "SKILL.md {ln} 行 / {ch} 字符".format(
            files=summary.get("files", 0),
            ref=summary.get("ref_count", 0),
            sc=len(summary.get("scripts") or []),
            ts=len(summary.get("tests") or []),
            cold=("/".join(cold) if cold else "无"),
            rt=(str(len(routes)) + " 条" if routes else "无"),
            r="有" if summary.get("has_readme") else "无",
            a="有" if summary.get("has_arch") else "无",
            ln=summary.get("line_count", 0),
            ch=summary.get("char_count", 0),
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="检查 Skill 的 frontmatter、工作区隔离、受控迭代与文件治理。"
    )
    parser.add_argument("skill", type=Path, help="目标 Skill 目录或 SKILL.md")
    args = parser.parse_args()

    target = args.skill.expanduser().resolve()
    errors, warnings, summary = validate(target)
    skill_md = target / "SKILL.md" if target.is_dir() else target

    for item in warnings:
        print(f"WARN: {item}")
    for item in errors:
        print(f"ERROR: {item}")

    if summary:
        _report(summary)

    if errors:
        print(f"FAIL: {skill_md}")
        return 1

    print(f"PASS: {skill_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
