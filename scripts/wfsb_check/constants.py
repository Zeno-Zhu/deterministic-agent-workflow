#!/usr/bin/env python3
"""常量、正则与通用工具 —— 校验器的唯一事实源。

阈值对应的规则权威在 references/ 的四份文档里，本文件只放「机器可判定」的那一份：

  · vnext-contracts.md         —— frontmatter / workspace / iteration
  · file-governance.md         —— 组 4 的布局与知识分层
  · multi-platform-routing.md  —— 中控路由
  · code-engineering.md        —— 代码规模与密钥纪律

改阈值 = 改本文件 ＋ 改对应文档 ＋ 跑 tests/test_validator_negative.py。
"""

from __future__ import annotations

import re
from pathlib import Path

# ------------------------------------------------------------ group 1-3

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
FIELD_RE = re.compile(r"^(name|description):\s*(.+)$", re.MULTILINE)
LOAD_FIRST_RE = re.compile(
    r"^##\s*(?:Load First|先读|必读|加载顺序)\s*$(?P<body>.*?)(?=^##\s|\Z)",
    re.MULTILINE | re.DOTALL,
)

# ------------------------------------------------------------ 4.1 残留

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

# ------------------------------------------------------------ 4.2 产物

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

# ------------------------------------------------------------ 4.3 未毕业 test

#: 测试 / 试验 / 探针文件名：只能待在 tests/，出现在 scripts/ 就是没毕业（§4）
UNPROMOTED_TEST_RE = re.compile(
    r"^(?:test|try|probe|tmp|experiment|e2e|smoke)[_-]"
    r"|[_-](?:test|try|probe|tmp|experiment|e2e|smoke)\b"
    r"|\.(?:test|spec|smoke|e2e)\.",
    re.IGNORECASE,
)

# ------------------------------------------------------------ 4.4 草稿命名

#: 草稿命名标记：不得出现在任何非 scripts/ 文件名里（§8）
DRAFT_NAME_RE = re.compile(
    r"^(?:tmp[_-]|new[_-]|old[_-]|draft[_-]|wip[_-])|"
    r"(?:[_-](?:new|old|draft|wip|copy|副本))\.",
    re.IGNORECASE,
)

# ------------------------------------------------------------ 4.6 冷存层

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

# ------------------------------------------------------------ 4.8 Load First

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

# ------------------------------------------------------------ 4.9 文档三件套

README_REQUIRED_OVER_LINES = 80
ARCHITECTURE_NAMES = ("ARCHITECTURE.md", "TECH.md", "TECHNICAL.md", "技术文档.md")

# ------------------------------------------------------------ 4.10 SKILL.md 预算

#: SKILL.md 读取预算（file-governance §7「按触发频率分档」）
SKILL_MD_WARN_CHARS = 8000     # 每日多次档
SKILL_MD_WARN_LINES = 300
SKILL_MD_ERROR_CHARS = 12000   # 每周数次档，母工作流上限
SKILL_MD_ERROR_LINES = 400

# ------------------------------------------------------------ 4.11 中控路由

