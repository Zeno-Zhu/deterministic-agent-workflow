#!/usr/bin/env python3
"""组 1–3：frontmatter / 工作区隔离 / 受控迭代。

规则权威：references/vnext-contracts.md
"""

from __future__ import annotations

import re

from .constants import FIELD_RE, FRONTMATTER_RE, has_any


def check_frontmatter(text: str, errors: list, warnings: list):
    """组 1。返回 frontmatter 之后的正文；**frontmatter 缺失时返回 None**。

    注意：返回空串和返回 None 含义不同 —— 前者是「正文确实为空」，
    后者是「frontmatter 不合法」。校验器只在前者继续跑治理检查，
    否则会出现「只写 frontmatter 的空壳 skill 反而全项通过」的漏洞。
    """
    match = FRONTMATTER_RE.search(text)
    if not match:
        errors.append("缺少有效的 YAML frontmatter。")
        return None

    fields = dict(FIELD_RE.findall(match.group(1)))
    name = fields.get("name", "").strip().strip("\"'")
    description = fields.get("description", "").strip().strip("\"'")

    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        errors.append("name 必须使用小写字母、数字和连字符。")
    if len(name) > 64:
        errors.append("name 不能超过 64 个字符。")
    if not description:
        errors.append("description 不能为空。")
    if len(description) > 1024:
        warnings.append("description 超过 1024 字符，可能挤占触发判断预算。")

    return text[match.end():]


def check_workspace(body: str, errors: list) -> None:
    """组 2。任务产物不得落进 Skill 目录。"""
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
    }
    for label, patterns in checks.items():
        if not has_any(body, patterns):
            errors.append(f"缺少：{label}。")


def check_iteration(body: str, errors: list, warnings: list) -> None:
    """组 3。受控迭代：证据驱动 + 暂存后审阅再采用。"""
    checks = {
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
