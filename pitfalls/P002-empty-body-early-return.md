# P002 · `if not body` 把「正文为空」当成「frontmatter 不合法」，空壳 skill 全项放过

> 冷存件：**默认不读**。只有当 `INDEX.md` 中本行匹配到当前现象时才打开。

## 现象

用临时样本测「单文件行数例外声明」时，样本 `SKILL.md` 只写了 frontmatter、没有正文。
按预期它该被报一堆 `缺少：…`，实际输出里**一条治理检查都没有**，只看到 `INFO` 与 `FAIL`，
且换成「违规样本」时一切正常 —— 症状是「某些 skill 的检查好像整段没跑」。

## 根因

`validate()` 里写的是：

```python
body = check_frontmatter(text, errors, warnings)
if not body:                 # ← 想表达「frontmatter 不合格就别往下查了」
    return errors, warnings, summary
```

但 `check_frontmatter` 失败时返回 `""`，**成功但正文为空时也返回 `""`**。
两种含义共用一个哨兵值 ⇒ 一个「只有 frontmatter 的空壳 skill」把后续**全部**治理检查跳过，
只剩 frontmatter 一项通过 —— 反而是最容易藏垃圾的形态被放行。

## 解决方案

把两种结果分开：**失败返回 `None`，空正文返回 `""`**。

```python
def check_frontmatter(text, errors, warnings):
    match = FRONTMATTER_RE.search(text)
    if not match:
        errors.append("缺少有效的 YAML frontmatter。")
        return None          # ← 只有这一种情况才返回 None
    ...
    return text[match.end():]   # 可能是空串，含义是「正文确实为空」

# 调用侧
body = check_frontmatter(...)
if body is None:            # ← 不再用 `if not body`
    return errors, warnings, summary
```

同时在回归测试里加一个**空壳样本**，断言它必须 FAIL。

## 为什么不是别的方案

- ❌ 在 `if not body` 后面补一句「正文为空也报错」—— 治的是表象，哨兵值混用还在；
- ❌ 不返回 body、让每个检查自己去解析 frontmatter —— 解析重复执行，且失败语义更糊。

## 复现条件

- 环境：跨机通用
- 触发：任何「函数用同一个返回值表示两种含义」的地方
- 概率：必现（只要输入落进第二个含义）

## 通用性判定

- 判断：`✅ 一类操作`
- 「换个项目还成立吗」自检：成立 —— 这是**哨兵值语义混淆**的通病，
  在「解析函数返回内容 / 返回失败」这一对职责上最容易出现。

## 晋升记录

| 日期 | 命中 | 处置 |
|---|---|---|
| 2026-09-30 | 1 | 备案 |

≤2 次：留在这里。
≥3 次且通用且可执行 → 把通用规则（失败与「结果为空」必须用不同返回值区分）写进 `SKILL.md`。
