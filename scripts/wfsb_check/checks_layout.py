#!/usr/bin/env python3
"""组 4 前半（4.1–4.8）：文件布局与知识分层。

规则权威：references/file-governance.md
"""

from __future__ import annotations

import re
from pathlib import Path

from .constants import (
    ARTIFACT_DIRS,
    COLD_DECLARATION_MARKERS,
    COLD_PATH_TOKENS,
    DRAFT_GLOBS,
    DRAFT_NAME_RE,
    IGNORED_FILES,
    LOAD_FIRST_RE,
    SKIP_DIRS,
    UNPROMOTED_TEST_RE,
    has_any,
    is_cold_dir,
    iter_files,
    read_text,
)


def check_files(skill_dir: Path, body: str, errors: list, warnings: list,
                summary: dict) -> None:
    files = list(iter_files(skill_dir))
    summary["files"] = len(files)

    _check_residue(skill_dir, files, errors)
    _check_artifact_dirs(skill_dir, errors)
    _check_ungraduated_tests(skill_dir, errors, summary)
    _check_draft_names(skill_dir, files, errors, warnings)
    _check_tests_dir(skill_dir, body, errors, warnings, summary)
    _check_cold_dirs(skill_dir, errors, summary)
    _check_indexes(skill_dir, errors, warnings)
    _check_load_first(body, errors)


def _check_residue(skill_dir: Path, files: list, errors: list) -> None:
    """4.1 草稿 / 版本 / 构建残留。"""
    drafts = set()
    for path in files:
        for pattern in DRAFT_GLOBS:
            if path.match(pattern):
                drafts.add(path.relative_to(skill_dir).as_posix())
                break
    if drafts:
        errors.append(
            "存在草稿/版本残留（版本应交给 git）：" + "、".join(sorted(drafts))
        )


def _check_artifact_dirs(skill_dir: Path, errors: list) -> None:
    """4.2 运行产物目录。"""
    artifact_dirs = set()
    for name in ARTIFACT_DIRS:
        for hit in skill_dir.rglob(name):
            if hit.is_dir() and not any(p in SKIP_DIRS for p in hit.parts):
                artifact_dirs.add(hit.relative_to(skill_dir).as_posix())
    if artifact_dirs:
        errors.append(
            "存在运行产物/依赖目录，不属于可复用能力："
            + "、".join(sorted(artifact_dirs))
        )


def _check_ungraduated_tests(skill_dir: Path, errors: list, summary: dict) -> None:
    """4.3 scripts/ 下未毕业的 test。"""
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.is_dir():
        return
    ungraduated = []
    for path in sorted(scripts_dir.rglob("*")):
        if not path.is_file() or any(p in SKIP_DIRS for p in path.parts):
            continue
        if path.name in IGNORED_FILES:
            continue
        summary["scripts"].append(path.relative_to(skill_dir).as_posix())
        if UNPROMOTED_TEST_RE.search(path.name):
            ungraduated.append(path.relative_to(skill_dir).as_posix())
    if ungraduated:
        errors.append(
            "scripts/ 下存在未毕业的测试代码（应转正去掉 test 名，或删除）："
            + "、".join(ungraduated)
        )


def _check_draft_names(skill_dir: Path, files: list, errors: list,
                       warnings: list) -> None:
    """4.4 其余位置的草稿命名。"""
    scripts_dir = skill_dir / "scripts"
    draft_named = set()
    for path in files:
        if scripts_dir in path.parents:
            continue
        if DRAFT_NAME_RE.search(path.name):
            draft_named.add(path.relative_to(skill_dir).as_posix())
    if draft_named:
        warnings.append("存在草稿命名文件：" + "、".join(sorted(draft_named)))


def _check_tests_dir(skill_dir: Path, body: str, errors: list, warnings: list,
                     summary: dict) -> None:
    """4.5 tests/ 登记（空壳要删；非空要说明转正规则）。"""
    tests_dir = skill_dir / "tests"
    if not tests_dir.is_dir():
        return
    summary["tests"] = [
        p.relative_to(skill_dir).as_posix()
        for p in sorted(tests_dir.rglob("*"))
        if p.is_file() and not any(q in SKIP_DIRS for q in p.parts)
    ]
    if not summary["tests"]:
        errors.append("tests/ 是空目录：删掉它，不要为结构完整留空壳。")
    elif not has_any(body, (r"tests?/", r"毕业", r"转正", r"promote")):
        warnings.append("存在 tests/ 但 SKILL.md 未说明测试的转正/删除规则。")


def _check_cold_dirs(skill_dir: Path, errors: list, summary: dict) -> None:
    """4.6 冷存层 / 死稿层自声明 README。"""
    for child in sorted(skill_dir.iterdir()):
        if not child.is_dir() or child.name in SKIP_DIRS or not is_cold_dir(child):
            continue
        summary["cold_dirs"].append(child.name)
        readme = None
        for candidate in ("README.md", "_README.md", "readme.md"):
            if (child / candidate).is_file():
                readme = child / candidate
                break
        if readme is None:
            errors.append(
                f"冷存/死稿目录 {child.name}/ 缺少自声明 README.md"
                "（第一段须写明「默认不读」）。"
            )
            continue
        head = read_text(readme)[:1500]
        markers = tuple(re.escape(m) for m in COLD_DECLARATION_MARKERS)
        if not has_any(head, markers):
            errors.append(
                f"{child.name}/README.md 未声明「默认不读」："
                "第一段第一句必须写清什么情况下才读。"
            )


def _check_indexes(skill_dir: Path, errors: list, warnings: list) -> None:
    """4.7 冷存层索引存在性。"""
    pitfalls = skill_dir / "pitfalls"
    if pitfalls.is_dir():
        index = pitfalls / "INDEX.md"
        if not index.is_file():
            errors.append("存在 pitfalls/ 但没有 pitfalls/INDEX.md（冷存层必须有索引）。")
        else:
            index_text = read_text(index)
            if "| ID |" not in index_text:
                errors.append(
                    "pitfalls/INDEX.md 缺少固定列头"
                    " `| ID | 一句话现象 | 命中 | 处置 | 详情 | 通用化 |`。"
                )
            if not has_any(index_text, (r"命中", r"hits?")):
                warnings.append("pitfalls/INDEX.md 未识别到「命中」计数列。")
    logs = skill_dir / "logs"
    if logs.is_dir() and not (logs / "README.md").is_file():
        errors.append("存在 logs/ 但没有 logs/README.md（须写清保留策略）。")


def _check_load_first(body: str, errors: list) -> None:
    """4.8 Load First 不得引用冷存 / 死稿层。"""
    load_first = LOAD_FIRST_RE.search(body)
    if not load_first:
        return
    segment = load_first.group("body")
    hit_tokens = [t for t in COLD_PATH_TOKENS if t in segment]
    if hit_tokens:
        errors.append(
            "Load First 引用了冷存/死稿层路径（"
            + "、".join(hit_tokens)
            + "）：Load First 只允许引用 H / W 层。"
        )
