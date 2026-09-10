#!/usr/bin/env python3
"""Mechanical checks for a produced or upgraded Codex SKILL.md."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
FIELD_RE = re.compile(r"^(name|description):\s*(.+)$", re.MULTILINE)


def has_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE | re.DOTALL) for pattern in patterns)


def validate(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.is_file():
        return [f"文件不存在：{path}"], warnings

    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.search(text)
    if not match:
        return ["缺少有效的 YAML frontmatter。"], warnings

    fields = dict(FIELD_RE.findall(match.group(1)))
    name = fields.get("name", "").strip().strip('"\'')
    description = fields.get("description", "").strip().strip('"\'')

    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        errors.append("name 必须使用小写字母、数字和连字符。")
    if len(name) > 64:
        errors.append("name 不能超过 64 个字符。")
    if not description:
        errors.append("description 不能为空。")

    body = text[match.end() :]
    checks = {
        "目标项目中的新任务文件夹": (
            r"目标项目.{0,80}(新|新的).{0,20}(任务文件夹|任务目录)",
            r"target project.{0,80}new.{0,20}(task folder|task directory)",
        ),
        "任务产物不得写入 Skill 目录": (
            r"(绝不|禁止|不能|不得).{0,60}(写入|进入|承载).{0,30}Skill.{0,15}目录",
            r"(never|must not|do not).{0,50}(write|store).{0,40}skill directory",
            r"Skill.{0,15}目录.{0,40}(绝不|禁止|不能|不得).{0,30}(任务|输出|产物|运行数据)",
        ),
        "脚本使用显式输出路径": (
            r"脚本.{0,40}(显式|明确).{0,15}输出路径",
            r"script.{0,40}explicit output path",
        ),
        "复盘与迭代规则": (
            r"复盘与迭代",
            r"review and iteration",
            r"evidence-driven evolution",
        ),
        "暂存后审阅再采用": (
            r"(run|候选).{0,60}(暂存|stage).{0,100}(审阅|review).{0,60}(adopt|采用)",
            r"stage.{0,100}review.{0,100}adopt",
        ),
    }

    for label, patterns in checks.items():
        if not has_any(body, patterns):
            errors.append(f"缺少：{label}。")

    if not has_any(body, (r"held[- ]out", r"留出")):
        warnings.append("未识别到 held-out / 留出集门禁。")
    if not has_any(body, (r"dry-run",)):
        warnings.append("未识别到 dry-run 预检。")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="检查 SKILL.md 的 frontmatter、工作区隔离和受控迭代规则。"
    )
    parser.add_argument("skill", type=Path, help="目标 SKILL.md 或 Skill 目录")
    args = parser.parse_args()

    target = args.skill.expanduser().resolve()
    if target.is_dir():
        target = target / "SKILL.md"

    errors, warnings = validate(target)
    for item in warnings:
        print(f"WARN: {item}")
    for item in errors:
        print(f"ERROR: {item}")

    if errors:
        print(f"FAIL: {target}")
        return 1

    print(f"PASS: {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
