# 示例：reverse 路由

## 触发 prompt

> 使用 fetchflow：逆向这个 crackme 二进制，帮我找到它的 flag 校验逻辑。

## 期望路由

`reverse` → 委托 `reverse-flow`（`~/.zcode/skills/reverse-flow`）。

## 期望执行

1. 确认 `reverse-flow` 委托可用。
2. 建 case：`python scripts/make_case.py --case crackme --goal "找 flag 校验逻辑" --out ./work`。
3. 套用 reverse-flow 流程：
   - Intake：副本入 `artifacts/`，记录 SHA-256。
   - Analysis：`python .../reverse-flow/scripts/triage_artifact.py <样本> --out ./work/crackme/triage`；识别类型/架构/编译器/字符串。
   - Report：`report_from_triage.py` 生成初始报告。
   - Reverse/Deep：定位校验分支，映射控制/数据流，推导期望输入/flag 格式。
4. 统一输出 → `shared-evidence-protocol`（映射见 `evidence-contract.md`）。

## 期望输出（节选）

```md
当前阶段: reverse（deep）
目标: crackme（SHA-256: 9f8e…）
已路由模块: reverse（委托 reverse-flow）
已验证事实: ELF x86-64；在 offset 0x12a4 发现 strcmp 校验分支；字符串 "key=" 命中
关键证据: offset 0x12a4 校验函数；导入 strcmp；常量 "flag{…}"
推断与置信度: Medium（静态指示支持，未动态执行验证）
风险/漏洞候选: 无（本地 crackme）
建议下一步: 1) 动态单步确认输入映射；2) 写合法输入验证；3) 导出报告
```

## 回归检查

- 是否委托了 reverse-flow 阶段/证据/工具（而非自行重造）？是。
- 事实与推断分离、结论绑 offset/字符串/哈希？是。
- 仅对本地/授权样本、操作副本？是。
