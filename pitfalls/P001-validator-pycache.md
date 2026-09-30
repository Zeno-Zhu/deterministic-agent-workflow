# P001 · 校验器拆出子包后，跑一次就多出 `__pycache__`，下次校验被 4.2 判 FAIL

> 冷存件：**默认不读**。只有当 `INDEX.md` 中本行匹配到当前现象时才打开。

## 现象

把 503 行的 `scripts/validate-skill.py` 按「单文件 ≤300 行」拆成入口 + `scripts/wfsb_check/` 包之后：

1. 第一次跑 `python3 scripts/validate-skill.py .` → PASS；
2. 第二次跑**同一个命令** → 报
   `ERROR: 存在运行产物/依赖目录，不属于可复用能力：scripts/wfsb_check/__pycache__`；
3. 手动删掉 `__pycache__` 后又 PASS —— 再跑一次又 FAIL。

即：**校验器自己把自己判违规**，且症状是「同一命令结果翻转」。

## 根因

`import wfsb_check.checks_core` 会让解释器在包目录下写字节码缓存 `__pycache__/`。
而校验器自己的 4.2 检查（`ARTIFACT_DIRS` 含 `__pycache__`）把这个目录判为运行产物。

**看起来是「4.2 检查太严」，其实是「入口脚本没关字节码写入」。**

## 解决方案

入口脚本**在任何 `wfsb_check` 导入之前**设置：

```python
import sys
sys.dont_write_bytecode = True   # ★ 必须早于 import
```

之后无论用 `python` 还是 `python3`、带不带 `-B`，都不会再写 `__pycache__`。

## 为什么不是别的方案

- ❌ 把 `__pycache__` 从 `ARTIFACT_DIRS` 里删掉 —— 那样所有产出 skill 的真实 `__pycache__` 也就漏报了，检查等于废掉；
- ❌ 让人每次记得加 `python3 -B` —— 靠人记的规则等于没有规则；
- ❌ 每次校验完自动删 `__pycache__` —— 校验器不该有写副作用，且删目录本身有风险。

## 复现条件

- 环境：跨机通用（CPython 默认行为）
- 触发：入口脚本 import 同目录下的子包，且该子包是新建的
- 概率：必现（首次 import 时）

## 通用性判定

- 判断：`✅ 一类操作`
- 「换个项目还成立吗」自检：成立 —— **任何「CLI 入口 + 同级子包」的脚本，
  只要目录下同时有「禁止运行产物」的检查，就会撞上**。

## 晋升记录

| 日期 | 命中 | 处置 |
|---|---|---|
| 2026-09-30 | 1 | 备案 |

≤2 次：留在这里。
≥3 次且通用且可执行 → 把**通用规则**（入口脚本先关字节码写入）写进 `SKILL.md` 避坑节。
