"""
Context Monitor MCP Server — 精确 token 计数服务

为 Claude Code 提供精确的 token 计数能力，支持多种 tokenizer：
- tiktoken（OpenAI 模型）
- 通用估算（fallback for Claude 等模型）

使用方式：
  1. 安装依赖：pip install mcp tiktoken
  2. 在 Claude Code settings.json 中添加 MCP 配置
  3. 重启 Claude Code

MCP v2 兼容。
"""

from __future__ import annotations

import json
from typing import Any

import mcp.types as types
from mcp.server.lowlevel import Server

__all__ = ["serve"]

# ── 模型上下文窗口表 ──────────────────────────────────────────────
# 来源：各模型官方 API 文档（2026-08 更新）
MODEL_CONTEXT_LIMITS: dict[str, int] = {
    # ── Claude 5 系列 ──
    "claude-fable-5": 1_000_000,
    "claude-opus-4-8": 1_000_000,
    "claude-sonnet-5": 1_000_000,
    "claude-haiku-4-5": 200_000,
    # ── Claude 3.5/3 系列（已退役/弃用） ──
    "claude-3-5-sonnet": 200_000,
    "claude-3-5-haiku": 200_000,
    "claude-3-opus": 200_000,
    "claude-3-sonnet": 200_000,
    "claude-3-haiku": 200_000,
    # ── OpenAI GPT-4.1 系列（1M 上下文） ──
    "gpt-4.1": 1_000_000,
    "gpt-4.1-mini": 1_000_000,
    "gpt-4.1-nano": 1_000_000,
    # ── OpenAI GPT-4o 系列 ──
    "gpt-4o": 128_000,
    "gpt-4o-mini": 128_000,
    "gpt-4-turbo": 128_000,
    "gpt-4": 8_192,
    "gpt-4-32k": 32_768,
    "gpt-3.5-turbo": 16_385,
    # ── OpenAI o 系列（推理模型） ──
    "o1": 200_000,
    "o1-mini": 128_000,
    "o1-pro": 200_000,
    "o3": 200_000,
    "o3-mini": 200_000,
    "o4-mini": 200_000,
    "o3-deep-research": 200_000,
    "o4-mini-deep-research": 200_000,
    # ── OpenAI GPT-5 系列 ──
    "gpt-5-mini": 400_000,
    # ── DeepSeek ──
    "deepseek-v4-flash": 1_000_000,
    "deepseek-v4-flash-200k": 200_000,  # 旧版 200K 变体
    "deepseek-v4-pro": 1_000_000,
    "deepseek-v3": 128_000,
    "deepseek-r1": 128_000,
    # ── Google Gemini ──
    "gemini-2.5-pro": 1_048_576,
    "gemini-2.5-flash": 1_048_576,
    "gemini-2.0-flash": 1_048_576,
    # ── Meta Llama ──
    "llama-3.1-8b": 131_072,
    "llama-3.1-70b": 131_072,
    "llama-3.1-405b": 131_072,
    "llama-3.3-70b": 131_072,
    "llama-4-scout": 10_000_000,
    "llama-4-maverick": 10_000_000,
    "llama-4-behemoth": 10_000_000,
    # ── Mistral AI ──
    "mistral-large-3": 256_000,
    "mistral-small-4": 256_000,
    "mistral-medium-3.5": 256_000,
    "ministral-3": 256_000,
    "pixtral-12b": 128_000,
    "pixtral-large": 128_000,
    "codestral": 128_000,
    # ── Alibaba Qwen ──
    "qwen2.5-7b": 32_768,
    "qwen2.5-72b": 32_768,
    "qwen-plus": 131_072,
    "qwen-max": 32_768,
    "qwen-turbo": 1_000_000,
    # ── xAI Grok ──
    "grok-2": 32_768,
    "grok-3": 1_000_000,
    "grok-beta": 131_072,
    # ── Cohere ──
    "command-r": 128_000,
    "command-r-plus": 128_000,
    "command-a": 128_000,
    # ── 01.AI Yi ──
    "yi-lightning": 128_000,
    "yi-large": 128_000,
    # ── Amazon Nova ──
    "amazon-nova-pro": 300_000,
    "amazon-nova-lite": 300_000,
    "amazon-nova-micro": 128_000,
    # ── 默认 ──
    "default": 100_000,
}

