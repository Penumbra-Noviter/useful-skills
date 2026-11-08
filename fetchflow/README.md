# fetchflow

目标驱动的「采集 + 逆向」编排 skill。薄编排层，复用两个成熟仓库，不重复造轮子。

> 版本：1.1.0（2026-11-09）。SKILL.md frontmatter 受 dao-skill 质检白名单（仅 name/description）约束，版本记录落在 README，与 PROVENANCE / DEV_LOG 修订联动。

| 模块 | 委托对象 | 复用点 |
|---|---|---|
| `modules/crawl` | [crawl4ai](https://github.com/unclecode/crawl4ai)（`pip install crawl4ai`） | 提取策略（LLM/CSS/XPath/Regex）、反爬检测、隐匿指纹、代理轮换、深爬、会话 |
| `modules/reverse` | [reverse-flow-skill](https://github.com/...)（`~/.zcode/skills/reverse-flow`）+ [REA](https://github.com/morluto/rea)（覆盖面外目标的工具加速器） | 阶段流程、证据/置信度协议、工具目录、分诊脚本；REA 决策层见 `modules/reverse/references/rea-toolchain.md` |

## 安装

```bash
# 1. 采集引擎（Python 依赖）
pip install -U crawl4ai
crawl4ai-setup

# 2. 逆向方法论（skill 委托依赖，已随 fetchflow 一起落地）
#    ~/.zcode/skills/reverse-flow/  由 reverse-flow-skill 仓库复制而来

# 3. 若浏览器缺失
python -m playwright install --with-deps chromium
```

## 目录结构

```txt
fetchflow/
  SKILL.md                 # Router：路由 + 组合 + 统一报告 + 授权边界（metadata.version 随修订更新）
  README.md
  modules/
    crawl/
      SKILL.md
      references/strategy-selection.md   # 按目标类型选提取策略（选型决策）
      references/antibot-fallback.md     # 被挡时如何降级（决策树 L0-L5）
    reverse/
      SKILL.md                            # 委托 reverse-flow 的薄壳 + REA 工具链分层
      references/evidence-contract.md     # 逆向产出如何映射到统一证据协议（含 chain 线索格式）
      references/rea-toolchain.md         # REA 工具链决策层（reverse-flow 覆盖面之外的目标）
  references/
    shared-evidence-protocol.md           # 统一报告模板（唯一权威源）
    trust-boundaries.md                   # 边界与红线（唯一权威源）
    authorization-check.md                # 授权预检判定语义（ALLOW/CHECKPOINT）
    network-profile.md                    # 任务级网络行为四档分档
    local-toolchain.md                    # 本机工具链映射（唯一权威源）
    tool-matrix.md                        # 按目标类型选工具/策略的决策表
  scripts/
    run_crawl.py                          # 薄壳：封装 crawl4ai arun/arun_many
    make_case.py                          # 建统一 case 工作区
    check_target.py                       # 授权预检（只产出 ALLOW/CHECKPOINT）
    smoke_examples.py                     # 回归 smoke（examples E3 路径可重放）
  examples/
    crawl-route.md  reverse-route.md  chain-route.md   # 路由示例 + 回归检查
    reverse-e3.md   chain-e3.md                        # E3 实测验证记录
```

## 使用

```text
使用 fetchflow：爬取 https://example.com 的所有产品价格
使用 fetchflow：逆向这个 APK，看它的校验逻辑
使用 fetchflow：这个接口一直反爬挡我，先逆向它的签名算法再帮我抓下来
```

## 边界（用户约定）

- 一句话版：爬取按「方法可行性即采」，逆向按「能力以内即做」，红线是不违背法律采集受法律保护的数据。
- **唯一权威源**：`references/trust-boundaries.md`（预检执行层 `references/authorization-check.md`），不在此处重复展开。

## 验证（证据状态）

- 爬取：**E3 已验证** —— `run_crawl.py` 对 example.com 实采通过：markdown（status=200, markdown_len=166）与 jsoncss（baseSelector+fields schema，提取到 heading）两条路径均成功。
- 逆向：**E3 已验证** —— 对本地 PyInstaller exe 走通 reverse 委托链：`make_case.py` → reverse-flow `triage_artifact.py` → `report_from_triage.py` 全部真实跑通，产出分诊 + 初始报告，并静态识别为 PySide6/Qt6 GUI 应用（详见 `examples/reverse-e3.md`）。
- 组合：**E3 已验证** —— 对授权目标 `aigirlfriendstudio.com` 走通 crawl→reverse→retry 闭环：首采只拿到 SPA 加载壳（245 字符），逆向定位为 Next.js/Turbopack 动态渲染（非 WAF），以 `wait_for` 渲染条件重试后拿到真实内容（245→29467 字符）（详见 `examples/chain-e3.md`）。
- 脚本：`py_compile` 全过；`make_case.py`、`check_target.py`、`run_crawl.py` 冒烟/E3 通过；dao-skill `quality_check` 通过。
- 回归：`python scripts/smoke_examples.py`（离线）／加 `--net` 含探测失败路径与 crawl4ai 实采（未装 crawl4ai 自动 SKIP）；2026-11-09 全量通过（0 FAIL）。
