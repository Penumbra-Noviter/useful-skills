---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

Use /tdd where possible, at pre-agreed seams.

## 栈级坑（Resource Guide）

涉及 FastAPI / SQLAlchemy / Pydantic v2 / PySide6 实现时，先读 `references/stack-pitfalls.md`——从知识库蒸馏的实现期反复踩坑清单（枚举值存取、response_model 序列化、静态挂载顺序、Qt block 范围、主题双消费者、替身 sys.modules 缓存等），每条给「反模式 → 正解 → 验证点」。别凭训练记忆重踩这些坑。

## 交付标准

### 测试诚实协议
- **证据数组**：每次 PASS 必须附带 `command + exit code + Expected/Actual`，本会话新鲜生成。Confidence is not evidence. Exit code 0 is evidence.
- **弱化断言 = 洗白失败**：改代码不许改测试断言。如果测试不通过，修代码，不是修断言来骗过门禁。
- **Flaky 处理**：只重试一次；第二次仍失败则标 `flaky:true` 并记入 progress，不允许静默跳过。
- **验证级别标定**：每个测试结果标明 `Deterministic / Probabilistic / Manual / Live`。

### 四状态报告
子智能体完成工单时，用以下四种状态之一报告，替代 pass/fail 二元：

| 状态 | 含义 | 后续动作 |
|---|---|---|
| `DONE` | 正常完成，验收标准满足 | 进波末合并 |
| `DONE_WITH_CONCERNS` | 功能完成，但留有非阻断性顾虑 | 顾虑记入 progress 段，照常合并 |
| `NEEDS_CONTEXT` | 上下文耗尽或推理质量下降，无法完成剩余工作 | 触发交接摘要，按链中重启点机制接续 |
| `BLOCKED` | 遇到无法解决的阻塞（依赖冲突、环境问题、设计矛盾） | 禁止同模型重试，升级更强模型/新实现者 |

`BLOCKED` 状态下禁止同模型直接重试——升级模型档位或换新实现者，按「已定前提不得重开」声明接续。

## 执行

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, use /code-review to review the work.

Commit your work to the current branch.