# 模型别名 → 标准名映射
MODEL_ALIASES: dict[str, str] = {
    # ── Anthropic Claude ──
    "fable": "claude-fable-5",
    "fable-5": "claude-fable-5",
    "opus": "claude-opus-4-8",
    "opus-4-8": "claude-opus-4-8",
    "sonnet": "claude-sonnet-5",
    "sonnet-5": "claude-sonnet-5",
    "haiku": "claude-haiku-4-5",
    "haiku-4-5": "claude-haiku-4-5",
    "claude-3-5-sonnet": "claude-3-5-sonnet",
    "claude-3-5-haiku": "claude-3-5-haiku",
    "claude-3-opus": "claude-3-opus",
    "claude-3-sonnet": "claude-3-sonnet",
    "claude-3-haiku": "claude-3-haiku",
    # ── OpenAI GPT 系列 ──
    "gpt4o": "gpt-4o",
    "gpt-4o": "gpt-4o",
    "gpt4": "gpt-4",
    "gpt-4": "gpt-4",
    "gpt-4-32k": "gpt-4-32k",
    "gpt-4-turbo": "gpt-4-turbo",
    "gpt-3.5": "gpt-3.5-turbo",
    "gpt-3.5-turbo": "gpt-3.5-turbo",
    "gpt-4.1": "gpt-4.1",
    "gpt-4.1-mini": "gpt-4.1-mini",
    "gpt-4.1-nano": "gpt-4.1-nano",
    "gpt-5-mini": "gpt-5-mini",
    # ── OpenAI o 系列 ──
    "o1": "o1",
    "o1-mini": "o1-mini",
    "o1-pro": "o1-pro",
    "o3": "o3",
    "o3-mini": "o3-mini",
    "o4-mini": "o4-mini",
    # ── DeepSeek ──
    "deepseek": "deepseek-v4-flash",
    "deepseek-v4-flash": "deepseek-v4-flash",
    "v4-flash": "deepseek-v4-flash",
    "deepseek-v4-flash-200k": "deepseek-v4-flash-200k",
    "deepseek-v4-flash-200k[1m]": "deepseek-v4-flash-200k",
    "deepseek-v4-flash[1m]": "deepseek-v4-flash",
    "deepseek-v4-pro": "deepseek-v4-pro",
    "v4-pro": "deepseek-v4-pro",
    "deepseek-v3": "deepseek-v3",
    "deepseek-r1": "deepseek-r1",
    # ── Google Gemini ──
    "gemini": "gemini-2.5-pro",
    "gemini-2.5-pro": "gemini-2.5-pro",
    "gemini-2.5-flash": "gemini-2.5-flash",
    "gemini-2.0-flash": "gemini-2.0-flash",
    # ── Meta Llama ──
    "llama": "llama-3.3-70b",
    "llama-3.1-8b": "llama-3.1-8b",
    "llama-3.1-70b": "llama-3.1-70b",
    "llama-3.1-405b": "llama-3.1-405b",
    "llama-3.3-70b": "llama-3.3-70b",
    "llama-4-scout": "llama-4-scout",
    "llama-4-maverick": "llama-4-maverick",
    "llama-4-behemoth": "llama-4-behemoth",
    # ── Mistral AI ──
    "mistral": "mistral-large-3",
    "mistral-large-3": "mistral-large-3",
    "mistral-small-4": "mistral-small-4",
    "mistral-medium": "mistral-medium-3.5",
    "pixtral": "pixtral-12b",
    "pixtral-12b": "pixtral-12b",
    "pixtral-large": "pixtral-large",
    "codestral": "codestral",
    "ministral": "ministral-3",
    "ministral-3": "ministral-3",
    # ── Alibaba Qwen ──
    "qwen": "qwen-turbo",
    "qwen-plus": "qwen-plus",
    "qwen-max": "qwen-max",
    "qwen-turbo": "qwen-turbo",
    "qwen2.5": "qwen2.5-72b",
    "qwen2.5-72b": "qwen2.5-72b",
    "qwen2.5-7b": "qwen2.5-7b",
    # ── xAI Grok ──
    "grok": "grok-3",
    "grok-2": "grok-2",
    "grok-3": "grok-3",
    "grok-beta": "grok-beta",
    # ── Cohere ──
    "command-r": "command-r",
    "command-r-plus": "command-r-plus",
    "command-a": "command-a",
    # ── 01.AI Yi ──
    "yi": "yi-lightning",
    "yi-lightning": "yi-lightning",
    "yi-large": "yi-large",
    # ── Amazon Nova ──
    "nova": "amazon-nova-pro",
    "amazon-nova-pro": "amazon-nova-pro",
    "amazon-nova-lite": "amazon-nova-lite",
    "amazon-nova-micro": "amazon-nova-micro",
}


