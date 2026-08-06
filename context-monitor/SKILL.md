---
name: context-monitor
description: 实时显示当前会话的上下文占用（token 用量），辅助根据上下文长度上限调度不同模型。触发词：/context、/ctx、上下文占用、token 用量、context usage
---

# 上下文监控器 (Context Monitor)

当用户输入 `/context`、`/ctx`、或询问"上下文占用多少"时，执行以下流程：

## 1. 获取当前模型

从系统提示中的 `model` 信息获取当前模型名。如果无法确定，询问用户当前使用的模型。

## 2. 估算当前上下文 token 用量

使用以下方法估算：

**方法 A：经验估算（推荐，不消耗额外上下文）**
- 回顾当前会话：系统提示 + 用户消息 + 助理消息的总长度
- 估算公式：`estimated_tokens = total_chars / 3.5`
  - 中英文混合场景下，平均每 token 约 3.5 字符
  - 纯英文场景用 `/ 4.0`，纯中文场景用 `/ 2.5`
- 系统提示基础开销：约 3000–8000 tokens（取决于启用的技能、MCP 服务器数量）
- 每轮对话：约 300–3000 tokens（取决于内容长度）

**方法 B：精确计数（如果有 MCP 分词工具）**
- 如果用户配置了 tokenizer MCP 服务，优先使用精确计数

## 3. 查表获取模型上下文上限

| 模型 | 上下文窗口 | 来源 |
|------|-----------|------|
| **Anthropic Claude 5** | | |
| claude-fable-5 / claude-opus-4-8 / claude-sonnet-5 | **1,000K tokens (1M)** | Anthropic 官方文档 |
| claude-haiku-4-5 | 200K tokens | Anthropic 官方文档 |
| **Anthropic Claude 3.5/3（已退役）** | | |
| claude-3-5-sonnet / claude-3-5-haiku / claude-3-opus | 200K tokens | 历史规格 |
| **OpenAI GPT-4.1 系列** | | |
| gpt-4.1 / gpt-4.1-mini / gpt-4.1-nano | **1,000K tokens (1M)** | OpenAI 官方文档 |
| **OpenAI GPT-4o 系列** | | |
| gpt-4o / gpt-4o-mini | 128K tokens | OpenAI 官方文档 |
| gpt-4-turbo | 128K tokens | OpenAI 官方文档 |
| gpt-4 / gpt-3.5-turbo | 8K / 16K 变体 | OpenAI 官方文档 |
| **OpenAI o 系列（推理模型）** | | |
| o1 / o3 / o3-mini / o4-mini | **200K tokens** | OpenAI 官方文档 |
| o1-mini | 128K tokens | OpenAI 官方文档 |
| **OpenAI GPT-5** | | |
| gpt-5-mini | **400K tokens** | OpenAI 官方文档 |
| **DeepSeek** | | |
| deepseek-v4-flash / deepseek-v4-pro | **1,000K tokens (1M)** · 输出 384K | DeepSeek 官方文档 |
| deepseek-v3 / deepseek-r1 | 128K tokens | DeepSeek 官方文档 |
| **Google Gemini** | | |
| gemini-2.5-pro / gemini-2.5-flash | **1,048K tokens (1M)** | Google 官方文档 |
| **Meta Llama** | | |
| llama-4-scout / llama-4-maverick | **10,000K tokens (10M)** | Meta 官方文档 |
| llama-3.1 / llama-3.3 | 128K tokens | Meta 官方文档 |
| **Mistral AI** | | |
| mistral-large-3 / mistral-small-4 / ministral-3 | **256K tokens** | Mistral 官方文档 |
| pixtral / codestral | 128K tokens | Mistral 官方文档 |
| **Alibaba Qwen** | | |
| qwen-turbo | **1,000K tokens (1M)** | DashScope API 文档 |
| qwen-plus | 128K tokens | DashScope API 文档 |
| qwen2.5 / qwen-max | 32K tokens | Qwen 官方文档 |
| **xAI Grok** | | |
| grok-3 | **1,000K tokens (1M)** | xAI 官方文档 |
| grok-beta | 128K tokens | xAI 官方文档 |
| **Cohere** | | |
| command-r / command-r-plus / command-a | 128K tokens | Cohere 官方文档 |
| **Amazon Nova** | | |
| amazon-nova-pro / amazon-nova-lite | **300K tokens** | AWS 官方文档 |
| amazon-nova-micro | 128K tokens | AWS 官方文档 |
| **01.AI** | | |
| yi-lightning / yi-large | 128K tokens | 01.AI 平台文档 |
| **未知模型** | 默认 100K，注明"估算" | — |

## 4. 输出格式

渲染一个视觉进度条，格式如下：

```
┌─ Context Usage ──────────────────────────────────┐
│  ██████████████████████████░░░░░░░░░░  72%       │
│  ─────────────────────────────────────────────    │
│  Model:  claude-fable-5                          │
│  Used:   ~144K / 200K tokens                     │
│  Avail:  ~56K tokens remaining                   │
│  ─────────────────────────────────────────────    │
│  💡 Tip: 接近 80% 时可考虑 /new 新会话            │
│          或切换到更大上下文的模型                   │
└──────────────────────────────────────────────────┘
```

进度条颜色规则：
- 0–60%: 绿色（正常）
- 60–80%: 黄色（注意）
- 80–95%: 橙色（警告）
- 95%+: 红色（紧急）

## 5. 阈值建议

根据占用百分比提供建议：

| 占用 | 建议 |
|------|------|
| < 50% | 无需操作 |
| 50–70% | 注意，长任务可继续 |
| 70–85% | 考虑开始收尾，或计划新会话 |
| 85–95% | 建议使用 `/new` 或 `/clear` 开始新会话 |
| > 95% | 模型可能开始丢失早期信息，强烈建议新会话 |

## 输出样式联动

如果用户启用了 `context-footer` 输出样式，每次回复末尾会自动追加一行紧凑的上下文占用信息。无需手动调用 `/context`。