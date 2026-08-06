---
name: vision
description: 识别图片内容，或根据描述生成图片。当用户主动要求分析/描述/识别图片，或说"生图"/"生成图片"/"画一张"时使用。用 vision.js 调用视觉模型返回文字描述，或用 SiliconFlow 免费生图。
allowed-tools: Bash
---

# 图片识别 + 图片生成

## 图片识别（原有功能）

### 触发场景（仅用户主动要求时）

- 用户分享图片路径（本地或网络 URL）
- 消息中出现 "Saved attachments:" 并列出图片
- 用户明确要求分析、描述、识别图片内容

用户未主动要求时，**不要**自动识别图片，也不要主动提及此能力。

### 用法

```bash
node vision.js "<图片路径>" "请用中文描述这张图片的内容"
node vision.js --url "<图片链接>" "请用中文描述这张图片的内容"
```

### 规则

1. 本地图片使用绝对路径；网络图片用 `--url` 加可访问的链接
2. 多张图片时，对每张依次执行，全部拿到描述后再统一回复
3. 问题参数缺省时，脚本默认提示为「请详细描述这张图片的内容。」
4. 调用失败时如实报告错误信息，不要编造图片内容

---

## 图片生成（新增功能）

### 触发场景

- 用户说"生图"、"生成图片"、"画一张"、"生成一张..."
- 用户描述一个场景并明确要求生成图片

### 工作流程

1. **理解用户意图**：从用户描述中提取核心场景、风格、构图、色彩等要素
2. **润色英文 Prompt**：将用户的中文描述转化为详细、高质量的英文 prompt，包含：
   - 主体描述（Subject）
   - 环境/背景（Environment）
   - 风格/媒介（Style/Medium）
   - 光照/色彩（Lighting/Color）
   - 画质词（Quality boosters）
3. **执行生图**：运行 `node vision.js --generate "<prompt>" [选项]`
4. **返回结果**：告知用户图片保存路径，并描述生成内容

### 参数映射

用户描述中隐含的要求，你提取后传递给脚本：

| 用户说 | 脚本参数 |
|--------|----------|
| "16:9"、"横屏"、"宽屏" | `--width 1280 --height 720` |
| "9:16"、"竖屏"、"手机屏" | `--width 720 --height 1280` |
| "1:1"、"方形"、"头像" | `--width 1024 --height 1024` |
| "写实"、"照片级" | 在 prompt 中加 photorealistic |
| "动漫"、"二次元" | 在 prompt 中加 anime style |
| "用默认模型" | `--model kolors` |
| "用qwen模型" | `--model qwen` |

### 示例

```
用户: 生图：一只赛博朋克猫，雨夜，霓虹灯
  → 你生成 prompt: "A cyberpunk cat with neon cyan and magenta glowing fur, standing on a rainy street at night, reflections on wet pavement, cinematic lighting, photorealistic, 8k, highly detailed"
  → 执行: node vision.js --generate "A cyberpunk cat..." --width 1024 --height 1024
  → 返回: "图片已生成！保存在 D:\path\to\generated_xxx.png"
```

### 规则

1. 生图模式使用 SiliconFlow API（免费，需在 `.env` 中配置 `SILICONFLOW_API_KEY`）
2. 如果用户没有明确指定风格，默认写实风格（photorealistic）
3. 如果用户没有指定宽高比，默认 1:1 (1024×1024)
4. 默认模型为 Kolors（快手开源文生图模型），效果均衡
5. 失败时如实报告错误信息