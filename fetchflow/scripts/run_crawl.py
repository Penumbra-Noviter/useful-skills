#!/usr/bin/env python3
"""fetchflow 采集薄壳：封装 crawl4ai 的 arun / arun_many。

只做"配置组装 + 结果检查 + 反爬回退"的薄层，实际抓取/解析/提取全交给 crawl4ai。
用法示例：
    python run_crawl.py https://example.com --extraction markdown
    python run_crawl.py https://example.com/products --extraction jsoncss \
        --schema '{"baseSelector":".product","fields":[{"name":"title","selector":"h2","type":"text"},{"name":"price","selector":".price","type":"text"}]}'
    python run_crawl.py https://example.com --extraction llm --query "提取所有价格"
    python run_crawl.py https://example.com --session sid --proxy http://127.0.0.1:8080
    python run_crawl.py url1 url2 url3 --extraction markdown   # 批量
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional

# crawl4ai 是外部依赖；缺失时给出明确提示，不自行降级实现。
try:
    from crawl4ai import (  # type: ignore
        AsyncWebCrawler,
        BrowserConfig,
        CacheMode,
        CrawlerRunConfig,
        LLMExtractionStrategy,
        JsonCssExtractionStrategy,
        JsonXPathExtractionStrategy,
        LLMConfig,
    )
except ImportError as exc:  # pragma: no cover - 依赖缺失提示
    sys.exit("缺少依赖 crawl4ai。请先: pip install -U crawl4ai && crawl4ai-setup")


def _build_strategy(extraction: str, schema: Optional[str], css: Optional[str],
                    query: Optional[str]) -> Any:
    """按 --extraction 组装 crawl4ai 提取策略。只做选型，不实现解析。"""
    if extraction == "jsoncss":
        if not schema:
            sys.exit("--extraction jsoncss 需要 --schema JSON（含 baseSelector + fields）")
        parsed = json.loads(schema)
        # crawl4ai 0.9.2 的 JsonCss schema 必须含 baseSelector（容器）+ fields 列表
        if "baseSelector" not in parsed and css:
            parsed["baseSelector"] = css
        if "baseSelector" not in parsed:
            sys.exit("schema 缺 baseSelector，或用 --css 指定容器选择器")
        if "fields" not in parsed:
            sys.exit("schema 缺 fields（crawl4ai 格式：[{name, selector, type, ...}]）")
        return JsonCssExtractionStrategy(schema=parsed)
    if extraction == "jsonxpath":
        if not schema:
            sys.exit("--extraction jsonxpath 需要 --schema JSON")
        return JsonXPathExtractionStrategy(schema=json.loads(schema))
    if extraction == "llm":
        # crawl4ai 0.9.2 的 LLMConfig 拒绝 env: 前缀（防凭证外泄）。这里由
        # 本脚本自行读取环境变量并传入真实 token——这是编排层的正当职责。
        token = os.getenv("OPENAI_API_KEY")
        if not token:
            sys.exit("LLM 提取需要环境变量 OPENAI_API_KEY")
        llm = LLMConfig(provider="openai/gpt-4o-mini", api_token=token)
        return LLMExtractionStrategy(llm_config=llm, extraction_type="schema",
                                     instruction=query or "提取页面的结构化数据")
    return None  # markdown / none：用默认抓取


def _build_config(args: argparse.Namespace) -> CrawlerRunConfig:
    strategy = _build_strategy(args.extraction, args.schema, args.css, args.query)
    kwargs: Dict[str, Any] = {}
    if strategy is not None:
        kwargs["extraction_strategy"] = strategy
    if args.session:
        kwargs["session_id"] = args.session
    if args.proxy:
        kwargs["proxy"] = args.proxy
    if args.cache == "enabled":
        kwargs["cache_mode"] = CacheMode.ENABLED
    elif args.cache == "bypass":
        kwargs["cache_mode"] = CacheMode.BYPASS
    elif args.cache == "disabled":
        kwargs["cache_mode"] = CacheMode.DISABLED
    if args.wait_for:
        kwargs["wait_for"] = args.wait_for
    return CrawlerRunConfig(verbose=args.verbose, **kwargs)


def _report(res, url: str) -> None:
    """检查结果并输出统一证据摘要。CrawlResultContainer 可迭代、转发首结果属性。"""
    r = res[0] if hasattr(res, "__getitem__") else res
    print(json.dumps({
        "url": url,
        "success": bool(getattr(r, "success", None)),
        "status_code": getattr(r, "status_code", None),
        "error_message": getattr(r, "error_message", None),
        "extracted_content": (getattr(r, "extracted_content", None) or "")[:2000],
        "markdown_len": len(getattr(r, "markdown", "") or "") if hasattr(r, "markdown") else None,
        "cache_status": getattr(r, "cache_status", None),
    }, ensure_ascii=False, indent=2))


async def _run(args: argparse.Namespace) -> None:
    urls: List[str] = args.urls
    config = _build_config(args)
    browser = BrowserConfig(headless=True)
    async with AsyncWebCrawler(config=browser) as crawler:
        if len(urls) == 1:
            res = await crawler.arun(urls[0], config=config)
            _report(res, urls[0])
        else:
            results = await crawler.arun_many(urls, config=config)
            for res, url in zip(results, urls):
                _report(res, url)


def main() -> None:
    p = argparse.ArgumentParser(description="fetchflow 采集薄壳（封装 crawl4ai）")
    p.add_argument("urls", nargs="+", help="一个或多个目标 URL")
    p.add_argument("--extraction", choices=["markdown", "none", "jsoncss", "jsonxpath", "llm"],
                   default="markdown")
    p.add_argument("--schema", default=None, help="jsoncss/jsonxpath 的 JSON schema")
    p.add_argument("--css", default=None, help="jsoncss 的容器 baseSelector（schema 缺 baseSelector 时）")
    p.add_argument("--query", default=None, help="LLM 提取的指令/问题")
    p.add_argument("--session", default=None, help="复用 session_id")
    p.add_argument("--proxy", default=None, help="代理 URL")
    p.add_argument("--cache", choices=["enabled", "bypass", "disabled"], default="enabled")
    p.add_argument("--wait-for", default=None, help="等待的 CSS/JS 条件（SPA）")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()
    try:
        asyncio.run(_run(args))
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
