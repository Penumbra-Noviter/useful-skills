---
name: research
description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
---

## Resource Guide

涉及引用外部项目结论、调研第三方 API、解析 LLM 结构化输出时，先读 `references/pitfalls.md`——从知识库蒸馏的调研坑（参考实现结论须本机复验、真实响应先行、findings 不复制被审逻辑、LLM JSON 三级提取）。别凭文档想象或把他人实证当自身实证。

Spin up a **background agent** to do the research, so you keep working while it reads.

Its job:

1. Investigate the question against **primary sources** (official docs, source code, specs, first-party APIs), not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single Markdown file, citing each claim's source.
3. Save it where the repo already keeps such notes; match the existing convention, and if there is none, put it somewhere sensible and say where.