def resolve_model(model: str) -> str:
    """解析模型名（别名 → 标准名）。"""
    m = model.lower().strip()
    if m in MODEL_ALIASES:
        return MODEL_ALIASES[m]
    for key in MODEL_CONTEXT_LIMITS:
        if key in m or m in key:
            return key
    return model


def get_context_limit(model: str) -> int:
    """获取模型的上下文窗口上限。"""
    resolved = resolve_model(model)
    return MODEL_CONTEXT_LIMITS.get(resolved, MODEL_CONTEXT_LIMITS["default"])


# ── Tokenizer ────────────────────────────────────────────────────

_tiktoken_encodings: dict[str, Any] = {}

# 预加载标记：成功加载过 tiktoken 编码后设为 True
_tiktoken_available: bool | None = None


def _check_tiktoken_available() -> bool:
    """检查 tiktoken 是否可用（不触发下载）。"""
    global _tiktoken_available
    if _tiktoken_available is not None:
        return _tiktoken_available

    try:
        import tiktoken  # noqa: F401
        _tiktoken_available = True
        return True
    except ImportError:
        _tiktoken_available = False
        return False


def _get_tiktoken_encoding(model: str) -> Any | None:
    """获取 tiktoken 编码器，失败返回 None。

    注意：tiktoken 可能因网络问题无法下载编码文件，此时静默降级到估算。
    """
    if not _check_tiktoken_available():
        return None

    import tiktoken as _tiktoken

    model_to_encoding: dict[str, str] = {
        # OpenAI
        "gpt-4o": "o200k_base",
        "gpt-4o-mini": "o200k_base",
        "gpt-4-turbo": "cl100k_base",
        "gpt-4": "cl100k_base",
        "gpt-4-32k": "cl100k_base",
        "gpt-4.1": "o200k_base",
        "gpt-4.1-mini": "o200k_base",
        "gpt-4.1-nano": "o200k_base",
        "gpt-3.5-turbo": "cl100k_base",
        "gpt-5-mini": "o200k_base",
        # o 系列（推理模型）
        "o1": "o200k_base",
        "o1-mini": "o200k_base",
        "o1-pro": "o200k_base",
        "o3": "o200k_base",
        "o3-mini": "o200k_base",
        "o4-mini": "o200k_base",
        # DeepSeek（使用 cl100k_base 兼容）
        "deepseek-v4-flash": "cl100k_base",
        "deepseek-v4-flash-200k": "cl100k_base",
        "deepseek-v4-pro": "cl100k_base",
        "deepseek-v3": "cl100k_base",
        "deepseek-r1": "cl100k_base",
        # Qwen
        "qwen-plus": "cl100k_base",
        "qwen-turbo": "cl100k_base",
        "qwen2.5": "cl100k_base",
        # Cohere
        "command-r": "cl100k_base",
        "command-r-plus": "cl100k_base",
        "command-a": "cl100k_base",
    }

    resolved = resolve_model(model)
    enc_name = model_to_encoding.get(resolved)
    if not enc_name:
        for m, enc in model_to_encoding.items():
            if m in model or model in m:
                enc_name = enc
                break
    if not enc_name:
        return None

    cached = _tiktoken_encodings.get(enc_name)
    if cached is not None:
        return cached
    try:
        # 使用线程超时，防止 tiktoken 下载编码文件时挂起
        import threading
        result: list[Any] = []
        error: list[Exception] = []

        def _load():
            try:
                enc = _tiktoken.get_encoding(enc_name)
                result.append(enc)
            except Exception as e:
                error.append(e)

        t = threading.Thread(target=_load, daemon=True)
        t.start()
        t.join(timeout=5.0)  # 5 秒超时

        if t.is_alive():
            # 超时，放弃加载
            return None
        if error:
            return None
        if result:
            _tiktoken_encodings[enc_name] = result[0]
            return result[0]
        return None
    except Exception:
        return None


def count_tokens(text: str, model: str = "default") -> int:
    """精确计数 token 数。优先使用 tiktoken，fallback 到估算。"""
    enc = _get_tiktoken_encoding(model)
    if enc is not None:
        return len(enc.encode(text))

    # Fallback: 估算
    return _estimate_tokens(text)


def _estimate_tokens(text: str) -> int:
    """估算 token 数（中英文混合）。"""
    if not text:
        return 0
    chinese_chars = sum(1 for c in text if '一' <= c <= '鿿')
    non_chinese = len(text) - chinese_chars
    estimated = chinese_chars / 2.0 + non_chinese / 4.0
    return int(estimated)


