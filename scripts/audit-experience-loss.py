#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""经验流失审计：把「重构前的 skill 快照」与「重构后的 skill 全集」做机械比对，
列出**快照里有、现在找不到**的可辨识事实。

═══ 为什么需要 ═══
`multi-platform-routing.md` 要求「一条主线 + N 个渠道差异层」，主线/差异层拆分会
**大量搬移与删改文字**。刻意丢弃（实现细节、被新口径取代的旧值）是好事；
但**必须区分「刻意丢弃」与「改丢了」** —— 后者不报错、不告警，只在下一次
踩坑时才发现「这条经验明明记过」。

本工具把这件事从"人肉记忆"变成"可复跑的清单"。

═══ 判据（怎么算"一条经验"）═══
只抽**可辨识、可检索**的东西，不抽自然语言句子：
  · 反引号包裹的标识符 / 路径 / 命令 / 参数（`tools/x.py`、`--flag`、`core/Mod.Fn`）
  · 带单位的数值（`30 秒` / `56 字` / `9 张` / `$0.06` / `¥3` / `86%` / `2048×1136`）
  · 档位串（`5/8/10/12/15`）与错误码 / 全大写常量（`429`、`RATE_LIMITED`、`MAX=10`）
两侧都**规范化**（去空白、`×`→`x`、全角括号→半角、小写）后再比，压掉纯排版假阳性。

═══ 退出码 ═══
默认 **0**（审计报告，不当门）。
加 `--fail-on-missing` → 有缺失即 **1**（可挂进 CI / 重构流程的收尾步骤）。

═══ 用法 ═══
  # 1) 最常用：拿归档快照当"重构前"，拿 skills 目录当"重构后"
  python audit-experience-loss.py \\
    --archive "E:/…/_归档/01_skill快照_20260930" \\
    --current "C:/Users/Administrator/.workbuddy/skills" \\
    --only manju-* --show-all

  # 2) 只想看渠道差异层（排除公共 skill）
  python audit-experience-loss.py --archive <快照> --current <skills> --exclude "manju-asset-*"

  # 3) 挂门：缺失就失败
  python audit-experience-loss.py --archive <快照> --current <skills> --fail-on-missing

═══ 怎么读结果（★ 重要）═══
"找不到"**不等于"丢了"**。逐条判读，落进三类之一：
  A. **刻意丢弃** —— 代码内部符号（`emit()`、`prune`）、已被新口径取代的旧值。
     保留现状，**不用管**。
  B. **写法差异** —— 同一条经验两边写法不同（`30秒` vs `30 秒`、路径前缀不同）。
     确认语义在即可，**不用管**。
  C. **真缺口** —— 语义确实无处安放。**必须补**，并判断补进哪一层：
     换渠道仍成立 → 主线；因渠道而异 → 差异层（见 `experience-distillation.md` 三问）。
