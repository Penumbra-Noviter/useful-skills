#!/usr/bin/env node
/**
 * 识图脚本 — 调用千问 VL 模型识图，返回文字描述。
 *
 * 用法:
 *   node vision.js <图片路径> [问题]
 *   node vision.js --url <图片链接> [问题]
 *
 * 多模型兜底:
 *   默认按顺序尝试 qwen3.7-flash → qwen3.7-flash-2026-07-15 → qwen3.5-omni-plus，
 *   当前模型报错（额度/限流/不可用）时自动切换下一个，全部失败才退出。
 *
 * 依赖:
 *   npm install dotenv (可选，如果有 .env 文件)
 *   DASHSCOPE_API_KEY 环境变量 或 同目录 .env 文件（免费在 bailian.console.aliyun.com 获取）
 */

const fs = require("fs");
const path = require("path");
const https = require("https");
const http = require("http");

// 尝试加载 .env（先找当前目录，再找脚本所在目录）；quiet 压掉 dotenv v17 的横幅日志，避免污染 stdout
try { require("dotenv").config({ quiet: true }); } catch {}
try { require("dotenv").config({ path: path.resolve(__dirname, ".env"), quiet: true }); } catch {}

const BASE_URL = process.env.DASHSCOPE_BASE_URL || "https://dashscope.aliyuncs.com/compatible-mode/v1";
// 安全：API Key 只从环境变量或同目录 .env 读取，禁止硬编码进代码
const API_KEY = process.env.DASHSCOPE_API_KEY || "";
// 请求超时（毫秒）：防止 API 挂起时兜底链卡死，可用 VISION_TIMEOUT_MS 覆盖
const TIMEOUT_MS = Number(process.env.VISION_TIMEOUT_MS) || 60000;
// 本地图片上限：阿里云百炼要求图片 base64 后不超过 10MB，超过则前置报错而非盲发
const MAX_IMAGE_BYTES = 10 * 1024 * 1024;

// 模型兜底列表：前一个模型额度/限流失败时自动切换下一个
const DEFAULT_MODELS = [
  "qwen3.7-flash",
  "qwen3.7-flash-2026-07-15",
  "qwen3.5-omni-plus",
];

function resolveModels() {
  // VISION_MODELS（逗号分隔）自定义整个列表，优先级最高
  const fromList = (process.env.VISION_MODELS || "").split(",").map((s) => s.trim()).filter(Boolean);
  if (fromList.length) return fromList;
  // VISION_MODEL 单独指定主模型（兼容旧配置）
  const single = process.env.VISION_MODEL;
  if (single) return [single];
  return DEFAULT_MODELS;
}

function parseArgs(argv = process.argv.slice(2)) {
  let imageSource = "", prompt = "", isUrl = false;

  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--url" && argv[i + 1]) {
      isUrl = true;
      imageSource = argv[++i];
    } else if (!argv[i].startsWith("--")) {
      if (!imageSource) {
        imageSource = argv[i];
      } else {
        prompt = prompt ? prompt + " " + argv[i] : argv[i];
      }
    }
  }
  if (!prompt) prompt = "请详细描述这张图片的内容。";
  return { imageSource, prompt, isUrl };
}

function resolveImageUrl(source, isUrl) {
  if (isUrl) return source;
  const resolved = path.resolve(source);
  if (!fs.existsSync(resolved)) throw new Error(`文件不存在: ${resolved}`);
  const stat = fs.statSync(resolved);
  if (stat.size > MAX_IMAGE_BYTES) {
    throw new Error(`图片过大（${stat.size} 字节 > 10MB），超过识图服务上传上限，请压缩后重试`);
  }
  const ext = path.extname(resolved).toLowerCase().replace(".", "");
  const mimeMap = { jpg: "jpeg", jpeg: "jpeg", png: "png", gif: "gif", webp: "webp", bmp: "bmp" };
  const data = fs.readFileSync(resolved);
  return `data:image/${mimeMap[ext] || "jpeg"};base64,${data.toString("base64")}`;
}

function request(payload) {
  const url = new URL(BASE_URL.replace(/\/?$/, "/") + "chat/completions");
  const body = JSON.stringify(payload);
  const transport = url.protocol === "https:" ? https : http;

  return new Promise((resolve, reject) => {
    const req = transport.request(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${API_KEY}`,
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(body),
      },
    }, (res) => {
      let data = "";
      res.on("data", (c) => data += c);
      res.on("end", () => {
        if (res.statusCode >= 400) return reject(new Error(`API ${res.statusCode}: ${data.slice(0, 300)}`));
        try {
          const parsed = JSON.parse(data);
          const raw = parsed?.choices?.[0]?.message?.content;
          // 部分兼容服务把 content 返回为数组（[{type:"text",text:"..."}])，统一取文本
          const content = Array.isArray(raw) ? raw.map((p) => p?.text || "").join("") : raw;
          if (typeof content === "string" && content.trim()) return resolve(content);
          // 200 但无文本内容：模型可能不支持识图（如文生图模型），视为失败让兜底链继续
          reject(new Error(`API 200 但无文本内容（模型 ${parsed?.model || "?"} 可能不支持识图）: ${data.slice(0, 200)}`));
        } catch { resolve(data); }
      });
    });
    req.setTimeout(TIMEOUT_MS, () => {
      req.destroy(new Error(`请求超时（${TIMEOUT_MS}ms）: 模型 ${payload.model || "?"}`));
    });
    req.on("error", reject);
    req.write(body);
    req.end();
  });
}

async function main() {
  const args = parseArgs();

  if (!API_KEY) {
    console.error("请设置 DASHSCOPE_API_KEY 环境变量或在 .env 文件中配置。");
    console.error("获取 Key: https://bailian.console.aliyun.com/");
    process.exit(1);
  }
  if (!args.imageSource) {
    console.error("用法: node vision.js <图片路径> [问题]");
    console.error("      node vision.js --url <图片链接> [问题]");
    process.exit(1);
  }

  const models = resolveModels();
  try {
    const imageUrl = resolveImageUrl(args.imageSource, args.isUrl);
    let lastError = null;

    for (const model of models) {
      try {
        const result = await request({
          model,
          messages: [{ role: "user", content: [
            { type: "image_url", image_url: { url: imageUrl } },
            { type: "text", text: args.prompt },
          ]}],
          stream: false,
          max_tokens: 1024,
        });
        if (models.length > 1) console.error(`模型 ${model} 识图成功`);
        console.log(result);
        return;
      } catch (err) {
        lastError = err;
        if (models.length > 1) console.error(`模型 ${model} 失败: ${err.message}`);
      }
    }

    console.error("识图失败（所有模型均失败）:", lastError.message);
    process.exit(1);
  } catch (err) {
    console.error("识图失败:", err.message);
    process.exit(1);
  }
}

// 直接运行时执行主流程；被 require（测试）时只导出纯函数
if (require.main === module) {
  main();
}

module.exports = { parseArgs, resolveModels, resolveImageUrl, request, DEFAULT_MODELS };
