# 任务网络画像（network-profile）

> 吸收自 [reverse-skill](https://github.com/zhaoxuya520/reverse-skill) `skills/ops/scope-contract.md`（MIT, v1.0.1）——蒸馏其「任务级网络行为分档」概念，2026-09-01 本地化改写，非逐字复制。

`check_target.py`（授权预检）判定的是**目标级**问题：这个目标能不能碰，碰之前有哪些需要用户确认的信号。本文件补充**任务级**分档：在一个已获准的任务里，允许对目标施加什么程度的网络行为。两者正交——目标合法不代表可以把所有网络行为都开满。

## 四档模式

每个任务开始前选定一档，写入 case 记录（`make_case.py` 产出或手写）：

| 模式 | 允许 | 禁止 | 典型场景 |
|---|---|---|---|
| `offline` | 静态分析、本地样本、模拟 | 任意外连、公网 RPC | 恶意样本静态拆解、本地 APK/二进制分析 |
| `lab_only` | 仅 lab/CTF 靶机网段 | 生产/未授权 IP | CTF、受控实验网 |
| `authorized_target_only` | 仅 in_scope 列表内资产 | 列表外资产 | 有书面授权的目标测试 |
| `unrestricted_lab` | 隔离实验网（需书面依据） | 互联网生产 | 自建隔离环境的开放实验 |

## 离线样本合法化

本地自持样本（APK/二进制/固件路径存在、用户提供或用户自持）按以下条件视为可操作，不额外要求授权材料：

- 目标是本地文件路径且存在（用户自持）；
- `network_profile=offline`，不对外发包；
- 若请求启动外部行为（沙箱联网、上传分析、下载配套工具），回到 `check_target.py` 走 CHECKPOINT 流程。

此条消除「逆向本地样本还要反复无意义确认」的摩擦，保持 fetchflow 开放执行的基调。

## 与授权预检的衔接

```text
任务进入
  → check_target.py <target>       # 目标级：ALLOW / CHECKPOINT / BLOCK
  → 选定 network_profile 一档      # 任务级：本任务允许的网络行为边界
  → offline + 本地自持样本 → 直接推进
  → 网络行为超出所选档位 → 停下问用户
```

预检结果与所选档位一并写入 `shared-evidence-protocol` 报告首项：

```md
授权预检 / Authorization pre-flight: ALLOW | CHECKPOINT(<signals>) | BLOCK(<reason>)
网络画像 / Network profile: offline | lab_only | authorized_target_only | unrestricted_lab
```

## 边界原则

- **不设死门槛**：档案的作用是让用户明确知道并同意一个任务的网络边界，不是机械阻断。用户确认调档即可。
- **离线样本不豁免目标级预检**：`offline` 只是网络行为档位，本地样本若触发来源不明等信号仍走 CHECKPOINT。
- **无覆盖面默认**：任务未声明档位且目标要求网络行为时，不默认最低档也不默认最高档——停下让用户选。