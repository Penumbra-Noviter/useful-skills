---
name: vision
description: 识别图片内容、分析/描述/识别本地或网络图片。当用户主动要求分析/描述/识别图片，或消息中出现 "Saved attachments:" 时使用。用 vision.js 调用视觉模型返回文字描述。
allowed-tools: Bash
---

# 图片识别

## 触发场景（仅用户主动要求时）

- 用户分享图片路径（本地或网络 URL）
- 消息中出现 "Saved attachments:" 并列出图片
- 用户明确要求分析、描述、识别图片内容

用户未主动要求时，**不要**自动识别图片，也不要主动提及此能力。

## 用法

```bash
node vision.js "<图片路径>" "请用中文描述这张图片的内容"
node vision.js --url "<图片链接>" "请用中文描述这张图片的内容"
```

## 规则

1. 本地图片使用绝对路径；网络图片用 `--url` 加可访问的链接
2. 多张图片时，对每张依次执行，全部拿到描述后再统一回复
3. 问题参数缺省时，脚本默认提示为「请详细描述这张图片的内容。」
4. 调用失败时如实报告错误信息，不要编造图片内容

## 配置

- 需要 `DASHSCOPE_API_KEY`（同目录 `.env` 或环境变量，免费在 https://bailian.console.aliyun.com/ 获取）
- 识图模型默认按顺序尝试 `qwen3.7-flash` → `qwen3.7-flash-2026-07-15` → `qwen3.5-omni-plus`；当前模型报错（额度/限流/不可用）自动切换下一个，全部失败才退出
- `VISION_MODELS` 环境变量可自定义整个模型列表（逗号分隔）；`VISION_MODEL` 仍可单独指定主模型（未设 `VISION_MODELS` 时生效）
- 中转地址可用 `DASHSCOPE_BASE_URL` 覆盖，默认 `https://dashscope.aliyuncs.com/compatible-mode/v1`
