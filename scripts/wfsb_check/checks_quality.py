#!/usr/bin/env python3
"""组 4 后半（4.9–4.14）：文档、预算、中控路由、代码规模、密钥。

规则权威：file-governance.md / multi-platform-routing.md / code-engineering.md
"""

from __future__ import annotations

from pathlib import Path

from .constants import (
    ARCHITECTURE_NAMES,
    CODE_EXTS,
    CODE_FILE_ERROR_LINES,
    CODE_FILE_WARN_LINES,
    CODE_SCALE_DECLARATION,
    INLINED_CHANNEL_PARAM_RE,
    README_REQUIRED_OVER_LINES,
    ROUTING_TABLE_REL,
    SECRET_PATTERNS,
    SECRET_PLACEHOLDER_RE,
    SKILL_MD_ERROR_CHARS,
    SKILL_MD_ERROR_LINES,
    SKILL_MD_WARN_CHARS,
    SKILL_MD_WARN_LINES,
    SKILL_NAME_RE,
    arch_text,
    iter_text_files,
    read_text,
)


def check_quality(skill_dir: Path, skill_md: Path, body: str, errors: list,
                  warnings: list, summary: dict) -> None:
    source = read_text(skill_md)
    summary["line_count"] = len(source.splitlines())
    summary["char_count"] = len(source)

    declared_arch = arch_text(skill_dir)
    _check_docs_trio(skill_dir, summary, errors)
    _check_budget(declared_arch, summary, errors, warnings)
    _check_routing(skill_dir, body, errors, warnings, summary)
    _check_code_scale(skill_dir, declared_arch, summary, errors, warnings)
    _check_secrets(skill_dir, errors)


def _check_docs_trio(skill_dir: Path, summary: dict, errors: list) -> None:
    """4.9 文档三件套：SKILL.md 永远在，README / ARCHITECTURE 按规模配。"""
    has_readme = (skill_dir / "README.md").is_file()
    has_arch = any((skill_dir / n).is_file() for n in ARCHITECTURE_NAMES)
    refs_dir = skill_dir / "references"
    ref_count = len(list(refs_dir.glob("*.md"))) if refs_dir.is_dir() else 0
    summary["ref_count"] = ref_count
    summary["has_readme"] = has_readme
    summary["has_arch"] = has_arch

    if summary["line_count"] > README_REQUIRED_OVER_LINES and not has_readme:
        errors.append(
            f"SKILL.md 有 {summary['line_count']} 行"
            f"（> {README_REQUIRED_OVER_LINES}），"
            "必须有 README.md（给人看 + 给 AI 速览）。"
        )
    if ((skill_dir / "scripts").is_dir() or ref_count >= 2) and not has_arch:
        errors.append(
            "已有 scripts/ 或 ≥2 份 references/，必须有 ARCHITECTURE.md"
            "（文件地图 + 现象→查哪里 + 改动影响面 + 校验重建）。"
        )


def _check_budget(declared_arch: str, summary: dict, errors: list,
                  warnings: list) -> None:
    """4.10 SKILL.md 读取预算（按触发频率分档，file-governance §7）。"""
    chars, lines = summary["char_count"], summary["line_count"]
    if chars > SKILL_MD_ERROR_CHARS or lines > SKILL_MD_ERROR_LINES:
        errors.append(
            f"SKILL.md 超出读取预算硬线：{chars} 字符 / {lines} 行"
            f"（硬线 {SKILL_MD_ERROR_CHARS} 字符 / {SKILL_MD_ERROR_LINES} 行）。"
            "把细节下沉到 references/，SKILL.md 只留触发 + 主干 + Gate + 硬规则。"
        )
        return
    if chars > SKILL_MD_WARN_CHARS or lines > SKILL_MD_WARN_LINES:
        # 若 skill 已在 ARCHITECTURE.md 显式声明自己的预算档位，就不再唠叨
        if "读取预算档" in declared_arch:
            return
        warnings.append(
            f"SKILL.md {chars} 字符 / {lines} 行，已超「每日多次」档"
            f"（{SKILL_MD_WARN_CHARS} 字符 / {SKILL_MD_WARN_LINES} 行）。"
            "确认它是否属于「每周数次或更少」档，否则下沉到 references/；"
            "确认后在 ARCHITECTURE.md 写一行 `读取预算档：<档位>`。"
        )