"""
import argparse
import io
import os
import re
import sys
from collections import OrderedDict

DOC_EXT = (".md", ".txt")

# ── 抽取模式 ──────────────────────────────────────────────────────────
BACKTICK = re.compile(r"`([^`\n]{3,80})`")
NUM_UNIT = re.compile(r"\d+(?:\.\d+)?\s*(?:秒|字|张|元|小时|分钟|天|%|万)")
SIZE = re.compile(r"\d{3,5}\s*[×xX]\s*\d{3,5}")
TIER_SET = re.compile(r"\b\d{1,2}(?:\s*/\s*\d{1,2}){2,}\b")
CODE_TOKEN = re.compile(r"\b(?:[45]\d{2}|[A-Z][A-Z0-9_]{5,})\b")

# 明显不是"经验"的通用词，抽到也是噪声
NOISE = {
    "bash", "python", "python3", "json", "jsonc", "yaml", "toml", "md", "txt",
    "mp4", "png", "jpg", "wav", "mp3", "true", "false", "none", "null", "utf-8",
    "stdin", "stdout", "stderr", "todo", "note", "example",
}

KIND_LABEL = {
    "token": "标识/路径/命令",
    "num": "数值",
    "size": "尺寸",
    "tier": "档位串",
    "code": "码/常量",
}


def read(path):
    for enc in ("utf-8", "gbk", "latin-1"):
        try:
            return io.open(path, encoding=enc).read()
        except (UnicodeDecodeError, LookupError):
            continue
        except OSError:
            return ""
    return ""


def norm(text):
    """规范化：抹掉纯排版差异，让 '30 秒' 与 '30秒' 等价。"""
    text = text.replace("\u3000", "").replace("\t", "").replace(" ", "")
    text = text.replace("×", "x").replace("＊", "*")
    text = text.replace("（", "(").replace("）", ")").replace("，", ",")
    return text.lower()


def collect_docs(root, only=None, exclude=None):
    """递归收集文档；only / exclude 用 fnmatch 风格匹配**相对路径**。"""
    import fnmatch

    docs = []
    for base, _dirs, files in os.walk(root):
        for fn in files:
            if not fn.endswith(tuple(DOC_EXT) + (".瘦身前",)) and ".md." not in fn:
                if not fn.endswith(DOC_EXT):
                    continue
            rel = os.path.relpath(os.path.join(base, fn), root).replace("\\", "/")
            if only and not any(fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(rel.split("/")[0], p)
                                for p in only):
                continue
            if exclude and any(fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(rel.split("/")[0], p)
                               for p in exclude):
                continue
            docs.append(os.path.join(base, fn))
    return sorted(docs)


def extract(text):
    """抽「可辨识事实」→ OrderedDict{原文: kind}。"""
    facts = OrderedDict()
    for m in BACKTICK.finditer(text):
        token = m.group(1).strip()
        if len(token) < 3 or token.lower() in NOISE:
            continue
        facts.setdefault(token, "token")
    for rx, kind in ((NUM_UNIT, "num"), (SIZE, "size"), (TIER_SET, "tier"), (CODE_TOKEN, "code")):
        for m in rx.finditer(text):
            facts.setdefault(re.sub(r"\s+", "", m.group(0)), kind)
    return facts


def main():
    ap = argparse.ArgumentParser(
        description="经验流失审计：重构前后 skill 文档的可辨识事实比对",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--archive", required=True,
                    help="重构前的快照目录（可含多份文档 / 子目录）")
    ap.add_argument("--current", required=True,
                    help="重构后的 skill 全集目录（递归扫描）")
    ap.add_argument("--only", nargs="*",
                    help="只比对这些路径模式（匹配相对路径或其首段），如 manju-*")
    ap.add_argument("--exclude", nargs="*",
                    help="排除这些路径模式")
    ap.add_argument("--min-doc-chars", type=int, default=800,
                    help="归档文档小于此长度跳过（默认 800）")
    ap.add_argument("--show-all", action="store_true",
                    help="列出全部缺失条目（默认每份最多 60 条）")
    ap.add_argument("--fail-on-missing", action="store_true",
                    help="有缺失即退出码 1（默认恒 0，只出报告）")
    args = ap.parse_args()

    if not os.path.isdir(args.archive):
        sys.exit("✗ --archive 不是目录：%s" % args.archive)
    if not os.path.isdir(args.current):
        sys.exit("✗ --current 不是目录：%s" % args.current)

    arch_docs = collect_docs(args.archive, args.only, args.exclude)
    cur_docs = collect_docs(args.current)
    if not arch_docs:
        sys.exit("✗ 归档里没扫到文档（检查 --archive / --only）")
    if not cur_docs:
        sys.exit("✗ 当前目录里没扫到文档（检查 --current）")

    current_blob = norm("\n".join(read(p) for p in cur_docs))

    print("归档文档 %d 份　→　当前文档 %d 份\n" % (len(arch_docs), len(cur_docs)))
    total_facts = total_missing = 0
    for path in arch_docs:
        text = read(path)
        if len(text) < args.min_doc_chars:
            continue
        facts = extract(text)
        missing = [(k, v) for k, v in facts.items() if norm(k) not in current_blob]
        rel = os.path.relpath(path, args.archive).replace("\\", "/")
        flag = "★ 需判读" if missing else "✓"
        print("=== %s  %s" % (rel, flag))
        print("    抽出 %d 条 ｜ 找不到 %d 条" % (len(facts), len(missing)))
        limit = len(missing) if args.show_all else 60
        for k, v in missing[:limit]:
            print("      [%s] %s" % (KIND_LABEL.get(v, v), k))
        if len(missing) > limit:
            print("      … 其余 %d 条（--show-all 全列）" % (len(missing) - limit))
        print()
        total_facts += len(facts)
        total_missing += len(missing)

    print("—— 合计：抽出 %d 条，找不到 %d 条 ——" % (total_facts, total_missing))
    print("★ 「找不到」≠「丢了」。逐条判读：A 刻意丢弃 / B 写法差异 / C 真缺口（C 才要补）。")
    print("  判读口径与补哪一层 → references/experience-distillation.md")

    if args.fail_on_missing and total_missing:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