# ── 工具定义 ──────────────────────────────────────────────────────

TOOLS: list[types.Tool] = [
    types.Tool(
        name="count_tokens",
        description="精确计数给定文本的 token 数。支持 OpenAI (tiktoken) 和 Claude 模型。",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "要计数的文本"},
                "model": {
                    "type": "string",
                    "description": "模型名（如 claude-fable-5, gpt-4o）",
                    "default": "default",
                },
            },
            "required": ["text"],
        },
    ),
    types.Tool(
        name="get_model_context_limit",
        description="查询指定模型的上下文窗口上限（token 数）。",
        inputSchema={
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "description": "模型名或别名（如 fable-5, gpt-4o, deepseek）",
                },
            },
            "required": ["model"],
        },
    ),
    types.Tool(
        name="context_status",
        description="给出当前上下文占用状态报告（基于用户提供的参数）。返回格式化状态条。",
        inputSchema={
            "type": "object",
            "properties": {
                "model": {"type": "string", "description": "当前使用的模型"},
                "used_tokens": {"type": "integer", "description": "已使用的 token 数"},
            },
            "required": ["model", "used_tokens"],
        },
    ),
]


def _handle_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """处理工具调用。"""
    try:
        if name == "count_tokens":
            text = arguments["text"]
            model = arguments.get("model", "default")
            count = count_tokens(text, model)
            return [types.TextContent(
                type="text",
                text=json.dumps({"token_count": count, "model": model}, ensure_ascii=False),
            )]

        elif name == "get_model_context_limit":
            model = arguments["model"]
            limit = get_context_limit(model)
            resolved = resolve_model(model)
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "model": resolved,
                    "context_limit": limit,
                }, ensure_ascii=False),
            )]

        elif name == "context_status":
            model = arguments["model"]
            used = arguments["used_tokens"]
            limit = get_context_limit(model)
            pct = round(used / limit * 100, 1) if limit > 0 else 0
            remaining = max(0, limit - used)

            bar_len = 20
            filled = min(bar_len, int(bar_len * pct / 100))
            bar = "█" * filled + "░" * (bar_len - filled)

            if pct < 60:
                indicator = "🟢"
                tip = "正常"
            elif pct < 80:
                indicator = "🟡"
                tip = "注意使用量"
            elif pct < 95:
                indicator = "🟠"
                tip = "建议准备新会话"
            else:
                indicator = "🔴"
                tip = "强烈建议开始新会话"

            resolved = resolve_model(model)
            formatted = (
                f"┌─ Context Usage ──────────────────────────────────┐\n"
                f"│  {bar}  {pct:.0f}%{' ' * (22 - len(str(int(pct))))}│\n"
                f"│  ─────────────────────────────────────────────    │\n"
                f"│  Model:  {resolved:<35}│\n"
                f"│  Used:   ~{used:,} / {limit:,} tokens         │\n"
                f"│  Avail:  ~{remaining:,} tokens remaining     │\n"
                f"│  ─────────────────────────────────────────────    │\n"
                f"│  {indicator} {tip:<47}│\n"
                f"└──────────────────────────────────────────────────┘"
            )

            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "model": resolved,
                    "context_limit": limit,
                    "used_tokens": used,
                    "remaining_tokens": remaining,
                    "percentage": pct,
                    "bar": f"┃{bar}┃ {pct:.0f}%",
                    "indicator": indicator,
                    "tip": tip,
                    "formatted": formatted,
                }, ensure_ascii=False),
            )]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, ensure_ascii=False),
        )]


# ── MCP Server ──────────────────────────────────────────────────

def serve() -> None:
    """以 stdio MCP 协议运行上下文监控服务。"""

    import anyio
    from mcp.server.stdio import stdio_server

    async def list_tools(_server: Server, _params: Any | None) -> types.ListToolsResult:
        return types.ListToolsResult(tools=TOOLS)

    async def call_tool(_server: Server, params: types.CallToolRequestParams) -> types.CallToolResult:
        result = _handle_tool(params.name, params.arguments or {})
        return types.CallToolResult(content=result)

    server = Server(
        "context-monitor",
        on_list_tools=list_tools,
        on_call_tool=call_tool,
        version="1.0.0",
    )

    async def main():
        async with stdio_server() as (read_stream, write_stream):
            init_opts = server.create_initialization_options()
            await server.run(read_stream, write_stream, init_opts)

    anyio.run(main)


if __name__ == "__main__":
    serve()