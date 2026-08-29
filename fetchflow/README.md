# fetchflow

目标驱动的「采集 + 逆向」编排 skill。薄编排层，复用两个成熟仓库，不重复造轮子：

| 模块 | 委托对象 | 复用点 |
|---|---|---|
| `modules/crawl` | [crawl4ai](https://github.com/unclecode/crawl4ai)（`pip install crawl4ai`） | 提取策略（LLM/CSS/XPath/Regex）、反爬检测、隐匿指纹、代理轮换、深爬、会话 |
| `modules/reverse` | [reverse-flow-skill](https://github.com/...)（`~/.zcode/skills/reverse-flow`） | 阶段流程、证据/置信度协议、工具目录、分诊脚本 |

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
  SKILL.md                 # Router：路由 + 组合 + 统一报告 + 授权边界
  README.md
  modules/
    crawl/
      SKILL.md
      references/strategy-selection.md   # 按目标类型选提取策略（选型决策）
      references/antibot-fallback.md     # 被挡时如何降级（决策树）
    reverse/
      SKILL.md                            # 委托 reverse-flow 的薄壳
      references/evidence-contract.md     # 逆向产出如何映射到统一证据协议
  references/
    shared-evidence-protocol.md           # 统一事实/推断/置信度/证据绑定
    trust-boundaries.md                   # 采集 vs 逆向 的边界与红线
    tool-matrix.md                        # 按目标类型选工具/策略的决策表
  scripts/
    run_crawl.py                          # 薄壳：封装 crawl4ai arun/arun_many
    make_case.py                          # 建统一 case 工作区
  examples/
    crawl-route.md  reverse-route.md  chain-route.md
```

## 使用

```text
使用 fetchflow：爬取 https://example.com 的所有产品价格
使用 fetchflow：逆向这个 APK，看它的校验逻辑
使用 fetchflow：这个接口一直反爬挡我，先逆向它的签名算法再帮我抓下来
```

## 边界（用户约定）

- 爬取：一切从方法可行性出发可以爬取的数据都尝试采。
- 逆向：一切能力以内可以逆向的目标都逆向。
- 红线：不违背法律采集受法律保护的数据。

## 验证（证据状态）

- 爬取：**E3 已验证** —— `run_crawl.py` 对 example.com 实采通过：markdown（status=200, markdown_len=166）与 jsoncss（baseSelector+fields schema，提取到 heading）两条路径均成功。
- 逆向：**E3 已验证** —— 对本地 PyInstaller exe 走通 reverse 委托链：`make_case.py` → reverse-flow `triage_artifact.py` → `report_from_triage.py` 全部真实跑通，产出分诊 + 初始报告，并静态识别为 PySide6/Qt6 GUI 应用（详见 `examples/reverse-e3.md`）。
- 组合：**E3 已验证** —— 对授权目标 `aigirlfriendstudio.com` 走通 crawl→reverse→retry 闭环：首采只拿到 SPA 加载壳（245 字符），逆向定位为 Next.js/Turbopack 动态渲染（非 WAF），以 `wait_for` 渲染条件重试后拿到真实内容（245→29467 字符）（详见 `examples/chain-e3.md`）。
- 脚本：`py_compile` 全过；`make_case.py`、`check_target.py`、`run_crawl.py` 冒烟/E3 通过；dao-skill `quality_check` 通过。
