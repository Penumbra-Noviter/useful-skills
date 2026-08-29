---
name: fetchflow-reverse
description: fetchflow 的逆向模块。委托 reverse-flow-skill 分析二进制/固件/APK/脚本/协议/校验/加密等目标的内部机制。当 fetchflow 路由到 reverse，或用户要「逆向/分析样本/破解/解锁/看校验逻辑/接口签名/反调试」时使用。复用 reverse-flow 的阶段流程、证据协议、工具目录，不重写。
---

# Reverse 模块（委托 reverse-flow-skill）

## Overview

本模块**委托** `reverse-flow` skill（已安装于 `~/.zcode/skills/reverse-flow`），复用它成熟的逆向方法论，本模块只负责三件事：**确认委托可用、把 fetchflow 的统一证据协议套上去、把逆向产出接回 fetchflow（尤其 chain 场景）**。不重写 reverse-flow 的任何阶段逻辑。

委托依赖存在性：`~/.zcode/skills/reverse-flow/SKILL.md`。若缺失，提示安装（从 reverse-flow-skill 仓库复制）。

## 复用点（来自 reverse-flow）

- 阶段流程：`分析 → 报告 → 逆向 → 深度逆向 → 漏洞研判 → 用户选择下一步`。
- 阶段闸门与交付物（`references/workflow.md`）：intake 清单、分析交付、初始报告、深度逆向、漏洞研判。
- 证据/置信度协议（`references/evidence-reporting.md`）：`facts vs inferences` 分离、High/Medium/Low 置信度、证据表（offset/函数/字符串/哈希）。
- 工具目录（`references/tool-catalog.md` + `tooling-matrix.md`）：native / android / firmware / dynamic / vulnerability profile。
- 脚本：`triage_artifact.py`、`create_case.py`、`report_from_triage.py`、`tool_audit.py`。
- CTF 口语归一化：把「解锁/去除/绕过/拿 flag」归一化为具体逆向目标。

## Workflow

1. **确认委托可用**：检查 `reverse-flow` skill 存在；缺失则提示安装，不自行降级重写。
2. **套用 reverse-flow 流程**：以 reverse-flow 的阶段推进（Intake → Analysis → Report → Reverse → Deep → Vuln review → 下一步），在其工作区内用其脚本分诊。
3. **统一证据输出**：把 reverse-flow 的产出映射到 fetchflow 的 `shared-evidence-protocol`（映射表见 `references/evidence-contract.md`）。
4. **接回 chain**：若逆向出「接口 / 协议 / 签名 / 校验输入」等可采集线索，明确标注并交给 crawl 模块。

## Output Protocol

遵循共享协议，逆向特有字段：
- 样本：哈希（SHA-256）、类型、架构、编译器/运行时指纹、packer 指示。
- 关键证据：`offset`、函数名、字符串、导入、反调试 API。
- 深度产出：状态机、数据流、协议字段表、patch 差异、漏洞候选（root cause + 影响面 + 修复）。
- 置信度：High（代码/运行直接观察）/ Medium（多静态指示）/ Low（有限证据的合理推测）。

## Boundaries

- 沿用 reverse-flow 的沙箱执行安全（操作副本、不执行未知样本、不外部服务）；能力以内即推进分析。
- 不重写 reverse-flow 的阶段流程与工具目录。
- 模糊目标（破解/解锁/绕过/拿 flag）先归一化为逆向目标，不预设拒绝。

## Quality Standard

- 确实委托了 reverse-flow（阶段、证据、工具），而非自行重造。
- 事实与推断分离，每条结论绑证据（offset/函数/字符串/哈希）。
- 产出能被 fetchflow 统一协议消费，chain 线索明确标注。