ROUTING_TABLE_REL = "references/routing-table.md"
SKILL_NAME_RE = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`")
#: 疑似内联渠道专属参数（中控不该出现）：数值+张 / 计费口径 / 货币金额
INLINED_CHANNEL_PARAM_RE = re.compile(
    r"\d+\s*张|按秒|按次|按小时|[¥$￥]\s*\d", re.IGNORECASE
)

# ------------------------------------------------------------ 4.13 代码规模

#: 业务代码文件（code-engineering §0 第 7 条）
CODE_EXTS = frozenset(
    {
        ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".sh", ".bash",
        ".zsh", ".ps1", ".bat", ".cmd", ".rb", ".go", ".rs", ".java", ".kt",
        ".php", ".lua", ".pl",
    }
)
#: 软线：超了就 WARN（可在 ARCHITECTURE.md 里逐文件声明例外）
CODE_FILE_WARN_LINES = 300
#: 硬线：超了就 ERROR，不接受例外
CODE_FILE_ERROR_LINES = 600
#: 例外声明标记（ARCHITECTURE.md 里写：`单文件行数例外：<相对路径> —— <理由>`）
CODE_SCALE_DECLARATION = "单文件行数例外"

# ------------------------------------------------------------ 4.14 密钥

#: 明确不能提交的二进制 / 大文件（密钥扫描不碰它们）
BINARY_EXTS = frozenset(
    {
        ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico", ".svgz",
        ".wav", ".mp3", ".m4a", ".flac", ".mp4", ".mov", ".avi", ".webm",
        ".zip", ".gz", ".tgz", ".bz2", ".7z", ".rar", ".tar", ".jar",
        ".pdf", ".woff", ".woff2", ".ttf", ".otf", ".eot",
        ".pyc", ".pyo", ".so", ".dll", ".dylib", ".exe", ".bin", ".class",
        ".onnx", ".pt", ".pth", ".safetensors", ".ckpt", ".db", ".sqlite",
        ".xlsx", ".xls", ".docx", ".pptx",
    }
)
TEXT_SCAN_MAX_BYTES = 512 * 1024

#: 「值长得像密钥」的字符类：无空白、无逗号/括号/问号，以字母数字开头。
#: 这一条专治跨字符串边界的误报 —— 例如
#: `console.log("token :", obj.token ?? "(未知)")` 里的展示文本。
SECRET_VALUE_CLASS = r"[A-Za-z0-9_\-][A-Za-z0-9_\-._+/=:@]{15,}"

#: `键名 = "值"` 形式的密钥赋值；第 2 组是值，用于放行占位符。
#: 键必须落在代码边界上（行首 / 空白 / `,;{([` 之后），不能在引号中间。
SECRET_ASSIGN_RE = re.compile(
    r"(?i)(?:^|[\s,;{([])['\"]?"
    r"(api[_-]?key|apikey|secret|token|password|passwd|pwd|access[_-]?key"
    r"|secret[_-]?key|client[_-]?secret|auth[_-]?token)"
    r"['\"]?\s*[:=]\s*['\"](" + SECRET_VALUE_CLASS + r")['\"]"
)

#: (标签, 正则, 取值组号)；组号 0 表示整段匹配
SECRET_PATTERNS = (
    ("键值赋值", SECRET_ASSIGN_RE, 2),
    ("OpenAI 风格 token", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}"), 0),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"), 0),
    ("AWS Access Key", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), 0),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"), 0),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{6,}"), 0),
)

#: 命中值的放行词：占位符 / 环境变量读取 / 示例值都不算泄露
SECRET_PLACEHOLDER_RE = re.compile(
    r"(?i)(?:x{3,}|your|placeholder|change[_-]?me|redacted|<[^>]{1,40}>|\{\{|\$\{"
    r"|process\.env|os\.environ|getenv|\benv\b|example|dummy|sample|\bfake\b|\btest\b"
    r"|\.\.\.|\*{3,}|todo|_here\b)"
)

# ------------------------------------------------------------ 通用

SKIP_DIRS = frozenset({".git"})
IGNORED_FILES = frozenset({"_user_meta.json"})


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def arch_text(skill_dir: Path) -> str:
    """ARCHITECTURE.md（或同义文件名）全文；不存在则返回空串。"""
    for name in ARCHITECTURE_NAMES:
        candidate = skill_dir / name
        if candidate.is_file():
            return read_text(candidate)
    return ""


def has_any(text: str, patterns) -> bool:
    return any(re.search(p, text, re.IGNORECASE | re.DOTALL) for p in patterns)


def iter_files(root: Path):
    """Yield every file under root, skipping VCS internals."""
    for path in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.name not in IGNORED_FILES:
            yield path


def iter_text_files(root: Path):
    """Yield files worth text-scanning (skip binaries and oversized blobs)."""
    for path in iter_files(root):
        if path.suffix.lower() in BINARY_EXTS:
            continue
        try:
            if path.stat().st_size > TEXT_SCAN_MAX_BYTES:
                continue
        except OSError:
            continue
        yield path


def is_cold_dir(path: Path) -> bool:
    name = path.name
    if name in COLD_DIR_NAMES:
        return True
    return name.startswith("_") and not name.startswith("__")


def line_count(path: Path) -> int:
    return len(read_text(path).splitlines())
