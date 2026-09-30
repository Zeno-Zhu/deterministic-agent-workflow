#!/usr/bin/env python3
"""Mechanical checks for a produced or upgraded Codex Skill.

Five check groups (all L1 mechanical, no LLM, stdlib only, Python 3.9+):

  1. frontmatter        name / description 合法
  2. workspace          Skill 目录不承载任务产物；脚本用显式输出路径
  3. iteration          受控迭代：复盘与迭代 + 暂存后审阅再采用
  4. file governance    草稿残留 / 未毕业 test / 冷存层自声明 / 索引 / 文档三件套 /
                        SKILL.md 读取预算分档
                        （规则权威：references/file-governance.md）
  5. multi-platform     中控路由表 / 死路由 / 疑似内联渠道参数
                        （规则权威：references/multi-platform-routing.md）

Usage:
    python3 validate-skill.py <skill-dir | SKILL.md>

Exit code 0 = PASS, 1 = FAIL.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
FIELD_RE = re.compile(r"^(name|description):\s*(.+)$", re.MULTILINE)
LOAD_FIRST_RE = re.compile(
    r"^##\s*(?:Load First|先读|必读|加载顺序)\s*$(?P<body>.*?)(?=^##\s|\Z)",
    re.MULTILINE | re.DOTALL,
)

# ---------------------------------------------------------------- governance

#: 草稿 / 版本 / 构建残留：一律不允许留在 Skill 里（file-governance §8）
DRAFT_GLOBS = (
    "*.bak",
    "*.bak-*",
    "*.orig",
    "*~",
    "*.tmp",
    "*.pyc",
    ".DS_Store",
    "Thumbs.db",
)

#: 运行产物目录：不是可复用能力（file-governance §5、§8）
ARTIFACT_DIRS = (
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
    "dist",
    "build",
    "chatgpt-out",
    ".mypy_cache",
    ".ruff_cache",
)

#: 测试 / 试验 / 探针文件名：只能待在 tests/，出现在 scripts/ 就是没毕业（§4）
UNPROMOTED_TEST_RE = re.compile(
    r"^(?:test|try|probe|tmp|experiment|e2e|smoke)[_-]"
    r"|[_-](?:test|try|probe|tmp|experiment|e2e|smoke)\b"
    r"|\.(?:test|spec|smoke|e2e)\.",
    re.IGNORECASE,
)

#: 草稿命名标记：不得出现在任何非 scripts/ 文件名里（§8）
DRAFT_NAME_RE = re.compile(
    r"^(?:tmp[_-]|new[_-]|old[_-]|draft[_-]|wip[_-])|"
    r"(?:[_-](?:new|old|draft|wip|copy|副本))\.",
    re.IGNORECASE,
)

#: 冷存层 / 死稿层目录的特征名（§1）
COLD_DIR_NAMES = frozenset(
    {"pitfalls", "logs", "history", "archive", "cold", "dead", "废案", "旧版", "归档"}
)

#: 自声明 README 里必须出现的「默认不读」标记（§1 硬规则 2）
COLD_DECLARATION_MARKERS = (
    "默认不读",
    "禁止读取",
    "禁止读",
    "do not read",
    "never read",
    "read only when",
)

#: `SKILL.md` 的 Load First 里不允许出现的冷存路径片段（§1 硬规则 4）
COLD_PATH_TOKENS = (
    "pitfalls/",
    "logs/",
    "history/",
    "archive/",
    "_归档",
    "_旧版",
    "_废案",
    "cold/",
    "dead/",
)

#: 文档三件套阈值（§6）
README_REQUIRED_OVER_LINES = 80
ARCHITECTURE_NAMES = ("ARCHITECTURE.md", "TECH.md", "TECHNICAL.md", "技术文档.md")

#: SKILL.md 读取预算（file-governance §7「按触发频率分档」）
SKILL_MD_WARN_CHARS = 8000     # 每日多次档
SKILL_MD_WARN_LINES = 300
SKILL_MD_ERROR_CHARS = 12000   # 每周数次档，母工作流上限
SKILL_MD_ERROR_LINES = 400

#: 中控路由检查（multi-platform-routing §3）
ROUTING_TABLE_REL = "references/routing-table.md"
SKILL_NAME_RE = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`")
#: 疑似内联渠道专属参数（中控不该出现）：数值+张 / 计费口径 / 货币金额
INLINED_CHANNEL_PARAM_RE = re.compile(
    r"\d+\s*张|按秒|按次|按小时|[¥$￥]\s*\d", re.IGNORECASE
)

SKIP_DIRS = frozenset({".git"})
IGNORED_FILES = frozenset({"_user_meta.json"})


def has_any(text: str, patterns) -> bool:
    return any(re.search(p, text, re.IGNORECASE | re.DOTALL) for p in patterns)


def iter_files(root: Path):
    """Yield every file under root, skipping VCS internals."""
    for path in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.name not in IGNORED_FILES:
            yield path


def is_cold_dir(path: Path) -> bool:
    name = path.name
    if name in COLD_DIR_NAMES:
        return True
    return name.startswith("_") and not name.startswith("__")


# ---------------------------------------------------------------- checks

def check_frontmatter(text: str, errors: list, warnings: list) -> str:
    match = FRONTMATTER_RE.search(text)
    if not match:
        errors.append("缺少有效的 YAML frontmatter。")
        return text

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


def check_file_governance(skill_dir: Path, skill_md: Path, body: str,
                          errors: list, warnings: list) -> dict:
    """Group 4 —— 文件治理。规则权威：references/file-governance.md"""
    summary = {"files": 0, "cold_dirs": [], "tests": [], "scripts": []}

    files = list(iter_files(skill_dir))
    summary["files"] = len(files)

    # --- 4.1 草稿 / 版本 / 构建残留
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

    # --- 4.2 运行产物目录
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

    # --- 4.3 scripts/ 下未毕业的 test
    scripts_dir = skill_dir / "scripts"
    ungraduated = []
    if scripts_dir.is_dir():
        for path in sorted(scripts_dir.rglob("*")):
            if not path.is_file() or any(p in SKIP_DIRS for p in path.parts):
                continue
            summary["scripts"].append(path.relative_to(skill_dir).as_posix())
            if UNPROMOTED_TEST_RE.search(path.name):
                ungraduated.append(path.relative_to(skill_dir).as_posix())
    if ungraduated:
        errors.append(
            "scripts/ 下存在未毕业的测试代码（应转正去掉 test 名，或删除）："
            + "、".join(ungraduated)
        )

    # --- 4.4 其余位置的草稿命名
    draft_named = set()
    for path in files:
        if scripts_dir in path.parents:
            continue
        if DRAFT_NAME_RE.search(path.name):
            draft_named.add(path.relative_to(skill_dir).as_posix())
    if draft_named:
        warnings.append("存在草稿命名文件：" + "、".join(sorted(draft_named)))

    # --- 4.5 tests/ 登记
    tests_dir = skill_dir / "tests"
    if tests_dir.is_dir():
        summary["tests"] = [
            p.relative_to(skill_dir).as_posix()
            for p in sorted(tests_dir.rglob("*"))
            if p.is_file() and not any(q in SKIP_DIRS for q in p.parts)
        ]
        if not summary["tests"]:
            errors.append("tests/ 是空目录：删掉它，不要为结构完整留空壳。")
        elif not has_any(body, (r"tests?/", r"毕业", r"转正", r"promote")):
            warnings.append("存在 tests/ 但 SKILL.md 未说明测试的转正/删除规则。")

    # --- 4.6 冷存层 / 死稿层自声明
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
        head = readme.read_text(encoding="utf-8", errors="replace")[:1500]
        markers = tuple(re.escape(m) for m in COLD_DECLARATION_MARKERS)
        if not has_any(head, markers):
            errors.append(
                f"{child.name}/README.md 未声明「默认不读」："
                "第一段第一句必须写清什么情况下才读。"
            )

    # --- 4.7 索引存在性
    pitfalls = skill_dir / "pitfalls"
    if pitfalls.is_dir():
        index = pitfalls / "INDEX.md"
        if not index.is_file():
            errors.append("存在 pitfalls/ 但没有 pitfalls/INDEX.md（冷存层必须有索引）。")
        else:
            index_text = index.read_text(encoding="utf-8", errors="replace")
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

    # --- 4.8 Load First 不得引用冷存层
    load_first = LOAD_FIRST_RE.search(body)
    if load_first:
        segment = load_first.group("body")
        hit_tokens = [t for t in COLD_PATH_TOKENS if t in segment]
        if hit_tokens:
            errors.append(
                "Load First 引用了冷存/死稿层路径（"
                + "、".join(hit_tokens)
                + "）：Load First 只允许引用 H / W 层。"
            )

    # --- 4.9 文档三件套
    line_count = len(skill_md.read_text(encoding="utf-8", errors="replace").splitlines())
    char_count = len(skill_md.read_text(encoding="utf-8", errors="replace"))
    has_readme = (skill_dir / "README.md").is_file()
    has_arch = any((skill_dir / n).is_file() for n in ARCHITECTURE_NAMES)
    refs_dir = skill_dir / "references"
    ref_count = len(list(refs_dir.glob("*.md"))) if refs_dir.is_dir() else 0

    if line_count > README_REQUIRED_OVER_LINES and not has_readme:
        errors.append(
            f"SKILL.md 有 {line_count} 行（> {README_REQUIRED_OVER_LINES}），"
            "必须有 README.md（给人看 + 给 AI 速览）。"
        )
    if (scripts_dir.is_dir() or ref_count >= 2) and not has_arch:
        errors.append(
            "已有 scripts/ 或 ≥2 份 references/，必须有 ARCHITECTURE.md"
            "（文件地图 + 现象→查哪里 + 改动影响面 + 校验重建）。"
        )

    # --- 4.10 SKILL.md 读取预算（按触发频率分档，见 file-governance §7）
    if char_count > SKILL_MD_ERROR_CHARS or line_count > SKILL_MD_ERROR_LINES:
        errors.append(
            f"SKILL.md 超出读取预算硬线：{char_count} 字符 / {line_count} 行"
            f"（硬线 {SKILL_MD_ERROR_CHARS} 字符 / {SKILL_MD_ERROR_LINES} 行）。"
            "把细节下沉到 references/，SKILL.md 只留触发 + 主干 + Gate + 硬规则。"
        )
    elif char_count > SKILL_MD_WARN_CHARS or line_count > SKILL_MD_WARN_LINES:
        # 若 skill 已在 ARCHITECTURE.md 显式声明自己的预算档位，就不再唠叨
        declared = ""
        for name in ARCHITECTURE_NAMES:
            candidate = skill_dir / name
            if candidate.is_file():
                declared = candidate.read_text(encoding="utf-8", errors="replace")
                break
        if "读取预算档" not in declared:
            warnings.append(
                f"SKILL.md {char_count} 字符 / {line_count} 行，已超「每日多次」档"
                f"（{SKILL_MD_WARN_CHARS} 字符 / {SKILL_MD_WARN_LINES} 行）。"
                "确认它是否属于「每周数次或更少」档，否则下沉到 references/；"
                "确认后在 ARCHITECTURE.md 写一行 `读取预算档：<档位>`。"
            )

    # --- 4.11 中控路由表：死路由检查（multi-platform-routing §3）
    routing_table = skill_dir / ROUTING_TABLE_REL
    mentions_routing = "routing-table.md" in body
    if routing_table.is_file():
        table_text = routing_table.read_text(encoding="utf-8", errors="replace")
        if "| 渠道 |" not in table_text:
            errors.append(
                f"{ROUTING_TABLE_REL} 缺少固定列头"
                " `| 渠道 | 触发词 | 子 skill | 关键差异（一句话） | 协议文档 |`。"
            )
        names = set()
        for row in table_text.splitlines():
            if row.lstrip().startswith("|"):
                names.update(SKILL_NAME_RE.findall(row))
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
        summary["routes"] = sorted(names)
    elif mentions_routing:
        errors.append(f"SKILL.md 引用了 {ROUTING_TABLE_REL}，但该文件不存在（中控必须有路由表）。")

    # --- 4.12 中控疑似内联渠道专属参数
    if routing_table.is_file() and INLINED_CHANNEL_PARAM_RE.search(body):
        warnings.append(
            "SKILL.md 疑似内联了渠道专属参数（命中「N 张 / 按秒 / 按次 / ¥N」）。"
            "中控只做路由：参数上限、计费、字段名应下沉到对应渠道 skill。"
        )

    summary["line_count"] = line_count
    summary["char_count"] = char_count
    summary["has_readme"] = has_readme
    summary["has_arch"] = has_arch
    summary["ref_count"] = ref_count
    return summary


# ---------------------------------------------------------------- main

def validate(target: Path) -> tuple:
    errors: list = []
    warnings: list = []
    summary: dict = {}

    if target.is_dir():
        skill_dir, skill_md = target, target / "SKILL.md"
    else:
        skill_dir, skill_md = target.parent, target

    if not skill_md.is_file():
        return [f"文件不存在：{skill_md}"], warnings, summary

    text = skill_md.read_text(encoding="utf-8", errors="replace")
    body = check_frontmatter(text, errors, warnings)
    if not body:
        return errors, warnings, summary

    check_workspace(body, errors)
    check_iteration(body, errors, warnings)
    summary = check_file_governance(skill_dir, skill_md, body, errors, warnings)

    return errors, warnings, summary


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

    if errors:
        print(f"FAIL: {skill_md}")
        return 1

    print(f"PASS: {skill_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