def _check_routing(skill_dir: Path, body: str, errors: list, warnings: list,
                   summary: dict) -> None:
    """4.11–4.12 中控路由（multi-platform-routing §3）。"""
    routing_table = skill_dir / ROUTING_TABLE_REL
    if not routing_table.is_file():
        if "routing-table.md" in body:
            errors.append(
                f"SKILL.md 引用了 {ROUTING_TABLE_REL}，但该文件不存在"
                "（中控必须有路由表）。"
            )
        return

    table_text = read_text(routing_table)
    if "| 渠道 |" not in table_text:
        errors.append(
            f"{ROUTING_TABLE_REL} 缺少固定列头"
            " `| 渠道 | 触发词 | 子 skill | 关键差异（一句话） | 协议文档 |`。"
        )
    names = set()
    for row in table_text.splitlines():
        if row.lstrip().startswith("|"):
            names.update(SKILL_NAME_RE.findall(row))
    summary["routes"] = sorted(names)

    siblings = {
        d.name for d in skill_dir.parent.iterdir()
        if d.is_dir() and d.name != skill_dir.name and (d / "SKILL.md").is_file()
    }
    if not siblings:
        warnings.append(
            f"同级目录没有其他 skill，无法校验 {ROUTING_TABLE_REL} 的死路由。"
        )
    else:
        dead = sorted(n for n in names if n not in siblings)
        if dead:
            errors.append(
                "路由表存在死路由（子 skill 不存在于同级目录）：" + "、".join(dead)
            )

    if INLINED_CHANNEL_PARAM_RE.search(body):
        warnings.append(
            "SKILL.md 疑似内联了渠道专属参数（命中「N 张 / 按秒 / 按次 / ¥N」）。"
            "中控只做路由：参数上限、计费、字段名应下沉到对应渠道 skill。"
        )


def _check_code_scale(skill_dir: Path, declared_arch: str, summary: dict,
                      errors: list, warnings: list) -> None:
    """4.13 scripts/ 单文件行数（code-engineering §0 第 7 条）。"""
    for rel in summary.get("scripts") or []:
        path = skill_dir / rel
        if path.suffix.lower() not in CODE_EXTS or not path.is_file():
            continue
        count = len(read_text(path).splitlines())
        if count > CODE_FILE_ERROR_LINES:
            errors.append(
                f"scripts/ 下 {rel} 有 {count} 行，超过硬线"
                f" {CODE_FILE_ERROR_LINES} 行：必须拆成 ≤300 行的模块"
                "（单文件无限膨胀会让后续 AI 无法定位，见 code-engineering §3）。"
            )
        elif count > CODE_FILE_WARN_LINES:
            # 逐文件例外：ARCHITECTURE.md 里同时出现标记和该相对路径才算声明过
            if CODE_SCALE_DECLARATION in declared_arch and rel in declared_arch:
                continue
            warnings.append(
                f"scripts/ 下 {rel} 有 {count} 行，超过软线"
                f" {CODE_FILE_WARN_LINES} 行：拆成按职责分开的模块；若确实不该拆，"
                f"在 ARCHITECTURE.md 写一行 `{CODE_SCALE_DECLARATION}：{rel} —— <理由>`。"
            )


def _check_secrets(skill_dir: Path, errors: list) -> None:
    """4.14 硬编码密钥 / 令牌（code-engineering §10 第 11 条）。

    只报位置，不回显值 —— 报告本身不该成为泄露渠道。
    """
    hits = []
    for path in iter_text_files(skill_dir):
        rel = path.relative_to(skill_dir).as_posix()
        for lineno, line in enumerate(read_text(path).splitlines(), 1):
            for label, regex, group in SECRET_PATTERNS:
                match = regex.search(line)
                if not match:
                    continue
                value = match.group(group) if group else match.group(0)
                if SECRET_PLACEHOLDER_RE.search(value):
                    continue
                hits.append(f"{rel}:{lineno}（{label}）")
                break
    if hits:
        errors.append(
            "疑似硬编码密钥/令牌（值不回显）：" + "、".join(hits)
            + " —— 改用环境变量或 config/，并把已泄露的值作废重签。"
        )
